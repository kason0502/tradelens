"""
Metrics + equity curve. All computed from the realized trade log (real fills,
all costs already deducted in engine._close). No gross/mid numbers anywhere.
"""
from __future__ import annotations
import math
import pandas as pd


def _sharpe(daily_returns: list[float]) -> float:
    if len(daily_returns) < 2:
        return 0.0
    s = pd.Series(daily_returns)
    sd = s.std(ddof=1)
    if sd == 0 or math.isnan(sd):
        return 0.0
    return float(s.mean() / sd * math.sqrt(252))  # annualized from daily


def _max_drawdown(equity: list[float]) -> float:
    peak = -float("inf")
    mdd = 0.0
    for v in equity:
        peak = max(peak, v)
        if peak > 0:
            mdd = min(mdd, (v - peak) / peak)
    return float(mdd)  # negative fraction, e.g. -0.18


def compute(trades: list[dict], cfg: dict) -> dict:
    cap = cfg["account"]["starting_capital"]
    if not trades:
        return {"n_trades": 0, "note": "No trades — nothing to measure. (Honest zero, not a hidden error.)"}

    trades = sorted(trades, key=lambda t: t["exit_ts"])
    pnls = [t["pnl"] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]

    # Equity curve (cumulative $ on the configured starting capital).
    equity, run = [], cap
    for p in pnls:
        run += p
        equity.append(round(run, 2))

    gross_win = sum(wins)
    gross_loss = -sum(losses)
    profit_factor = (gross_win / gross_loss) if gross_loss > 0 else float("inf")

    # Daily returns for Sharpe.
    by_day = {}
    for t in trades:
        by_day.setdefault(t["day"], 0.0)
        by_day[t["day"]] += t["pnl"]
    daily_ret = [v / cap for v in by_day.values()]

    total_pnl = sum(pnls)
    out = {
        "n_trades": len(trades),
        "starting_capital": cap,
        "total_pnl": round(total_pnl, 2),
        "total_return_pct": round(total_pnl / cap * 100, 2),
        "win_rate_pct": round(len(wins) / len(trades) * 100, 1),
        "profit_factor": round(profit_factor, 2) if profit_factor != float("inf") else None,
        "sharpe": round(_sharpe(daily_ret), 2),
        "max_drawdown_pct": round(_max_drawdown([cap] + equity) * 100, 2),
        "avg_trade": round(total_pnl / len(trades), 2),
        "avg_win": round(sum(wins) / len(wins), 2) if wins else 0.0,
        "avg_loss": round(sum(losses) / len(losses), 2) if losses else 0.0,
        "worst_trade": round(min(pnls), 2),
        "best_trade": round(max(pnls), 2),
        "avg_hold_minutes": round(sum(t["hold_minutes"] for t in trades) / len(trades), 1),
        "total_spread_cost": round(sum(t["spread_cost_paid"] for t in trades), 2),
        "total_commission": round(sum(t["commission_paid"] for t in trades), 2),
        "equity_curve": equity,
        "equity_labels": [t["exit_ts"] for t in trades],
        "by_time_of_day": _by_tod(trades),
        "exit_reasons": _counts(t["exit_reason"] for t in trades),
    }
    return out


def _by_tod(trades: list[dict]) -> dict:
    out = {}
    for bucket in ["open", "midday", "power_hour", "last_30"]:
        sub = [t for t in trades if t["tod"] == bucket]
        if not sub:
            out[bucket] = {"n": 0}
            continue
        pnls = [t["pnl"] for t in sub]
        w = [p for p in pnls if p > 0]
        out[bucket] = {
            "n": len(sub),
            "pnl": round(sum(pnls), 2),
            "win_rate_pct": round(len(w) / len(sub) * 100, 1),
            "avg_trade": round(sum(pnls) / len(sub), 2),
        }
    return out


def _counts(it) -> dict:
    out = {}
    for x in it:
        out[x] = out.get(x, 0) + 1
    return out
