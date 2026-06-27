"""
Fragility report — the "is this edge real or an artifact of my fill assumptions?"
test. We re-run the backtest with HARSHER costs and see how fast the edge dies.

If a small change in assumptions flips profit -> loss, we say so loudly. A robust
edge degrades gracefully; a fragile one collapses.
"""
from __future__ import annotations
import copy

from . import engine
from . import metrics as M


def run_report(provider, cfg: dict, base_metrics: dict) -> dict:
    base_pnl = base_metrics.get("total_pnl", 0.0)
    scenarios = []

    slip_mults = cfg["fragility"]["slippage_multipliers"]
    base_slip = cfg["fills"]["extra_slippage_cents"]
    for m in slip_mults:
        c = copy.deepcopy(cfg)
        c["fills"]["extra_slippage_cents"] = round(base_slip * m, 4)
        tr = engine.run(provider, c)
        mt = M.compute(tr, c)
        scenarios.append({
            "label": f"slippage x{m}",
            "slippage_cents": c["fills"]["extra_slippage_cents"],
            "total_pnl": mt.get("total_pnl", 0.0),
            "win_rate_pct": mt.get("win_rate_pct", 0.0),
            "profit_factor": mt.get("profit_factor"),
        })

    # Tighter spread filter = more trades skipped (or, with take_worse, more pain).
    base_thr = cfg["fills"]["spread_threshold_dollars"]
    for f in cfg["fragility"]["spread_threshold_tighten"]:
        c = copy.deepcopy(cfg)
        c["fills"]["spread_threshold_dollars"] = round(base_thr * f, 4)
        tr = engine.run(provider, c)
        mt = M.compute(tr, c)
        scenarios.append({
            "label": f"spread filter x{f}",
            "spread_threshold": c["fills"]["spread_threshold_dollars"],
            "total_pnl": mt.get("total_pnl", 0.0),
            "win_rate_pct": mt.get("win_rate_pct", 0.0),
            "n_trades": mt.get("n_trades", 0),
        })

    # The headline fragility number: P&L change when slippage is widened 50%.
    plus50 = next((s for s in scenarios if s["label"] == "slippage x1.5"), None)
    degrade_pct = None
    flips = False
    if plus50 is not None and base_pnl != 0:
        degrade_pct = round((plus50["total_pnl"] - base_pnl) / abs(base_pnl) * 100, 1)
        flips = (base_pnl > 0) and (plus50["total_pnl"] <= 0)

    verdict = "n/a"
    if base_pnl <= 0:
        verdict = "Base case is not profitable — fragility is moot until it is."
    elif flips:
        verdict = ("⚠ FRAGILE: a 50% wider slippage assumption flips this from profit to LOSS. "
                   "Do not trust the base result — it lives or dies on the fill model.")
    elif degrade_pct is not None and degrade_pct <= -50:
        verdict = ("⚠ SHAKY: +50% slippage erases more than half the P&L. The edge is thin relative "
                   "to fill costs.")
    elif degrade_pct is not None:
        verdict = ("Reasonably robust: +50% slippage costs "
                   f"{abs(degrade_pct)}% of P&L but it stays positive. Still verify out-of-sample.")

    return {
        "base_total_pnl": base_pnl,
        "slippage_plus50_total_pnl": plus50["total_pnl"] if plus50 else None,
        "degrade_pct_at_plus50_slippage": degrade_pct,
        "flips_to_loss": flips,
        "verdict": verdict,
        "scenarios": scenarios,
    }
