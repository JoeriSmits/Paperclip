#!/usr/bin/env bash
# Wrapper script for running Tempo hours fetch as a cron job.
# Loads TEMPO_TOKEN from env file and fetches worklogs for the previous workday.
#
# Why launchd instead of a Paperclip scheduled trigger:
# This script needs local filesystem access (config files, env secrets)
# and produces local output files. launchd runs it directly with zero overhead.
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
export $(grep -E "^TEMPO_TOKEN=" "$ENV_FILE" | xargs)

# Determine target date: previous workday
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

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Fetching Tempo worklogs for $TARGET"

"$SCRIPT_DIR/tempo-reconstruct.sh" "$TARGET" 2>&1 | tee "$LOG_DIR/tempo-$TARGET.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done"
