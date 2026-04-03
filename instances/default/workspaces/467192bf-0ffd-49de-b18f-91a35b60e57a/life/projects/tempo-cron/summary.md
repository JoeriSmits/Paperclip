# Tempo Hours Reconstruction Cron

Migrated from OpenClaw to Paperclip workspace (2026-04-03).

## What it does
Reconstructs Joeri's daily work hours from three data sources:
1. **GitHub commits** — searches org `webbio` for commits by `JoeriSmits`
2. **Jira transitions** — status changes on assigned issues at `webbiohq.atlassian.net`
3. **Google Calendar** — events from `joeri@webbio.nl` via `gog` CLI

Produces JSON worklog drafts per day, allocated across Jira tickets with 15-minute quantization. Minimum 7h/day.

## Schedule
Weekdays at 17:00 Amsterdam time, processes the previous workday.

## Location
Project workspace: `$PROJECT_ROOT/_default/`
- `tempo-reconstruct.sh` — core script (Python embedded in bash)
- `tempo-config.json` — Jira/Tempo/GitHub config
- `run-tempo-cron.sh` — wrapper with secret loading + weekday logic
- `nl.webbio.paperclip.tempo-cron.plist` — launchd plist for persistent scheduling
- `tempo-drafts/` — output JSON files
- `tempo-logs/` — execution logs

## Secrets
`JIRA_TOKEN`, `TEMPO_TOKEN`, `GITHUB_TOKEN` sourced from `~/.openclaw/.env`.

## Status
- Script migrated and tested ✓
- launchd plist ready but not yet installed (needs board action)
- `gog` OAuth token expired — calendar events unavailable until re-authed
