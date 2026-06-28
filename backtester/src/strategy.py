"""
Strategy = swappable functions for STRUCTURE, ENTRY, EXIT, and CONTRACT SELECTION.

Every function takes only data it is allowed to see at decision time. The ENGINE
is what enforces next-bar execution; these functions never peek past the bar they
are handed. Look-ahead-danger spots are marked  # LOOKAHEAD-GUARD .

To test a different idea, write new functions with the same signatures and pass
them to the engine — nothing else changes.
"""
from __future__ import annotations
import datetime as dt
import pandas as pd


# ───────────────────────── STRUCTURE ─────────────────────────
def opening_range(day_bars: pd.DataFrame, minutes: int):
    """
    High/low of the first `minutes` after the open.

    LOOKAHEAD-GUARD: the range is defined ONLY by bars inside the opening window.
    Signals are allowed to fire strictly AFTER this window closes (enforced below
    via `or_end_ts`), so the range never uses future bars relative to a signal.
    """
    if day_bars.empty:
        return None
    open_ts = day_bars["ts"].iloc[0]
    or_end_ts = open_ts + pd.Timedelta(minutes=minutes)
    window = day_bars[day_bars["ts"] < or_end_ts]
    if window.empty:
        return None
    return {
        "orh": float(window["high"].max()),
        "orl": float(window["low"].min()),
        "or_end_ts": or_end_ts,
        "open_ts": open_ts,
        "day_open": float(day_bars["open"].iloc[0]),
    }


def _passes_trend(bars_so_far, rng, cfg):
    """Optional trend filter — only take the long breakout when the day is bullish."""
    tf = cfg.get("trend_filter", "none")
    if tf == "none":
        return True
    cur = bars_so_far.iloc[-1]
    if tf == "above_open":
        return cur["close"] > rng.get("day_open", cur["close"])
    if tf == "above_sma":
        p = int(cfg.get("trend_sma_period", 20))
        closes = bars_so_far["close"]
        if len(closes) < p:
            return True                      # not enough history yet — don't block
        return cur["close"] > closes.tail(p).mean()
    return True


def detect_breakout(bars_so_far: pd.DataFrame, rng: dict, cfg: dict):
    """
    Long signal: price breaks above the opening-range high, then (optionally)
    retests and HOLDS the level. Returns 'long' or None, judged at the LAST bar
    of `bars_so_far`.

    LOOKAHEAD-GUARD: `bars_so_far` must already be truncated to <= current bar by
    the engine. We only ever read its last rows.
    """
    if rng is None:
        return None
    cur = bars_so_far.iloc[-1]
    # No signals until the opening range has fully formed.
    if cur["ts"] < rng["or_end_ts"]:
        return None
    orh = rng["orh"]
    post = bars_so_far[bars_so_far["ts"] >= rng["or_end_ts"]]
    if post.empty:
        return None
    broke = (post["close"] > orh).any()
    if not broke:
        return None
    if not cfg.get("require_retest", True):
        # Plain breakout: fire on the bar that closes above the level.
        base = cur["close"] > orh
    else:
        # Retest-and-hold: after the first break, price must dip back near the level
        # and the CURRENT bar must close back above it (the hold).
        tol = orh * (cfg.get("retest_tolerance_pct", 0.05) / 100.0)
        first_break_idx = post.index[post["close"] > orh][0]
        after_break = post.loc[first_break_idx:]
        retested = (after_break["low"] <= orh + tol).any()
        base = bool(retested and cur["close"] > orh)
    return "long" if (base and _passes_trend(bars_so_far, rng, cfg)) else None


# ───────────────────── CONTRACT SELECTION ─────────────────────
def select_contract(chain_now: pd.DataFrame, underlying_px: float, cfg: dict):
    """
    Pick the 0DTE call to buy from the quotes available AT the entry timestamp.

    LOOKAHEAD-GUARD: `chain_now` must be the asof-snapshot (<= entry ts) built by
    the engine. We never look at later quotes.
    """
    calls = chain_now[chain_now["type"] == "C"].copy()
    if calls.empty:
        return None
    selection = cfg.get("contract_selection", "target_delta")
    target = cfg.get("target_delta", 0.45)
    tol = cfg.get("delta_tolerance", 0.15)
    if selection == "target_delta" and "delta" in calls.columns and calls["delta"].notna().any():
        calls["score"] = (calls["delta"] - target).abs()
        calls = calls[calls["score"] <= tol] if tol else calls
        if calls.empty:
            return None
        return calls.sort_values("score").iloc[0]
    # No greeks -> nearest-ATM by strike (schema.py already warned/aborted as configured).
    calls["score"] = (calls["strike"] - underlying_px).abs()
    return calls.sort_values("score").iloc[0]


# ─────────────────────────── EXIT ───────────────────────────
def exit_decision(position: dict, bar: pd.Series, opt_quote, rng: dict, cfg: dict,
                  sellable_value: float):
    """
    Decide whether to EXIT, judged at the current bar. Returns a reason string or None.

    `sellable_value` is what we'd actually receive selling now (bid - slippage, net
    of commission) — computed by the fill model, never the mid.

    LOOKAHEAD-GUARD: only the current bar + the position's own entry data are read.
    The engine executes the resulting exit on the NEXT bar.
    """
    # 1) Take-profit on the REAL sellable value vs. what we paid.
    tp = cfg.get("take_profit_pct", 40) / 100.0
    if sellable_value >= position["entry_cost"] * (1.0 + tp):
        return "take_profit"
    # 2) Structural stop: underlying closes back below the level we broke.
    if cfg.get("stop_rule") == "close_back_below_level" and rng is not None:
        if bar["close"] < rng["orh"]:
            return "stop_close_below_level"
    # 3) End-of-day flat (config eod_exit_minute) — handled as a hard stop here;
    #    the engine also force-closes any still-open position on the last bar.
    eod = cfg.get("eod_exit_minute", "15:55")
    hh, mm = (int(x) for x in eod.split(":"))
    if (bar["ts"].hour, bar["ts"].minute) >= (hh, mm):
        return "eod"
    return None


# ───────────────── PUT CREDIT SPREAD (premium SELLING) ─────────────────
# Bullish/neutral, defined-risk, theta-positive: SELL a put, BUY a further-OTM
# put for protection. You collect a credit and keep it if price stays up. The
# opposite cost profile to buying calls — you're collecting the spread, not paying it.
def pcs_select(chain_now: pd.DataFrame, S: float, cfg: dict):
    """Pick the short + long put legs from the asof snapshot. Returns (short_row, long_row) or None.
    LOOKAHEAD-GUARD: chain_now is the <= entry-ts snapshot built by the engine."""
    puts = chain_now[chain_now["type"] == "P"].copy()
    if puts.empty:
        return None
    width = float(cfg.get("spread_width", 5))
    otm = float(cfg.get("short_otm_pct", 0.5)) / 100.0
    target_short = S * (1.0 - otm)                       # short put a touch OTM (below price)
    below = puts[puts["strike"] <= target_short]
    pool = below if not below.empty else puts
    short_row = pool.iloc[(pool["strike"] - target_short).abs().values.argmin()]
    short_K = float(short_row["strike"])
    long_K = short_K - width
    long_rows = puts[(puts["strike"] - long_K).abs() < 1e-3]
    if long_rows.empty:                                  # need the exact protective strike to exist
        return None
    return short_row, long_rows.iloc[0]
