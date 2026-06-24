# CLAUDE.md

Guidance for AI assistants (and humans) working in this repository.

## What this is

A small, readable Python client for the [Alpaca](https://alpaca.markets)
**paper trading** API. It is built on `requests` only — deliberately no Alpaca
SDK — and exposes both a CLI (`main.py`) and an importable package
(`alpaca_client`).

The guiding principle of this codebase is **simplicity and readability over
features**. Keep new code thin, dependency-light, and easy to read end to end.

## Layout

```
ady/
├── main.py              # CLI entry point (argparse subcommands)
├── setup_keys.py        # Interactive helper to write .env credentials
├── requirements.txt     # Single dependency: requests
├── .env.example         # Template for credentials (copy to .env)
├── .env                 # Your real keys — gitignored, never committed
├── README.md            # User-facing setup & usage docs
└── alpaca_client/
    ├── __init__.py      # Public exports: AlpacaClient, AlpacaError, load_config, Config
    ├── client.py        # AlpacaClient — thin REST wrapper over the Alpaca API
    └── config.py        # Config dataclass + .env / env-var loading
```

### Module responsibilities

- **`alpaca_client/config.py`** — Loads credentials from environment variables,
  falling back to a local `.env` file parsed by a tiny hand-rolled parser (no
  `python-dotenv` dependency). Exposes the `Config` dataclass and
  `load_config()`. Raises `ConfigError` with a friendly message when keys are
  missing. `Config.is_paper` distinguishes paper vs. live by inspecting the
  base URL.
- **`alpaca_client/client.py`** — `AlpacaClient`, a `requests.Session`-based
  wrapper. All HTTP goes through the private `_request()` helper, which handles
  URL building, error translation (`AlpacaError`), and empty-body responses.
  Covers account, positions, orders (submit/list/cancel), and latest quotes.
  Market-data calls target a separate `data_url` base.
- **`main.py`** — argparse CLI. Each subcommand is a `cmd_*` function wired up
  in `build_parser()`. `_client()` centralizes client construction and turns
  `ConfigError` into a clean exit.
- **`setup_keys.py`** — Standalone convenience script that writes `.env` with
  `0o600` permissions. Has no dependency on the `alpaca_client` package.

## Setup & running

```bash
pip install -r requirements.txt        # just `requests`

python setup_keys.py                    # interactive: paste Key ID + Secret
# or: python setup_keys.py --key-id ID --secret SECRET
# or: cp .env.example .env  and edit by hand

python main.py connect                  # verify credentials
```

### CLI commands

```bash
python main.py connect                  # verify connection, show summary
python main.py account                  # full account JSON
python main.py positions                # open positions
python main.py orders [open|closed|all] # list orders (default: open)
python main.py quote AAPL               # latest bid/ask
python main.py buy AAPL --qty 1         # market buy by share count
python main.py buy AAPL --notional 100  # market buy by dollar amount
python main.py sell AAPL --qty 1
python main.py buy AAPL --qty 1 --type limit --limit-price 150
python main.py cancel <order_id>
```

### Library usage

```python
from alpaca_client import AlpacaClient

client = AlpacaClient.from_env()
account = client.get_account()
order = client.submit_order("AAPL", qty=1, side="buy")
```

## Conventions

- **Python style**: `from __future__ import annotations` at the top of every
  module; modern type hints (`dict[str, Any]`, `str | None`). Target Python 3.9+.
- **Docstrings**: Every module, class, and public function has a concise
  docstring. Match the existing terse, example-driven tone.
- **HTTP**: Never call `requests` directly from command or method code — route
  everything through `AlpacaClient._request()` so error handling and headers
  stay consistent. Use the `base=` argument for market-data endpoints
  (`config.data_url`) vs. the default trading base URL.
- **Errors**: Raise `AlpacaError` for API/network failures (it carries
  `status_code`); raise `ConfigError` for missing configuration; raise
  `ValueError` for caller misuse (e.g. passing both `qty` and `notional`). The
  CLI catches these at the top level and exits non-zero with a `✗` message.
- **Order quantities**: Exactly one of `qty` (shares) or `notional` (dollars)
  must be provided to `submit_order`; numeric values are stringified in the
  request body, as the Alpaca API expects strings.
- **CLI output**: User-facing success uses a `✓` prefix, errors a `✗` prefix
  (errors go to stderr). Keep this consistent when adding commands.
- **Adding a CLI command**: write a `cmd_<name>(args)` function, then register
  a subparser in `build_parser()` with `.set_defaults(func=cmd_<name>)`.

## Security & safety

- **Credentials never get committed.** `.env`, `.env.local`, and `*.key` are
  gitignored. Never hardcode keys, never echo secrets into logs or commit
  messages, and never add a real `.env` to the repo.
- **Paper by default.** The default base URL is
  `https://paper-api.alpaca.markets` — no real money. Live trading requires
  explicitly setting `APCA_API_BASE_URL=https://api.alpaca.markets`. Treat any
  change that points at the live endpoint as high-risk and call it out
  explicitly; never switch to live trading silently.

## Configuration (environment variables)

| Variable               | Required | Default                                | Purpose                    |
| ---------------------- | -------- | -------------------------------------- | -------------------------- |
| `APCA_API_KEY_ID`      | yes      | —                                      | Alpaca key ID              |
| `APCA_API_SECRET_KEY`  | yes      | —                                      | Alpaca secret key          |
| `APCA_API_BASE_URL`    | no       | `https://paper-api.alpaca.markets`     | Trading endpoint           |
| `APCA_DATA_URL`        | no       | `https://data.alpaca.markets`          | Market-data endpoint       |

Real environment variables take precedence over values in `.env`.

## Tests & tooling

There is currently **no test suite, linter config, or CI** in this repository.
There is no build step — it runs directly with the Python interpreter. If you
add tests, prefer `pytest` (the `.gitignore` already ignores `.pytest_cache/`)
and keep them dependency-light to match the project's spirit.

## Git workflow

- Active development branch: `claude/claude-md-docs-dpawuk`.
- Commit with clear, descriptive messages; do not open a pull request unless
  explicitly asked.
- Verify `.env` and other secrets are never staged before committing.
