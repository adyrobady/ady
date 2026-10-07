# Strategies

Every trading strategy lives here, one folder each, so any Claude session (phone,
Mac or cloud) can find it. Each folder has:

- `README.md` — the rules in plain English with exact numbers, status, latest
  results with the test window and costs, and findings
- the code (backtest and/or live bot)

Shared price data goes in `data/` (CSV, `date,close` at minimum).

## Index

| Strategy | Folder | Status |
|---|---|---|
| RSI mean reversion on SPY | [`rsi_spy/`](rsi_spy/) | Researched, not traded |
| Oscillating strategy (dip bounce, fixed +5% exit, 66 names) | — | **Not saved yet.** Code is on the Mac from the "Oscillating strategy" / "Oscillating strategy research" sessions |
| Oscillator backtest with earnings | — | **Not saved yet.** Branch `claude/oscillator-backtest-earnings-pn7tbi` was never pushed |
| RVOL (RVOL2, RVOL3, RVOL5, rvol6, pre-market gaps) | — | **Not saved yet** |
| T212 surprise | — | **Not saved yet** |
| QQQ golden cross | — | **Not saved yet** |
| Dip test / volatile stocks / stop-loss width | — | **Not saved yet** |

To rescue one of the unsaved strategies, open the session that built it and say:
"Save this strategy into `strategies/<name>/` in adyrobady/ady following
`strategies/README.md`, then commit and push to main."
