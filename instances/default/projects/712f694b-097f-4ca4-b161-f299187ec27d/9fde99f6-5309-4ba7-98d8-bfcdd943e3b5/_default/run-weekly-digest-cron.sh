#!/bin/bash
# Weekly AI Digest — cron wrapper
# Loads API credentials and runs the weekly digest synthesizer

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load environment (Slack + Anthropic tokens)
if [ -f "$HOME/.openclaw/.env" ]; then
    set -a
    source "$HOME/.openclaw/.env"
    set +a
fi

exec /usr/bin/env python3 "$SCRIPT_DIR/weekly-digest.py" "$@"
