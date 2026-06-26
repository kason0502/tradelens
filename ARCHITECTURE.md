# TradeLens Pro — Architecture

> Living doc. Update when structure, key functions, or data flow change.
> Last updated: 2026-06-25

Everything lives in **`index.html`** (~3,500 lines): one `<style>` block, the landing markup, the app markup + modals, and one inline `<script>`. External deps loaded via CDN: **Chart.js** (mini sparkline) and **TradingView** `tv.js` (main chart).

## Top-level page structure
```
<head><style> … all CSS … </style></head>
<body>
  #landing            ← marketing page (lx- namespace), shown first, position:fixed z-index:1000
  <aside class="appnav"> … </aside>   ← APP left SIDEBAR (logo + grouped .snav tabs + footer); replaces the old top <nav>
  .page-wrap          ← shifted right (margin-left = sidebar width)
    .appbar           ← sticky MOVERS banner (#appBarTrack streaming tape)
    .main-col
      #aiBanner       ← slim "connect AI" strip
      .tab-pane#tab-dashboard   ← the terminal
      .tab-pane#tab-movers      ← High Volume / big movers (renderMovers)
      .tab-pane#tab-traders / #tab-backtest / #tab-performance /
               #tab-ailab / #tab-ai / #tab-screener / #tab-news / #tab-alerts / #tab-feedback
  modals: #moAcct #moAlert #moAI
  <script> … all JS … </script>
</body>
```
- `launchApp()` hides `#landing`; `showLanding()` shows it. The sidebar logo calls `showLanding()`.
- `mainTab(name, btn)` switches `.tab-pane` and sets the sidebar `.snav[data-tab=name]` active (also clears legacy `.ntab`); lazily inits each tab (movers, screener, traders, backtest, performance, ailab, news, feedback).
- **Sidebar** `.appnav` (grouped Terminal/Research/Assistant + footer Live/Connect-AI/Account). The top "✨ AI" key button was removed; `#aiKeyBtn` is now the footer `.snav` (`updateAIBadge` toggles its label).
- **Movers** (`#tab-movers`): `MOVERS_UNIVERSE` → `loadMovers` (parallel `fetchQuote`; **recomputes day-% from the price series** since the proxy prev-close is unreliable, filters `|pct|>22`) → `paintMovers` (sortable cards) + `paintMoversStats` (breadth header) + `paintMoversBanner` (the `.appbar` tape). `fetchQuote` now also returns raw `vol`.
- **Screener** (`#tab-screener`): `renderScreener`→`loadScreener` reuses the movers universe and runs `analyze` per name; `scanFilter` (bullish/breakout/oversold/bearish/trend/all) + `paintScreen` (breadth stats + results table). Replaced the old static `runScan`/`SCAN_DATA` (still in file, unused).
- **Performance** (`renderPerformance`): btHistory stats + by-strategy/direction/timeframe + `drawEquityCurve(id)` (cumulative sim-P&L; id defaults to `#perfEquity`, also drawn into `#btEquity` on the Backtest scoreboard) + risk/edge metrics (profit factor, avg win/loss, expectancy, discipline) + AI coach.
- **Journal** (`#tab-journal`, `renderJournal`): self-grading trade journal. Dashboard "+ Track this setup" (`trackSetup`) logs the current plan into `JOURNAL` (localStorage `tlpro_journal_v1`). Background `journalTick` (init poller, `bgIdle`-gated) pulls `fetchLivePrice` per tracked ticker and `gradeJournal` advances state pending→open→win/loss in **R**. `updateJournalBadge` drives the nav pill; `jToast` for confirmations; `journalClose`/`journalRemove`/`journalClearResolved` manage entries.
- **Strategy** (`#tab-strategy`, `renderStrategy`): day-by-day ideas. `STRAT_DAYS` (Mon–Fri themes + scan type) drives a "Today's focus" card (weekday from `new Date()`), a date-computed event calendar (`eventCalendar` via `_nthFriday`/`_lastWeekday`: OPEX/witching/NFP/month-end with TODAY/THIS-WEEK badges), and an expandable weekday playbook. `loadStratCandidates(type,elId)` reuses `loadScreener`/`SCREEN`/`scanFilter` (movers cache) to surface live names per day's setup. Each day renders the setup on a **real annotated chart** — `loadRealStrategyChart(ticker,key,elId)` fetches real candles, runs `labLevels`+`aiStrategyLevels`, and `annotatedChartHTML` draws the real price line + 20-day avg + labeled Resistance/Support/Entry/Stop/Target lines + swing markers + the strategy's numbered thought process (ticker editable; Today auto-loads SPY, weekday cards lazy-load). The pure-SVG schematic (`strategyChartBlock`/`strategyDiagram`/`STRAT_DIAGRAMS`, `STRAT_DKEY` maps weekday→pattern) remains as the data-failure fallback.
- **Animated background** (`#fxCanvas`, end-of-script IIFE): aurora blobs + perspective grid + parallax constellation + trade-print flashes; fixed at `z-index:0` behind both landing (made transparent) and app.

## Data layer (real market data)
- `tryOne(url)` → `buildAttempts(yahooUrl)` returns an array of CORS-proxy-wrapped fetchers; `extractChart(txt)` parses Yahoo JSON out of whatever a proxy returns.
- `fetchQuote(ticker)` — 1y daily + best-effort 1m intraday; returns `{price,change,pct,hi52,lo52,volFmt,name,closes,h1d,h1m,h3m,h6m,h1y}`. Falls back to `fetchStooq`.
- `fetchBacktestSeries(ticker,tf)` — OHLC at 1m/5m/10m/1d for the backtest.
- `fetchLivePrice(ticker)` — lightweight single-request latest price for streaming.
- `analyze(ticker,price,pct,hi52,lo52,closes)` → indicators + sentiment/score + `signals` + `strategies` text.

## Strategy engine (shared by Dashboard + AI Lab)
- `LAB_STRATEGIES` — 5 strategies: `pullback, breakout, breakdown, oversold, rangefade`. Each has `compute(candles)` → `{dir, steps[]}` where steps carry entry/stop/tp prices.
- `labLevels(d)` → `{resis,lo,support,sma20Val,range,last,atr,swHigh,swLow}` (real structure). Helpers: `atr()`, `swingPivot()`.
- `normTrade(dir,e,st,t1,t2,lv)` — enforces correct ordering + min reward:risk (≥1.3R TP1, ≥2.2R TP2).
- **Horizon-aware levels (dashboard):** `horizonCandles(q)` picks the structure window by `currentDTE` (`HZ_WIN`: 0DTE→intraday `h1d`, 1W/1M→a few recent daily bars, 1Y→~170 daily); `clampLevels(entry,sl,tp1,tp2)` scales the whole setup around entry so the stop stays in a realistic %-band per horizon (`HZ_RISK`), preserving R:R. So the horizon selector now actually changes how near/far the stop & targets sit.
- `classifySetup(candles,a)` — picks the best strategy from structure + learned confidence.
- `aiStrategyLevels(key,candles)` — pulls final entry/sl/tp1/tp2 from a strategy's steps.

## Self-learning AI (algorithmic, no Claude needed)
- `AI_MEMORY` persisted in localStorage key `tlpro_ai_memory_v1`. `stratConf(key)` (Wilson-shrunk win rate).
- **Outcome-based learning:** `simulateSetup(tk,full,cut,q)` walks the chosen strategy's real entry/stop/target forward bar-by-bar → win (target first), loss (stop first), or no-fill; result in **R**. `applyLearning(sim,auto)` updates per-strategy wins/losses/pnl + records confidence before→after, logs a rich entry, posts to the shared pool. Used by both `aiSelfBacktest(rounds)` (manual) and `aiAutoLearnOnce()` (idle auto).
- **Live console:** `renderAIConsole()` renders `AI_MEMORY.log` into `#aiConsole` (terminal stream: time/ticker/setup/dir/levels/result-R/conf-delta). `renderAILearnStats()` (confidence bars + scoreboard) calls it. UI: AI Lab tab. `resetAIMemory()`.
- **Proof windows ("show the receipts"):** reusable modal `#moWhy` + `openWhy(title,sub,body)`. `simulateSetup` stores a compact candle `snap` (decision tail + forward bars) per trade. Clicking a console row → `aiWhy(idx)` → `proofChartSVG(snap,e)` (candlesticks + a "decision" divider, real Support/Resistance/Entry/Stop/Target + 20-MA) + `setupWhy(e)` (per-strategy rationale via `STRAT_WHY`). Dashboard AI-read "See the chart & reasoning ↗" → `dashWhy()` reuses `proofChartSVG(...,live)` + `coachReadHTML`.
- **Timeframe-aware bias:** `renderDash` windows `q.closes` by `HZ_LOOKBACK[currentDTE]` before `analyze`, so the sentiment/bias reflects the selected horizon.

## AI Coach (rule-based, in the dashboard AI-read panel)
- `coachRead(L)` takes the current setup (`{ticker,q,a,entry,sl,tp1,tp2,isShort,isNeutral,aiPick}`) and derives, from the real indicators only: a mentor **narrative** (`lines[]`), a **would-I-take-it** verdict (`call` YES/NO/WAIT + `callNote`), a **factor checklist** (`factors[]` ✓/~/✕), and **bull/bear** cases (from `a.signals`). `coachReadHTML(L)` renders the verdict / notebook / Bull-vs-Bear / checklist HTML injected into `#dashConv` by `renderDash`. Key-metrics tiles (`#dashMetrics`) carry condition-aware `title` tooltips. No external data — all from `analyze`/`macdOf`/`smaN`/`atr`.

## Claude AI integration (optional)
- Key held in-memory (`AI_KEY`) via `#moAI` modal (`saveAIKey`, `clearAIKey`), or server proxy at `/api/claude` (`probeProxy`, `AI_PROXY_OK`). `aiReady()`, `callClaude(system,user,maxTokens)`, `fmtAI()`.
- Consumers: `aiMarketDirection` (dashboard deep-read), `btAIStrategyHelp` (backtest coach), `perfCoach` (performance), chat (`askAI`/`sendChat`).

## Charts
- **Main dashboard chart** = TradingView widget. State `chartView` ('pro' | 'ai'). `mountTV(ticker)` builds the widget (only remounts on ticker change); `setChartView(v)` / `applyChartView(...)` toggle Pro Chart vs AI Levels.
- **AI Levels** = custom canvas `drawCanvasChart(q,entry,sl,tp1,tp2,sentiment,isShort,isNeutral)` on `#mainCanvas`: candle/line/volume modes, ranges, entry/stop/tp lines, **pressure zones** (`detectPressureZones`), and a pulsing live-price dot (`positionLiveDot`). Pan/zoom via `setupCanvasPan`.
- `drawMiniChart` — Chart.js sparkline in the price header.
- Backtest chart: `drawBacktestChart`; Mini per-tab canvases elsewhere.

## Live streaming
- `startLiveRefresh()` sets a 15s interval → `liveTick()`: lightweight `fetchLivePrice`, updates `lastData.q`, animates the header price (`tweenPrice`), updates the change badge (`updateHeaderChange`), redraws the AI canvas only if that view is active. **Never rebuilds the DOM** (so the TradingView widget keeps its own live state).

## Dashboard = panel terminal driven by an ask bar (current)
- The Dashboard tab (`#tab-dashboard`) is a **fixed panel layout**, not a chat. A command bar (`.dash-cmd`: `#cpInput` + `#cpHorizon` + `.dash-chip`s) drives `renderDash(text)`, which writes into stable panel IDs:
  - `#dashHead` — symbol, name, **`.th-price`** + **`.chg-badge`** (classes kept so the live stream updates them), `#miniCanvas` sparkline, conviction %.
  - `#dashTV` — the **TradingView** widget (`mountTVInto('dashTV',ticker)`, remounted only when the symbol changes; tracked by `dashTVTicker`).
  - `#dashPlan` — verdict + the **single** entry/stop/target table (price primary, tick-distance secondary; 1 tick = $0.01) + R:R + follow-up buttons.
  - `#dashConv` — conviction bar + AI rationale. `#dashMetrics` — metric tiles. `#dashWhy` — live signal rows. `#dashNote` — hidden AI-note panel for `cpExplainStop`/`cpAIdeep`.
- `renderDash` reuses the engine: `resolveTicker` → `fetchQuote`+`analyze`+`classifySetup`+`aiStrategyLevels`+`stratConf`, sets `lastData` (other features depend on it), then fills panels. Entry points: `cpInit` (startup → AAPL), `cpSend`/`cpChip` (ask bar / chips), `cpSetHorizon` (re-reads `lastData.ticker`), `loadTicker` (e.g. from News). Live price stream starts after the first render (`liveStarted` guard → `startLiveRefresh`).
- The old conversational copilot (`askCopilot`, `appendUserBubble`, `#cpThread`, `.cp-*` CSS) was removed.
- Legacy `renderDash`/`applyChartView`/`load` remain in the file but are DISABLED for the dashboard: `load()` early-returns when `#main` is absent. (The Focus/`.fc` and workspace/`.wk` CSS also linger, unused.)

## Legacy dashboard render (disabled)
- `renderDash(ticker,q,a)` built the terminal into `#main` as the **`.wk` workspace** — a 12-col CSS-grid (`grid-template-areas`): command header → dominant chart panel (`.wk-chart`, spans 2 rows) + elevated Trade Plan (`.wk-plan.elevated`) + AI Conviction (`.wk-ai`) → metric tiles (`.wk-metrics`) → Why / Indicators / Strategies / Feedback panels. Collapses to a single column under 1040px. Panels use the `.wk-panel` style. Keep these IDs/classes when editing (the JS reads them): `.th-price`, `.chg-badge`, `miniCanvas`, `sentFill`, `proChartWrap`/`tvChart`/`aiChartWrap`/`cvtAI`/`cvtPro`/`mainCanvas`/`chart-legend`, `aiDirOut`, `fbBox` + feedback buttons. Globals: `lastData`, `lastCanvasData`, `currentDTE`, `DTE` config. The ticker chips / search / horizon (`.dte-row`) live in the static `#tab-dashboard` markup *above* `#main` (not in renderDash).

## Shared (cross-user) AI learning — `api/learn.js`
- Vercel serverless function backed by Vercel KV/Upstash (REST via `fetch`, no npm deps). `GET` returns pooled `{strats,trials,wins,log}`; `POST {key,win,pnl,tk,name,dir}` merges one self-test. Key `tlpro:shared_memory_v1`. Returns 503 if KV env vars absent.
- Client (`index.html`): `syncSharedMemory()` (on load) + `postShared()` (per self-test) + `mergeShared()` fold the pooled model into `AI_MEMORY` so `stratConf`/`classifySetup` reflect everyone. `SHARED_OK` flag; silent fallback to localStorage when the backend isn't deployed. See `DEPLOY_BACKEND.md`.

## Landing — "living terminal" hero (`.lx-bento` / `.tp` panels)
- The hero is a data-first bento grid, now **kinetic** ("living terminal" direction): a streaming **ticker tape** (`.lx-tape`/`#lxTapeTrack`) above it, an animated candlestick **river** on `#heroCanvas` (replaces the old static SVG), and a live-ticking watchlist (`[data-sym]` rows). Driven by an IIFE at the end of the script (`buildTape`/`pullQuotes`/`applyQuote`/`heroRiver`) using `fetchLivePrice` for best-effort real quotes. Other bento panels (volume profile, AI probability, setup score, R:R, sentiment) remain static. The old `.lx-stage`/`.lx-panel`/`.lx-float` tilted-panel hero is removed (CSS may linger, unused).

## Landing motion (lx-)
- `lxObserve()` — IntersectionObserver (root:null) adds `.in` to `.lx-reveal` on scroll; old-browser + safety-net fallback guarantees visibility.
- `lxMaybeCount()` — count-up numbers (`.lx-count[data-to]`). Nav solidifies on scroll; hero panel parallax on pointermove. `lpScroll(id)` smooth-scrolls.

## Tooling
- `.claude/launch.json` + `.claude/serve.ps1` — local static preview on :8777.
- `.vercelignore` excludes `.claude`. `index.html` at root for Vercel.
