"""
Sanity tests for the parts that MUST be correct for honesty:
  1) fill math is pessimistic (buy>ask-ref, sell<bid-ref, costs deducted),
  2) no look-ahead: the asof quote helper never returns a future quote,
  3) wide-spread skip works.

Run: python -m pytest tests/
These test mechanics, NOT "performance".
"""
import pandas as pd
import pytest

from src import fills
from src import engine


FCFG = {
    "extra_slippage_cents": 1.5,
    "commission_per_contract": 0.65,
    "spread_threshold_dollars": 0.10,
    "wide_spread_policy": "skip",
}


def test_buy_at_ask_plus_slippage():
    q = {"bid": 1.00, "ask": 1.05}
    f = fills.entry_fill(q, FCFG, 1)
    # fill price = ask + 0.015
    assert f["fill_price"] == pytest.approx(1.065)
    # cost = 1.065*100 + 0.65
    assert f["cost"] == pytest.approx(107.15, abs=0.01)


def test_sell_at_bid_minus_slippage():
    q = {"bid": 1.00, "ask": 1.05}
    f = fills.exit_fill(q, FCFG, 1)
    assert f["fill_price"] == pytest.approx(0.985)
    assert f["proceeds"] == pytest.approx(97.85, abs=0.01)


def test_round_trip_loses_the_spread_plus_costs_when_price_unchanged():
    q = {"bid": 1.00, "ask": 1.05}
    cost = fills.entry_fill(q, FCFG, 1)["cost"]
    proceeds = fills.exit_fill(q, FCFG, 1)["proceeds"]
    # buying and instantly selling the SAME quote must LOSE money (spread+slip+comm).
    assert proceeds < cost


def test_wide_spread_skips_entry():
    q = {"bid": 1.00, "ask": 1.20}  # 20c spread > 10c threshold
    assert fills.entry_fill(q, FCFG, 1) is None
    # exit is never skipped (you must be able to get out)
    assert fills.exit_fill(q, FCFG, 1) is not None


def test_quote_asof_never_returns_future():
    tz = "America/New_York"
    ts = pd.to_datetime(["2024-01-02 09:30", "2024-01-02 09:31", "2024-01-02 09:32"]).tz_localize(tz)
    df = pd.DataFrame({"ts": ts, "bid": [1, 2, 3], "ask": [1.1, 2.1, 3.1]}).set_index("ts").sort_index()
    # asof 09:31:30 must return the 09:31 row (bid 2), never the 09:32 row.
    row = engine._quote_asof(df, pd.Timestamp("2024-01-02 09:31:30", tz=tz))
    assert row["bid"] == 2
    # before the first quote -> None
    assert engine._quote_asof(df, pd.Timestamp("2024-01-02 09:29", tz=tz)) is None


def test_chain_asof_excludes_future():
    tz = "America/New_York"
    rows = []
    for t, b in [("09:30", 1.0), ("09:31", 1.1), ("09:32", 1.2)]:
        rows.append({"ts": pd.Timestamp(f"2024-01-02 {t}", tz=tz), "strike": 500.0, "type": "C", "bid": b, "ask": b + 0.1})
    chain = pd.DataFrame(rows)
    snap = engine._chain_asof(chain, pd.Timestamp("2024-01-02 09:31", tz=tz))
    # latest at/<=09:31 is the 09:31 quote (bid 1.1), not 09:32
    assert snap.iloc[0]["bid"] == pytest.approx(1.1)
