import os
import sys
from pathlib import Path


def _candidate_env_paths() -> list[Path]:
    paths = []
    # 1) Current working directory (most common for deployed binaries)
    paths.append(Path.cwd() / ".env")
    # 2) Directory of the running executable (PyInstaller onefile)
    paths.append(Path(sys.executable).resolve().parent / ".env")
    # 3) Directory of this file (source run)
    paths.append(Path(__file__).resolve().parent / ".env")
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def _load_dotenv() -> None:
    env_path = None
    for candidate in _candidate_env_paths():
        if candidate.exists():
            env_path = candidate
            break
    if env_path is None:
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
