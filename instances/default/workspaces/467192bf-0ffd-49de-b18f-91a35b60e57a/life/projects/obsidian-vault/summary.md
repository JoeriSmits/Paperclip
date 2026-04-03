---
type: project
agent: Mitch
tags: [project, obsidian, vault, infrastructure]
date: 2026-04-03
---

# Obsidian Vault

Shared Obsidian vault at `~/.paperclip/instances/default/vault/` providing a human-readable window into all agent workspaces.

## Key Details

- Uses **real file copies** (NOT symlinks of any kind) for all agent workspace content
- Obsidian on macOS doesn't index symlinks at all — neither directory-level nor file-level
- Sync script `.sync-vault.sh` uses `rsync` to copy workspace files into the vault
- Agents: Mitch, Nox, Oscar, Rex, Tommy
- Dataview + Templater plugins configured but need manual install on first vault open
- Dashboards in `Dashboards/`, templates in `_templates/`
