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
            allowed = s_cfg.get("allowed_sessions")
            in_session = (not allowed) or (_tod_bucket(bar["ts"]) in set(allowed))
            if in_session:
                bars_so_far = bars.iloc[: i + 1]                  # LOOKAHEAD-GUARD: <= i only
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


# ════════════════════ PUT CREDIT SPREAD (premium selling) ════════════════════
def run_day_spread(day: dt.date, bars: pd.DataFrame, chain: pd.DataFrame, cfg: dict) -> list[dict]:
    s = cfg["strategy"]; f = cfg["fills"]; contracts = cfg["account"]["contracts_per_trade"]
    bars = bars.sort_values("ts").reset_index(drop=True)
    if len(bars) < 5:
        return []
    slip = f["extra_slippage_cents"] / 100.0
    comm = f["commission_per_contract"]
    thr = f["spread_threshold_dollars"]
    width = float(s.get("spread_width", 5))
    tp_pct = s.get("tp_pct_of_credit", 50) / 100.0
    stop_mult = s.get("stop_mult_of_credit", 2.0)
    eh, em = (int(x) for x in s.get("entry_time", "10:00").split(":"))
    rng = {"day_open": float(bars["open"].iloc[0])}             # for the trend filter

    trades = []
    position = None
    pending_entry = False
    pending_exit = None
    done_today = False
    n = len(bars)

    def leg_asof(df, ts):
        return _quote_asof(df, ts)

    for i in range(n):
        bar = bars.iloc[i]; is_last = (i == n - 1)

        # ── execute a scheduled intraday exit (next-bar) ──
        if pending_exit and position is not None:
            sq = leg_asof(position["short_df"], bar["ts"]); lq = leg_asof(position["long_df"], bar["ts"])
            if sq is not None and lq is not None:
                trades.append(_settle_spread(position, bar, sq, lq, slip, comm, contracts, pending_exit, expiry=False))
                position = None
            pending_exit = None

        # ── execute a scheduled entry (next-bar) ──
        if pending_entry and position is None and not is_last:
            snap = _chain_asof(chain, bar["ts"])               # LOOKAHEAD-GUARD
            sel = strat.pcs_select(snap, float(bar["close"]), s)
            if sel is not None:
                short_row, long_row = sel
                sb, sa = float(short_row["bid"]), float(short_row["ask"])
                lb, la = float(long_row["bid"]), float(long_row["ask"])
                wide = (sa - sb) > thr or (la - lb) > thr
                cred_ps = (sb - slip) - (la + slip)            # SELL short at bid, BUY long at ask
                if not (wide and f.get("wide_spread_policy", "skip") == "skip") and cred_ps > 0:
                    credit = cred_ps * 100 * contracts - 2 * comm * contracts
                    mid_credit = ((sb + sa) / 2 - (lb + la) / 2)
                    position = {
                        "day": day, "tod": _tod_bucket(bar["ts"]), "entry_ts": bar["ts"],
                        "short_K": float(short_row["strike"]), "long_K": float(long_row["strike"]),
                        "credit": credit, "cred_ps": cred_ps,
                        "open_spread_cost": (mid_credit - cred_ps) * 100 * contracts,
                        "open_comm": 2 * comm * contracts,
                        "sb": sb, "sa": sa,
                        "short_df": _contract_series(chain, float(short_row["strike"]), "P"),
                        "long_df": _contract_series(chain, float(long_row["strike"]), "P"),
                    }
                    done_today = True
            pending_entry = False

        # ── force-settle at expiry (intrinsic) on the last bar ──
        if is_last and position is not None:
            trades.append(_settle_spread(position, bar, None, None, slip, comm, contracts, "eod_expiry",
                                         expiry=True, S=float(bar["close"]), width=width))
            position = None
            continue

        # ── generate signals (acted next bar) ──
        if position is not None:
            sq = leg_asof(position["short_df"], bar["ts"]); lq = leg_asof(position["long_df"], bar["ts"])
            if sq is not None and lq is not None:
                debit_ps = (float(sq["ask"]) + slip) - (float(lq["bid"]) - slip)  # cost to close now
                close_cash = debit_ps * 100 * contracts + 2 * comm * contracts
                pnl_now = position["credit"] - close_cash
                if pnl_now >= position["credit"] * tp_pct:
                    pending_exit = "take_profit"
                elif pnl_now <= -position["credit"] * stop_mult:
                    pending_exit = "stop_loss"
        elif not done_today and not pending_entry:
            if (bar["ts"].hour, bar["ts"].minute) >= (eh, em) and strat._passes_trend(bars.iloc[: i + 1], rng, s):
                pending_entry = True

    return trades


def _settle_spread(pos, bar, sq, lq, slip, comm, contracts, reason, expiry, S=None, width=5.0):
    if expiry:
        short_intr = max(0.0, pos["short_K"] - S); long_intr = max(0.0, pos["long_K"] - S)
        liab = (short_intr - long_intr) * 100 * contracts      # what you owe at expiry (0..width)
        pnl = pos["credit"] - liab
        exit_px = round((short_intr - long_intr), 4); close_comm = 0.0; close_spread_cost = 0.0
        sb = sa = None
    else:
        sb, sa = float(sq["bid"]), float(sq["ask"]); lb, la = float(lq["bid"]), float(lq["ask"])
        debit_ps = (sa + slip) - (lb - slip)
        close_cash = debit_ps * 100 * contracts + 2 * comm * contracts
        pnl = pos["credit"] - close_cash
        mid_debit = ((sb + sa) / 2 - (lb + la) / 2)
        close_spread_cost = (debit_ps - mid_debit) * 100 * contracts
        close_comm = 2 * comm * contracts
        exit_px = round(debit_ps, 4)
    hold_min = (bar["ts"] - pos["entry_ts"]).total_seconds() / 60.0
    return {
        "day": str(pos["day"]), "tod": pos["tod"], "type": "PCS",
        "strike": pos["short_K"], "entry_delta": None,
        "entry_ts": pos["entry_ts"].isoformat(), "exit_ts": bar["ts"].isoformat(),
        "exit_reason": reason,
        "entry_fill_price": round(pos["cred_ps"], 4),          # credit collected /share
        "entry_ref_bid": pos["sb"], "entry_ref_ask": pos["sa"],
        "exit_fill_price": exit_px,                            # debit to close /share (or intrinsic)
        "exit_ref_bid": sb, "exit_ref_ask": sa,
        "entry_cost": round(-pos["credit"], 2),               # negative = credit received
        "exit_proceeds": round(pos["credit"] + pnl - pos["credit"], 2),
        "spread_cost_paid": round(pos["open_spread_cost"] + close_spread_cost, 2),
        "commission_paid": round(pos["open_comm"] + close_comm, 2),
        "pnl": round(pnl, 2),
        "hold_minutes": round(hold_min, 1),
    }


# ════════════════════ FUTURES (trade the contract directly) ════════════════════
def run_day_futures(day: dt.date, bars: pd.DataFrame, _chain, cfg: dict) -> list[dict]:
    s = cfg["strategy"]; fu = cfg.get("futures", {})
    bars = bars.sort_values("ts").reset_index(drop=True)
    if len(bars) < 5:
        return []
    rng = strat.opening_range(bars, s["opening_range_minutes"])
    if rng is None:
        return []
    pv = fu.get("point_value", 50.0)                 # $ per point (ES=50, MES=5, NQ=20, MNQ=2)
    tick = fu.get("tick_size", 0.25)
    slip = fu.get("slippage_ticks", 1) * tick        # slippage in price, applied against you
    comm = fu.get("commission_per_contract", 2.5)
    contracts = cfg["account"]["contracts_per_trade"]
    tp = s.get("take_profit_pct", None)
    max_trades = s.get("max_trades_per_day", 1)
    eh, em = (int(x) for x in s.get("eod_exit_minute", "15:55").split(":"))

    trades = []; position = None; pending_entry = False; pending_exit = None; trades_today = 0
    n = len(bars)
    for i in range(n):
        bar = bars.iloc[i]; is_last = (i == n - 1)

        if pending_exit and position is not None:                # next-bar exit fill
            px = float(bar["open"]) - slip                       # sell to close, slip against us
            trades.append(_close_futures(position, bar, px, pv, slip, comm, contracts, pending_exit))
            position = None; pending_exit = None

        if pending_entry and position is None and trades_today < max_trades and not is_last:
            px = float(bar["open"]) + slip                       # buy long, slip against us
            position = {"day": day, "tod": _tod_bucket(bar["ts"]), "entry_ts": bar["ts"],
                        "entry": px, "entry_ref": float(bar["open"])}
            trades_today += 1; pending_entry = False
        elif pending_entry:
            pending_entry = False

        if is_last and position is not None:                     # force flat at session end
            trades.append(_close_futures(position, bar, float(bar["close"]) - slip, pv, slip, comm, contracts, "eod"))
            position = None; continue

        if position is not None:
            cur = float(bar["close"]); reason = None
            stop_pct = s.get("stop_pct")
            if tp is not None and cur >= position["entry"] * (1 + tp / 100.0):
                reason = "take_profit"
            elif s.get("stop_rule") == "close_back_below_level" and cur < rng["orh"]:
                reason = "stop_close_below_level"
            elif s.get("stop_rule") == "pct" and stop_pct and cur <= position["entry"] * (1 - stop_pct / 100.0):
                reason = "stop_pct"
            elif (bar["ts"].hour, bar["ts"].minute) >= (eh, em):
                reason = "eod"
            if reason:
                pending_exit = reason
        elif trades_today < max_trades and not pending_entry:
            allowed = s.get("allowed_sessions")
            in_session = (not allowed) or (_tod_bucket(bar["ts"]) in set(allowed))
            if in_session and strat.detect_signal(bars.iloc[: i + 1], rng, s) == "long":
                pending_entry = True
    return trades


def _close_futures(pos, bar, exit_px, pv, slip, comm, contracts, reason):
    pnl = (exit_px - pos["entry"]) * pv * contracts - 2 * comm * contracts
    hold = (bar["ts"] - pos["entry_ts"]).total_seconds() / 60.0
    return {
        "day": str(pos["day"]), "tod": pos["tod"], "type": "FUT", "strike": None, "entry_delta": None,
        "entry_ts": pos["entry_ts"].isoformat(), "exit_ts": bar["ts"].isoformat(), "exit_reason": reason,
        "entry_fill_price": round(pos["entry"], 4), "entry_ref_bid": pos["entry_ref"], "entry_ref_ask": pos["entry_ref"],
        "exit_fill_price": round(exit_px, 4), "exit_ref_bid": round(exit_px, 4), "exit_ref_ask": round(exit_px, 4),
        "entry_cost": round(pos["entry"] * pv * contracts, 2), "exit_proceeds": round(exit_px * pv * contracts, 2),
        "spread_cost_paid": round(2 * slip * pv * contracts, 2),     # the slippage we assumed, both sides
        "commission_paid": round(2 * comm * contracts, 2),
        "pnl": round(pnl, 2), "hold_minutes": round(hold, 1),
    }


# ════════════════════ FUTURES SWING (daily bars, hold across days) ════════════════════
def run_swing(bars: pd.DataFrame, cfg: dict) -> list[dict]:
    """Daily/swing: one bar per day, positions held across days. Uses the same
    signal functions (pullback/meanrev/orb-ish) on the rolling DAILY window.
    Exit on take-profit, % stop, or trend break (close below the long MA)."""
    s = cfg["strategy"]; fu = cfg.get("futures", {})
    bars = bars.sort_values("ts").reset_index(drop=True)
    if len(bars) < 60:
        return []
    pv = fu.get("point_value", 50.0); tick = fu.get("tick_size", 0.25)
    slip = fu.get("slippage_ticks", 1) * tick; comm = fu.get("commission_per_contract", 2.5)
    contracts = cfg["account"]["contracts_per_trade"]
    tp = s.get("take_profit_pct"); stop_pct = s.get("stop_pct")
    trend_n = int(s.get("pullback_trend_sma", 50))

    trades = []; position = None; pending_entry = False; pending_exit = None
    n = len(bars)
    for i in range(n):
        bar = bars.iloc[i]; is_last = (i == n - 1)

        if pending_exit and position is not None:
            trades.append(_close_futures(position, bar, float(bar["open"]) - slip, pv, slip, comm, contracts, pending_exit))
            position = None; pending_exit = None
        if pending_entry and position is None and not is_last:
            px = float(bar["open"]) + slip
            position = {"day": bar["ts"].date(), "tod": "swing", "entry_ts": bar["ts"],
                        "entry": px, "entry_ref": float(bar["open"])}
            pending_entry = False
        elif pending_entry:
            pending_entry = False
        if is_last and position is not None:
            trades.append(_close_futures(position, bar, float(bar["close"]) - slip, pv, slip, comm, contracts, "end_of_data"))
            position = None; continue

        win = bars.iloc[: i + 1]
        if position is not None:
            cur = float(bar["close"]); reason = None
            if tp and cur >= position["entry"] * (1 + tp / 100.0):
                reason = "take_profit"
            elif stop_pct and cur <= position["entry"] * (1 - stop_pct / 100.0):
                reason = "stop_pct"
            elif len(win) >= trend_n and cur < win["close"].tail(trend_n).mean():
                reason = "trend_break"
            if reason:
                pending_exit = reason
        elif not pending_entry:
            if strat.detect_signal(win, None, s) == "long":
                pending_entry = True
    return trades


def run(provider, cfg: dict, quiet: bool = False) -> list[dict]:
    all_trades: list[dict] = []
    stype = cfg["strategy"].get("type")
    if stype == "futures_swing":                       # daily series, single pass (not per-day)
        if not quiet:
            print("[engine] daily/swing mode — loading full series…", flush=True)
        bars = provider.all_bars()
        if not quiet:
            print(f"[engine] {len(bars)} daily bars "
                  f"({cfg.get('start_date')}..{cfg.get('end_date')})", flush=True)
        return run_swing(bars, cfg)
    is_futures = (stype == "futures_orb")
    runner = run_day_futures if is_futures else (run_day_spread if stype == "put_credit_spread" else run_day)
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
            chain = None if is_futures else provider.load_options(day)   # futures needs no option chain
        except Exception as e:
            if not quiet:
                print(f"skip (no data: {str(e)[:60]})", flush=True)
            continue
        if bars is None or len(bars) == 0 or (not is_futures and (chain is None or len(chain) == 0)):
            if not quiet:
                print("skip (no data)", flush=True)
            continue
        t = runner(day, bars, chain, cfg)
        all_trades.extend(t)
        if not quiet:
            print(f"{len(t)} trade(s)", flush=True)
    return all_trades
