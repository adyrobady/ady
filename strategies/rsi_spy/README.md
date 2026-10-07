# RSI mean reversion on SPY (daily)

**Status:** researched, not traded
**Run:** `python strategies/rsi_spy/backtest.py [--cost 0.0005] [--cash-yield 0.018]`

## Rules

**Original**
1. Buy when RSI(14) closes under 30
2. Sell when RSI closes above 50

**Commenter's five-rule version**
1. Buy when daily RSI is under 30
2. Sell if price closes below your buy price
3. Sell if RSI falls under 52 after being above 70
4. Buy back if RSI crosses above 52 (only after a previous exit)
5. Sell if RSI crosses below 49

## Results (2000-01-03 to 2026-03-30, 6,599 candles, 0.05%/side, prices without dividends)

| Version | Return | Trades | Win % | PF | Max DD | In market |
|---|---|---|---|---|---|---|
| Original | +66.6% | 35 | 85.7% | 3.27 | 29.0% | 7% |
| Commenter, literal | +79.9% | 371 | 21.6% | 1.29 | 38.8% | 52% |
| Commenter, no rule 2 | +189.7% | 274 | 38.0% | 1.46 | 43.8% | 69% |
| Buy & hold | +334.1% | 1 | — | — | 56.5% | 100% |

With 1.8%/yr interest on idle cash: original +157%, commenter literal +126%.

## Findings

- The commenter's posted result (+179%, 41.8% win) only reproduces if rule 2 is
  dropped or rule 5 is read as "RSI below 49" rather than a cross. Small wording
  changes move it between +80% and +190%, so the edge is fragile.
- Rule 2 (stop at entry price on a daily close) is a hair-trigger and drives the
  21% win rate.
- Very cost-sensitive: commenter version is +161% at 0 cost, +24% at 0.10%/side,
  -41% at 0.20%/side. The original barely changes.
- 2000-2012: original +42.5%, commenter +0.5%, hold -2.2%. All of the
  commenter's edge comes after 2013.
- Useful idea to reuse: re-entering on momentum (rule 4), but it needs a trend
  filter. Rules 4+5 alone made only +50% with a 43% drawdown.
