"""A small, dependency-light client for Alpaca paper trading."""

from .client import AlpacaClient, AlpacaError
from .config import load_config, Config

__all__ = ["AlpacaClient", "AlpacaError", "load_config", "Config"]
