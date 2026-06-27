# STRATA — Project Context

> Living doc. Update at the end of any session that changes scope, status, or direction.
> Last updated: 2026-06-27 (session 23). **New: `/backtester`** — a standalone, honesty-first Python 0DTE options backtesting engine (pessimistic fills: buy ask/sell bid + slippage + commission; strict no-look-ahead; next-bar execution; fragility report). It's separate from the single-file STRATA app; STRATA gained a **0DTE Lab** tab that renders the engine's `results.json` in its own UI (synthetic sample fallback until you wire a real options feed — ThetaData/Polygon/Databento). See `backtester/README.md` + `ASSUMPTIONS.md`. Session 22 below covers the in-app scorecard/dollars work.
> Last updated: 2026-06-27 (session 22). **Setup scorecard + dollars:** the dashboard plan now leads with a scorecard (probability · confidence · samples · win rate · R:R · expected value → approve/skip), and the AI Lab has a per-timeframe "profit in dollars" panel proving a low win rate can still be profitable (worked $ math + always-on principle). Also rebalanced the level engine: stops sit beyond MAJOR swings with a ≥1.1×ATR floor (fixed a tight-stop bug that crushed the win rate), targets take the nearest reachable real pivot. The engine is honestly ~breakeven and selective — EV gates the recommendation, it won't fake a positive edge. See session 21 below.
> Last updated: 2026-06-27 (session 21). **Structure-anchored levels:** stops & targets are placed on REAL market-structure pivots (multi-scale swing liquidity + supply/demand), preferring a real level that also fits the horizon's risk band; the band/clamp only acts as a last resort when no pivot qualifies, and the plan labels honestly say whether each level is "real structure" or "fitted to the horizon". Probability/EV (session 20) is a separate scoring layer and never moves the levels. See session 20 below.
> Last updated: 2026-06-27 (session 20). **Probabilistic edge engine:** the AI now predicts a calibrated **win probability** per setup via an online logistic model trained per timeframe from every self-test (real-indicator feature vector), and the dashboard leads with **Expected Value (R)** + win% + a ¼-Kelly size and a +EV/skip verdict. Honesty is provable: **Brier-score calibration** + **explainable factor weights** in a new AI Lab panel. See session 19 below for the dashboard↔AI-Lab link.
> Last updated: 2026-06-27 (session 19). **Dashboard ↔ AI Lab:** the Trade Plan now shows an "AI Lab · {Intraday/Swing/Position} model" strip (tests, win%, R-edge, learned construction) + a "{style} style" tag, so picking a swing (1W/1M) or position (3M–1Y) horizon visibly pulls a different learned model; a "Sharpen {model} ↗" button trains that bucket from the dashboard. Swing vs Position are now genuinely different (per-bucket forward-holding cap `FWD_CAP`). See session 18 below for the per-timeframe engine.
> Last updated: 2026-06-27 (session 18). **Per-timeframe learning:** the self-learning engine now learns **each timeframe separately** — Intraday / Swing / Position buckets, each with its own evolutionary genome population and per-strategy edge (`byTF`). Intraday trains on **real 5-/1-min bars**, swing/position on daily; the dashboard reads the bucket matching the selected horizon, so shorter *and* longer setups both improve and drive the live plan. AI Lab gained a timeframe selector (per-bucket scoreboard/leaderboard/construction); auto-learn rotates all three buckets. See session-17 note below for the prior timeframe/levels fixes.
> Last updated: 2026-06-27 (session 17). **Timeframe fix:** the dashboard now defaults to **Intraday · 1-min** and short horizons read near-term structure (intraday uses real live 1-minute bars) instead of a year of daily candles — so short timeframes no longer target monthly lows / record highs. `clampLevels` (previously dead) is wired in so every horizon's stop/target respects its realistic risk band (R:R preserved). The AI Lab now actually refreshes the live prediction after learning (it was calling the disabled legacy `load()`), and shows a "Recent form" trend. Known gap: self-tests still train on daily data only (see TODO "intraday learning").
> Last updated: 2026-06-27 (session 16). The **self-learning AI is the headline now**: it grades trades to the real stop/target, is **regime-aware**, ranks strategies by **edge + efficiency**, and **evolves its own trade construction** (stop-buffer + min-R:R genomes) toward max expectancy — the winning construction drives the dashboard. Levels sit on **real structure (supply/demand/liquidity zones)** with the stop closer than the target; the dashboard reads in **$ and %** (not ticks); the **AI read talks like a human coach**; **proof windows** back any claim with a chart + reasoning. Tabs added this session: **Strategy** and **Journal** (self-grading). See "Current state" + the standing self-critique directive (memory + `TODO.md` polish backlog).

## What this is
STRATA (formerly TradeLens Pro) is a **single-file** web app (`index.html`, no build step, no framework) that combines:
1. A **premium marketing landing page** (shown first), and
2. A **trading-analysis dashboard** ("the app") behind a *Launch App* button.

It pulls **real market data**, derives structure-based trade plans (entry / stop / targets), embeds professional charts, and offers AI analysis. Educational tool — not financial advice.

## Who it's for
Serious independent retail traders. Voice/feel: precise, institutional, trustworthy, data-driven — not flashy marketing.

## Current state (2026-06-27, session 16)
- **Self-learning engine (AI Lab) — the core differentiator.** It runs self-tests on real history: classify a setup → build levels from **real structure** → take a **market entry at the decision close** → walk **every forward bar until the stop or target hits** (no time-exit; win only if target beats stop, scored in **R**; "open" if it never resolves = not counted). It learns on three levels — (1) **which strategy** (structure fit), (2) **how much to trust each** via `stratStats` = expectancy × sample-trust + **efficiency** (R per bar), **per market regime** (`marketRegime`: uptrend/downtrend/range/volatile), and (3) **how to construct the trade** — an **evolutionary genome layer** (`AI_MEMORY.params.pop`) searching `{stopBuf, minRR}` for max expectancy (ε-greedy pick + mutate-the-best every 25 trials). The **best learned construction drives the live dashboard**. AI Lab shows: Win/Loss %, expectancy, net R + split bar; an **edge-ranked strategy leaderboard**; the **regime matrix**; the **"learned by evolution" construction panel**; and a **live console** where each trade is clickable to **replay it on real candles** (decision divider, why, confidence Δ) via the reusable **proof window** (`#moWhy`).
- **Structure-based levels (zones), not arbitrary numbers.** `findZones` (swing highs = supply/sell, swing lows = demand/buy) + `structureLevels(candles,dir,atr,cfg)`: stop just **beyond the nearest liquidity**, target at the **next opposing zone** that pays ≥ the learned min-R:R — so **stop is always closer than target** (loss < win). `structCandles` feeds a wider, horizon-scaled context window.
- **Dashboard = panel terminal driven by a ticker-only ask bar.** `renderDash` fills: header (live price + conviction), **TradingView** chart, an **AI-prediction candlestick chart** (full-width, real OHLC + price axis + "now" divider + forward reward/risk cone + **shaded demand/supply zones**), the **Trade Plan** (entry/stop/target in **$ and %**, each row naming its structure; R:R), a **human-coach AI read** (timestamped mentor narration + Bull-vs-Bear + conviction checklist + per-indicator tooltips), a key-metrics strip, signals, an options-Greeks panel, and a persistent watchlist. **Bull/bear bias is timeframe-aware** (windowed by the horizon selector). "+ Track this setup" sends a plan to the Journal.
- **Tabs (left sidebar `.appnav`, grouped Terminal/Research/Assistant):** Dashboard · High Volume (movers) · Screener · News · **Strategy** (day-by-day playbook + real candlestick charts w/ zones + date-computed event calendar + live candidate scans) · Pro Traders · Backtest · Performance · AI Lab · **Journal** (self-grading: live price grades tracked setups pending→open→win/loss in R) · AI Chat · Alerts · Feedback.
- **Sentiment-reactive theme:** the whole UI flips **red when bearish**, green otherwise (`setMood`, `--ac-rgb`, `body.bearish`, `FX_MOOD`). Brand = the user's PNGs (`logo.png`, `bull.png`/`bear.png` mascots). Accent = **emerald `#22c55e`**; green/red reserved for up/down (P&L). Animated `#fxCanvas` backdrop behind the app.
- **Reliable market data via the `/api/yf` proxy** (local PowerShell `serve.ps1` / Vercel `api/yf.js`); `raceAttempts` prefers it, public CORS proxies are fallback. Background pollers stand down during user lookups (`bgIdle`, `window.__userFetch`). **Shared cross-user learning** via `api/learn.js` (Vercel KV) with per-device localStorage fallback.
- **Standing directive (session 16+):** continuously self-critique (designer/FE/UX/QA) and fix weaknesses without being asked — see the memory note + the polish backlog in `TODO.md`. Known cleanup: dead `dashWhy`/legacy `renderDash(ticker,q,a)`/`.wk`/`runScan`; reusable candlestick renderer; AI-read panel is tall.
- Repo git-tracked (`main`) and **on GitHub at `kason0502/tradelens`**, auto-deployed via Vercel (`index.html` homepage; `api/yf.js`/`api/claude.js`/`api/learn.js`; `.vercelignore` excludes `.claude` + `*.md`).

## How to run / preview
- No Node/Python on this machine. Use the bundled PowerShell server (**which is also the `/api/yf` data proxy** — that's what makes data load reliably):
  - Preview config `tradelens` → `.claude/serve.ps1` serves the repo root at `http://localhost:8777`.
  - In Claude Code: `preview_start` with name `tradelens`. **Restart the preview after editing `serve.ps1`.**
  - Always open via `http://localhost:8777` (through the server) — opening `index.html` as a bare file has no proxy and falls back to flaky public proxies.
- **To host it for everyone (so the server runs in the cloud, not just locally):** see `DEPLOY.md` (GitHub → Vercel; `api/yf.js` runs the proxy server-side for all visitors).
- ⚠️ The **screenshot tool cannot capture this page** (live TradingView iframe + offscreen tab pauses CSS animations → timeout). Verify with `preview_eval` / computed styles / console logs instead, and ask the user to view in a real browser.

## Server, data & hosting (how the server works + GitHub/Vercel)

### Why a server at all
Browsers can't fetch stock data straight from Yahoo (CORS blocks it). The app used to bounce requests through flaky free public CORS proxies → "nothing loads". The fix is a **server-side proxy**: the *server* fetches Yahoo (servers aren't bound by CORS), so data loads fast and reliably. There are two server functions:
- **`/api/yf?url=…`** — market-data proxy (Yahoo/Stooq). The reason stocks load.
- **`/api/claude`** — Claude (Anthropic) proxy. Lets the owner's key power AI for every visitor.

### Same code, two homes
- **Local dev:** `.claude/serve.ps1` is the preview server AND the `/api/yf` proxy (pure PowerShell `Invoke-WebRequest`, no Node). `/api/claude` does NOT exist locally (PowerShell only does `/api/yf`), so locally AI is bring-your-own-key. **Restart the preview after editing `serve.ps1`.** Always open via `http://localhost:8777`.
- **Deployed (Vercel):** `api/yf.js` and `api/claude.js` are serverless functions that do the same thing in the cloud for **every visitor**. `vercel.json` gives `api/claude.js` a 30s timeout.
- **Client fallback chain** (`raceAttempts` in `index.html`): try `/api/yf` first (`_yfProxyOK`); if absent (bare file / plain static host), race the public CORS proxies in parallel. Background pollers throttle + stand down during a user lookup (`bgIdle`, `window.__userFetch`).

### GitHub + Vercel
- **Repo:** `https://github.com/kason0502/tradelens` (`origin/main`). Connected via `git remote add origin …`.
- **History note:** the GitHub repo had been updated by *manual file uploads* ("Add files via upload"), so it diverged from the local git history and was **missing files** (the PNGs, `api/yf.js`, `api/learn.js`). Reconciled in session 14 by **merging** `origin/main` into the complete local project with `-X ours` (keep local files) + `--allow-unrelated-histories`, then a normal push. Local and GitHub are now in sync.
- **Deploy flow:** push to GitHub → **Vercel auto-redeploys** in ~30s. `index.html` at root is the homepage; `api/*.js` become functions. `.vercelignore` keeps `.claude` + `*.md` out of the build.
- **AI for everyone:** the owner set **`ANTHROPIC_API_KEY`** (encrypted) in Vercel env vars; once `api/claude.js` is deployed, the app probes `/api/claude` on load and gives all visitors AI with no key prompt (this bills the owner's key). Optional: Vercel KV for pooled learning (`api/learn.js`, see `DEPLOY_BACKEND.md`).
- **Pushing updates:** normal `git add -A && git commit -m "…" && git push` (first time needed `git push --set-upstream origin main` to set tracking). Full step-by-step in **`DEPLOY.md`**.

## Key product decisions
- **Real data only** — never simulate/fake prices. If a feed fails, show an honest error. (Educational — not financial advice.)
- **One accent (emerald `#22c55e`), used sparingly.** Green/red are reserved for up/down (P&L) only; a neutral near-white (`#e8eaed`) marks the current-price/entry reference on charts. No big gradients or glowing blobs (except the deliberate `#fxCanvas` backdrop).
- **AI is optional.** The whole engine (analysis + self-learning) is rule-based and works with **no key**; a Claude key (or the deployed `/api/claude` proxy) only enriches the natural-language reads. Self-test learning is **pooled across users** when the backend is deployed.
- **Levels come from real structure (zones) + ATR, never arbitrary numbers** — stop just beyond liquidity, target at the next supply/demand zone, **stop always closer than target**. The construction (`{stopBuf, minRR}`) is itself **learned by evolution**. Dashboard reads distances in **$ and %** (the old "ticks" framing is gone).
- **Two charts on the dashboard:** the **TradingView** widget (interactive) + STRATA's own **AI-prediction candlestick** (draws the entry/stop/target, projection cone, and shaded zones TradingView can't).
- **Honesty over hype:** judge the learning by **expectancy (R)**, not win rate — a sub-50% win rate is profitable at the right R:R. Don't claim it invents strategies; it tunes which to trust, when (regime), and how to build the trade.

## Known constraints / gotchas
- **Data reliability is solved by the `/api/yf` proxy** (local PowerShell or deployed Vercel). The public CORS proxies are now only a *fallback* (used when the page is opened as a bare file with no server) — flaky/rate-limited. `raceAttempts` fires proxies in parallel (first valid wins), so even the fallback fails fast instead of hanging.
- TradingView widget needs internet; shows a fallback message pointing to "AI Levels" if blocked.
- `/api/claude` exists (`api/claude.js`) but only runs when **deployed** (Vercel reads `ANTHROPIC_API_KEY`); the **local** PowerShell server doesn't run it, so locally AI is bring-your-own-key.
- Commits warn `LF will be replaced by CRLF` — harmless (Windows).

## The doc set (keep all current)
- `PROJECT_CONTEXT.md` — this file: what/why/status.
- `ARCHITECTURE.md` — code structure, key functions, data flow.
- `DESIGN_SYSTEM.md` — tokens, colors, components, conventions.
- `TODO.md` — prioritized outstanding work.
- `CHANGELOG.md` — notable changes, newest first.
