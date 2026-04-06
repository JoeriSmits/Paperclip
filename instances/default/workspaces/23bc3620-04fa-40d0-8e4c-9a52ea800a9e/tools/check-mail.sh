#!/usr/bin/env bash
# check-mail.sh — Poll Resend inbound API for new emails.
#
# Usage:
#   check-mail.sh              # List recent emails (summary)
#   check-mail.sh read <id>    # Read full email content
#   check-mail.sh new          # Show only unread emails (since last check)
#
# Environment (loaded from tools/.env):
#   RESEND_API_KEY — Resend API key (required)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LAST_CHECK_FILE="$SCRIPT_DIR/.last-mail-check"

# Load .env if present
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
fi

if [ -z "${RESEND_API_KEY:-}" ]; then
  echo "ERROR: RESEND_API_KEY not set. Add it to tools/.env" >&2
  exit 1
fi

ACTION="${1:-list}"
EMAIL_ID="${2:-}"

case "$ACTION" in
  list)
    RESULT=$(curl -s -H "Authorization: Bearer $RESEND_API_KEY" \
      "https://api.resend.com/emails/receiving?limit=10")
    echo "$RESULT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
emails = data.get('data', [])
if not emails:
    print('No emails received.')
    sys.exit(0)
print(f\"{'ID':<40} {'From':<30} {'Subject':<50} {'Date'}\")
print('-' * 140)
for e in emails:
    eid = e.get('id', '?')
    frm = e.get('from', '?')[:28]
    subj = e.get('subject', '(no subject)')[:48]
    date = e.get('created_at', '?')[:19]
    print(f'{eid:<40} {frm:<30} {subj:<50} {date}')
"
    ;;

  read)
    if [ -z "$EMAIL_ID" ]; then
      echo "Usage: check-mail.sh read <email-id>" >&2
      exit 1
    fi
    RESULT=$(curl -s -H "Authorization: Bearer $RESEND_API_KEY" \
      "https://api.resend.com/emails/receiving/$EMAIL_ID")
    echo "$RESULT" | python3 -c "
import json, sys
e = json.load(sys.stdin)
print('From:', e.get('from', '?'))
print('To:', e.get('to', '?'))
print('Subject:', e.get('subject', '?'))
print('Date:', e.get('created_at', '?'))
print('Message-ID:', e.get('message_id', '?'))
print('---')
text = e.get('text', '')
html = e.get('html', '')
if text:
    print(text)
elif html:
    print('[HTML content - text version not available]')
    print(html[:2000])
else:
    print('[No content]')
"
    ;;

  new)
    AFTER=""
    if [ -f "$LAST_CHECK_FILE" ]; then
      AFTER="&after=$(cat "$LAST_CHECK_FILE")"
    fi
    RESULT=$(curl -s -H "Authorization: Bearer $RESEND_API_KEY" \
      "https://api.resend.com/emails/receiving?limit=20${AFTER}")

    echo "$RESULT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
emails = data.get('data', [])
if not emails:
    print('No new emails.')
    sys.exit(0)
print(f'Found {len(emails)} new email(s):')
print()
for e in emails:
    eid = e.get('id', '?')
    frm = e.get('from', '?')
    subj = e.get('subject', '(no subject)')
    date = e.get('created_at', '?')[:19]
    print(f'  [{date}] {frm}')
    print(f'  Subject: {subj}')
    print(f'  ID: {eid}')
    print()
"
    # Update cursor with latest email ID
    LATEST=$(echo "$RESULT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
emails = data.get('data', [])
if emails:
    print(emails[0]['id'])
" 2>/dev/null || true)
    if [ -n "$LATEST" ]; then
      echo "$LATEST" > "$LAST_CHECK_FILE"
    fi
    ;;

  *)
    echo "Usage: check-mail.sh [list|read <id>|new]" >&2
    exit 1
    ;;
esac
