#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_PATH="${TEMPO_CONFIG_PATH:-$SCRIPT_DIR/tempo-config.json}"
OUTPUT_DIR="${TEMPO_OUTPUT_DIR:-$SCRIPT_DIR/tempo-drafts}"
DEFAULT_TZ="${TEMPO_TIMEZONE:-Europe/Amsterdam}"
TARGET_DATE="${1:-$(date +%F)}"

python3 - "$CONFIG_PATH" "$OUTPUT_DIR" "$TARGET_DATE" "$DEFAULT_TZ" <<'PY'
import base64
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

TICKET_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_secret(value: str) -> str:
    if isinstance(value, str) and value.startswith("env:"):
        env_key = value.split(":", 1)[1]
        env_value = os.getenv(env_key)
        if not env_value:
            die(f"Missing required environment variable: {env_key}")
        return env_value
    return value


def http_json(url: str, headers=None, method="GET", payload=None):
    headers = headers or {}
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers = {**headers, "Content-Type": "application/json"}

    req = urllib.request.Request(url=url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} for {url}: {detail[:400]}") from e


def parse_iso(value: str, fallback_tz: dt.tzinfo) -> dt.datetime:
    if not value:
        return None
    cleaned = value.replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(cleaned)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=fallback_tz)
    return parsed


def seconds_between(a: dt.datetime, b: dt.datetime) -> int:
    return max(0, int((b - a).total_seconds()))


def bucket_issue(store, key):
    if key not in store:
        store[key] = {
            "git_commits": 0,
            "git_titles": [],
            "git_repos": set(),
            "jira_transitions": 0,
            "jira_labels": [],
            "calendar_seconds": 0,
            "calendar_labels": [],
            "source_flags": set(),
        }
    return store[key]


def normalize_issue(key: str) -> str:
    return (key or "").strip().upper()


def find_ticket(text: str):
    if not text:
        return None
    m = TICKET_RE.search(text.upper())
    return m.group(1) if m else None


def infer_project_code(text: str, known_projects):
    if not text:
        return None
    upper = text.upper()
    for code in sorted(known_projects, key=len, reverse=True):
        if code and code in upper:
            return code
    return None


def map_comm_task(project_code: str, comm_tasks: dict, general_task: str) -> str:
    if project_code and project_code in comm_tasks:
        return comm_tasks[project_code]
    return general_task


def github_commits_for_day(github_cfg, day: dt.date):
    token = resolve_secret(github_cfg.get("token", ""))
    username = github_cfg.get("username")
    org = github_cfg.get("org")
    if not token or not username or not org:
        die("GitHub config incomplete in tempo-config.json")

    headers = {
        "Accept": "application/vnd.github.cloak-preview+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "tempo-reconstruct/1.0",
    }

    results = []
    page = 1
    while page <= 4:
        q = f"author:{username} org:{org} author-date:{day.isoformat()}"
        params = urllib.parse.urlencode({"q": q, "per_page": 100, "page": page})
        url = f"https://api.github.com/search/commits?{params}"
        payload = http_json(url, headers=headers)
        items = payload.get("items", [])
        if not items:
            break
        results.extend(items)
        if len(items) < 100:
            break
        page += 1

    return results, headers


def github_branches_for_commit(repo_full: str, sha: str, headers: dict):
    url = f"https://api.github.com/repos/{repo_full}/commits/{sha}/branches-where-head"
    try:
        payload = http_json(url, headers=headers)
    except RuntimeError:
        return []
    branches = []
    for item in payload:
        name = item.get("name")
        if name:
            branches.append(name)
    return branches


def jira_issues_for_day(jira_cfg, day: dt.date, next_day: dt.date):
    base_url = jira_cfg.get("baseUrl", "").rstrip("/")
    email = jira_cfg.get("email")
    account_id = jira_cfg.get("accountId")
    token = resolve_secret(jira_cfg.get("token", ""))
    if not base_url or not email or not token or not account_id:
        die("Jira config incomplete in tempo-config.json")

    auth = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
        "User-Agent": "tempo-reconstruct/1.0",
    }

    jql = (
        f"assignee = '{account_id}' "
        f"AND updated >= '{day.isoformat()} 00:00' "
        f"AND updated < '{next_day.isoformat()} 00:00'"
    )

    payload = {
        "jql": jql,
        "maxResults": 100,
        "fields": ["summary", "project", "updated"],
        "expand": "changelog",
    }

    search_url = f"{base_url}/rest/api/3/search/jql"
    try:
        response = http_json(search_url, headers=headers, method="POST", payload=payload)
    except RuntimeError as e:
        die(f"Jira search endpoint failed: {e}")

    issues = response.get("issues", [])
    next_page_token = response.get("nextPageToken")

    while next_page_token:
        payload["nextPageToken"] = next_page_token
        try:
            page = http_json(search_url, headers=headers, method="POST", payload=payload)
        except RuntimeError:
            break
        issues.extend(page.get("issues", []))
        next_page_token = page.get("nextPageToken")

    return issues, account_id


def extract_jira_transitions(issue: dict, account_id: str, day_start: dt.datetime, day_end: dt.datetime):
    changelog = issue.get("changelog", {})
    histories = changelog.get("histories", [])
    transitions = 0
    labels = []

    for hist in histories:
        author = (hist.get("author") or {}).get("accountId")
        if author != account_id:
            continue
        created = parse_iso(hist.get("created"), day_start.tzinfo)
        if not created or created < day_start or created >= day_end:
            continue

        status_changes = []
        for item in hist.get("items", []):
            if item.get("field") == "status":
                from_s = item.get("fromString") or "?"
                to_s = item.get("toString") or "?"
                status_changes.append(f"{from_s}->{to_s}")

        if status_changes:
            transitions += len(status_changes)
            labels.extend(status_changes)

    return transitions, labels


def calendar_events_for_day(day: dt.date, tz_name: str):
    start = f"{day.isoformat()}T00:00:00+01:00"
    end = f"{day.isoformat()}T23:59:59+01:00"
    cmd = [
        "gog",
        "calendar",
        "events",
        "primary",
        "--from",
        start,
        "--to",
        end,
        "--account",
        "joeri@webbio.nl",
        "--json",
    ]
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        return []
    except subprocess.CalledProcessError:
        return []

    text = (proc.stdout or "").strip()
    if not text:
        return []

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []

    if isinstance(parsed, dict):
        if "events" in parsed and isinstance(parsed["events"], list):
            return parsed["events"]
        return [parsed]
    if isinstance(parsed, list):
        return parsed
    return []


def is_lunch(summary: str) -> bool:
    s = (summary or "").strip().lower()
    return any(x in s for x in ["lunch", "pauze", "break"])


def quantize_15m(seconds: int) -> int:
    if seconds <= 0:
        return 0
    return max(900, int(round(seconds / 900.0)) * 900)


def build_description(data: dict) -> str:
    parts = []
    if data["git_commits"]:
        parts.append(f"GitHub commits ({data['git_commits']})")
    if data["jira_transitions"]:
        parts.append(f"Jira status changes ({data['jira_transitions']})")
    if data["calendar_seconds"]:
        parts.append("Calendar events")
    if not parts:
        return "Werkreconstructie"
    return " + ".join(parts)


def main():
    if len(sys.argv) != 5:
        die("Usage: tempo-reconstruct.sh [YYYY-MM-DD]")

    config_path, output_dir, target_date, tz_name = sys.argv[1:5]
    config = load_json(config_path)

    rules = config.get("rules", {})
    min_daily_hours = float(rules.get("minDailyHours", 7))
    min_daily_seconds = int(min_daily_hours * 3600)
    general_task = rules.get("generalTask", "FAC-145")
    comm_tasks = rules.get("commManagementTasks", {})
    known_projects = set(comm_tasks.keys())

    try:
        day = dt.date.fromisoformat(target_date)
    except ValueError:
        die(f"Invalid date: {target_date}")

    if ZoneInfo:
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = dt.timezone(dt.timedelta(hours=1))
    else:
        tz = dt.timezone(dt.timedelta(hours=1))
    day_start = dt.datetime.combine(day, dt.time(0, 0, 0, tzinfo=tz))
    day_end = day_start + dt.timedelta(days=1)

    issue_data = {}

    commits, gh_headers = github_commits_for_day(config.get("github", {}), day)
    for item in commits:
        repo_full = ((item.get("repository") or {}).get("full_name") or "").strip()
        repo_name = ((item.get("repository") or {}).get("name") or "").strip()
        sha = (item.get("sha") or "").strip()
        commit = item.get("commit") or {}
        msg = (commit.get("message") or "").strip()

        branch_names = github_branches_for_commit(repo_full, sha, gh_headers) if repo_full and sha else []

        ticket = find_ticket(msg)
        if not ticket:
            for branch in branch_names:
                ticket = find_ticket(branch)
                if ticket:
                    break

        if not ticket:
            project_code = infer_project_code(f"{repo_name} {' '.join(branch_names)}", known_projects)
            ticket = map_comm_task(project_code, comm_tasks, general_task)

        issue = bucket_issue(issue_data, normalize_issue(ticket))
        issue["git_commits"] += 1
        if msg:
            issue["git_titles"].append(msg.splitlines()[0][:120])
        if repo_name:
            issue["git_repos"].add(repo_name)
        issue["source_flags"].add("git")

    jira_issues, jira_account_id = jira_issues_for_day(config.get("jira", {}), day, day + dt.timedelta(days=1))
    for issue in jira_issues:
        key = normalize_issue(issue.get("key") or "")
        if not key:
            continue
        transitions, labels = extract_jira_transitions(issue, jira_account_id, day_start, day_end)
        if transitions <= 0:
            continue

        bucket = bucket_issue(issue_data, key)
        bucket["jira_transitions"] += transitions
        bucket["jira_labels"].extend(labels)
        bucket["source_flags"].add("jira")

    events = calendar_events_for_day(day, tz_name)
    calendar_work_seconds = 0
    for event in events:
        summary = event.get("summary") or event.get("title") or ""
        if is_lunch(summary):
            continue

        start_raw = (
            ((event.get("start") or {}).get("dateTime"))
            if isinstance(event.get("start"), dict)
            else event.get("start")
        )
        end_raw = (
            ((event.get("end") or {}).get("dateTime"))
            if isinstance(event.get("end"), dict)
            else event.get("end")
        )

        start_dt = parse_iso(start_raw, tz)
        end_dt = parse_iso(end_raw, tz)
        if not start_dt or not end_dt:
            continue
        duration = seconds_between(start_dt, end_dt)
        if duration <= 0:
            continue

        calendar_work_seconds += duration

        ticket = find_ticket(summary)
        if not ticket:
            project_code = infer_project_code(summary, known_projects)
            ticket = map_comm_task(project_code, comm_tasks, general_task)

        bucket = bucket_issue(issue_data, normalize_issue(ticket))
        bucket["calendar_seconds"] += duration
        bucket["calendar_labels"].append(summary.strip()[:120] if summary else "Calendar event")
        bucket["source_flags"].add("calendar")

    weighted = {}
    for key, data in issue_data.items():
        git_sec = 0
        jira_sec = 0
        cal_sec = 0

        if data["git_commits"] > 0:
            git_sec = max(1800, data["git_commits"] * 2400)
        if data["jira_transitions"] > 0:
            jira_sec = data["jira_transitions"] * 900
        if data["calendar_seconds"] > 0:
            cal_sec = int(data["calendar_seconds"] * 0.5)

        score = git_sec + jira_sec + cal_sec
        if score > 0:
            weighted[key] = {
                "score": score,
                "desc": build_description(data),
                "priority": (
                    3 if "git" in data["source_flags"] else 2 if "jira" in data["source_flags"] else 1
                ),
            }

    if not weighted:
        weighted = {
            general_task: {
                "score": min_daily_seconds,
                "desc": "Geen activiteiten gevonden; fallback op algemene taak",
                "priority": 0,
            }
        }

    target_total = max(min_daily_seconds, calendar_work_seconds)
    current_total = sum(v["score"] for v in weighted.values())

    allocations = {}
    for key, info in weighted.items():
        ratio = info["score"] / current_total if current_total else 0
        allocations[key] = quantize_15m(int(target_total * ratio))

    # Enforce minimum 15 min for each non-zero bucket and normalize exact total.
    allocation_keys = list(allocations.keys())
    for key in allocation_keys:
        if allocations[key] <= 0:
            allocations[key] = 900

    total_alloc = sum(allocations.values())
    delta = target_total - total_alloc
    if allocation_keys and delta != 0:
        ordered = sorted(
            allocation_keys,
            key=lambda k: (weighted[k]["priority"], weighted[k]["score"]),
            reverse=True,
        )
        i = 0
        step = 900 if delta > 0 else -900
        guard = 0
        while delta != 0 and guard < 10000:
            key = ordered[i % len(ordered)]
            if step < 0 and allocations[key] <= 900:
                i += 1
                guard += 1
                continue
            allocations[key] += step
            delta -= step
            i += 1
            guard += 1
            if abs(delta) < 900:
                break

    sorted_issues = sorted(
        allocations.keys(),
        key=lambda k: (weighted[k]["priority"], allocations[k]),
        reverse=True,
    )

    work_start = dt.datetime.combine(day, dt.time(9, 0, 0, tzinfo=tz))

    rows = []
    cursor = work_start
    for key in sorted_issues:
        seconds = max(900, allocations[key])
        row = {
            "issueKey": key,
            "timeSpentSeconds": int(seconds),
            "startDate": day.isoformat(),
            "startTime": cursor.time().replace(microsecond=0).isoformat(),
            "description": weighted[key]["desc"][:240],
        }
        rows.append(row)
        cursor += dt.timedelta(seconds=seconds)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"tempo-draft-{day.isoformat()}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(out_path)
    print(json.dumps(rows, ensure_ascii=False))


if __name__ == "__main__":
    main()
PY
