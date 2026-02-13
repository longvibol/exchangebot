# exchangebot

Telegram bot for live currency conversion using ExchangeRate-API.

## Requirements
- OCI Cloud Shell (Linux aarch64) with `bash`
- Internet access from the instance
- Telegram Bot token (from @BotFather)
- ExchangeRate-API token (from exchangerate-api.com)

## Quick Start (OCI Cloud Shell)
1) Enter the project folder:
```bash
cd exchangebot
```

2) Make scripts executable (one-time):
```bash
chmod +x build_oci_arm64.sh run_oci_arm64.sh build_oci_arm64_binary.sh run_oci_arm64_binary.sh
```

3) Create your `.env`:
```bash
cp .env.example .env
```
Edit `.env` and set real values.

4) Install dependencies and run from source:
```bash
./build_oci_arm64.sh
./run_oci_arm64.sh
```

## Build and Run a Binary (Optional)
```bash
./build_oci_arm64_binary.sh
./run_oci_arm64_binary.sh
```

## Troubleshooting
- `Token must contain a colon`:
Your Telegram bot token is missing or invalid. It must look like `123456789:ABCDEF...`.
- `Missing TELEGRAM_BOT_TOKEN` or `Missing EXCHANGE_RATE_TOKEN`:
Set the values in `.env` or export them in the shell before running.
