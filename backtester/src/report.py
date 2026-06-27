"""
Write results.json (consumed by STRATA's 0DTE Lab tab) + an optional PNG and a
plain-text console summary. The JSON is the single source of truth STRATA renders.
"""
from __future__ import annotations
import json
import os
import datetime as dt


def build_payload(cfg: dict, trades: list[dict], metrics: dict, fragility: dict,
                  synthetic: bool = False) -> dict:
    return {
        "schema_version": 1,
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "synthetic": synthetic,   # STRATA shows a red "SAMPLE — NOT REAL" banner when true
        "config": {
            "symbol": cfg["symbol"],
            "start_date": cfg["start_date"],
            "end_date": cfg["end_date"],
            "strategy": cfg["strategy"],
            "fills": cfg["fills"],
            "account": cfg["account"],
            "data_provider": cfg["data"]["provider"],
        },
        "metrics": metrics,
        "fragility": fragility,
        "trades": trades,
    }


def write_json(payload: dict, path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"[report] wrote {path}")


def console_summary(payload: dict):
    m = payload["metrics"]
    fr = payload["fragility"]
    print("\n" + "=" * 64)
    if payload["synthetic"]:
        print("  ⚠  SYNTHETIC DATA — these numbers are FAKE (UI/plumbing demo only)")
        print("=" * 64)
    print(f"  0DTE backtest — {payload['config']['symbol']} "
          f"{payload['config']['start_date']}..{payload['config']['end_date']}")
    print("=" * 64)
    if m.get("n_trades", 0) == 0:
        print("  No trades.", m.get("note", ""))
        return
    print(f"  Trades              {m['n_trades']}")
    print(f"  Total P&L           ${m['total_pnl']:,.2f}  ({m['total_return_pct']}% on ${m['starting_capital']:,})")
    print(f"  Win rate            {m['win_rate_pct']}%")
    print(f"  Profit factor       {m['profit_factor']}")
    print(f"  Sharpe (annual)     {m['sharpe']}")
    print(f"  Max drawdown        {m['max_drawdown_pct']}%")
    print(f"  Avg / worst trade   ${m['avg_trade']:,.2f} / ${m['worst_trade']:,.2f}")
    print(f"  Avg hold            {m['avg_hold_minutes']} min")
    print(f"  Costs paid          spread ${m['total_spread_cost']:,.2f} + commission ${m['total_commission']:,.2f}")
    print("-" * 64)
    print("  FRAGILITY:", fr.get("verdict", "n/a"))
    print("=" * 64 + "\n")


def write_png(payload: dict, path: str):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        print("[report] matplotlib not installed — skipping PNG (STRATA renders its own curve).")
        return
    eq = payload["metrics"].get("equity_curve", [])
    if not eq:
        return
    plt.figure(figsize=(10, 4))
    plt.plot(eq)
    plt.title(f"Equity curve — {payload['config']['symbol']} 0DTE"
              + (" (SYNTHETIC)" if payload["synthetic"] else ""))
    plt.xlabel("trade #"); plt.ylabel("equity ($)")
    plt.tight_layout(); plt.savefig(path, dpi=110); plt.close()
    print(f"[report] wrote {path}")
