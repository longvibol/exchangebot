#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "Virtualenv not found. Will try system python3 instead."
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found. Run ./build_oci_arm64.sh first or install python3."
    exit 1
  fi
fi

# Optional: provide tokens via env vars to avoid hardcoding in mytoken.py
# export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
# export EXCHANGE_RATE_TOKEN="your-exchange-rate-api-token"

python3 convert.py
