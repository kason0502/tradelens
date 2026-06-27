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
    print("[run] computing fragility report (re-running with harsher costs; uses the cache, so fast)…", flush=True)
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
    """Discover which ThetaData v3 endpoints/intervals work + their JSON shape, and
    where the underlying price comes from. Tries several candidates; print to share."""
    import requests
    base = cfg["data"]["thetadata"]["base_url"].rstrip("/")
    sym = cfg.get("symbol", "SPY")
    d = day_str
    candidates = [
        ("list expirations", "/v3/option/list/expirations", {"symbol": sym}),
        ("list strikes", "/v3/option/list/strikes", {"symbol": sym, "expiration": d}),
        ("quote EOD all-strikes", "/v3/option/history/quote",
         {"symbol": sym, "expiration": d, "strike": "*", "right": "call", "start_date": d, "end_date": d, "interval": "eod"}),
        ("quote 1m all-strikes", "/v3/option/history/quote",
         {"symbol": sym, "expiration": d, "strike": "*", "right": "call", "start_date": d, "end_date": d, "interval": "1m"}),
        ("greeks EOD (path)", "/v3/option/history/greeks/eod",
         {"symbol": sym, "expiration": d, "strike": "*", "right": "call", "start_date": d, "end_date": d}),
        ("greeks 1m (path)", "/v3/option/history/greeks/1m",
         {"symbol": sym, "expiration": d, "strike": "*", "right": "call", "start_date": d, "end_date": d}),
        ("greeks (query ivl)", "/v3/option/history/greeks",
         {"symbol": sym, "expiration": d, "strike": "*", "right": "call", "start_date": d, "end_date": d, "interval": "eod"}),
        ("stock ohlc 1m", "/v3/stock/history/ohlc",
         {"symbol": sym, "start_date": d, "end_date": d, "interval": "1m"}),
        ("stock quote 1m", "/v3/stock/history/quote",
         {"symbol": sym, "start_date": d, "end_date": d, "interval": "1m"}),
        ("stock ohlc eod", "/v3/stock/history/ohlc",
         {"symbol": sym, "start_date": d, "end_date": d, "interval": "eod"}),
    ]
    print(f"\nProbing ThetaData v3 at {base} for {sym} {d}\n" + "=" * 64)
    for label, path, params in candidates:
        try:
            r = requests.get(base + path, params=params, timeout=60)
            body = r.text.replace("\n", " ")
            print(f"\n### {label}  [{path}]  HTTP {r.status_code}")
            print(body[:700] + (f" …[{len(r.text)} chars]" if len(r.text) > 700 else ""))
        except Exception as e:
            print(f"\n### {label}  [{path}]  ERROR: {e}")
    print("\n" + "=" * 64 + "\nPaste ALL of this back to your assistant.")


def _publish(cfg: dict):
    """Commit + push results.json so the PUBLIC (Vercel) site picks it up.
    Only needed for the deployed site — the local localhost:8777 view reads the
    file directly and needs no commit."""
    import subprocess
    out = cfg["output"]["results_json"]
    rng = f"{cfg.get('symbol','')} {cfg.get('start_date','')}..{cfg.get('end_date','')}"
    try:
        # -f because results.json is gitignored for normal commits; we publish it explicitly.
        subprocess.run(["git", "add", "-f", out], check=True)
        r = subprocess.run(["git", "commit", "-m", f"backtest results: {rng}"],
                           capture_output=True, text=True)
        if r.returncode != 0 and "nothing to commit" in (r.stdout + r.stderr).lower():
            print("[publish] results unchanged — nothing to push.")
            return
        subprocess.run(["git", "push"], check=True)
        print("[publish] Pushed to GitHub. The public Vercel site will redeploy in ~30s.")
    except FileNotFoundError:
        print("[publish] git not found on PATH — can't auto-publish. Commit/push manually.")
    except subprocess.CalledProcessError as e:
        print(f"[publish] git step failed: {e}. (Local site at localhost:8777 still works without publishing.)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--demo", action="store_true", help="synthetic data (LABELLED fake)")
    ap.add_argument("--start", help="override start date, e.g. 2024-05-15")
    ap.add_argument("--end", help="override end date (omit = same as --start, i.e. one day)")
    ap.add_argument("--symbol", help="override symbol, e.g. SPY")
    ap.add_argument("--check", action="store_true", help="probe what your Polygon key can access, then exit")
    ap.add_argument("--probe-theta", action="store_true", help="dump raw ThetaData v3 response shape, then exit")
    ap.add_argument("--publish", action="store_true", help="after the run, commit+push results.json so the PUBLIC (Vercel) site updates")
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
    if args.publish:
        _publish(cfg)


if __name__ == "__main__":
    main()
