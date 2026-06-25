# TradeLens Pro — Architecture

> Living doc. Update when structure, key functions, or data flow change.
> Last updated: 2026-06-25

Everything lives in **`index.html`** (~3,500 lines): one `<style>` block, the landing markup, the app markup + modals, and one inline `<script>`. External deps loaded via CDN: **Chart.js** (mini sparkline) and **TradingView** `tv.js` (main chart).

## Top-level page structure
```
<head><style> … all CSS … </style></head>
<body>
  #landing            ← marketing page (lx- namespace), shown first, position:fixed z-index:1000
  <nav> … </nav>      ← the APP top nav (9 tabs)
  .page-wrap          ← single column now (sidebars hidden)
    .main-col
      #aiBanner       ← slim "connect AI" strip
      .tab-pane#tab-dashboard   ← the terminal
      .tab-pane#tab-traders / #tab-backtest / #tab-performance /
               #tab-ailab / #tab-ai / #tab-screener / #tab-alerts / #tab-feedback
  modals: #moAcct #moAlert #moAI
  <script> … all JS … </script>
</body>
```
- `launchApp()` hides `#landing`; `showLanding()` shows it. App logo (top-left) calls `showLanding()`.
- `mainTab(name, btn)` switches `.tab-pane`/`.ntab` and lazily inits each tab (backtest, screener, traders, performance, ailab, feedback).

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
- `classifySetup(candles,a)` — picks the best strategy from structure + learned confidence.
- `aiStrategyLevels(key,candles)` — pulls final entry/sl/tp1/tp2 from a strategy's steps.

## Self-learning AI (algorithmic, no Claude needed)
- `AI_MEMORY` persisted in localStorage key `tlpro_ai_memory_v1`. `stratConf(key)` (Wilson-shrunk win rate).
- `aiSelfBacktest(rounds)` — tests its own picks across history, logs W/L, updates confidence (drives dashboard level weighting). UI: AI Lab tab. `renderAILearnStats()`, `resetAIMemory()`.

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

## Dashboard render
- `renderDash(ticker,q,a)` builds the whole terminal into `#main` as the **`.wk` workspace** — a 12-col CSS-grid (`grid-template-areas`): command header → dominant chart panel (`.wk-chart`, spans 2 rows) + elevated Trade Plan (`.wk-plan.elevated`) + AI Conviction (`.wk-ai`) → metric tiles (`.wk-metrics`) → Why / Indicators / Strategies / Feedback panels. Collapses to a single column under 1040px. Panels use the `.wk-panel` style. Keep these IDs/classes when editing (the JS reads them): `.th-price`, `.chg-badge`, `miniCanvas`, `sentFill`, `proChartWrap`/`tvChart`/`aiChartWrap`/`cvtAI`/`cvtPro`/`mainCanvas`/`chart-legend`, `aiDirOut`, `fbBox` + feedback buttons. Globals: `lastData`, `lastCanvasData`, `currentDTE`, `DTE` config. The ticker chips / search / horizon (`.dte-row`) live in the static `#tab-dashboard` markup *above* `#main` (not in renderDash).

## Shared (cross-user) AI learning — `api/learn.js`
- Vercel serverless function backed by Vercel KV/Upstash (REST via `fetch`, no npm deps). `GET` returns pooled `{strats,trials,wins,log}`; `POST {key,win,pnl,tk,name,dir}` merges one self-test. Key `tlpro:shared_memory_v1`. Returns 503 if KV env vars absent.
- Client (`index.html`): `syncSharedMemory()` (on load) + `postShared()` (per self-test) + `mergeShared()` fold the pooled model into `AI_MEMORY` so `stratConf`/`classifySetup` reflect everyone. `SHARED_OK` flag; silent fallback to localStorage when the backend isn't deployed. See `DEPLOY_BACKEND.md`.

## Landing — hero is a terminal bento (`.lx-bento` / `.tp` panels)
- The hero is a data-first bento grid (no decorative graphics): candlestick chart (inline SVG with entry/stop/target lines), watchlist, volume profile, AI probability, setup score, risk/reward, market sentiment. The old `.lx-stage`/`.lx-panel`/`.lx-float` tilted-panel hero is removed (CSS may linger, unused).

## Landing motion (lx-)
- `lxObserve()` — IntersectionObserver (root:null) adds `.in` to `.lx-reveal` on scroll; old-browser + safety-net fallback guarantees visibility.
- `lxMaybeCount()` — count-up numbers (`.lx-count[data-to]`). Nav solidifies on scroll; hero panel parallax on pointermove. `lpScroll(id)` smooth-scrolls.

## Tooling
- `.claude/launch.json` + `.claude/serve.ps1` — local static preview on :8777.
- `.vercelignore` excludes `.claude`. `index.html` at root for Vercel.
