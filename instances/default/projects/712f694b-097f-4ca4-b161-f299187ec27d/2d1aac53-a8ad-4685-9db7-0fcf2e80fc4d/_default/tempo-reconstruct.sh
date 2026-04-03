#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_PATH="${TEMPO_CONFIG_PATH:-$SCRIPT_DIR/tempo-config.json}"
OUTPUT_DIR="${TEMPO_OUTPUT_DIR:-$SCRIPT_DIR/tempo-drafts}"
DEFAULT_TZ="${TEMPO_TIMEZONE:-Europe/Amsterdam}"
TARGET_DATE=""
for arg in "$@"; do
  case "$arg" in
    *) TARGET_DATE="$arg" ;;
  esac
done
TARGET_DATE="${TARGET_DATE:-$(date +%F)}"

python3 - "$CONFIG_PATH" "$OUTPUT_DIR" "$TARGET_DATE" "$DEFAULT_TZ" <<'PY'
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request

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


def http_json(url: str, headers=None, method="GET"):
    headers = headers or {}
    req = urllib.request.Request(url=url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} for {url}: {detail[:400]}") from e


def fetch_worklogs(tempo_token: str, account_id: str, day: dt.date) -> list:
    """Fetch all worklogs for account_id on a given day from Tempo v4 API."""
    headers = {
        "Authorization": f"Bearer {tempo_token}",
        "Accept": "application/json",
    }
    date_str = day.isoformat()
    url = f"https://api.tempo.io/4/worklogs/user/{account_id}?from={date_str}&to={date_str}"
    response = http_json(url, headers=headers)
    return response.get("results", [])


def format_duration(seconds: int) -> str:
    h, remainder = divmod(seconds, 3600)
    m = remainder // 60
    return f"{h}h {m:02d}m"


def main():
    if len(sys.argv) != 5:
        die("Usage: tempo-reconstruct.sh [YYYY-MM-DD]")

    config_path, output_dir, target_date, tz_name = sys.argv[1:5]
    config = load_json(config_path)

    tempo_token = resolve_secret(config.get("tempo", {}).get("token", ""))
    account_id = config.get("jira", {}).get("accountId", "")
    if not tempo_token:
        die("TEMPO_TOKEN not set")
    if not account_id:
        die("jira.accountId not configured")

    try:
        day = dt.date.fromisoformat(target_date)
    except ValueError:
        die(f"Invalid date: {target_date}")

    worklogs = fetch_worklogs(tempo_token, account_id, day)

    total_seconds = 0
    rows = []
    for wl in worklogs:
        issue_obj = wl.get("issue") or {}
        issue_key = issue_obj.get("key", "")
        if not issue_key:
            # Tempo v4 returns issue.id (numeric) not key; extract from description
            desc_text = wl.get("description") or ""
            m = TICKET_RE.search(desc_text.upper())
            issue_key = m.group(1) if m else f"issue-{issue_obj.get('id', 'unknown')}"
        seconds = wl.get("timeSpentSeconds", 0)
        description = wl.get("description") or ""
        start_date = wl.get("startDate", day.isoformat())
        start_time = wl.get("startTime", "09:00:00")
        worklog_id = wl.get("tempoWorklogId", "?")

        total_seconds += seconds
        rows.append({
            "tempoWorklogId": worklog_id,
            "issueKey": issue_key,
            "timeSpentSeconds": seconds,
            "duration": format_duration(seconds),
            "startDate": start_date,
            "startTime": start_time,
            "description": description,
        })

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"tempo-{day.isoformat()}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(out_path)
    print(json.dumps(rows, ensure_ascii=False))

    print(f"\n{day.isoformat()}: {len(rows)} worklog(s), {format_duration(total_seconds)} total", file=sys.stderr)


if __name__ == "__main__":
    main()
PY
