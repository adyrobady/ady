#!/usr/bin/env python3
"""Backtest two RSI rule sets on SPY daily closes against buy-and-hold.

    python strategies/rsi_spy/backtest.py
    python strategies/rsi_spy/backtest.py --cost 0.001 --cash-yield 0.018

Fills at the signal day's close. Prices are not dividend-adjusted.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "SPY_daily.csv"


def load(path: Path) -> tuple[list[str], list[float]]:
    with open(path) as f:
        rows = list(csv.DictReader(f))
    return [r["date"] for r in rows], [float(r["close"]) for r in rows]


def rsi(c: list[float], n: int = 14) -> list[float | None]:
    """Wilder's RSI."""
    out: list[float | None] = [None] * len(c)
    g = sum(max(c[i] - c[i - 1], 0) for i in range(1, n + 1)) / n
    l = sum(max(c[i - 1] - c[i], 0) for i in range(1, n + 1)) / n
    out[n] = 100 - 100 / (1 + g / l) if l else 100
    for i in range(n + 1, len(c)):
        ch = c[i] - c[i - 1]
        g = (g * (n - 1) + max(ch, 0)) / n
        l = (l * (n - 1) + max(-ch, 0)) / n
        out[i] = 100 - 100 / (1 + g / l) if l else 100
    return out


def original(flat, p, r, rp, entry, st, opt):
    """Buy RSI<30, sell RSI>50."""
    return r < 30 if flat else r > 50


def commenter(flat, p, r, rp, entry, st, opt):
    """The five-rule version from the Reddit comment."""
    if flat:
        if r < 30:                                   # rule 1
            return True
        return st["exited"] and rp <= 52 < r         # rule 4: cross back above 52
    if opt.get("stop", True) and p < entry:          # rule 2: close below buy price
        return True
    if st["saw70"] and r < 52:                       # rule 3
        return True
    return rp >= 49 > r                              # rule 5: cross below 49


def hold(flat, *_):
    return flat


def run(strategy, closes, R, lo, hi, cost, cash_yield=0.0, **opt) -> dict:
    cash, sh, entry = 100_000.0, 0.0, 0.0
    trades: list[float] = []
    peak = mdd = 0.0
    days_in = 0
    st = {"saw70": False, "exited": False}
    for i in range(lo, hi + 1):
        p, r, rp = closes[i], R[i], R[i - 1]
        if sh:
            days_in += 1
            st["saw70"] |= r > 70
            if strategy(False, p, r, rp, entry, st, opt):
                cash = sh * p * (1 - cost)
                trades.append(p * (1 - cost) / (entry * (1 + cost)) - 1)
                sh, st["exited"] = 0.0, True
        elif strategy(True, p, r, rp, entry, st, opt):
            sh, cash, entry = cash / (p * (1 + cost)), 0.0, p
            st["saw70"] = r > 70
        cash *= (1 + cash_yield) ** (1 / 252)
        e = cash + sh * p
        peak = max(peak, e)
        mdd = max(mdd, 1 - e / peak)
    if sh:
        cash = sh * closes[hi] * (1 - cost)
        trades.append(closes[hi] * (1 - cost) / (entry * (1 + cost)) - 1)
    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t <= 0]
    n = hi - lo + 1
    return {
        "ret": cash / 1e5 - 1,
        "cagr": (cash / 1e5) ** (252 / n) - 1,
        "trades": len(trades),
        "win": len(wins) / max(len(trades), 1),
        "pf": sum(wins) / -sum(losses) if sum(losses) else float("inf"),
        "mdd": mdd,
        "expo": days_in / n,
    }


def fmt(name: str, s: dict) -> str:
    return (f"{name:<28} ret {s['ret']*100:7.1f}%  CAGR {s['cagr']*100:5.1f}%  "
            f"trades {s['trades']:4d}  win {s['win']*100:5.1f}%  PF {s['pf']:5.2f}  "
            f"maxDD {s['mdd']*100:5.1f}%  in-mkt {s['expo']*100:4.0f}%")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--start", default="2000-01-03")
    ap.add_argument("--end", default="2026-03-30")
    ap.add_argument("--cost", type=float, default=0.0005, help="per side, e.g. 0.0005 = 0.05%%")
    ap.add_argument("--cash-yield", type=float, default=0.0, help="annual yield on idle cash")
    a = ap.parse_args()

    dates, closes = load(DATA)
    R = rsi(closes)
    lo = next(i for i, d in enumerate(dates) if d >= a.start)
    hi = max(i for i, d in enumerate(dates) if d <= a.end)
    print(f"{hi - lo + 1} candles {dates[lo]} -> {dates[hi]}, cost {a.cost*100:.2f}%/side, "
          f"cash yield {a.cash_yield*100:.1f}%\n")
    kw = dict(closes=closes, R=R, lo=lo, hi=hi, cost=a.cost, cash_yield=a.cash_yield)
    print(fmt("Original (30 in / 50 out)", run(original, **kw)))
    print(fmt("Commenter 5 rules", run(commenter, **kw)))
    print(fmt("Commenter, no rule 2", run(commenter, stop=False, **kw)))
    print(fmt("Buy & hold", run(hold, **kw)))


if __name__ == "__main__":
    main()
