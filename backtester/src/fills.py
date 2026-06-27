"""
Fill modeling — the pessimistic core. Every assumption here is worst-case on
purpose, so that a strategy showing profit AFTER these costs is more likely real.

Rules:
  - BUY at the ASK, SELL at the BID. Never the mid. Always.
  - Extra slippage of `extra_slippage_cents` per contract, applied AGAINST you on
    both entry and exit (you pay more to buy, receive less to sell).
  - Commission `commission_per_contract` per leg (entry is a leg, exit is a leg).
  - If the spread > `spread_threshold_dollars`:
        policy 'skip'        -> the trade does not happen (returns None).
        policy 'take_worse'  -> you still trade, at ask/bid + full slippage
                                (already the worst side); modeled explicitly, not silently.
"""
from __future__ import annotations

MULT = 100  # one option contract controls 100 shares


def _cents(x):  # cents -> dollars
    return x / 100.0


def entry_fill(quote, cfg: dict, contracts: int):
    """
    Cost to OPEN a long option position. Returns dict or None (skipped).
    Positive `cost` = cash out.
    """
    bid, ask = float(quote["bid"]), float(quote["ask"])
    spread = ask - bid
    slip = _cents(cfg["extra_slippage_cents"])
    comm = cfg["commission_per_contract"]
    thr = cfg["spread_threshold_dollars"]

    if spread > thr:
        if cfg.get("wide_spread_policy", "skip") == "skip":
            return None  # LOOKAHEAD-SAFE: decided from the same-bar quote only
        # take_worse: proceed, fully penalized (no mid mercy).
    fill_price = ask + slip               # buy at ask, pay extra
    cost = fill_price * MULT * contracts + comm * contracts
    return {
        "fill_price": round(fill_price, 4),
        "ref_bid": round(bid, 4),
        "ref_ask": round(ask, 4),
        "spread": round(spread, 4),
        "spread_cost": round((spread + slip) * MULT * contracts, 2),  # vs. trading at the bid
        "commission": round(comm * contracts, 2),
        "cost": round(cost, 2),
    }


def exit_fill(quote, cfg: dict, contracts: int):
    """
    Proceeds from CLOSING the long position. `proceeds` = cash in (after costs).
    Always sells at the bid minus slippage minus commission — never skipped (you
    must be able to get out), but the wide-spread penalty still bites.
    """
    bid, ask = float(quote["bid"]), float(quote["ask"])
    spread = ask - bid
    slip = _cents(cfg["extra_slippage_cents"])
    comm = cfg["commission_per_contract"]
    fill_price = max(0.0, bid - slip)     # sell at bid, receive less
    proceeds = fill_price * MULT * contracts - comm * contracts
    return {
        "fill_price": round(fill_price, 4),
        "ref_bid": round(bid, 4),
        "ref_ask": round(ask, 4),
        "spread": round(spread, 4),
        "spread_cost": round((spread + slip) * MULT * contracts, 2),
        "commission": round(comm * contracts, 2),
        "proceeds": round(proceeds, 2),
    }


def sellable_value(quote, cfg: dict, contracts: int) -> float:
    """What we'd NET right now if we sold — used by exit logic (bid, not mid)."""
    return exit_fill(quote, cfg, contracts)["proceeds"]
