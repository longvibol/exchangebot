import os
import sys
from pathlib import Path
from typing import Optional


def _candidate_env_paths() -> list[Path]:
    paths = [
        Path.cwd() / ".env",
        Path(sys.executable).resolve().parent / ".env",
        Path(__file__).resolve().parent / ".env",
    ]

    seen = set()
    unique: list[Path] = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def _load_dotenv(force: bool = True) -> Optional[Path]:
    """
    Load .env variables into os.environ.

    force=True means .env values OVERRIDE any existing environment variables.
    This fixes cases where CloudShell already has TELEGRAM_BOT_TOKEN set to an old value.
    """
    env_path: Optional[Path] = None
    for candidate in _candidate_env_paths():
        if candidate.exists():
            env_path = candidate
            break
    if env_path is None:
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if force:
            os.environ[key] = value
        else:
            os.environ.setdefault(key, value)

    return env_path


class TelegramConfig:
    def __init__(self):
        self._env_path = _load_dotenv(force=True)

        self._bot_token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
        self._exchange_rate_token = (os.getenv("EXCHANGE_RATE_TOKEN") or "").strip()

        # Normalize common fullwidth colon copy/paste error.
        if ":" not in self._bot_token and "：" in self._bot_token:
            self._bot_token = self._bot_token.replace("：", ":")

        if not self._bot_token:
            raise ValueError(
                "Missing TELEGRAM_BOT_TOKEN. Set it in .env or export it in the shell."
            )

        if ":" not in self._bot_token:
            token_hint = f"length={len(self._bot_token)}"
            if self._env_path:
                token_hint += f", env={self._env_path}"
            raise ValueError(
                "Invalid TELEGRAM_BOT_TOKEN. Telegram bot tokens must contain a colon. "
                + token_hint
            )

        if not self._exchange_rate_token:
            raise ValueError(
                "Missing EXCHANGE_RATE_TOKEN. Set it in .env or export it in the shell."
            )

    def get_token(self) -> str:
        return self._bot_token

    def get_exchange_rate_token(self) -> str:
        return self._exchange_rate_token


if __name__ == "__main__":
    config = TelegramConfig()
    print(config.get_token())
