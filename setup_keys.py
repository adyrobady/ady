#!/usr/bin/env python3
"""Dead-simple helper to save your Alpaca paper API keys into a .env file.

Run it and paste your two keys when prompted:

    python setup_keys.py

You can also pass them as arguments (handy for automation):

    python setup_keys.py --key-id YOUR_ID --secret YOUR_SECRET

The .env file it writes is gitignored and never committed.
"""

from __future__ import annotations

import argparse
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"
PAPER_BASE_URL = "https://paper-api.alpaca.markets"


def write_env(key_id: str, secret: str, base_url: str = PAPER_BASE_URL) -> None:
    content = (
        "# Alpaca paper trading credentials — DO NOT COMMIT.\n"
        f"APCA_API_KEY_ID={key_id.strip()}\n"
        f"APCA_API_SECRET_KEY={secret.strip()}\n"
        f"APCA_API_BASE_URL={base_url.strip()}\n"
    )
    ENV_PATH.write_text(content)
    ENV_PATH.chmod(0o600)  # readable only by you
    print(f"✓ Saved credentials to {ENV_PATH}")
    print("  This file is gitignored and will not be committed.")
    print("  Next: run `python main.py connect` to verify.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Save Alpaca paper keys to .env")
    parser.add_argument("--key-id", help="APCA_API_KEY_ID")
    parser.add_argument("--secret", help="APCA_API_SECRET_KEY")
    parser.add_argument("--base-url", default=PAPER_BASE_URL)
    args = parser.parse_args()

    key_id = args.key_id or input("Alpaca paper API Key ID:     ").strip()
    secret = args.secret or input("Alpaca paper Secret Key:     ").strip()

    if not key_id or not secret:
        raise SystemExit("✗ Both key id and secret are required.")

    write_env(key_id, secret, args.base_url)


if __name__ == "__main__":
    main()
