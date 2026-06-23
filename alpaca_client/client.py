"""A thin, readable wrapper over the Alpaca REST API (paper trading by default).

Built on `requests` only — no Alpaca SDK required. Covers the common
operations: account, positions, orders (place/list/cancel) and latest quotes.
"""

from __future__ import annotations

from typing import Any

import requests

from .config import Config, load_config


class AlpacaError(RuntimeError):
    """Raised when the Alpaca API returns an error response."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"[HTTP {status_code}] {message}")


class AlpacaClient:
    """Minimal Alpaca trading client.

    Example
    -------
    >>> client = AlpacaClient.from_env()
    >>> account = client.get_account()
    >>> print(account["status"], account["buying_power"])
    """

    def __init__(self, config: Config, timeout: float = 15.0):
        self.config = config
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "APCA-API-KEY-ID": config.key_id,
                "APCA-API-SECRET-KEY": config.secret_key,
                "Accept": "application/json",
            }
        )

    @classmethod
    def from_env(cls, timeout: float = 15.0) -> "AlpacaClient":
        """Build a client from environment variables / .env file."""
        return cls(load_config(), timeout=timeout)

    # -- internal -------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        base: str | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{base or self.config.base_url}{path}"
        try:
            resp = self._session.request(
                method, url, params=params, json=json, timeout=self.timeout
            )
        except requests.RequestException as exc:  # network-level failure
            raise AlpacaError(0, f"Network error reaching {url}: {exc}") from exc

        if resp.status_code >= 400:
            # Alpaca returns JSON like {"code": ..., "message": ...}
            try:
                detail = resp.json().get("message", resp.text)
            except ValueError:
                detail = resp.text
            raise AlpacaError(resp.status_code, detail)

        if not resp.content:
            return None
        return resp.json()

    # -- account & positions -------------------------------------------

    def get_account(self) -> dict[str, Any]:
        """Return account info (status, cash, buying power, equity, ...)."""
        return self._request("GET", "/v2/account")

    def get_positions(self) -> list[dict[str, Any]]:
        """Return all open positions."""
        return self._request("GET", "/v2/positions")

    def get_position(self, symbol: str) -> dict[str, Any]:
        """Return the open position for a single symbol."""
        return self._request("GET", f"/v2/positions/{symbol.upper()}")

    # -- orders ---------------------------------------------------------

    def list_orders(
        self, status: str = "open", limit: int = 50
    ) -> list[dict[str, Any]]:
        """List orders. status: 'open', 'closed', or 'all'."""
        return self._request(
            "GET", "/v2/orders", params={"status": status, "limit": limit}
        )

    def submit_order(
        self,
        symbol: str,
        qty: float | None = None,
        notional: float | None = None,
        side: str = "buy",
        order_type: str = "market",
        time_in_force: str = "day",
        limit_price: float | None = None,
    ) -> dict[str, Any]:
        """Submit an order. Provide either `qty` (shares) or `notional` ($)."""
        if (qty is None) == (notional is None):
            raise ValueError("Provide exactly one of `qty` or `notional`.")

        body: dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
        }
        if qty is not None:
            body["qty"] = str(qty)
        if notional is not None:
            body["notional"] = str(notional)
        if limit_price is not None:
            body["limit_price"] = str(limit_price)

        return self._request("POST", "/v2/orders", json=body)

    def cancel_order(self, order_id: str) -> None:
        """Cancel a single open order by id."""
        self._request("DELETE", f"/v2/orders/{order_id}")

    def cancel_all_orders(self) -> Any:
        """Cancel all open orders."""
        return self._request("DELETE", "/v2/orders")

    # -- market data ----------------------------------------------------

    def get_latest_quote(self, symbol: str) -> dict[str, Any]:
        """Return the latest quote (bid/ask) for a stock symbol."""
        data = self._request(
            "GET",
            f"/v2/stocks/{symbol.upper()}/quotes/latest",
            base=self.config.data_url,
        )
        return data.get("quote", data)

    # -- convenience ----------------------------------------------------

    def ping(self) -> dict[str, Any]:
        """Verify credentials by fetching the account. Raises on failure."""
        return self.get_account()
