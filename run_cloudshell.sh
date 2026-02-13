#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install Python 3 and try again." >&2
  exit 1
fi

if [ ! -f ".env" ]; then
  echo "Missing .env. Copy .env.example to .env and set your tokens." >&2
  exit 1
fi

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  python -m pip install -r requirements.txt
else
  python -m pip install pyTelegramBotAPI requests
fi

python convert.py
