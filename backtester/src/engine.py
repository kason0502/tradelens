"""
Backtest engine — the no-look-ahead, next-bar-execution loop.

Execution model (read this — it's the anti-bias core):
  * At bar i we may GENERATE a signal using bars[0..i] only.
  * That signal is ACTED ON at bar i+1 (entry/exit fills use bar i+1's quotes).
  * Option quotes are fetched "asof" (the latest quote timestamped <= the bar),
    so we never read a quote from the future.
Every place future data could sneak in is marked  # LOOKAHEAD-GUARD .
"""
from __future__ import annotations
import datetime as dt
import pandas as pd

from . import strategy as strat
from . import fills as fillmod


def _tod_bucket(ts: pd.Timestamp) -> str:
    t = (ts.hour, ts.minute)
    if t < (10, 30):
        return "open"          # 09:30–10:30
    if t < (14, 0):
        return "midday"        # 10:30–14:00
    if t < (15, 30):
        return "power_hour"    # 14:00–15:30
    return "last_30"           # 15:30–16:00


def _chain_asof(chain: pd.DataFrame, ts: pd.Timestamp) -> pd.DataFrame:
    """Latest quote per (strike,type) at or before `ts`. LOOKAHEAD-GUARD: ts<= only."""
    past = chain[chain["ts"] <= ts]
    if past.empty:
        return past
    return past.sort_values("ts").groupby(["strike", "type"], as_index=False).tail(1)


def _contract_series(chain: pd.DataFrame, strike: float, typ: str) -> pd.DataFrame:
    sub = chain[(chain["strike"] == strike) & (chain["type"] == typ)].copy()
    return sub.set_index("ts").sort_index()


def _quote_asof(contract_df: pd.DataFrame, ts: pd.Timestamp):
    """The contract's latest quote at or before `ts`, or None. LOOKAHEAD-GUARD."""
    if contract_df.empty:
        return None
    idx = contract_df.index
    pos = idx.searchsorted(ts, side="right") - 1
    if pos < 0:
        return None
    return contract_df.iloc[pos]


def run_day(day: dt.date, bars: pd.DataFrame, chain: pd.DataFrame, cfg: dict) -> list[dict]:
    s_cfg = cfg["strategy"]
    f_cfg = cfg["fills"]
    contracts = cfg["account"]["contracts_per_trade"]
    max_trades = s_cfg.get("max_trades_per_day", 1)

    bars = bars.sort_values("ts").reset_index(drop=True)
    if len(bars) < 5:
        return []
    rng = strat.opening_range(bars, s_cfg["opening_range_minutes"])
    if rng is None:
        return []

    trades: list[dict] = []
    position = None
    pending_entry = False
    pending_exit = None
    trades_today = 0
    n = len(bars)

    for i in range(n):
        bar = bars.iloc[i]
        is_last = (i == n - 1)

        # ── 1) EXECUTE actions scheduled at the PREVIOUS bar (next-bar fills) ──
        if pending_exit and position is not None:
            q = _quote_asof(position["contract_df"], bar["ts"])
            if q is not None:
                ex = fillmod.exit_fill(q, f_cfg, contracts)
                trades.append(_close(position, bar, ex, pending_exit))
                position = None
            pending_exit = None

        if pending_entry and position is None and trades_today < max_trades and not is_last:
            snap = _chain_asof(chain, bar["ts"])                 # LOOKAHEAD-GUARD
            pick = strat.select_contract(snap, float(bar["close"]), s_cfg)
            if pick is not None:
                fill = fillmod.entry_fill(pick, f_cfg, contracts)  # may be None if spread skipped
                if fill is not None:
                    cdf = _contract_series(chain, float(pick["strike"]), pick["type"])
                    position = {
                        "day": day, "strike": float(pick["strike"]), "type": pick["type"],
                        "entry_ts": bar["ts"], "entry_fill": fill, "entry_cost": fill["cost"],
                        "contract_df": cdf, "tod": _tod_bucket(bar["ts"]),
                        "entry_delta": float(pick["delta"]) if "delta" in pick and pd.notna(pick.get("delta")) else None,
                    }
                    trades_today += 1
            pending_entry = False

        # ── 2) Force-close anything still open on the final bar (no overnight 0DTE) ──
        if is_last and position is not None:
            q = _quote_asof(position["contract_df"], bar["ts"])
            if q is not None:
                ex = fillmod.exit_fill(q, f_cfg, contracts)
                trades.append(_close(position, bar, ex, "eod_forced"))
                position = None
            continue

        # ── 3) GENERATE signals from data up to THIS bar (acted next iteration) ──
        if position is not None:
            q = _quote_asof(position["contract_df"], bar["ts"])
            if q is not None:
                sv = fillmod.sellable_value(q, f_cfg, contracts)
                reason = strat.exit_decision(position, bar, q, rng, s_cfg, sv)
                if reason:
                    pending_exit = reason
        elif trades_today < max_trades and not pending_entry:
            bars_so_far = bars.iloc[: i + 1]                      # LOOKAHEAD-GUARD: <= i only
            if strat.detect_breakout(bars_so_far, rng, s_cfg) == "long":
                pending_entry = True

    return trades


def _close(position: dict, bar: pd.Series, ex: dict, reason: str) -> dict:
    pnl = ex["proceeds"] - position["entry_cost"]
    hold_min = (bar["ts"] - position["entry_ts"]).total_seconds() / 60.0
    return {
        "day": str(position["day"]),
        "tod": position["tod"],
        "type": position["type"],
        "strike": position["strike"],
        "entry_delta": position["entry_delta"],
        "entry_ts": position["entry_ts"].isoformat(),
        "exit_ts": bar["ts"].isoformat(),
        "exit_reason": reason,
        "entry_fill_price": position["entry_fill"]["fill_price"],
        "entry_ref_bid": position["entry_fill"]["ref_bid"],
        "entry_ref_ask": position["entry_fill"]["ref_ask"],
        "exit_fill_price": ex["fill_price"],
        "exit_ref_bid": ex["ref_bid"],
        "exit_ref_ask": ex["ref_ask"],
        "entry_cost": round(position["entry_cost"], 2),
        "exit_proceeds": round(ex["proceeds"], 2),
        "spread_cost_paid": round(position["entry_fill"]["spread_cost"] + ex["spread_cost"], 2),
        "commission_paid": round(position["entry_fill"]["commission"] + ex["commission"], 2),
        "pnl": round(pnl, 2),
        "hold_minutes": round(hold_min, 1),
    }


def run(provider, cfg: dict, quiet: bool = False) -> list[dict]:
    all_trades: list[dict] = []
    days = provider.trading_days()
    if not quiet:
        print(f"[engine] processing {len(days)} trading days "
              f"({cfg.get('start_date')}..{cfg.get('end_date')})… first pass downloads + caches; re-runs are fast.",
              flush=True)
    for i, day in enumerate(days, 1):
        if not quiet:
            print(f"[engine] {i}/{len(days)}  {day} … ", end="", flush=True)
        try:
            bars = provider.load_underlying(day)
            chain = provider.load_options(day)
        except Exception as e:
            if not quiet:
                print(f"skip (no data: {str(e)[:60]})", flush=True)
            continue
        if bars is None or len(bars) == 0 or chain is None or len(chain) == 0:
            if not quiet:
                print("skip (no data)", flush=True)
            continue
        t = run_day(day, bars, chain, cfg)
        all_trades.extend(t)
        if not quiet:
            print(f"{len(t)} trade(s)", flush=True)
    return all_trades
