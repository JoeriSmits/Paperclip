#!/usr/bin/env python3
"""
News Digest — Paperclip migration of OpenClaw nieuws digest cron.

Fetches Dutch/international RSS feeds, curates top 6-8 items from past 24h,
and posts a formatted digest to Discord.

Schedule: daily at 08:30 Europe/Amsterdam
Discord channel: 1478050132749455411
"""

import json
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

# --- Configuration ---

DISCORD_CHANNEL_ID = "1478050132749455411"

RSS_FEEDS = [
    {"url": "https://www.nu.nl/rss/Algemeen", "source": "nu.nl", "weight": 1.0},
    {"url": "https://www.nu.nl/rss/Economie", "source": "nu.nl", "weight": 1.2},
    {"url": "https://www.nu.nl/rss/Tech", "source": "nu.nl", "weight": 1.3},
    {"url": "https://feeds.nos.nl/nosnieuwsalgemeen", "source": "NOS", "weight": 1.1},
    {"url": "https://tweakers.net/feeds/nieuws.xml", "source": "Tweakers", "weight": 1.3},
    {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "source": "BBC", "weight": 1.0},
]

# Keywords that boost relevance score
BOOST_KEYWORDS = [
    # Politics / society
    "politiek", "kabinet", "tweede kamer", "verkiezingen", "europa", "eu",
    "oorlog", "conflict", "ukraine", "klimaat", "migratie", "woningmarkt",
    "government", "election", "war", "crisis", "policy",
    # Economy
    "economie", "inflatie", "rente", "beurs", "handelsoorlog", "tarief",
    "economy", "inflation", "trade", "gdp", "recession", "bank",
    # Tech / AI
    "ai", "artificial intelligence", "kunstmatige intelligentie", "chatgpt",
    "openai", "google", "apple", "microsoft", "cybersecurity", "hack",
    "privacy", "data", "tech", "semiconductor", "chip",
]

# Keywords that indicate items to skip
SKIP_KEYWORDS = [
    "voetbal", "eredivisie", "champions league", "formule 1", "f1",
    "sport", "olympi", "tennis", "wielren",
    "koning", "koningin", "royal", "prinses", "prins",
    "celebrity", "bn'er", "showbizz", "reality",
]

DUTCH_DAYS = {
    0: "maandag", 1: "dinsdag", 2: "woensdag",
    3: "donderdag", 4: "vrijdag", 5: "zaterdag", 6: "zondag",
}

DUTCH_MONTHS = {
    1: "januari", 2: "februari", 3: "maart", 4: "april",
    5: "mei", 6: "juni", 7: "juli", 8: "augustus",
    9: "september", 10: "oktober", 11: "november", 12: "december",
}


def fetch_feed(url: str, timeout: int = 15) -> str:
    """Fetch RSS feed content."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "PaperclipNewsDigest/1.0",
        "Accept": "application/rss+xml, application/xml, text/xml",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_rss_items(xml_text: str, source: str, weight: float, cutoff: datetime) -> list[dict]:
    """Parse RSS XML and return items from the last 24 hours."""
    items = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items

    # Handle both RSS 2.0 and Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # RSS 2.0
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        pub_date_str = item.findtext("pubDate") or ""

        if not title or not link:
            continue

        pub_date = parse_date(pub_date_str)
        if pub_date and pub_date < cutoff:
            continue

        items.append({
            "title": title,
            "link": link,
            "description": strip_html(desc)[:200],
            "pub_date": pub_date,
            "source": source,
            "weight": weight,
        })

    # Atom
    for entry in root.iter(f"{{{ns['atom']}}}entry"):
        title = (entry.findtext(f"{{{ns['atom']}}}title") or "").strip()
        link_el = entry.find(f"{{{ns['atom']}}}link")
        link = link_el.get("href", "") if link_el is not None else ""
        summary = (entry.findtext(f"{{{ns['atom']}}}summary") or "").strip()
        updated = entry.findtext(f"{{{ns['atom']}}}updated") or ""

        if not title or not link:
            continue

        pub_date = parse_date(updated)
        if pub_date and pub_date < cutoff:
            continue

        items.append({
            "title": title,
            "link": link,
            "description": strip_html(summary)[:200],
            "pub_date": pub_date,
            "source": source,
            "weight": weight,
        })

    return items


def parse_date(date_str: str) -> datetime | None:
    """Parse various date formats from RSS feeds."""
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str)
    except (ValueError, TypeError):
        pass
    # Try ISO 8601
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text).strip()


def score_item(item: dict) -> float:
    """Score an item for relevance."""
    text = f"{item['title']} {item['description']}".lower()

    # Skip sports, royals, celebrity
    for kw in SKIP_KEYWORDS:
        if kw in text:
            return -1.0

    score = item["weight"]

    # Boost for relevant keywords
    for kw in BOOST_KEYWORDS:
        if kw in text:
            score += 0.3

    # Recency bonus (newer = better)
    if item["pub_date"]:
        hours_ago = (datetime.now(timezone.utc) - item["pub_date"]).total_seconds() / 3600
        if hours_ago < 6:
            score += 0.5
        elif hours_ago < 12:
            score += 0.2

    return score


def deduplicate(items: list[dict]) -> list[dict]:
    """Remove near-duplicate titles."""
    seen_titles = set()
    unique = []
    for item in items:
        # Normalize title for dedup
        norm = re.sub(r"[^a-z0-9 ]", "", item["title"].lower())
        words = set(norm.split())
        is_dup = False
        for seen in seen_titles:
            overlap = len(words & seen) / max(len(words | seen), 1)
            if overlap > 0.6:
                is_dup = True
                break
        if not is_dup:
            seen_titles.add(frozenset(words))
            unique.append(item)
    return unique


def format_digest(items: list[dict], now: datetime) -> str:
    """Format the digest message for Discord (max 2000 chars)."""
    day_name = DUTCH_DAYS[now.weekday()]
    month_name = DUTCH_MONTHS[now.month]
    date_str = f"{day_name} {now.day} {month_name}"

    header = f"\U0001f4f0 **Nieuws \u2014 {date_str}**\n"
    sources = sorted(set(i["source"] for i in items))
    footer = f"\n_Bronnen: {' \u00b7 '.join(sources)}_"

    entry_lines = []
    for item in items:
        title = item["title"]
        link = item["link"]
        desc = item["description"]

        # Truncate description to one sentence
        if ". " in desc:
            desc = desc[:desc.index(". ") + 1]
        if len(desc) > 100:
            desc = desc[:97] + "..."

        entry_lines.append(f"\u25b8 **{title}**\n{desc} \u2014 <{link}>")

    # Build message within 2000 char Discord limit
    message = header
    for entry in entry_lines:
        candidate = message + "\n" + entry
        if len(candidate + footer) > 1990:
            break
        message = candidate
    message += footer

    return message


def post_to_discord(message: str, channel_id: str, bot_token: str) -> bool:
    """Post message to Discord channel via bot API."""
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    payload = json.dumps({"content": message}).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json",
        "User-Agent": "PaperclipNewsDigest/1.0",
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status in (200, 201):
                return True
            print(f"Discord API returned {resp.status}", file=sys.stderr)
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Discord API error {e.code}: {body}", file=sys.stderr)
        return False


def main():
    # Load config
    config_path = Path(__file__).parent / "news-config.json"
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)

    bot_token = config.get("discord_bot_token", "")
    channel_id = config.get("discord_channel_id", DISCORD_CHANNEL_ID)
    dry_run = "--dry-run" in sys.argv

    if not bot_token and not dry_run:
        print("Error: discord_bot_token not set in news-config.json", file=sys.stderr)
        sys.exit(1)

    # Fetch and parse feeds
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    all_items = []

    for feed in RSS_FEEDS:
        try:
            xml_text = fetch_feed(feed["url"])
            items = parse_rss_items(xml_text, feed["source"], feed["weight"], cutoff)
            all_items.extend(items)
            print(f"  {feed['source']}: {len(items)} items", file=sys.stderr)
        except Exception as e:
            print(f"  {feed['source']}: FAILED - {e}", file=sys.stderr)

    if not all_items:
        print("No items found from any feed. Exiting.", file=sys.stderr)
        sys.exit(0)

    # Score and rank
    scored = [(score_item(item), item) for item in all_items]
    scored = [(s, i) for s, i in scored if s >= 0]  # Remove skipped items
    scored.sort(key=lambda x: x[0], reverse=True)

    # Deduplicate and take top 6-8
    candidates = deduplicate([item for _, item in scored])
    top_items = candidates[:8]

    if len(top_items) < 3:
        print(f"Only {len(top_items)} items after filtering. Skipping digest.", file=sys.stderr)
        sys.exit(0)

    # Get Amsterdam time for the header
    # Simple CET/CEST offset (CET=+1, CEST=+2; CEST roughly Mar last Sun to Oct last Sun)
    utc_now = datetime.now(timezone.utc)
    month = utc_now.month
    amsterdam_offset = timedelta(hours=2 if 3 < month < 10 else 1)  # Simplified DST
    amsterdam_now = utc_now + amsterdam_offset

    # Format and post
    message = format_digest(top_items, amsterdam_now)

    if dry_run:
        print("\n--- DRY RUN ---\n")
        print(message)
        print(f"\n--- {len(top_items)} items selected from {len(all_items)} total ---")
        return

    success = post_to_discord(message, channel_id, bot_token)
    if success:
        print(f"Posted digest with {len(top_items)} items to Discord.", file=sys.stderr)
    else:
        print("Failed to post digest to Discord.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
