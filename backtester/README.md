# 0DTE Options Backtester (honesty-first)

A minute-level intraday options backtesting engine for 0DTE structural strategies.
The design priority is **honesty over flattering results**: pessimistic, worst-case
fill assumptions throughout, strict no-look-ahead, and a fragility report — so that
any strategy showing profit *after* all of this is more likely to be real.

It is a **standalone Python project**. Results are written to `results.json`, which
the STRATA app renders in its **0DTE Lab** tab (same UI) — see "STRATA integration".

> ⚠️ There is **no Python or options data in this repo by default.** This engine is
> the plumbing; you point it at a real options feed and run it where Python lives.

---

## Quick start

```bash
cd backtester
pip install -r requirements.txt

# See the STRATA UI immediately with SYNTHETIC (fake, labelled) data:
python run_backtest.py --demo

# Real run (after wiring a provider + config.json):
python run_backtest.py
```

`--demo` writes a `results.json` stamped `"synthetic": true`; STRATA shows a red
**SAMPLE — NOT REAL** banner. Never read demo numbers as performance.

---

## Strategy (first one implemented): SPY 0DTE ORB calls

- **Structure:** opening range = high/low of the first 15 min (09:30–09:45 ET).
- **Entry:** underlying breaks above the opening-range high, then **retests and
  holds** (dips back near the level, current bar closes back above). Long the 0DTE
  call nearest `target_delta` (0.45).
- **Exit:** take-profit at **+40% on the real sellable value** (bid, not mid),
  **stop** if the underlying closes back below the level, **EOD flat** at 15:55.
- All swappable — see `src/strategy.py`.

---

## Pessimistic fills (the core; `src/fills.py`)

| Assumption | Setting |
|---|---|
| Buy price | **ASK** + slippage (never mid) |
| Sell price | **BID** − slippage (never mid) |
| Extra slippage | **1.5¢/contract** each side (configurable) |
| Commission | **$0.65/contract per leg** |
| Wide spread (> $0.10) | **skip** the trade (or `take_worse` — modeled explicitly) |

The trade log shows the spread cost you paid on every fill.

---

## Bias prevention

- **No look-ahead:** at bar *i*, only data with `ts <= i` is used. Option quotes are
  fetched **asof** (latest quote at/before the bar). Every risky spot is marked
  `# LOOKAHEAD-GUARD` in the source (`grep -rn LOOKAHEAD-GUARD src`).
- **Next-bar execution:** a signal at bar *i* is filled at bar *i+1*, never the
  signal bar (`src/engine.py`).
- **Time-of-day slicing:** every trade is tagged open / midday / power_hour / last_30.

---

## Data — wire a provider

Default is **ThetaData** (`src/providers.py: ThetaDataProvider`), which pulls real
minute NBBO bid/ask + greeks from a locally-running **Theta Terminal**
(`http://127.0.0.1:25510`). You need a ThetaData subscription whose tier exposes
option **greeks**; if it doesn't, the run **aborts** (it will not invent delta).

> The exact endpoint paths/params and strike scaling vary by tier/version. The
> adapter targets the v2 REST API and is commented "verify against your docs."
> The bullet-proof path is `LocalFileProvider`: download to CSV/Parquet matching
> the schema in `src/schema.py` and set `data.provider: "local"`.

### Polygon.io (`PolygonProvider`)
Set `data.provider: "polygon"` and export your key: `setx POLYGON_API_KEY "..."`
(re-open the shell). Honest limits:
- Real **NBBO bid/ask** via `/v3/quotes` — needs an **Options tier that includes
  quotes** (not just trade aggregates). If you only have aggregates, the run
  **aborts** (it won't fake bid/ask from trades).
- **No historical greeks** on Polygon — so set `strategy.contract_selection:
  "nearest_atm"` (strike-based). Greeks are never invented.
- It pulls quotes only for strikes within `data.polygon.strike_window` of the
  opening ATM (a full 0DTE chain is huge); fine for an ATM strategy.

Databento drops in the same way by subclassing `BaseProvider`.

### What breaks if a field is missing (we never estimate)
- `bid`/`ask` → **abort** (every fill would be fiction).
- `expiration`/`strike`/`type`/`ts` → **abort** (can't identify/order contracts).
- `delta` → **abort if** selecting by target delta; or switch to nearest-ATM
  (strike-based) selection — your explicit choice, not a silent model.
- `gamma`/`theta` → diagnostics only; trade selection still works.
- `underlying_price` → falls back to the underlying bar close (same clock only).

---

## Output

- `results.json` — full trade-by-trade log (entry/exit timestamps, fill prices vs.
  bid/ask, spread cost paid, P&L), metrics, equity curve, time-of-day breakdown,
  and the fragility report.
- Console summary. Optional `equity_curve.png` (`output.write_png: true`).
- **Metrics:** total return, win rate, profit factor, Sharpe (annualized from daily),
  max drawdown, avg & worst trade, avg hold time, total spread/commission paid.
- **Fragility report:** P&L under slippage ×1.5 and ×2 and a tighter spread filter.
  If +50% slippage flips profit → loss, it says so **loudly**.

---

## STRATA integration

`run_backtest.py` also writes a copy to `output.results_into_strata` (default
`../backtester/results.json`). STRATA's **0DTE Lab** tab fetches it and renders the
scoreboard, equity curve, fragility report, time-of-day grid, and trade log in
STRATA's design. If no `results.json` exists it falls back to `results.sample.json`
(synthetic) with a SAMPLE banner.

---

## Where results could STILL overstate real performance
See the long-form list in `ASSUMPTIONS.md` — read it before trusting any green number.

## Tests
```bash
python -m pytest tests/        # no-look-ahead + fill-math checks
```
