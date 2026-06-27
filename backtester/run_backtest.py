#!/usr/bin/env python3
"""
Run one 0DTE backtest end to end.

    python run_backtest.py                 # uses config.json, real provider
    python run_backtest.py --demo          # synthetic data, LABELLED fake, to wire up the UI
    python run_backtest.py --config my.json

Outputs results.json (which STRATA's 0DTE Lab tab reads) + a console summary.
Honesty: with a real provider, missing data fields ABORT (see src/schema.py); we
never estimate option prices or greeks.
"""
from __future__ import annotations
import argparse
import json
import sys

from src import schema, providers, engine, metrics as M, fragility, report


def load_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def run_real(cfg: dict):
    provider = providers.get_provider(cfg)
    # Only require greeks when the strategy actually selects by delta. Polygon has
    # no historical greeks, so it runs with contract_selection='nearest_atm'.
    uses_delta = cfg["strategy"].get("contract_selection", "target_delta") == "target_delta"

    # Validate the FIRST available trading day's data up front, so schema problems
    # fail fast and loudly instead of silently producing a thin/empty backtest.
    for day in provider.trading_days():
        try:
            opt = provider.load_options(day)
            und = provider.load_underlying(day)
        except Exception as e:
            print(f"[run] {day}: load failed ({e}); trying next day for schema check…")
            continue
        if len(opt) and len(und):
            schema.validate_options(opt, target_uses_delta=uses_delta)
            schema.validate_underlying(und)
            break
    else:
        print("[run] No usable data in the requested range. Nothing estimated. Exiting.")
        sys.exit(2)

    trades = engine.run(provider, cfg)
    mt = M.compute(trades, cfg)
    fr = fragility.run_report(provider, cfg, mt)
    return trades, mt, fr, False


def run_demo(cfg: dict):
    """Synthetic data so you can see the STRATA UI before wiring a provider.
    Clearly flagged synthetic; never presented as performance."""
    from src.demo_data import DemoProvider
    provider = DemoProvider(cfg)
    trades = engine.run(provider, cfg)
    mt = M.compute(trades, cfg)
    fr = fragility.run_report(provider, cfg, mt)
    return trades, mt, fr, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--demo", action="store_true", help="synthetic data (LABELLED fake)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.demo:
        print("[run] DEMO MODE — synthetic data. Numbers are NOT real performance.")
        trades, mt, fr, synth = run_demo(cfg)
    else:
        trades, mt, fr, synth = run_real(cfg)

    payload = report.build_payload(cfg, trades, mt, fr, synthetic=synth)
    out = cfg["output"]["results_json"]
    report.write_json(payload, out)
    # also drop a copy where STRATA looks, if configured
    into = cfg["output"].get("results_into_strata")
    if into and into != out:
        report.write_json(payload, into)
    if cfg["output"].get("write_png"):
        report.write_png(payload, "equity_curve.png")
    report.console_summary(payload)


if __name__ == "__main__":
    main()
