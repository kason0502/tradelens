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


def _check(cfg: dict, day_str: str):
    import datetime as dt
    prov = providers.get_provider(cfg)
    if not hasattr(prov, "diagnose"):
        print("[check] The configured provider has no diagnose(); only Polygon does.")
        return
    day = dt.date.fromisoformat(day_str)
    print(f"\nProbing your Polygon entitlements on {day_str}…\n" + "-" * 60)
    res = prov.diagnose(day)
    for label, r in res.items():
        mark = "OK " if r["ok"] else "NO "
        line = f"  [{mark}] {label}"
        if not r["ok"]:
            line += f"  (status {r['status']}: {r['msg']})"
        print(line)
    print("-" * 60)
    stocks = res.get("Stocks minute bars (underlying SPY)", {}).get("ok")
    quotes = res.get(next((k for k in res if k.startswith("Options QUOTES")), ""), {}).get("ok")
    print("\nWhat this means:")
    if quotes and stocks:
        print("  ✅ You have BOTH the underlying bars and options quotes — run it for real:")
        print("     py run_backtest.py --start 2024-05-15")
    elif quotes and not stocks:
        print("  ⚠ You have OPTIONS QUOTES but NOT the underlying SPY stock bars.")
        print("     The structure strategy needs the underlying price. Two fixes:")
        print("       (A) add a Polygon STOCKS plan (cheapest fix), or")
        print("       (B) reconstruct the underlying from your option quotes via put-call")
        print("           parity (no extra cost; approximate). Ask and I'll enable it.")
    elif not quotes:
        print("  ✕ Your plan does NOT include options QUOTES (bid/ask). Honest fill modeling")
        print("    is impossible without them — the engine will not fake bid/ask. You'd need")
        print("    a Polygon options tier that includes quotes.")
    print()


def _probe_theta(cfg: dict, day_str: str):
    """Hit the v3 quote + greeks endpoints (small EOD pull) and dump the raw shape
    so the adapter can be written to match exactly."""
    import requests, json as _json
    base = cfg["data"]["thetadata"]["base_url"].rstrip("/")
    sym = cfg.get("symbol", "SPY")
    print(f"\nProbing ThetaData v3 at {base} for {sym} {day_str} (EOD, small)…\n" + "-" * 60)
    for label, path in [("OPTION QUOTE", "/v3/option/history/quote"),
                        ("OPTION GREEKS", "/v3/option/history/greeks")]:
        params = {"symbol": sym, "expiration": day_str, "strike": "*", "right": "call",
                  "start_date": day_str, "end_date": day_str, "interval": "1d"}
        try:
            r = requests.get(base + path, params=params, timeout=60)
            print(f"\n### {label}  {path}  -> HTTP {r.status_code}")
            txt = r.text
            print(txt[:1500])
            if len(txt) > 1500:
                print(f"... [truncated, {len(txt)} chars total]")
        except Exception as e:
            print(f"\n### {label}  {path}  -> ERROR: {e}")
    print("\n" + "-" * 60)
    print("Paste the above to your assistant — it reveals the v3 field names/format.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--demo", action="store_true", help="synthetic data (LABELLED fake)")
    ap.add_argument("--start", help="override start date, e.g. 2024-05-15")
    ap.add_argument("--end", help="override end date (omit = same as --start, i.e. one day)")
    ap.add_argument("--symbol", help="override symbol, e.g. SPY")
    ap.add_argument("--check", action="store_true", help="probe what your Polygon key can access, then exit")
    ap.add_argument("--probe-theta", action="store_true", help="dump raw ThetaData v3 response shape, then exit")
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.check:
        _check(cfg, args.start or "2024-05-15")
        return
    if args.probe_theta:
        _probe_theta(cfg, args.start or "2024-05-15")
        return
    # Command-line overrides so you never have to hand-edit config.json.
    if args.start:
        cfg["start_date"] = args.start
        cfg["end_date"] = args.end or args.start
    if args.end and not args.start:
        cfg["end_date"] = args.end
    if args.symbol:
        cfg["symbol"] = args.symbol
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
