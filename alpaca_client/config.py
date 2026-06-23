"""Configuration loading for the Alpaca client.

Keys are read from environment variables, with a fallback to a local `.env`
file (which is gitignored). No third-party dependency is needed to parse
`.env` — we do a tiny parse ourselves.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PAPER_BASE_URL = "https://paper-api.alpaca.markets"
DATA_BASE_URL = "https://data.alpaca.markets"

# Project root (one level up from this file).
_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _ROOT / ".env"


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


@dataclass
class Config:
    key_id: str
    secret_key: str
    base_url: str = PAPER_BASE_URL
    data_url: str = DATA_BASE_URL

    @property
    def is_paper(self) -> bool:
        return "paper-api" in self.base_url


def _parse_env_file(path: Path) -> dict[str, str]:
    """Minimal .env parser: KEY=VALUE lines, ignores blanks and # comments."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        # Strip surrounding quotes if present.
        value = value.strip().strip('"').strip("'")
        values[key.strip()] = value
    return values


def load_config(env_path: Path | None = None) -> Config:
    """Load configuration from environment, falling back to a `.env` file.

    Raises ConfigError with a friendly message if keys are missing.
    """
    file_values = _parse_env_file(env_path or _ENV_PATH)

    def get(name: str, default: str | None = None) -> str | None:
        return os.environ.get(name) or file_values.get(name) or default

    key_id = get("APCA_API_KEY_ID")
    secret_key = get("APCA_API_SECRET_KEY")
    base_url = get("APCA_API_BASE_URL", PAPER_BASE_URL)
    data_url = get("APCA_DATA_URL", DATA_BASE_URL)

    missing = [
        name
        for name, val in (
            ("APCA_API_KEY_ID", key_id),
            ("APCA_API_SECRET_KEY", secret_key),
        )
        if not val
    ]
    if missing:
        raise ConfigError(
            "Missing Alpaca credentials: "
            + ", ".join(missing)
            + ".\nSet them as environment variables or in a .env file "
            "(run `python setup_keys.py` to create one)."
        )

    return Config(
        key_id=key_id,
        secret_key=secret_key,
        base_url=base_url.rstrip("/"),
        data_url=data_url.rstrip("/"),
    )
