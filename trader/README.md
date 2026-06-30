# STRATA desktop tools

Two standalone programs (PowerShell, **no installs** — no Node/Python). Both run
the validated daily trend-pullback strategy on real Yahoo data.

## 1. STRATA Live — charting app (`strata-live.ps1`, double-click `run-live.bat`)
A windowed app that **reacts to the live chart**: draws candlesticks + the 10/50
averages, drops **`bull.png` on BUY signals** and **`bear.png` on downtrend/exit
signals**, and shows the current **entry / exit / hard-stop + position size**. It
auto-refreshes every 60s.

- **Timeframe dropdown:** *Daily* (~weeks hold) or *Hourly* (~couple-days hold).
- **Backtest button:** re-tests the edge on the selected timeframe and gives a verdict
  (EDGE HOLDS / MARGINAL / NO EDGE). Finding so far: the edge **holds on Daily**
  (PF ~1.4) but **does NOT hold on Hourly** for ES (PF ~0.8) — so a couple-day-hold
  version of this exact rule isn't profitable; try other markets/timeframes and re-test.
- Headless check (no window): `powershell -ExecutionPolicy Bypass -File strata-live.ps1 -NoUI -Interval 1h`

## 2. STRATA Trader — console backtester
# (original) standalone desktop tool

A single PowerShell program that runs the validated **daily trend-pullback** futures
strategy on real market data — **no website, no installs** (no Node, no Python).
It pulls real daily candles from Yahoo, replays the backtest **printing every trade as
it finds it**, prints the full stats, then tells you the **current setup: where to enter
and where to exit**.

> Educational only — not financial advice. It shows you the levels; it does **not** place orders.

## Run it

- **Easiest:** double-click **`run.bat`**.
- **Or** from a terminal in this folder:
  ```
  powershell -ExecutionPolicy Bypass -File strata-trader.ps1
  ```

### Options
| Command | What it does |
|---|---|
| `run.bat` | Full ES backtest (10y) + live setup |
| `run.bat -Symbol NQ=F -Years 10` | Backtest a different market / window |
| `run.bat -All` | Scan **every** market's live setup (ES, NQ, YM, RTY, CL, GC) |
| `run.bat -Watch -WatchMins 30` | Re-check the live setup every 30 min (Ctrl+C to stop) |
| `run.bat -Account 25000 -RiskPct 1` | Size the position off your account & risk % |

Symbols: `ES=F NQ=F YM=F RTY=F CL=F GC=F SPY QQQ` (or any Yahoo ticker).

## The strategy (same edge as the STRATA app)
- **Long only**, and only while price is **above its 50-day average** (uptrend).
- **Enter** when price pulls back to the **10-day average** and the day **turns up**.
- **Exit** on a daily **close below the 50-day average** (trend break).
- **Hard stop** at −10%. **No fixed target** — winners run (that's why the win rate is
  low but the profit factor is > 1: a few big winners pay for many small losers).

## Honest notes
- Backtest returns are **gross of costs** (no slippage/commission) — a quick cross-check,
  slightly rosier than a real fill. The Python engine in `../backtester` adds pessimistic costs.
- P&L is shown for **one micro contract** (e.g. MES = $5/point).
- Yahoo can rate-limit; if a fetch fails, wait a moment and re-run.
- A passing backtest is necessary, not sufficient — **paper-trade first.**
