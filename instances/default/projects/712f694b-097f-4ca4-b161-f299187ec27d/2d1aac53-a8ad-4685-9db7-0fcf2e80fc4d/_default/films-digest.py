#!/usr/bin/env python3
"""
Films & Series Weekly Digest — Paperclip migration of OpenClaw films cron.

Fetches trending movies and series from TMDB, filters by quality (IMDb 7.0+),
downloads posters, and posts a formatted digest to Discord with reaction tracking.

Schedule: weekly on Fridays at 10:00 Europe/Amsterdam
Discord channel: 1478091665049915452 (#films-series)
"""

import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

# --- Configuration ---

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "films-config.json"
STATE_FILE = SCRIPT_DIR / "films-state.json"
POSTER_DIR = SCRIPT_DIR / "films-posters"
DRY_RUN = "--dry-run" in sys.argv

TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
REACTION_MAP = {"\U0001f516": "watchlist", "\u2705": "watched", "\u274c": "skipped"}


def load_config() -> dict:
    """Load configuration from films-config.json."""
    if not CONFIG_FILE.exists():
        print("Error: films-config.json not found", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_FILE) as f:
        return json.load(f)


# --- State ---

def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"watchlist": [], "watched": [], "skipped": [], "posted": [],
            "message_map": {}, "lastUpdated": None}


def save_state(state: dict):
    state["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# --- HTTP helpers ---

def fetch(url: str, retries: int = 3, timeout: int = 15) -> bytes:
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
                return r.read()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(2 ** i)


def discord_api(method: str, url: str, headers: dict, data: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as r:
            resp_body = r.read()
            return json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"  Discord API error {e.code}: {err[:200]}", file=sys.stderr)
        return {}


def discord_multipart(url: str, headers: dict, payload_json: dict, file_path: str) -> dict:
    """Post a message with a file attachment using multipart/form-data."""
    boundary = f"----PaperclipFilms{int(time.time())}"
    filename = os.path.basename(file_path)

    parts = []
    # JSON payload part
    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="payload_json"\r\n'
        f"Content-Type: application/json\r\n\r\n"
        f"{json.dumps(payload_json)}\r\n"
    )
    # File part
    with open(file_path, "rb") as f:
        file_data = f.read()
    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="files[0]"; filename="{filename}"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    )

    body = b""
    body += parts[0].encode()
    body += parts[1].encode()
    body += file_data
    body += f"\r\n--{boundary}--\r\n".encode()

    h = {k: v for k, v in headers.items() if k != "Content-Type"}
    h["Content-Type"] = f"multipart/form-data; boundary={boundary}"

    req = urllib.request.Request(url, data=body, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"  Discord multipart error {e.code}: {err[:300]}", file=sys.stderr)
        return {}


# --- TMDB + OMDB ---

def tmdb_api(path: str, api_key: str) -> dict:
    sep = "&" if "?" in path else "?"
    url = f"https://api.themoviedb.org/3{path}{sep}api_key={api_key}"
    try:
        return json.loads(fetch(url))
    except Exception as e:
        print(f"  TMDB API error: {e}", file=sys.stderr)
        return {}


def get_tmdb_trending(api_key: str, kind: str = "movie", pages: int = 2) -> list[dict]:
    """Fetch trending titles from TMDB with IMDb IDs."""
    media = "movie" if kind == "movie" else "tv"
    results = []
    for page in range(1, pages + 1):
        data = tmdb_api(f"/trending/{media}/week?language=en-US&page={page}", api_key)
        results.extend(data.get("results", []))
        time.sleep(0.3)

    enriched = []
    for item in results:
        tmdb_id = item["id"]
        detail = tmdb_api(f"/{media}/{tmdb_id}/external_ids", api_key)
        imdb_id = detail.get("imdb_id")
        if not imdb_id:
            continue
        year_str = item.get("release_date", item.get("first_air_date", ""))[:4]
        try:
            year = int(year_str)
        except (ValueError, TypeError):
            year = 0
        enriched.append({
            "tmdb_id": tmdb_id,
            "imdb_id": imdb_id,
            "title": item.get("title", item.get("name", "")),
            "year": year,
            "poster_path": item.get("poster_path"),
            "overview": item.get("overview", ""),
            "tmdb_rating": item.get("vote_average", 0),
            "media_type": media,
        })
        time.sleep(0.25)
    return enriched


def get_imdb_details(imdb_id: str) -> dict | None:
    """Fetch details from OMDB API."""
    try:
        url = f"https://www.omdbapi.com/?i={imdb_id}&apikey=trilogy"
        data = json.loads(fetch(url))
        if data.get("Response") == "False":
            return None
        year = data.get("Year", "")[:4]
        try:
            year_int = int(year)
        except (ValueError, TypeError):
            year_int = 0
        try:
            rating = float(data.get("imdbRating", "0"))
        except (ValueError, TypeError):
            rating = 0.0
        try:
            votes = int(data.get("imdbVotes", "0").replace(",", ""))
        except (ValueError, TypeError):
            votes = 0
        return {
            "imdb_id": imdb_id,
            "title": data.get("Title", ""),
            "year": year_int,
            "rating": rating,
            "votes": votes,
            "genre": data.get("Genre", ""),
            "plot": data.get("Plot", ""),
            "poster_url": data.get("Poster", ""),
            "type": data.get("Type", ""),
        }
    except Exception as e:
        print(f"  OMDB error for {imdb_id}: {e}", file=sys.stderr)
        return None


def get_trailer_url(tmdb_id: int, kind: str, api_key: str) -> str | None:
    """Fetch YouTube trailer URL from TMDB."""
    data = tmdb_api(f"/{kind}/{tmdb_id}/videos", api_key)
    for v in data.get("results", []):
        if v.get("site") == "YouTube" and v.get("type") == "Trailer":
            return f"https://youtube.com/watch?v={v['key']}"
    for v in data.get("results", []):
        if v.get("site") == "YouTube" and v.get("type") == "Teaser":
            return f"https://youtube.com/watch?v={v['key']}"
    return None


def download_poster(imdb_id: str, poster_url: str) -> str | None:
    """Download poster to local directory."""
    if not poster_url or poster_url == "N/A":
        return None
    POSTER_DIR.mkdir(exist_ok=True)
    path = POSTER_DIR / f"poster_{imdb_id}.jpg"
    if path.exists():
        path.unlink()
    try:
        img_data = fetch(poster_url)
        if not img_data or len(img_data) < 500:
            return None
        with open(path, "wb") as f:
            f.write(img_data)
        print(f"  Poster saved: {path.name} ({len(img_data)} bytes)", file=sys.stderr)
        return str(path)
    except Exception as e:
        print(f"  Poster download error {imdb_id}: {e}", file=sys.stderr)
        return None


# --- Trending fetch with filtering ---

def get_trending(state: dict, api_key: str, kind: str = "movie", count: int = 5) -> list[dict]:
    min_votes = 5000 if kind == "movie" else 1000
    min_year = datetime.now().year - 1

    print(f"\nFetching TMDB trending {kind}...", file=sys.stderr)
    tmdb_items = get_tmdb_trending(api_key, kind=kind, pages=2)
    print(f"  Found {len(tmdb_items)} TMDB items", file=sys.stderr)

    skip_ids = set(state.get("watched", []) + state.get("skipped", []))
    posted_ids = set(state.get("posted", [])) - set(state.get("watchlist", []))

    results = []
    for item in tmdb_items:
        imdb_id = item["imdb_id"]
        if imdb_id in skip_ids or imdb_id in posted_ids:
            continue
        if item["year"] < min_year:
            continue

        print(f"  Checking {imdb_id} ({item['title']})...", file=sys.stderr)
        details = get_imdb_details(imdb_id)
        if not details:
            details = {
                "imdb_id": imdb_id, "title": item["title"], "year": item["year"],
                "rating": round(item["tmdb_rating"], 1), "votes": 0,
                "genre": "", "plot": item["overview"],
                "poster_url": f"{TMDB_IMG_BASE}{item['poster_path']}" if item.get("poster_path") else "",
                "type": "movie" if kind == "movie" else "series",
            }

        if details["rating"] < 7.0:
            continue
        if 0 < details["votes"] < min_votes:
            continue

        details["_tmdb_id"] = item["tmdb_id"]
        details["_tmdb_poster"] = item.get("poster_path")
        details["_media_type"] = item.get("media_type", "movie")

        print(f"    OK: {details['title']} ({details['year']}) {details['rating']}/10", file=sys.stderr)
        results.append(details)
        if len(results) >= count:
            break
        time.sleep(0.3)

    return results


# --- Discord posting ---

def clear_channel(base_url: str, headers: dict):
    print("\nClearing channel...", file=sys.stderr)
    while True:
        msgs = discord_api("GET", f"{base_url}/messages?limit=25", headers)
        if not msgs or not isinstance(msgs, list):
            break
        for m in msgs:
            discord_api("DELETE", f"{base_url}/messages/{m['id']}", headers)
            time.sleep(0.4)
        if len(msgs) < 25:
            break
    print("  Channel cleared", file=sys.stderr)


def add_reaction(base_url: str, headers: dict, message_id: str, emoji: str):
    encoded = urllib.request.quote(emoji)
    url = f"{base_url}/messages/{message_id}/reactions/{encoded}/@me"
    req = urllib.request.Request(url, data=b"", headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as _:
            pass
    except urllib.error.HTTPError as e:
        if e.code == 429:
            try:
                retry = json.loads(e.read()).get("retry_after", 1)
            except Exception:
                retry = 1
            time.sleep(retry + 0.5)
        else:
            print(f"  Reaction error {emoji}: {e.code}", file=sys.stderr)
    time.sleep(0.3)


def collect_reactions(state: dict, base_url: str, headers: dict) -> dict:
    """Read reactions on existing messages and update state."""
    msg_map = state.get("message_map", {})
    if not msg_map:
        return state

    print("\nCollecting reactions...", file=sys.stderr)
    for msg_id, imdb_id in msg_map.items():
        for emoji, action in REACTION_MAP.items():
            encoded = urllib.request.quote(emoji)
            url = f"{base_url}/messages/{msg_id}/reactions/{encoded}?limit=100"
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, context=SSL_CTX) as r:
                    users = json.loads(r.read())
                non_bot = [u for u in users if not u.get("bot", False)]
                if non_bot:
                    print(f"  {imdb_id} -> {action} ({len(non_bot)} users)", file=sys.stderr)
                    for lst in ["watchlist", "watched", "skipped"]:
                        if imdb_id in state.get(lst, []):
                            state[lst].remove(imdb_id)
                    state.setdefault(action, []).append(imdb_id)
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    try:
                        retry = json.loads(e.read()).get("retry_after", 1)
                    except Exception:
                        retry = 1
                    time.sleep(retry + 0.5)
            time.sleep(0.5)

    return state


def post_title(details: dict, poster_path: str | None,
               base_url: str, headers: dict) -> str | None:
    """Post a single title to Discord with poster and IMDb link."""
    imdb_id = details["imdb_id"]
    genre = details["genre"] if details["genre"] else "Film"
    plot = details["plot"]
    if not plot or plot == "N/A":
        plot = ""
    elif len(plot) > 200:
        plot = plot[:197] + "..."

    lines = [
        f"**{details['title']}** ({details['year']}) \u2014 \u2b50 {details['rating']}/10",
        f"\U0001f3ad {genre}",
    ]
    if plot:
        lines.append(f"\n> {plot}")

    imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
    trailer_url = details.get("trailer_url")
    link_line = f"\U0001f3ac [IMDb]({imdb_url})"
    if trailer_url:
        link_line += f" | [\u25b6\ufe0f Trailer]({trailer_url})"
    lines.append(f"\n{link_line}")

    content = "\n".join(lines)

    if DRY_RUN:
        print(f"  [DRY RUN] Would post: {details['title']} (poster: {poster_path})", file=sys.stderr)
        return None

    msg_url = f"{base_url}/messages"

    if poster_path and os.path.exists(poster_path) and os.path.getsize(poster_path) > 500:
        payload = {"content": content}
        resp = discord_multipart(msg_url, headers, payload, poster_path)
    else:
        resp = discord_api("POST", msg_url, headers, {"content": content})

    msg_id = resp.get("id")
    if msg_id:
        for emoji in REACTION_MAP:
            add_reaction(base_url, headers, msg_id, emoji)

    time.sleep(0.5)
    return msg_id


# --- Main ---

def main():
    config = load_config()
    bot_token = config.get("discord_bot_token", "")
    channel_id = config.get("discord_channel_id", "1478091665049915452")
    tmdb_api_key = config.get("tmdb_api_key", "")

    if not bot_token and not DRY_RUN:
        print("Error: discord_bot_token not set in films-config.json", file=sys.stderr)
        sys.exit(1)
    if not tmdb_api_key:
        print("Error: tmdb_api_key not set in films-config.json", file=sys.stderr)
        sys.exit(1)

    base_url = f"https://discord.com/api/v10/channels/{channel_id}"
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json",
        "User-Agent": "PaperclipFilmsDigest/1.0",
    }

    week = datetime.now().isocalendar()[1]
    year = datetime.now().year
    print(f"=== Films & Series Digest \u2014 week {week}, {year} ===", file=sys.stderr)
    if DRY_RUN:
        print("*** DRY RUN MODE ***\n", file=sys.stderr)

    state = load_state()
    print(f"State: {len(state['watched'])} watched, {len(state['skipped'])} skipped, "
          f"{len(state['watchlist'])} watchlist, {len(state['posted'])} posted", file=sys.stderr)

    # Collect reactions from previous week
    if not DRY_RUN:
        state = collect_reactions(state, base_url, headers)

    # Fetch trending
    series = get_trending(state, tmdb_api_key, kind="series", count=5)
    films = get_trending(state, tmdb_api_key, kind="movie", count=5)

    if not series and not films:
        print("\nNothing found to post.", file=sys.stderr)
        save_state(state)
        return

    # Fetch posters and trailers
    print("\nFetching posters & trailers...", file=sys.stderr)
    for item in series + films:
        tmdb_id = item.get("_tmdb_id")
        media_type = item.get("_media_type", "movie")
        tmdb_poster = item.get("_tmdb_poster")

        poster_url = f"{TMDB_IMG_BASE}{tmdb_poster}" if tmdb_poster else item.get("poster_url", "")
        item["poster_local"] = download_poster(item["imdb_id"], poster_url)

        if tmdb_id:
            item["trailer_url"] = get_trailer_url(tmdb_id, media_type, tmdb_api_key)

    # Clear channel and post
    if not DRY_RUN:
        clear_channel(base_url, headers)

    message_map = {}

    if series:
        if not DRY_RUN:
            discord_api("POST", f"{base_url}/messages", headers,
                        {"content": f"\U0001f4fa **Trending Series \u2014 week {week}, {year}** | "
                                    f"_IMDb 7.0+ | Alleen {year - 1}\u2013{year}_"})
            time.sleep(0.5)
        for item in series:
            print(f"  Posting: {item['title']}", file=sys.stderr)
            msg_id = post_title(item, item.get("poster_local"), base_url, headers)
            if msg_id:
                message_map[msg_id] = item["imdb_id"]

    if films:
        if not DRY_RUN:
            discord_api("POST", f"{base_url}/messages", headers,
                        {"content": f"\U0001f3ac **Trending Films \u2014 week {week}, {year}** | "
                                    f"_IMDb 7.0+ | Alleen {year - 1}\u2013{year}_"})
            time.sleep(0.5)
        for item in films:
            print(f"  Posting: {item['title']}", file=sys.stderr)
            msg_id = post_title(item, item.get("poster_local"), base_url, headers)
            if msg_id:
                message_map[msg_id] = item["imdb_id"]

    # Update state
    all_ids = [i["imdb_id"] for i in series + films]
    state["posted"] = list(set(state.get("posted", []) + all_ids))
    state["message_map"] = message_map
    if not DRY_RUN:
        save_state(state)
        print(f"\nDone! {len(series)} series + {len(films)} films posted.", file=sys.stderr)
    else:
        print(f"\n[DRY RUN] Would post {len(series)} series + {len(films)} films.", file=sys.stderr)

    # Clean up poster files
    if POSTER_DIR.exists():
        for p in POSTER_DIR.glob("poster_*.jpg"):
            try:
                p.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    main()
