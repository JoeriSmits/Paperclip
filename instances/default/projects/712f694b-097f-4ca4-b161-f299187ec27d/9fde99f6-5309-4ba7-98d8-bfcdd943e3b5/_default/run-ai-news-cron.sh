#!/bin/bash
# AI News Scanner — daily cron wrapper
# Loads Slack credentials from OpenClaw .env and runs the scanner

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load environment (Slack tokens)
if [ -f "$HOME/.openclaw/.env" ]; then
    set -a
    source "$HOME/.openclaw/.env"
    set +a
fi

exec /usr/bin/env python3 "$SCRIPT_DIR/ai-news-scanner.py" "$@"
