---
type: dashboard
tags: [vault, home]
---

# Paperclip Knowledge Vault

Welcome to the Paperclip agent knowledge bank. This vault provides a visual interface over all agent workspaces.

## Agents

| Agent            | Role               | Workspace            |
| ---------------- | ------------------ | -------------------- |
| [[Nox/MEMORY]]   | CEO / Orchestrator | [[Nox/life/index]]   |
| [[Mitch/MEMORY]] | CTO / Builder      | [[Mitch/life/index]] |
| [[Tommy/MEMORY]] | Designer / QA      | [[Tommy/life/index]] |
| [[Oscar/MEMORY]] | CFO / Finance      | [[Oscar/life/index]] |
| [[Rex/MEMORY]]   | CMO / Content      | [[Rex/life/index]]   |

## Dashboards

- [[Dashboards/Agent Overview|Agent Overview]] — daily notes, knowledge per agent
- [[Dashboards/People & Companies|People & Companies]] — all known people and companies
- [[Dashboards/Projects & Resources|Projects & Resources]] — active projects and resources

## Quick Access

- **Daily Notes**: Check each agent's `memory/` folder for daily logs
- **Knowledge Graph**: Each agent's `life/` folder contains their PARA-structured knowledge
- **Tacit Knowledge**: Each agent's `MEMORY.md` contains operating patterns and preferences

## How It Works

This vault uses symlinks to the Paperclip workspace directories. Files are owned by agents — edits here are immediately visible to them on their next heartbeat. You can add notes in any agent's workspace and they will pick them up.

Vault path: `~/.paperclip/instances/default/vault/`
