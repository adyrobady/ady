# Alpaca Paper Trading Client

A small, readable Python client for the [Alpaca](https://alpaca.markets) **paper
trading** API. Built on `requests` only — no Alpaca SDK required.

## What it does

- Connect to your Alpaca paper account and verify credentials
- View account details, buying power, equity
- List open positions
- Place and cancel orders (market / limit, by share qty or dollar amount)
- Fetch the latest quote for a symbol

## 1. Get your paper API keys

1. Log in at <https://app.alpaca.markets/paper/dashboard/overview>
2. In the right-hand panel, generate / view your **paper** API keys
3. Copy the **Key ID** and **Secret Key** (the secret is shown only once)

## 2. Save your keys (pick one)

**Easiest — interactive:**

```bash
python setup_keys.py
# paste your Key ID and Secret when prompted
```

**Or pass them as arguments:**

```bash
python setup_keys.py --key-id YOUR_KEY_ID --secret YOUR_SECRET
```

**Or by hand:** copy `.env.example` to `.env` and fill in the values.

Either way, your keys land in `.env`, which is **gitignored** and never committed.

## 3. Verify the connection

```bash
python main.py connect
```

You should see your account number, status, and buying power.

## Usage

```bash
python main.py account            # full account JSON
python main.py positions          # open positions
python main.py orders open        # open|closed|all
python main.py quote AAPL         # latest bid/ask
python main.py buy AAPL --qty 1   # buy 1 share (market)
python main.py buy AAPL --notional 100   # buy $100 worth
python main.py sell AAPL --qty 1
python main.py cancel <order_id>
```

## Use it from your own code

```python
from alpaca_client import AlpacaClient

client = AlpacaClient.from_env()
account = client.get_account()
print(account["buying_power"])

order = client.submit_order("AAPL", qty=1, side="buy")
print(order["id"], order["status"])
```

## Notes

- Defaults to the **paper** endpoint (`https://paper-api.alpaca.markets`). No
  real money is involved.
- To use live trading, change `APCA_API_BASE_URL` to
  `https://api.alpaca.markets` — but understand the risk first.
- Dependencies: `pip install -r requirements.txt` (just `requests`).

## Home Assistant (for Claude)

Home Assistant is connected to Claude as a **custom connector**, not through
files in this repo.

1. In Home Assistant, add the **Model Context Protocol Server** integration and
   choose which devices to share under *Settings → Voice assistants → Expose*.
2. At <https://claude.ai/customize/connectors>, click **Add custom connector**:
   - **URL:** `https://<your-id>.ui.nabu.casa/api/mcp`
   - **Authentication:** Sign in now
   - **OAuth client:** Use your own OAuth client, client ID `https://claude.ai`
3. Click **Add**, sign in to Home Assistant, then start a new session.
