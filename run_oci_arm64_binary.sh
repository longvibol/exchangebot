#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

BIN="./dist/exchange-rate-bot"
if [ ! -f "$BIN" ]; then
  echo "Binary not found at $BIN. Run ./build_oci_arm64_binary.sh first."
  exit 1
fi

# Optional: provide tokens via env vars to avoid hardcoding in mytoken.py
# export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
# export EXCHANGE_RATE_TOKEN="your-exchange-rate-api-token"

"$BIN"
