#!/usr/bin/env python3
"""
AI News Scanner — Daily AI/government/public sector news for Webbio.

Scans RSS feeds for AI developments relevant to Dutch government digital
services and Webbio's 6 pain points (P1-P6). Posts a curated digest to Slack.

Schedule: daily at 07:00 Europe/Amsterdam
Slack channel: C0AHZGX4F0A (#ai-burgerinformatie)

Pain points (P1-P6):
  P1: Burger vindt informatie niet
  P2: Informatie niet up-to-date
  P3: Inefficiënt intern (processen)
  P4: Websitebezoek daalt
  P5: Regie kwijt in AI-tijdperk
  P6: Ontevredenheid CMS
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

# --- Configuration ---

SLACK_CHANNEL = "C0AHZGX4F0A"

# RSS feeds focused on AI, government tech, and digital transformation
RSS_FEEDS = [
    # Dutch government / public sector
    {"url": "https://www.digitaleoverheid.nl/feed/", "source": "Digitale Overheid", "weight": 1.5},
    {"url": "https://news.google.com/rss/search?q=AI+overheid+digitalisering+gemeente&hl=nl&gl=NL", "source": "Google NL Gov+AI", "weight": 1.4},
    {"url": "https://www.nu.nl/rss/Tech", "source": "nu.nl Tech", "weight": 1.0},

    # AI / tech international
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "source": "TechCrunch AI", "weight": 1.3},
    {"url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "source": "Ars Technica", "weight": 1.1},
    {"url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "source": "The Verge AI", "weight": 1.2},

    # EU regulation / policy
    {"url": "https://digital-strategy.ec.europa.eu/en/rss.xml", "source": "EU Digital", "weight": 1.4},

    # Google News custom queries (AI + government)
    {"url": "https://news.google.com/rss/search?q=AI+government+public+sector&hl=en", "source": "Google News", "weight": 1.2},
    {"url": "https://news.google.com/rss/search?q=kunstmatige+intelligentie+overheid+Nederland&hl=nl", "source": "Google Nieuws NL", "weight": 1.5},
    {"url": "https://news.google.com/rss/search?q=AI+regulation+EU&hl=en", "source": "Google News EU", "weight": 1.3},
]

# Pain point keyword groups — items matching these get boosted
PAIN_POINT_KEYWORDS = {
    "P1: Vindbaarheid": [
        "zoekfunctie", "vindbaarheid", "search", "findability", "information retrieval",
        "chatbot", "conversational", "burger informatie", "citizen information",
        "website navigatie", "zoekgedrag", "search engine", "ai zoeken",
    ],
    "P2: Actualiteit": [
        "content management", "actualiteit", "up-to-date", "outdated",
        "content lifecycle", "automated publishing", "ai content",
        "generative content", "content generation", "dynamic content",
    ],
    "P3: Efficiëntie": [
        "workflow automation", "process automation", "rpa", "efficiency",
        "automatisering", "digitalisering", "digital transformation",
        "ai workflow", "productivity", "backoffice", "operational",
    ],
    "P4: Bereik": [
        "website traffic", "digital channel", "omnichannel", "bereik",
        "engagement", "user experience", "ux", "accessibility",
        "toegankelijkheid", "wcag", "digitale inclusie",
    ],
    "P5: AI-regie": [
        "ai strategy", "ai governance", "ai policy", "ai regulation",
        "ai act", "ai wet", "responsible ai", "ai ethics", "ai risico",
        "ai framework", "ai readiness", "ai maturity", "ai adoption",
        "generative ai", "genai", "large language model", "llm",
        "openai", "anthropic", "google ai", "microsoft ai", "copilot",
    ],
    "P6: CMS": [
        "cms", "content management system", "headless cms", "drupal",
        "wordpress", "sitecore", "umbraco", "contentful",
        "ai cms", "cms ai", "smart publishing",
    ],
}

# Strong relevance keywords — must match at least one for inclusion
RELEVANCE_KEYWORDS = [
    # AI core
    "artificial intelligence", "ai", "kunstmatige intelligentie", "machine learning",
    "deep learning", "neural network", "generative ai", "genai", "llm",
    "large language model", "chatgpt", "gpt", "claude", "gemini", "copilot",
    # Government / public sector
    "government", "overheid", "gemeente", "public sector", "publieke sector",
    "municipality", "citizen", "burger", "e-government", "digitale overheid",
    "digital service", "digitale dienstverlening",
    # Regulation
    "ai act", "ai regulation", "ai wet", "ai governance", "eu regulation",
    # Digital transformation
    "digital transformation", "digitale transformatie", "digitalisering",
]

# Items matching these are always excluded
EXCLUDE_KEYWORDS = [
    "crypto", "bitcoin", "nft", "blockchain",
    "gaming", "esports", "playstation", "xbox",
    "dating app", "tiktok dance",
]


def fetch_feed(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={
        "User-Agent": "WebbioAIScanner/1.0",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_rss_items(xml_text: str, source: str, weight: float, cutoff: datetime) -> list[dict]:
    items = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items

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
            "description": strip_html(desc)[:300],
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
            "description": strip_html(summary)[:300],
            "pub_date": pub_date,
            "source": source,
            "weight": weight,
        })

    return items


def parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str)
    except (ValueError, TypeError):
        pass
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
    return re.sub(r"<[^>]+>", "", text).strip()


def is_relevant(item: dict) -> bool:
    """Check if item has at least one AI or government relevance keyword."""
    text = f"{item['title']} {item['description']}".lower()
    return any(kw in text for kw in RELEVANCE_KEYWORDS)


def score_item(item: dict) -> tuple[float, list[str]]:
    """Score item for relevance. Returns (score, matched_pain_points)."""
    text = f"{item['title']} {item['description']}".lower()

    # Hard exclude
    for kw in EXCLUDE_KEYWORDS:
        if kw in text:
            return -1.0, []

    # Must be relevant to AI or government
    if not is_relevant(item):
        return -1.0, []

    score = item["weight"]
    matched_pains = []

    # Pain point matching — biggest boost
    for pain_label, keywords in PAIN_POINT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                score += 0.5
                matched_pains.append(pain_label)
                break  # One match per pain point is enough

    # Recency bonus
    if item["pub_date"]:
        hours_ago = (datetime.now(timezone.utc) - item["pub_date"]).total_seconds() / 3600
        if hours_ago < 6:
            score += 0.4
        elif hours_ago < 12:
            score += 0.2

    # Dutch government context = extra boost
    dutch_gov = ["overheid", "gemeente", "nederland", "dutch", "rijksoverheid", "vng"]
    if any(kw in text for kw in dutch_gov):
        score += 0.6

    return score, matched_pains


def deduplicate(items: list[dict]) -> list[dict]:
    seen_titles = set()
    unique = []
    for item in items:
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


def format_slack_message(items: list[dict], scored_items: dict, now: datetime) -> list[dict]:
    """Format as Slack Block Kit message."""
    dutch_days = {0: "maandag", 1: "dinsdag", 2: "woensdag", 3: "donderdag",
                  4: "vrijdag", 5: "zaterdag", 6: "zondag"}
    dutch_months = {1: "januari", 2: "februari", 3: "maart", 4: "april",
                    5: "mei", 6: "juni", 7: "juli", 8: "augustus",
                    9: "september", 10: "oktober", 11: "november", 12: "december"}

    day_name = dutch_days[now.weekday()]
    month_name = dutch_months[now.month]
    date_str = f"{day_name} {now.day} {month_name}"

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"🤖 AI Nieuws — {date_str}"}
        },
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": "Dagelijkse AI-scan voor overheid & digitale dienstverlening"}
            ]
        },
        {"type": "divider"},
    ]

    for item in items:
        title = item["title"]
        link = item["link"]
        desc = item["description"]
        source = item["source"]
        pain_points = scored_items.get(id(item), [])

        # Truncate description
        if ". " in desc:
            desc = desc[:desc.index(". ") + 1]
        if len(desc) > 150:
            desc = desc[:147] + "..."

        # Pain point tags
        tags = ""
        if pain_points:
            tag_labels = [p.split(":")[0] for p in pain_points]  # Just P1, P2, etc.
            tags = " | " + " ".join(f"`{t}`" for t in sorted(set(tag_labels)))

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<{link}|{title}>*\n{desc}\n_{source}_{tags}"
            }
        })

    sources = sorted(set(i["source"] for i in items))
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": f"Bronnen: {' · '.join(sources)} | {len(items)} artikelen geselecteerd"}
        ]
    })

    return blocks


def post_to_slack(blocks: list[dict], channel: str, bot_token: str, fallback_text: str) -> bool:
    """Post Block Kit message to Slack."""
    url = "https://slack.com/api/chat.postMessage"
    payload = json.dumps({
        "channel": channel,
        "text": fallback_text,
        "blocks": blocks,
        "unfurl_links": False,
        "unfurl_media": False,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"Bearer {bot_token}",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "WebbioAIScanner/1.0",
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            if body.get("ok"):
                return True
            print(f"Slack API error: {body.get('error', 'unknown')}", file=sys.stderr)
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Slack HTTP error {e.code}: {body}", file=sys.stderr)
        return False


def main():
    config_path = Path(__file__).parent / "ai-news-config.json"
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)

    bot_token = config.get("slack_bot_token", os.environ.get("SLACK_BOT_TOKEN", ""))
    channel = config.get("slack_channel", SLACK_CHANNEL)
    dry_run = "--dry-run" in sys.argv

    if not bot_token and not dry_run:
        print("Error: SLACK_BOT_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    # Fetch feeds (last 24 hours)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    all_items = []
    feed_errors = []

    for feed in RSS_FEEDS:
        try:
            xml_text = fetch_feed(feed["url"])
            items = parse_rss_items(xml_text, feed["source"], feed["weight"], cutoff)
            all_items.extend(items)
            print(f"  {feed['source']}: {len(items)} items", file=sys.stderr)
        except Exception as e:
            feed_errors.append(feed["source"])
            print(f"  {feed['source']}: FAILED - {e}", file=sys.stderr)

    print(f"\nTotal: {len(all_items)} items from {len(RSS_FEEDS) - len(feed_errors)}/{len(RSS_FEEDS)} feeds", file=sys.stderr)

    if not all_items:
        print("No items found. Exiting.", file=sys.stderr)
        sys.exit(0)

    # Score and rank
    scored_pain_points = {}
    scored = []
    for item in all_items:
        score, pains = score_item(item)
        if score >= 0:
            scored.append((score, item))
            if pains:
                scored_pain_points[id(item)] = pains

    scored.sort(key=lambda x: x[0], reverse=True)
    print(f"After relevance filter: {len(scored)} items", file=sys.stderr)

    # Deduplicate and take top 5-8
    candidates = deduplicate([item for _, item in scored])
    top_items = candidates[:8]

    if not top_items:
        print("No relevant AI/government items found today. Skipping.", file=sys.stderr)
        sys.exit(0)

    # Amsterdam time
    utc_now = datetime.now(timezone.utc)
    month = utc_now.month
    amsterdam_offset = timedelta(hours=2 if 3 < month < 10 else 1)
    amsterdam_now = utc_now + amsterdam_offset

    if dry_run:
        print("\n--- DRY RUN ---\n", file=sys.stderr)
        for i, item in enumerate(top_items, 1):
            pains = scored_pain_points.get(id(item), [])
            pain_str = f" [{', '.join(pains)}]" if pains else ""
            print(f"{i}. [{item['source']}] {item['title']}{pain_str}")
            desc = item["description"]
            if ". " in desc:
                desc = desc[:desc.index(". ") + 1]
            print(f"   {desc[:100]}")
            print(f"   {item['link']}\n")
        print(f"--- {len(top_items)} items selected from {len(all_items)} total ---")
        return

    # Format and post
    blocks = format_slack_message(top_items, scored_pain_points, amsterdam_now)
    fallback = f"🤖 AI Nieuws — {len(top_items)} artikelen over AI & overheid"
    success = post_to_slack(blocks, channel, bot_token, fallback)

    if success:
        print(f"Posted {len(top_items)} items to Slack #{channel}.", file=sys.stderr)
    else:
        print("Failed to post to Slack.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
