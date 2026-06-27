"""
Normalized data schema + validation.

Design rule (from the spec): if a field is missing, we say *exactly* what
breaks — we NEVER estimate it. A 0DTE options backtest is only as honest as its
quotes, so a missing field is a hard stop, not a silent fallback.
"""
from __future__ import annotations
import pandas as pd

# ── Option-quote frame: one row per (timestamp, expiration, strike, type) ──
OPTION_COLUMNS = {
    "ts":               "tz-aware datetime (the quote's exchange timestamp)",
    "expiration":       "date of option expiry",
    "strike":           "float strike price",
    "type":             "'C' or 'P'",
    "bid":              "float NBBO bid (what you SELL into)",
    "ask":              "float NBBO ask (what you BUY at)",
    "delta":            "float option delta",
    "gamma":            "float option gamma",
    "theta":            "float option theta",
    "underlying_price": "float underlying price stamped on the quote",
}

# ── Underlying minute bars (for structure detection) ──
UNDERLYING_COLUMNS = {
    "ts":    "tz-aware datetime (bar close time)",
    "open":  "float",
    "high":  "float",
    "low":   "float",
    "close": "float",
}

# What each field is USED for — so a missing field's blast radius is explicit.
_BREAKS_IF_MISSING = {
    "bid": "Cannot model exits. We SELL at the bid; without it every exit price is fiction. ABORT.",
    "ask": "Cannot model entries. We BUY at the ask; without it every entry price is fiction. ABORT.",
    "delta": "Cannot select a contract by target delta. Options: (a) supply delta, or "
             "(b) switch strategy.target to 'nearest_atm' (strike-based, no greeks). We do NOT compute delta from a pricing model.",
    "gamma": "Only used for reporting/diagnostics. Trade selection still works, but greek-risk columns will be blank.",
    "theta": "Only used for reporting/diagnostics. Trade selection still works, but decay columns will be blank.",
    "underlying_price": "Used to sanity-check structure vs. the option chain. If missing we fall back to the "
                        "underlying bar close, which is acceptable ONLY if both come from the same clock.",
    "expiration": "Cannot isolate the 0DTE contract (same-day expiry). ABORT.",
    "strike": "Cannot identify the contract. ABORT.",
    "type": "Cannot tell calls from puts. ABORT.",
    "ts": "Cannot order quotes in time — no-look-ahead is impossible. ABORT.",
}

# Fields whose absence is fatal vs. merely degrading.
_FATAL = {"ts", "expiration", "strike", "type", "bid", "ask"}


class SchemaError(Exception):
    pass


def explain_missing(field: str) -> str:
    return _BREAKS_IF_MISSING.get(field, f"Unknown field '{field}'.")


def validate_options(df: pd.DataFrame, *, target_uses_delta: bool) -> pd.DataFrame:
    """Validate an option-quote frame. Raise loudly on fatal gaps; warn on the rest."""
    missing = [c for c in OPTION_COLUMNS if c not in df.columns]
    fatal = [c for c in missing if c in _FATAL]
    if target_uses_delta and "delta" in missing:
        fatal.append("delta")
    if fatal:
        lines = [f"  - {c}: {explain_missing(c)}" for c in fatal]
        raise SchemaError(
            "Option quotes are missing fields the engine cannot honestly work around:\n"
            + "\n".join(lines)
            + "\n\nNothing was estimated. Fix the data source (or change config) and re-run."
        )
    for c in missing:
        print(f"[schema] WARNING: '{c}' missing — {explain_missing(c)}")

    if not isinstance(df["ts"].dtype, pd.DatetimeTZDtype):
        raise SchemaError(
            "'ts' is not timezone-aware. Naive timestamps make no-look-ahead unverifiable "
            "across DST and venue clocks. Localize it to the exchange tz first."
        )
    # Quotes must be sane: ask >= bid > 0. A crossed/zero quote is bad data, not an opportunity.
    bad = df[(df["ask"] < df["bid"]) | (df["bid"] <= 0)]
    if len(bad):
        print(f"[schema] WARNING: dropped {len(bad)} crossed/zero quotes (ask<bid or bid<=0).")
        df = df[(df["ask"] >= df["bid"]) & (df["bid"] > 0)].copy()
    return df.sort_values("ts").reset_index(drop=True)


def validate_underlying(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in UNDERLYING_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaError(
            "Underlying minute bars missing required columns: " + ", ".join(missing)
            + ". These drive structure detection (opening range / breaks); cannot proceed."
        )
    if not isinstance(df["ts"].dtype, pd.DatetimeTZDtype):
        raise SchemaError("Underlying 'ts' is not timezone-aware. Localize it first.")
    return df.sort_values("ts").reset_index(drop=True)
