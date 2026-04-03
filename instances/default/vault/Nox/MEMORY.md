---
type: tacit-knowledge
agent: Nox
tags: [memory, patterns]
---

# Tacit Knowledge

## Joeri's Operating Patterns
- Short, direct, no filler. Dutch directness is a feature.
- Discord = command interface. Slack = team output. Don't mix.
- Google Calendar doubles as todo list (solo events = tasks).
- Only ping for urgent/unexpected things. No reminders for standups, meetings, lunch.
- Hates hour logging, automated via Tempo cron.
- Films/series: new releases only (2025+), IMDb 7.0+.
- Houdt niet van pittig eten.
- Checks if content actually works (URLs, videos, data). Catches mock data immediately.
- Expects validation BEFORE adding items.

## Design Preferences
- Wants Linear/Vercel quality but WITH personality (pixel-art robots).
- Strict color palette: cyan-400, emerald-400, amber-400 + slate.
- No ALL CAPS headers, max 3 typography levels.
- Discord: no markdown tables, wrap links in <>.

## Improvement Rules (hard)
- NO improvements about Jira, Google Calendar, or GitHub.
- NO Slack, PR reviews, sprint tracking, agenda briefings.
- Focus: home automation, OpenClaw/Discord workflow, local tooling, comfort.

## My Role
- I'm Nox, the orchestrator. I don't build (max 5 lines of code). I delegate.
- Full Paperclip team: Nox (CEO), Sage (PM/Ops), Mitch (CTO/builder), Tommy (QA/design), Oscar (CFO), Rex (CMO).
- Atlas (security) not yet hired in Paperclip.

## Delivery Loop
```
Goals → Sage (plan & assign) → Mitch (build) → Tommy (QA) → Sage (goal validation) → Done
```

## Operational Cadence (weekly, driven by Sage)
- **Monday**: Sage runs weekly planning (goal review, task creation, team workload). Creates routine tasks for Oscar (financial snapshot) and Rex (content cycle).
- **Daily**: Sage checks task health (stale in_progress, unresolved blockers, agent overload).
- **Friday**: Sage runs weekly wrap-up (what shipped, what's open, process issues). Escalates to Nox if strategic decisions needed.
- **Joeri only involved for**: content approval (Rex), unusual financial flags (Oscar), strategic pivots (Nox).

## Integrations (from OpenClaw)
- Picnic/ChefClaw: groceries + recipes for weekly meal planning. Uses `picnic-api` npm package (not MCP).
- Buffer: LinkedIn posts via GraphQL API. Images via Imgur upload. No update mutation (delete+create).
- Tempo: automated hour logging. Reconstruction: GitHub commits > Jira > Calendar > FAC-145 filler.
- GoCardless: ING bank read-only (Oscar only). Financial data is private.
- Films/Series: OMDB (movies) + TVmaze (series) for posters. Discord buttons for watchlist.
- Smart Home: HomeWizard coffee controller + Sonos speakers.
- News: nu.nl via RSS (blocks scraping), Reuters via Google News RSS.

## Cron Jobs (from OpenClaw, to migrate)
| Job | Schedule | Agent |
|-----|----------|-------|
| Webbio AI Research Digest | Mon 09:15 | Nox |
| Webbio AI Alert Daily Scan | Weekdays 08:00 | Nox |
| Tempo Hour Reconstruction | Weekdays 17:30 | Nox |
| News Digest | Daily 08:30 | Nox |
| Breaking News Scanner | Every 2h 08-20 | Nox |
| Films & Series Digest | Fri 10:00 | Nox |
| Rex Weekly Trend Scan | Mon 08:00 | Rex |
| Workspace Git Sync | Daily 23:00 | Nox |

## Key Technical Lessons (from OpenClaw)
- MCP servers as one-shot calls are extremely slow (Node startup + auth per call). Use underlying library directly.
- Picnic 2FA codes expire fast -- must verify in same login session.
- Discord buttons: type "actions" works, "buttons" doesn't. Need `reusable: true`.
- yt-dlp needs `--impersonate chrome` for YouTube. Thumbnail check for video existence.
- Gateway stability: Slack WebSocket caused crashes. Discord-only is stable.
