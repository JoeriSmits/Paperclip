#!/usr/bin/env bash
# Wrapper script for running Tempo hours reconstruction as a cron job.
# Loads required secrets from OpenClaw .env and runs tempo-reconstruct.sh
# for the previous workday.
#
# Why launchd instead of a Paperclip scheduled trigger:
# This script needs local filesystem access (config files, env secrets, gog CLI)
# and produces local output files. Paperclip triggers wake agents for coordination
# work — using one here would add agent heartbeat overhead just to shell out to
# this same script. launchd runs it directly with zero overhead.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="${TEMPO_ENV_FILE:-$HOME/.openclaw/.env}"
LOG_DIR="$SCRIPT_DIR/tempo-logs"

mkdir -p "$LOG_DIR"

# Load secrets
if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: env file not found: $ENV_FILE" >&2
  exit 1
fi
export $(grep -E "^(JIRA_TOKEN|TEMPO_TOKEN|GITHUB_TOKEN)=" "$ENV_FILE" | xargs)

# Determine target date: previous workday
# If today is Monday, use Friday. Otherwise use yesterday.
DOW=$(date +%u) # 1=Monday ... 7=Sunday
if [[ "$DOW" == "1" ]]; then
  TARGET=$(date -v-3d +%F)
elif [[ "$DOW" == "7" ]]; then
  TARGET=$(date -v-2d +%F)
elif [[ "$DOW" == "6" ]]; then
  TARGET=$(date -v-1d +%F)
else
  TARGET=$(date -v-1d +%F)
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running tempo-reconstruct for $TARGET"

"$SCRIPT_DIR/tempo-reconstruct.sh" --submit "$TARGET" 2>&1 | tee "$LOG_DIR/tempo-$TARGET.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done"
