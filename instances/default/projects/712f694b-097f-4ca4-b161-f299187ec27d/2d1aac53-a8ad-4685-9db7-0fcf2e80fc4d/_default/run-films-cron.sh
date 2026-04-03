#!/usr/bin/env bash
# Films & Series Digest cron wrapper — runs weekly Fridays at 10:00 CET via launchd
# Migrated from OpenClaw films digest cron

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/films-logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d).log"

echo "=== Films Digest run: $(date -u '+%Y-%m-%dT%H:%M:%SZ') ===" >> "$LOG_FILE"

python3 "$SCRIPT_DIR/films-digest.py" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "FAILED with exit code $EXIT_CODE" >> "$LOG_FILE"
fi

# Keep 30 days of logs
find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true

exit $EXIT_CODE
