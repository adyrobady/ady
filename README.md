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

## Home Assistant MCP (for Claude Code)

This repo ships a project-scoped [`.mcp.json`](.mcp.json) that connects Claude
Code to Home Assistant's built-in **Model Context Protocol Server** integration,
so Claude can read entity states and control devices exposed to Assist.

1. **Enable the MCP server in Home Assistant** (2025.2 or newer):
   *Settings → Devices & services → Add integration → "Model Context Protocol Server"*.
2. **Choose what Claude can see/control:** *Settings → Voice assistants → Expose*.
   Only exposed entities are available over MCP.
3. **Create a token:** your HA profile → *Security* → *Long-lived access tokens* → *Create token*.
4. **Export the variables** in the shell you launch Claude Code from
   (Claude Code reads the environment, not `.env`):

   ```bash
   export HASS_URL=http://homeassistant.local:8123   # or your Nabu Casa / remote URL
   export HASS_TOKEN=your_long_lived_access_token
   ```

5. **Start Claude Code** in this directory, approve the `home-assistant` server
   when prompted, and check it with `/mcp` (or `claude mcp list`).

Claude must be able to reach `HASS_URL` over the network. A `homeassistant.local`
address only works on your home LAN; for cloud sessions use an externally
reachable URL (e.g. Nabu Casa remote UI) and allow that host in the
environment's network settings.
