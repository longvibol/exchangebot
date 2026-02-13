import os
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


class TelegramConfig:
    def __init__(self):
        _load_dotenv()
        self._bot_token = os.getenv(
            "TELEGRAM_BOT_TOKEN",
            "8338627964:AAE5OBrqHfERvlqd-lv2dXFe_TAb_eOBiNc",
        )
        self._exchange_rate_token = os.getenv(
            "EXCHANGE_RATE_TOKEN",
            "ea624cd9cb8959181c27c91d",
        )

    def get_token(self) -> str:
        return self._bot_token

    def get_exchange_rate_token(self) -> str:
        return self._exchange_rate_token


if __name__ == "__main__":
    config = TelegramConfig()
    print(config.get_token())
