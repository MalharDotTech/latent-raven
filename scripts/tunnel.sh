#!/usr/bin/env bash
set -euo pipefail
command -v cloudflared >/dev/null || { echo "Install cloudflared first: brew install cloudflared" >&2; exit 1; }
caffeinate -dimsu &
CAFFEINATE_PID=$!
trap 'kill "$CAFFEINATE_PID" 2>/dev/null || true' EXIT
printf 'Opening a temporary public URL for Raven at http://localhost:8000\n'
printf 'The https://…trycloudflare.com URL will be printed below. Keep this terminal open.\n'
cloudflared tunnel --url http://localhost:8000
