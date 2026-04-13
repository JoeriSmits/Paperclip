# Tools

## Email (Founder Communication)

- **notify-board.sh** -- Send strategic email to Joeri.
  Path: `/Users/joerismits/.paperclip/instances/default/workspaces/23bc3620-04fa-40d0-8e4c-9a52ea800a9e/tools/notify-board.sh`
  Usage: `bash <path> "<subject>" "<body>"`
  Requires RESEND_API_KEY in `tools/.env` (confirmed present).

- **check-mail.sh** -- Check for founder replies.
  Path: `/Users/joerismits/.paperclip/instances/default/workspaces/23bc3620-04fa-40d0-8e4c-9a52ea800a9e/tools/check-mail.sh`
  Usage: `bash <path> new` (check new), `bash <path> read <id>` (read specific)
