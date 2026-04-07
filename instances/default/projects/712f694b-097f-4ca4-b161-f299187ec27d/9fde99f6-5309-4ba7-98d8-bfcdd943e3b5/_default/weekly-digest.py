#!/usr/bin/env python3
"""
Weekly AI Research Digest — Webbio positioning & thought leadership.

Aggregates the week's AI/government/public sector news from RSS feeds,
synthesizes a structured digest, and posts to Slack.

Modes:
  (default)      -- standalone: fetch feeds, call Anthropic API, post to Slack
  --fetch-json   -- agent mode: fetch feeds, output articles + prompt as JSON
  --post-digest FILE -- agent mode: post pre-generated digest text to Slack
  --dry-run      -- print digest to stdout instead of posting
  --no-claude    -- skip Claude synthesis (with --dry-run: show article list only)

Schedule: Friday 16:00 Europe/Amsterdam (via Paperclip routine or LaunchAgent)
Slack channel: C0AHZGX4F0A (#ai-burgerinformatie)
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Import shared infrastructure from daily scanner
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module

# We import the daily scanner module to reuse its feed parsing and scoring
scanner = import_module("ai-news-scanner")

# --- Configuration ---

SLACK_CHANNEL = "C0AHZGX4F0A"
DIGEST_LOOKBACK_DAYS = 7
MAX_ITEMS_FOR_SYNTHESIS = 20  # Top scored items sent to Claude


def call_claude(prompt: str, api_key: str, max_tokens: int = 2000) -> str:
    """Call Anthropic Messages API to synthesize the digest."""
    url = "https://api.anthropic.com/v1/messages"
    payload = json.dumps({
        "model": "claude-sonnet-4-5-20250514",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
        "User-Agent": "WebbioWeeklyDigest/1.0",
    })

    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        return body["content"][0]["text"]


def build_synthesis_prompt(items: list[dict], scored_pains: dict) -> str:
    """Build the prompt for Claude to synthesize the weekly digest."""
    articles = []
    for i, item in enumerate(items, 1):
        pains = scored_pains.get(id(item), [])
        pain_str = f" [{', '.join(pains)}]" if pains else ""
        articles.append(
            f"{i}. [{item['source']}] {item['title']}{pain_str}\n"
            f"   {item['description'][:200]}\n"
            f"   URL: {item['link']}"
        )

    articles_text = "\n\n".join(articles)

    return f"""Je bent de AI-redacteur voor Webbio, een digitaal bureau dat gemeenten en overheidsorganisaties helpt met digitale dienstverlening. Webbio focust op 6 pijnpunten:

P1: Burger vindt informatie niet (vindbaarheid)
P2: Informatie niet up-to-date (actualiteit)
P3: Inefficient intern (processen/workflows)
P4: Websitebezoek daalt (bereik/engagement)
P5: Regie kwijt in AI-tijdperk (AI-strategie)
P6: Ontevredenheid CMS (content management)

Hieronder staan de {len(items)} meest relevante AI/overheid-artikelen van deze week:

{articles_text}

Schrijf een wekelijks digest in het Nederlands met deze structuur:

## Top 3 ontwikkelingen van de week
Per ontwikkeling (kies de 3 belangrijkste):
- **Titel**: korte, pakkende headline
- **Wat**: 2-3 zinnen samenvatting
- **Bron**: link naar het artikel

## Wat betekent dit voor gemeenten?
Per ontwikkeling: 1-2 zinnen over de concrete impact voor Nederlandse gemeenten en overheidsorganisaties. Koppel expliciet aan de relevante Webbio pijnpunten (P1-P6).

## Joeri's take
Per ontwikkeling: 1 scherpe zin die Joeri als CTO/thought leader op LinkedIn zou posten. Moet inzichtelijk, opiniërend en deelbaar zijn.

## Gespreksstarter van de week
1 concrete aanbeveling of gesprekspunt dat een Webbio-consultant direct kan gebruiken in klantgesprekken deze week. Maak het specifiek en actionable.

Schrijf beknopt, direct, en zonder filler. Gebruik markdown formatting."""


def format_slack_digest(digest_text: str, now: datetime, item_count: int) -> list[dict]:
    """Format the synthesized digest as Slack Block Kit blocks."""
    dutch_days = {0: "maandag", 1: "dinsdag", 2: "woensdag", 3: "donderdag",
                  4: "vrijdag", 5: "zaterdag", 6: "zondag"}
    dutch_months = {1: "januari", 2: "februari", 3: "maart", 4: "april",
                    5: "mei", 6: "juni", 7: "juli", 8: "augustus",
                    9: "september", 10: "oktober", 11: "november", 12: "december"}

    day_name = dutch_days[now.weekday()]
    month_name = dutch_months[now.month]
    week_num = now.isocalendar()[1]
    date_str = f"{day_name} {now.day} {month_name}"

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"📋 Wekelijks AI Digest — Week {week_num}"}
        },
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"AI-trends voor overheid & digitale dienstverlening | {date_str} | {item_count} bronnen geanalyseerd"}
            ]
        },
        {"type": "divider"},
    ]

    # Split digest into sections and add as text blocks
    # Slack has a 3000 char limit per section block
    sections = digest_text.split("\n## ")
    for i, section in enumerate(sections):
        if i > 0:
            section = "## " + section
        # Split long sections into chunks
        while section:
            chunk = section[:2900]
            if len(section) > 2900:
                # Try to break at a newline
                last_nl = chunk.rfind("\n")
                if last_nl > 500:
                    chunk = section[:last_nl]
            section = section[len(chunk):]

            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": chunk.strip()}
            })

    blocks.append({"type": "divider"})
    blocks.append({
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": "Samengesteld door Webbio AI Research · Powered by Claude"}
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
        "User-Agent": "WebbioWeeklyDigest/1.0",
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


def fetch_and_score_articles() -> tuple[list[dict], dict, int]:
    """Fetch RSS feeds, score, deduplicate, return (top_items, pain_points, total_count)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=DIGEST_LOOKBACK_DAYS)
    all_items = []
    feed_errors = []

    print(f"Scanning {len(scanner.RSS_FEEDS)} feeds for last {DIGEST_LOOKBACK_DAYS} days...", file=sys.stderr)
    for feed in scanner.RSS_FEEDS:
        try:
            xml_text = scanner.fetch_feed(feed["url"])
            items = scanner.parse_rss_items(xml_text, feed["source"], feed["weight"], cutoff)
            all_items.extend(items)
            print(f"  {feed['source']}: {len(items)} items", file=sys.stderr)
        except Exception as e:
            feed_errors.append(feed["source"])
            print(f"  {feed['source']}: FAILED - {e}", file=sys.stderr)

    print(f"\nTotal: {len(all_items)} items from {len(scanner.RSS_FEEDS) - len(feed_errors)}/{len(scanner.RSS_FEEDS)} feeds", file=sys.stderr)

    if not all_items:
        return [], {}, 0

    scored_pain_points = {}
    scored = []
    for item in all_items:
        score, pains = scanner.score_item(item)
        if score >= 0:
            scored.append((score, item))
            if pains:
                scored_pain_points[id(item)] = pains

    scored.sort(key=lambda x: x[0], reverse=True)
    print(f"After relevance filter: {len(scored)} items", file=sys.stderr)

    candidates = scanner.deduplicate([item for _, item in scored])
    top_items = candidates[:MAX_ITEMS_FOR_SYNTHESIS]

    return top_items, scored_pain_points, len(all_items)


def get_amsterdam_now() -> datetime:
    """Get current time in Amsterdam (approximate DST)."""
    utc_now = datetime.now(timezone.utc)
    month = utc_now.month
    amsterdam_offset = timedelta(hours=2 if 3 < month < 10 else 1)
    return utc_now + amsterdam_offset


def mode_fetch_json(config: dict):
    """Agent mode: fetch articles and output JSON with prompt for agent synthesis."""
    top_items, scored_pain_points, total_count = fetch_and_score_articles()

    if len(top_items) < 3:
        json.dump({"status": "skip", "reason": f"Only {len(top_items)} relevant items found, need 3+", "item_count": len(top_items)}, sys.stdout)
        return

    prompt = build_synthesis_prompt(top_items, scored_pain_points)

    # Serialize articles for reference
    articles = []
    for item in top_items:
        pains = scored_pain_points.get(id(item), [])
        articles.append({
            "title": item["title"],
            "source": item["source"],
            "link": item["link"],
            "description": item["description"][:200],
            "pain_points": pains,
        })

    json.dump({
        "status": "ready",
        "total_scanned": total_count,
        "article_count": len(top_items),
        "articles": articles,
        "synthesis_prompt": prompt,
        "slack_channel": config.get("slack_channel", SLACK_CHANNEL),
    }, sys.stdout, ensure_ascii=False)


def mode_post_digest(digest_file: str, config: dict):
    """Agent mode: post a pre-generated digest to Slack."""
    bot_token = config.get("slack_bot_token", os.environ.get("SLACK_BOT_TOKEN", ""))
    channel = config.get("slack_channel", SLACK_CHANNEL)

    if not bot_token:
        print("Error: SLACK_BOT_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    if digest_file == "-":
        digest_text = sys.stdin.read()
    else:
        with open(digest_file) as f:
            digest_text = f.read()

    if not digest_text.strip():
        print("Error: empty digest text", file=sys.stderr)
        sys.exit(1)

    # Try to parse as JSON (agent may wrap with metadata)
    try:
        parsed = json.loads(digest_text)
        if isinstance(parsed, dict) and "digest" in parsed:
            digest_text = parsed["digest"]
            total_count = parsed.get("total_scanned", 0)
        else:
            total_count = 0
    except (json.JSONDecodeError, KeyError):
        total_count = 0

    now = get_amsterdam_now()
    blocks = format_slack_digest(digest_text, now, total_count)
    week_num = now.isocalendar()[1]
    fallback = f"\U0001f4cb Wekelijks AI Digest \u2014 Week {week_num}"
    success = post_to_slack(blocks, channel, bot_token, fallback)

    if success:
        print(f"Posted weekly digest to Slack #{channel}.", file=sys.stderr)
    else:
        print("Failed to post to Slack.", file=sys.stderr)
        sys.exit(1)


def main():
    config_path = Path(__file__).parent / "ai-news-config.json"
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)

    # --- Agent mode: fetch articles as JSON ---
    if "--fetch-json" in sys.argv:
        mode_fetch_json(config)
        return

    # --- Agent mode: post pre-generated digest ---
    if "--post-digest" in sys.argv:
        idx = sys.argv.index("--post-digest")
        digest_file = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "-"
        mode_post_digest(digest_file, config)
        return

    # --- Standalone mode (original behavior) ---
    bot_token = config.get("slack_bot_token", os.environ.get("SLACK_BOT_TOKEN", ""))
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    channel = config.get("slack_channel", SLACK_CHANNEL)
    dry_run = "--dry-run" in sys.argv
    no_claude = "--no-claude" in sys.argv

    if not anthropic_key and not no_claude:
        print("Error: ANTHROPIC_API_KEY not set. Use --fetch-json for agent mode.", file=sys.stderr)
        sys.exit(1)

    if not bot_token and not dry_run:
        print("Error: SLACK_BOT_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    top_items, scored_pain_points, total_count = fetch_and_score_articles()

    if len(top_items) < 3:
        print(f"Only {len(top_items)} relevant items found. Need at least 3 for a digest. Skipping.", file=sys.stderr)
        sys.exit(0)

    print(f"\nSynthesizing digest from top {len(top_items)} items using Claude...", file=sys.stderr)

    prompt = build_synthesis_prompt(top_items, scored_pain_points)

    if dry_run and no_claude:
        print("\n--- DRY RUN (no Claude) ---\n")
        for i, item in enumerate(top_items, 1):
            pains = scored_pain_points.get(id(item), [])
            pain_str = f" [{', '.join(pains)}]" if pains else ""
            print(f"{i}. [{item['source']}] {item['title']}{pain_str}")
            print(f"   {item['link']}\n")
        print(f"--- {len(top_items)} items would be sent to Claude for synthesis ---")
        return

    digest_text = call_claude(prompt, anthropic_key)
    print("Claude synthesis complete.", file=sys.stderr)

    if dry_run:
        print("\n--- DRY RUN ---\n")
        print(digest_text)
        print(f"\n--- Digest synthesized from {len(top_items)} items ({total_count} total scanned) ---")
        return

    now = get_amsterdam_now()
    blocks = format_slack_digest(digest_text, now, total_count)
    week_num = now.isocalendar()[1]
    fallback = f"\U0001f4cb Wekelijks AI Digest \u2014 Week {week_num}"
    success = post_to_slack(blocks, channel, bot_token, fallback)

    if success:
        print(f"Posted weekly digest to Slack #{channel}.", file=sys.stderr)
    else:
        print("Failed to post to Slack.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
