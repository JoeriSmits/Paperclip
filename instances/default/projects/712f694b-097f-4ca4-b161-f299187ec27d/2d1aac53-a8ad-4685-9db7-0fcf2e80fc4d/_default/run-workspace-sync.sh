#!/bin/bash
# Paperclip workspace git sync — daily backup of agent workspaces, memory, and config
# Migrated from OpenClaw "Workspace Git Sync" cron
set -euo pipefail

PAPERCLIP_DIR="$HOME/.paperclip"
LOG_DIR="$PAPERCLIP_DIR/instances/default/data/run-logs"
LOG_FILE="$LOG_DIR/workspace-sync-$(date +%Y-%m-%d).log"
mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

cd "$PAPERCLIP_DIR"

# Ensure git repo exists
if [ ! -d .git ]; then
  log "ERROR: $PAPERCLIP_DIR is not a git repository"
  exit 1
fi

# Stage all changes
git add -A

# Check if there are changes to commit
if git diff --cached --quiet; then
  log "No changes to sync"
  exit 0
fi

# Commit
git commit -m "chore: daily workspace sync $(date +%Y-%m-%d)" \
  --author="Paperclip Sync <noreply@paperclip.ing>" \
  >> "$LOG_FILE" 2>&1

# Push if remote is configured
if git remote get-url origin >/dev/null 2>&1; then
  GIT_SSH_COMMAND="ssh -i $HOME/.ssh/automation_ed25519 -o IdentitiesOnly=yes" \
    git push origin main >> "$LOG_FILE" 2>&1
  log "Pushed to remote"
else
  log "No remote configured — commit only (local backup)"
fi

log "Sync complete"
