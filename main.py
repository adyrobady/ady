#!/usr/bin/env python3
"""Command-line entry point for the Alpaca paper trading client.

Usage examples
--------------
    python main.py connect                 # verify connection, show account
    python main.py account                 # full account details
    python main.py positions               # open positions
    python main.py orders [open|closed|all]
    python main.py quote AAPL
    python main.py buy AAPL --qty 1
    python main.py buy AAPL --notional 100
    python main.py sell AAPL --qty 1
    python main.py cancel <order_id>
    python main.py telegram               # generate telegram dashboard links
"""

from __future__ import annotations

import argparse
import sys

from alpaca_client import AlpacaClient, AlpacaError
from alpaca_client.config import ConfigError
from telegram_links import TelegramDashboardLinks


def _client() -> AlpacaClient:
    try:
        return AlpacaClient.from_env()
    except ConfigError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        sys.exit(2)


def cmd_connect(_: argparse.Namespace) -> None:
    client = _client()
    acct = client.ping()
    mode = "PAPER" if client.config.is_paper else "LIVE"
    print(f"✓ Connected to Alpaca ({mode})")
    print(f"  Account #:     {acct.get('account_number')}")
    print(f"  Status:        {acct.get('status')}")
    print(f"  Currency:      {acct.get('currency')}")
    print(f"  Cash:          ${acct.get('cash')}")
    print(f"  Buying power:  ${acct.get('buying_power')}")
    print(f"  Equity:        ${acct.get('equity')}")


def cmd_account(_: argparse.Namespace) -> None:
    _print_json(_client().get_account())


def cmd_positions(_: argparse.Namespace) -> None:
    positions = _client().get_positions()
    if not positions:
        print("No open positions.")
        return
    for p in positions:
        print(
            f"{p['symbol']:>6}  qty={p['qty']:>8}  "
            f"avg=${p['avg_entry_price']:>10}  "
            f"mkt=${p['market_value']:>12}  "
            f"P/L=${p['unrealized_pl']:>10}"
        )


def cmd_orders(args: argparse.Namespace) -> None:
    orders = _client().list_orders(status=args.status)
    if not orders:
        print(f"No {args.status} orders.")
        return
    for o in orders:
        print(
            f"{o['id']}  {o['side']:>4} {o.get('qty') or o.get('notional')} "
            f"{o['symbol']}  {o['type']}  status={o['status']}"
        )


def cmd_quote(args: argparse.Namespace) -> None:
    q = _client().get_latest_quote(args.symbol)
    print(f"{args.symbol.upper()}: bid ${q.get('bp')} x {q.get('bs')}  "
          f"ask ${q.get('ap')} x {q.get('as')}")


def cmd_buy(args: argparse.Namespace) -> None:
    _place(args, side="buy")


def cmd_sell(args: argparse.Namespace) -> None:
    _place(args, side="sell")


def _place(args: argparse.Namespace, side: str) -> None:
    order = _client().submit_order(
        symbol=args.symbol,
        qty=args.qty,
        notional=args.notional,
        side=side,
        order_type=args.type,
        limit_price=args.limit_price,
    )
    print(f"✓ {side.upper()} order submitted: id={order['id']} "
          f"status={order['status']}")


def cmd_cancel(args: argparse.Namespace) -> None:
    _client().cancel_order(args.order_id)
    print(f"✓ Cancelled order {args.order_id}")


def cmd_telegram(_: argparse.Namespace) -> None:
    TelegramDashboardLinks.print_links()


def _print_json(obj) -> None:
    import json

    print(json.dumps(obj, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Alpaca paper trading CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("connect", help="verify connection and show summary").set_defaults(
        func=cmd_connect
    )
    sub.add_parser("account", help="show full account JSON").set_defaults(
        func=cmd_account
    )
    sub.add_parser("positions", help="list open positions").set_defaults(
        func=cmd_positions
    )

    p_orders = sub.add_parser("orders", help="list orders")
    p_orders.add_argument(
        "status", nargs="?", default="open", choices=["open", "closed", "all"]
    )
    p_orders.set_defaults(func=cmd_orders)

    p_quote = sub.add_parser("quote", help="latest quote for a symbol")
    p_quote.add_argument("symbol")
    p_quote.set_defaults(func=cmd_quote)

    for name, func in (("buy", cmd_buy), ("sell", cmd_sell)):
        p = sub.add_parser(name, help=f"{name} shares")
        p.add_argument("symbol")
        p.add_argument("--qty", type=float, help="number of shares")
        p.add_argument("--notional", type=float, help="dollar amount")
        p.add_argument("--type", default="market", choices=["market", "limit"])
        p.add_argument("--limit-price", type=float, dest="limit_price")
        p.set_defaults(func=func)

    p_cancel = sub.add_parser("cancel", help="cancel an order by id")
    p_cancel.add_argument("order_id")
    p_cancel.set_defaults(func=cmd_cancel)

    sub.add_parser("telegram", help="generate telegram dashboard links").set_defaults(
        func=cmd_telegram
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except AlpacaError as exc:
        print(f"✗ Alpaca API error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
