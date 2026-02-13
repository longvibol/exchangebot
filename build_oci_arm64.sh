#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

SUDO=""
if command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
fi

if command -v apt-get >/dev/null 2>&1; then
  $SUDO apt-get update
  $SUDO apt-get install -y python3 python3-venv python3-pip
elif command -v dnf >/dev/null 2>&1; then
  $SUDO dnf install -y python3 python3-pip python3-virtualenv || true
elif command -v yum >/dev/null 2>&1; then
  $SUDO yum install -y python3 python3-pip python3-virtualenv || true
else
  echo "No supported package manager found. Ensure python3 and venv are installed."
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install python3 and retry."
  exit 1
fi

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
