#!/bin/zsh
# Sync agent workspace files into the Obsidian vault (copies, not symlinks)
# Obsidian on macOS doesn't index symlinked files — so we copy.
# Run this after agents complete heartbeats, or on a schedule.

VAULT="$HOME/.paperclip/instances/default/vault"
WORKSPACES="$HOME/.paperclip/instances/default/workspaces"

AGENT_NAMES=(Mitch Nox Oscar Rex Tommy)
AGENT_IDS=(
  467192bf-0ffd-49de-b18f-91a35b60e57a
  23bc3620-04fa-40d0-8e4c-9a52ea800a9e
  d1e84034-4c31-4926-a145-8a1f713ba3fc
  8db8080d-9064-4707-99c2-2e8d186f5e17
  7d8b001d-912c-4f3d-a5f4-77195261fac8
)

for i in {1..${#AGENT_NAMES[@]}}; do
  name="${AGENT_NAMES[$i]}"
  ws="$WORKSPACES/${AGENT_IDS[$i]}"
  [[ -d "$ws" ]] || continue

  mkdir -p "$VAULT/$name"
  rsync -a --delete \
    --exclude='.git' \
    --exclude='.claude' \
    --exclude='node_modules' \
    "$ws/" "$VAULT/$name/"
done

echo "Vault synced at $(date)"
