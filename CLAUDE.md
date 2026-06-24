# CLAUDE.md

Guidance for AI assistants (and humans) working in this repository.

## What this is

A small, readable **Alpaca paper-trading client** written in Python. It wraps a
subset of the [Alpaca](https://alpaca.markets) REST API using `requests` only —
**no Alpaca SDK**. It ships both a Python library (`alpaca_client`) and a thin
CLI (`main.py`).

Scope is intentionally narrow: account info, positions, orders (place / list /
cancel), and latest quotes. Defaults to the **paper** endpoint — no real money.

## Layout

```
main.py              CLI entry point (argparse subcommands -> client calls)
setup_keys.py        Interactive helper to write credentials into .env
requirements.txt     Single dependency: requests>=2.28
.env.example         Template for credentials (copy to .env)
alpaca_client/
  __init__.py        Public API: AlpacaClient, AlpacaError, load_config, Config
  client.py          AlpacaClient — the REST wrapper + AlpacaError
  config.py          Config dataclass, .env loader, ConfigError
```

There is no `tests/`, no packaging (`setup.py`/`pyproject.toml`), and no CI.
Keep it that way unless explicitly asked to add them.

## Architecture & responsibilities

- **`config.py`** owns all credential/endpoint resolution. `load_config()`
  reads from environment variables first, then falls back to a hand-parsed
  `.env` file (no `python-dotenv` dependency — there's a tiny parser,
  `_parse_env_file`). Missing keys raise `ConfigError` with a friendly message.
  `Config.is_paper` is derived from whether `paper-api` appears in `base_url`.
- **`client.py`** owns all HTTP. `AlpacaClient` holds a `requests.Session` with
  auth headers, and every API method routes through the private `_request()`
  helper, which centralizes URL building, timeouts, and error handling. API
  errors (HTTP >= 400) and network failures both surface as `AlpacaError`
  (network errors use `status_code=0`).
- **`main.py`** owns presentation only. Each `cmd_*` function builds a client
  via `_client()` (which exits with code 2 on `ConfigError`), calls the
  library, and prints. `main()` wraps execution to convert `AlpacaError` into a
  clean stderr message + exit code 1.

Endpoint split: trading calls use `config.base_url`
(`https://paper-api.alpaca.markets`); market-data calls (quotes) use
`config.data_url` (`https://data.alpaca.markets`) via the `base=` arg to
`_request()`.

## Conventions to follow

- **Stay dependency-light.** `requests` is the only runtime dependency. Do not
  add new ones (no `pandas`, no `python-dotenv`, no Alpaca SDK) without being
  asked.
- **Python style:** `from __future__ import annotations` at the top of every
  module; modern type hints (`str | None`, `dict[str, Any]`); concise
  docstrings on public functions/classes.
- **Errors:** raise `AlpacaError` for API/network problems and `ConfigError`
  for missing config. Don't let raw `requests` exceptions escape the client.
- **CLI pattern:** add a new command by writing a `cmd_<name>(args)` function
  and registering a subparser in `build_parser()` with `.set_defaults(func=...)`.
  Keep the library/presentation split — put logic in `alpaca_client`, printing
  in `main.py`.
- **Output style:** the CLI uses `✓`/`✗` prefixes for success/failure and
  aligned columnar output for lists. Match it.
- **`submit_order` invariant:** exactly one of `qty` or `notional` must be
  provided; numeric order fields are sent to the API as strings.
- **Symbols** are upper-cased before hitting the API.

## Security

- **Never commit credentials.** `.env`, `.env.local`, and `*.key` are
  gitignored. `setup_keys.py` writes `.env` with `chmod 600`.
- Secrets live only in env vars or `.env`. Don't hard-code keys, print the
  secret key, or echo it back in logs.
- Default to the paper endpoint. Switching to live trading
  (`https://api.alpaca.markets`) is a deliberate, risky change — never do it
  implicitly.

## Setup & common commands

```bash
pip install -r requirements.txt        # install requests

python setup_keys.py                    # interactive: save keys to .env
python setup_keys.py --key-id ID --secret SECRET   # non-interactive

python main.py connect                  # verify creds, print account summary
python main.py account                  # full account JSON
python main.py positions                # open positions
python main.py orders [open|closed|all] # list orders (default: open)
python main.py quote AAPL               # latest bid/ask
python main.py buy AAPL --qty 1         # market buy 1 share
python main.py buy AAPL --notional 100  # buy $100 worth
python main.py sell AAPL --qty 1
python main.py cancel <order_id>
```

Library usage:

```python
from alpaca_client import AlpacaClient

client = AlpacaClient.from_env()
print(client.get_account()["buying_power"])
order = client.submit_order("AAPL", qty=1, side="buy")
```

## Verifying changes

There is no test suite. To sanity-check changes without real API calls:

```bash
python -c "import main, alpaca_client"        # import / syntax check
python main.py --help                          # argparse wiring
python main.py buy --help                      # subcommand wiring
```

Live verification (`python main.py connect`) requires real paper credentials in
`.env`. Do not assume they are present in this environment, and never check them
in. If you add behavior worth testing, prefer testing `alpaca_client` functions
in isolation (e.g. `config._parse_env_file`, `submit_order` validation) since
they don't require network access.

## Git workflow

- Develop on the assigned feature branch; do not push to `main`/`master`.
- Commit with clear, descriptive messages; push with `git push -u origin <branch>`.
- Do not open a pull request unless explicitly asked.
