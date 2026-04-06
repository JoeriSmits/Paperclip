#!/usr/bin/env bash
# notify-board.sh — CEO-to-founder email via Resend API.
#
# This is a strategic communication channel. Use it when you need
# founder input on decisions, direction, or blockers that affect
# the company — not for routine task notifications.
#
# Usage:
#   notify-board.sh <subject> <body>
#
# Examples:
#   notify-board.sh "Should we continue investing in joeri.dev website?" \
#     "We have 3 tasks queued for the website redesign. Before the team spends cycles, I want to confirm this is still a priority."
#
#   notify-board.sh "Pipeline blocked — need your call on content direction" \
#     "Rex has 2 LinkedIn posts and a profile copy draft waiting for your review. Details: ..."
#
# Environment (loaded from tools/.env if present):
#   RESEND_API_KEY — Resend API key (required)
#   NOTIFY_BOARD_TO — recipient (default: email@joeri.dev)
#   NOTIFY_BOARD_FROM — sender (default: nox@joeri.dev)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load .env if present
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
fi

SUBJECT="${1:-}"
BODY="${2:-}"

if [ -z "$SUBJECT" ] || [ -z "$BODY" ]; then
  echo "Usage: notify-board.sh <subject> <body>" >&2
  exit 1
fi

if [ -z "${RESEND_API_KEY:-}" ]; then
  echo "ERROR: RESEND_API_KEY not set. Add it to tools/.env" >&2
  exit 1
fi

TO="${NOTIFY_BOARD_TO:-email@joeri.dev}"
FROM="${NOTIFY_BOARD_FROM:-nox@joeri.dev}"

# Build JSON payload and send via Resend API
export MAIL_TO="$TO"
export MAIL_FROM="$FROM"
export MAIL_SUBJECT="[joeri.dev] $SUBJECT"
export MAIL_BODY="$BODY"

REPLY_TO="${NOTIFY_BOARD_REPLY_TO:-$FROM}"
export MAIL_REPLY_TO="$REPLY_TO"

PAYLOAD=$(python3 -c '
import json, os
print(json.dumps({
    "from": "Nox (CEO) <" + os.environ["MAIL_FROM"] + ">",
    "to": [os.environ["MAIL_TO"]],
    "reply_to": [os.environ["MAIL_REPLY_TO"]],
    "subject": os.environ["MAIL_SUBJECT"],
    "text": os.environ["MAIL_BODY"] + "\n\n---\nSent by Nox, CEO agent at joeri.dev\nReply to this email \u2014 your response will guide the team."
}, ensure_ascii=False))
')

RESPONSE=$(curl -s -X POST 'https://api.resend.com/emails' \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD" 2>&1)

if echo "$RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('id')" 2>/dev/null; then
  EMAIL_ID=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
  echo "Email sent: [joeri.dev] $SUBJECT (id: $EMAIL_ID)"
else
  echo "ERROR: Resend API response: $RESPONSE" >&2
  exit 1
fi
