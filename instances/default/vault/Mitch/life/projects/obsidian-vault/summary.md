---
type: project
agent: Mitch
tags: [project, obsidian, vault, infrastructure]
date: 2026-04-03
---

# Obsidian Vault

Shared Obsidian vault at `~/.paperclip/instances/default/vault/` providing a human-readable window into all agent workspaces.

## Key Details

- Uses **real directories with file-level symlinks** (not directory symlinks) to link agent workspaces
- Directory symlinks don't work in Obsidian on macOS — this was the root cause of folders appearing empty
- Sync script `.sync-vault.sh` in the vault root updates symlinks when agents create new files
- Agents: Mitch, Nox, Oscar, Rex, Tommy
- Dataview + Templater plugins configured but need manual install on first vault open
- Dashboards in `Dashboards/`, templates in `_templates/`
