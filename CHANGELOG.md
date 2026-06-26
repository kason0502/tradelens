# TradeLens Pro — Changelog

> Living doc. Add an entry (newest first) each session that ships changes.
> Dates are YYYY-MM-DD. Mirrors git history; group by session/day.

## 2026-06-26 (session 16c) — self-grading trade journal
- **New "Journal" tab** (`#tab-journal`, Research group, active-count pill). Hit **+ Track this setup** on the dashboard Trade Plan and the plan is logged (`trackSetup`→`JOURNAL`, localStorage `tlpro_journal_v1`).
- **It grades itself from real price.** A background poller (`journalTick`, every 45s when `bgIdle`, ≤8 tickers via `fetchLivePrice`) runs `gradeJournal`: **pending → (entry hit) open → (target) win / (stop) loss**, scored in **R** (multiples of the defined risk). Pending setups expire after 7 days.
- **Journal view** (`renderJournal`): scoreboard (live / resolved / win-rate / avg R / total R), live cards with a **stop↔target progress bar + live-R**, a resolved/expired history, manual **Close now** / **Remove** / **Clear history**, and a plain-English "how grading works" note. Honest framing — delayed data, runs only while the app is open, not a brokerage fill. Toasts via `jToast`; nav badge via `updateJournalBadge`.

## 2026-06-26 (session 16b) — Strategy "anatomy" charts
- **Each strategy now shows on a chart.** New pure-SVG schematic (`strategyDiagram` / `strategyChartBlock`, configs in `STRAT_DIAGRAMS`) draws the setup's anatomy: the idealized price path, the **entry trigger** (dot + time line), dashed **Target 1/2** and **Stop** levels, shaded green **reward** + red **risk** zones, and an auto-computed **≈ 1 : N reward-to-risk**. Rendered in Today's focus and inside every weekday card (`STRAT_DKEY` maps day→pattern). Theme colors via CSS vars; labeled "schematic · not a live quote" (honest — it's a teaching diagram, not a price feed).

## 2026-06-26 (session 16) — Strategy tab (day-by-day ideas + live candidates)
- **New "Strategy" tab** (`#tab-strategy`, in the Research nav group, `DAILY` pill). Three parts, all from real data/date:
  - **Today's focus** — auto-detects the weekday from `new Date()` and shows that day's theme, lean (recommended strategy/bias), do's, any event badges, and a **live candidate scan** for the day's setup. Weekends show a "plan the week" card.
  - **Event calendar** (`eventCalendar`) — OPEX / quad-witching / NFP / month-/quarter-end are **computed from the date** (`_nthFriday`, `_lastWeekday`), each with a TODAY / THIS WEEK / UPCOMING / PASSED badge. FOMC/CPI noted as "check a calendar" (no fabricated dates — honest).
  - **Weekday playbook** — Mon–Fri expandable cards (today auto-open + highlighted), each with a "Find live candidates" button.
- **Live candidates reuse the screener engine** (`loadStratCandidates` → `loadScreener`/`SCREEN`/`scanFilter`, cached via the movers fetch) and map each day to a scan type (Mon trend · Tue pullback · Wed breakout · Thu oversold · Fri best-of). Click any candidate → opens on the dashboard. Guarded by `window.__userFetch` so it stands down for user lookups.

## 2026-06-26 (session 15) — ticker-only ask bar + self-running AI learning
- **Dashboard ask bar is now ticker-only.** Per the user: it's a symbol lookup, not a natural-language Q&A. Input is uppercased + stripped to A–Z on the fly (`maxlength=6`), placeholder reworded to "Enter a ticker — e.g. AAPL, NVDA, TSLA, SPY". `resolveTicker`/`cpSend` unchanged (already symbol-first).
- **AI now learns on its own.** New `aiAutoLearnOnce()` runs ONE silent self-test on a real historical chart when idle (folds win/loss into `AI_MEMORY`, posts to the shared pool when `SHARED_OK`). Scheduled in the init pollers (first run ~40s, then every 60s) behind `bgIdle()` so it stands down during user lookups / on the landing / when hidden. AI Lab gained a **Pause/Resume auto-learn** toggle (`toggleAutoLearn`, persisted to `tlpro_ai_auto`) + a live status line (`paintAutoStatus`); auto results tag as `auto` in the log. The manual "Run N self-tests" buttons still work and just accelerate it.
- **Richer info in every tab** (user asked for summary stats + plain-English legends + more depth, in tab order):
  - **News:** live breadth summary (headline tone, bull/bear/neutral counts, most-mentioned tickers) + a "how to read this" legend (`renderNewsTab`).
  - **Pro Traders:** legend on the desk-consensus panel + **2 new desk members** (Linda Raschke, Quant Macro Desk) for depth.
  - **Backtest:** scoreboard now shows an **equity curve** (`drawEquityCurve` generalized to take a canvas id) + a **per-strategy mastery** breakdown + legend (`renderBtScore`, ≥2 rounds).
  - **Performance:** new **Risk & edge metrics** card — profit factor, avg win/avg loss, expectancy, discipline (accuracy on taken trades) + legend.
  - **AI Chat:** "What I can explain" tappable topic grid mapped to the knowledge base + a tip linking concepts to the dashboard.
  - **Alerts:** how-to legend (set at entry/stop/target) + live active-alert count.
  - **Feedback:** legend clarifying the rating loop tunes indicator weighting vs the AI Lab's self-learning.
  - (Dashboard / High Volume / Screener already carried breadth stats + context, so left as-is.)

## 2026-06-26 (session 14) — hosted on GitHub→Vercel + AI proxy + brand images + fixes
- **Now hosted for everyone (GitHub → Vercel).** Connected `origin` = `github.com/kason0502/tradelens`. The GitHub repo had diverged (updated via manual "Add files via upload") and was **missing files** (PNGs, `api/yf.js`, `api/learn.js`); reconciled by merging `origin/main` into the complete local project (`-X ours` + `--allow-unrelated-histories`) then pushing. Local ↔ GitHub now in sync; Vercel auto-redeploys on push.
- **`api/claude.js`** — server-side Claude proxy. With `ANTHROPIC_API_KEY` set in Vercel, every deployed visitor gets AI with no key prompt (the app already probes `/api/claude`). Added `package.json` + `vercel.json` (30s timeout for the AI function). `DEPLOY.md` covers the whole flow.
- **Brand = the user's own transparent PNGs:** `logo.png` (bull-head) in the nav, `bull.png`/`bear.png` mascots in the dashboard.
- **Fixes:** landing top gap (aurora `.lx-orb` were `position:static` → stacked ~1720px in flow; made absolute + `.lx-bg` fixed); mascot hidden on **neutral** reads (only shows for bullish/bearish); mascot bigger (144×104) with a stronger double-glow.

## 2026-06-26 (session 13) — reliable data via a server-side proxy
- **Stocks now load reliably (no more flaky public CORS proxies).** Added a server-side market-data proxy at **`/api/yf?url=…`** that fetches Yahoo/Stooq server-side (no browser CORS, no per-user rate limits):
  - **Local:** `.claude/serve.ps1` (the PowerShell preview server) now handles `/api/yf` — pure PowerShell `Invoke-WebRequest`, no Node/Python. **Restart the preview** to pick it up. Verified: AAPL/NVDA/TSLA/SPY load in 200–700ms.
  - **Deployed:** `api/yf.js` is the equivalent Vercel serverless function, so a Vercel deploy is reliable too.
  - Client (`raceAttempts`) calls `/api/yf` **first** (`_yfProxyOK` flag) and only falls back to the public CORS proxies if that route is absent (bare file / plain static host).
- serve.ps1 also now serves image MIME types (png/jpg/webp/svg) so brand/mascot images can be dropped in.

## 2026-06-26 (session 12) — fix "nothing loads" (proxy flooding + slow sequential fetch)
- **Root cause:** the new background pollers (movers/watchlist/indices on timers) were hammering the shared CORS proxies into rate-limiting, AND every lookup tried proxies **sequentially** (2 passes × 2 hosts × 5 proxies ≈ up to ~140s) so a busy feed hung instead of failing.
- **Parallel proxy race** — new `raceAttempts(url)` fires all proxies at once and resolves on the first valid Yahoo chart; `tryFetch`, `fetchQuote` intraday, and `fetchLivePrice` all use it. Result: lookups now resolve in **~150ms** when proxies are up, and fail fast (~7s) when they're not. Trimmed 2 dead proxies, added 4 more providers, timeout 9s→7s.
- **Background pollers stand down** while you're analyzing a ticker (`window.__userFetch` gate + `bgIdle()` checks page-visible / not-landing), start **staggered**, and refresh far less often (indices 90s→5m, watchlist 60s→4m, movers 2m→6m) so they never starve your lookups. `liveTick` also yields during a lookup.

## 2026-06-26 (session 11) — watchlist · Greeks/indicators · TV live · landing tighten
- **Persistent watchlist** (`#dashWatch`, `WATCH`/`strata_watch_v1`): add by symbol, ✕ remove, "★ add current", live prices (`refreshWatch`), click a row to analyze. On the dashboard side column.
- **Options Greeks panel** (`#dashGreeks`, `renderGreeks` + Black–Scholes `bsGreeks`/`normCDF`): Delta · Gamma · Theta · Vega · est. premium · IV (from `histVol`) for an ATM call/put at the chosen horizon (`HZ_T`). Educational estimate.
- **More indicators on the dashboard:** metrics grid extended with **MACD** (`macdOf`), **MA 50/200 golden/death cross**, and **ATR%** (now 9 tiles).
- **TradingView kept live:** added `startDashTVRefresh` — re-mounts the chart ~every 2.5 min while the dashboard is visible (the free widget silently drops its data socket and appears "paused"). Combined with the session-10 load retries.
- **Landing tightened:** big section paddings reduced (`.lx-sec` 120→84, `.lx-statement` 120→80, hero 72/96→48/60, bento margin 52→34) so there's far less empty scrolling.
- **Beefier bull/bear** mascots — added a second horn, muscle lines, brow and breath (bull) and a roaring mouth, fangs, claws + raised hackles (bear). (Still original line-art; iterative without a live preview.)

## 2026-06-26 (session 10) — logo de-boxed · richer mascots · deeper AI read · TV reliability
- **Logo no longer in a box.** Removed the accent tile/box-shadow from `.logo-mark`; the bull mark now renders in the accent colour with a `drop-shadow` glow (and flips red when bearish). The conviction logo-pulse uses a glow filter instead of a box-shadow.
- **Redesigned bull/bear mascots** — replaced the basic front-facing heads with semi-realistic **profile silhouettes** (glowing outline + soft fill, `BULL_SVG`/`BEAR_SVG`), larger frame (`.mood-beast` 104×70).
- **Deeper AI read on the dashboard** — the AI-read panel now lists **"What the AI sees"**: a plain-language signal checklist (✓ bull / ✗ bear / • neutral, from `analyze().signals`), a bullish-vs-bearish signal tally, and a **what-keeps-it-valid / invalidation** level line.
- **TradingView reliability + auto-update** — `mountTVInto` now **retries** if the free widget fails to render an iframe (it often silently fails under load during market hours), waits for `tv.js` to finish loading, and shows a **"↻ Reload chart"** fallback (`tvFallback`). The widget streams live once mounted.

## 2026-06-26 (session 9) — sentiment-reactive theme · bull/bear · bull logo · index strip
- **The whole UI flips red when the read is bearish.** Accent is now a flippable RGB token (`--ac-rgb`, all chrome greens converted to `rgba(var(--ac-rgb),…)`); `body.bearish` overrides `--ac`/`--ac-rgb`/`--act`/etc. to red. `setMood(sentiment)` (called from `renderDash`) toggles `body.bearish` and `window.FX_MOOD`. The animated background (`#fxCanvas`) eases its aurora/grid/constellation between green↔red via `moodT`. Smooth `.7s` transitions on key surfaces. Bullish/neutral = green, bearish = red.
- **Original bull + bear mascots** (`BULL_SVG`/`BEAR_SVG`, hand-built STRATA line-art) glow in the dashboard **AI-read** panel — bull for bullish/neutral, bear for bearish, colour-matched with a `drop-shadow` glow (`.mood-beast`).
- **New bull-head logo** (original line mark) replaces the strata-blocks across sidebar/landing/footer. Sits on the accent tile, so it glows red in bearish mode.
- **Index strip** on the dashboard (`#idxStrip`): live S&P 500 / Nasdaq / Dow / VIX context chips (`buildIndexStrip`/`loadIndices`, best-effort `^GSPC`/`^IXIC`/`^DJI`/`^VIX`).

## 2026-06-26 (session 8) — emerald rebrand · premium animated nav · landing fix
- **Accent switched electric-blue → emerald green** (`--ac` `#22c55e`, light `#86efac`) to match the reference the user provided. Green is now the **brand + bullish** colour, red stays bearish. Global recolor of all `#2f81f7`/`rgba(47,129,247)`/`rgba(59,130,246)` chrome, the `#fxCanvas` particles/aurora, and the landing showcase strokes. (Old DESIGN_SYSTEM "one blue accent / green-red = P&L only" rule is superseded.)
- **Landing no longer shows the app behind it.** The previous turn made `#landing` transparent (so the canvas showed through) which leaked the dashboard behind the landing — confusing. `#landing` is opaque again; instead the landing gets its own depth from re-enabled soft green **aurora orbs** (`.lx-orb`). The `#fxCanvas` animated background now lives **behind the app only**.
- **Navigation redesigned into a premium animated rail** (per the user's detailed spec — Apple/Linear/Arc feel, "not a normal navbar"): a **floating glass panel** (inset, rounded, layered shadow, accent top-hairline); a **gliding active pill** that springs between tabs (`#snavGlide`, `cubic-bezier(.34,1.56,.5,1)`, driven from `mainTab` → `snavGlideTo`); a **hover highlight** that tracks the hovered item (`#snavHover`); a **cursor-follow glow** inside the rail (`#snavCursor`); **magnetic hover** (items pull toward the cursor); and **icons that spring-scale/rotate on hover**. Wiring in `initPremiumNav` (called at startup). Respects reduced-motion.

## 2026-06-26 (session 7) — rebrand to STRATA + pro app shell + "wow" pass
- **Animated "living market" background** (site-wide `#fxCanvas`, fixed behind everything): drifting aurora depth-blobs, a receding perspective trading-floor grid, a parallax data-constellation (points + proximity links), and occasional green/red "trade-print" flashes. Pointer parallax; paints a static first frame; pauses when hidden; respects reduced-motion. `#landing` made transparent (with a dimming veil) so the canvas shows behind it too; app surfaces got slightly translucent.
- **Screener is now LIVE** (`renderScreener`/`loadScreener`/`paintScreen`) — a real structure scan over the movers universe (`analyze` per name): sortable filters (bullish momentum / breakout / oversold / bearish / trend leaders / all), a breadth stat strip (scanned · bullish · bearish · breadth% · avg RSI), and a results table with sparkline, price, change, RSI and a verdict chip. Replaced the old static `SCAN_DATA`/`runScan`.
- **Performance — equity curve** (`drawEquityCurve`): a filled cumulative-sim-P&L line on `#perfEquity`, plus a "Best streak" scoreboard tile.
- **High Volume — market-breadth header** (`paintMoversStats`): advancers/decliners, breadth%, avg move, total $-volume, biggest mover.
- **Data-quality fix:** the movers/screener pipeline now **recomputes the day move from the price series** (the proxy's previous-close is often corrupt → it was showing e.g. "AAPL +36%") and tightens the sanity filter to `|pct|≤22%` for this mega-cap universe.
- **Rebrand: TradeLens Pro → STRATA** ("Structure Terminal" / "structure, not noise"). New logo: a "rising strata" mark (three ascending blocks) on the solid-accent tile, used in the app sidebar, landing nav, and footer. Page `<title>`, hero lead, statement, steps, footer, CTA and disclaimer copy all updated.
- **App nav moved to a left sidebar** (`.appnav`, replaces the top `<nav>`). Grouped: Terminal (Dashboard · High Volume · Screener · News), Research (Pro Traders · Backtest · Performance · AI Lab), Assistant (AI Chat · Alerts · Feedback), with a footer (Live indicator · Connect AI · Account). Line-icon per item, active rail accent. `.page-wrap` shifts right; collapses to a 64/56px icon rail under 1080/640px. `mainTab` now drives `.snav` active state by `data-tab`.
- **Removed the top "✨ AI" button** — connect-AI relocated to the sidebar footer (`#aiKeyBtn` is now a `.snav`; `updateAIBadge` toggles its label/active state instead of clobbering it).
- **Movers banner** at the top of the app (`.appbar` + `#appBarTrack`): a streaming tape of the day's biggest movers (by |%|), best-effort real quotes, seeded on load then refreshed every 2 min. Clicking a name analyzes it.
- **New "High Volume" tab** (`#tab-movers`, `renderMovers`): real-data cards of the most active / top gainers / losers / most volatile (sortable), each with a sparkline, price, volume and $-volume; clicking analyzes on the dashboard. Corrupted proxy quotes (absurd % / price far off recent close) are filtered out. `fetchQuote` now also returns raw `vol`.
- **Pro Traders expanded** — added a **desk-consensus** panel (bull/bear split bar, avg desk win rate, and the most-called names with their lean, clickable). Fixed a stale `.ntab` selector in the per-call "Analyze" button.
- **Backtest expanded** — added a **session scoreboard** (`renderBtScore`: rounds, accuracy, win streak, sim P&L, best-read strategy) above the setup, updating after every round, plus a **"Surprise me"** random-ticker button.

## 2026-06-25 (session 6)
- **"Living terminal" landing hero (kinetic data-art direction).** Chosen by the user to break the template feel. Added a full-width **streaming ticker tape** under the nav (`.lx-tape`, CSS marquee, duplicated track for a seamless loop, best-effort REAL quotes via `fetchLivePrice` → `applyQuote`, flashes on update). Replaced the static SVG candle chart in the hero bento with an **animated candlestick "river"** on `<canvas id="heroCanvas">` — candles continuously stream and regenerate with entry/stop/target level lines (`heroRiver`, rAF; paints a static frame first since hidden tabs throttle rAF; respects `prefers-reduced-motion`; idles when the landing is hidden). Watchlist rows are tagged `data-sym` and tick live from the same quote pass. Headline gained a kinetic accent underline on "structure" (`.glo`). All in an IIFE at the end of the script. *(Scope: hero only so far; the rest of the landing sections + dashboard are next if the direction lands.)*
- **Dashboard rebuilt as a real panel terminal (no more chat).** Replaced the conversational AI Copilot thread with a fixed dashboard driven by a slim **ask bar**: a search/command input + horizon select + ticker chips that drive every panel. Layout: a **ticker header** (symbol, company, live price, change badge, mini sparkline, conviction %), a wide **TradingView chart** panel, a **Trade Plan** panel (the single source of truth for entry/stop/target — price primary, tick-distance secondary, R:R), an **AI read** conviction panel (score bar + rationale), a **Key metrics** strip (RSI/trend/vs-SMA20/20D-range/Bollinger/R:R), and a **live signals** panel. New `renderDash(text)` reuses the existing engine (`fetchQuote`→`analyze`→`classifySetup`/`aiStrategyLevels`/`stratConf`); `cpInit/cpSend/cpChip/cpSetHorizon/loadTicker` now route to it; follow-ups (`cpExplainStop`/`cpAIdeep`) render into an AI-note panel. Live price stream re-wired to the new header (kept `.th-price`/`.chg-badge` classes so `tweenPrice`/`updateHeaderChange` just work). Removed the `.cp-*` chat CSS/markup and `askCopilot`/`appendUserBubble`/`cpThread` helpers.
- **Landing/site flattened to the refined black-terminal look.** Removed the remaining blue→cyan→purple gradients and glow: logo mark and `.btn-grad` → solid accent; bullet-icon tiles and learned-confidence bars → single accent; metrics band, pricing "Most Popular" card, and final-CTA slab → flat `--s1`/`--s2` surfaces with hairline borders (no purple, no glow); landing showcase chart strokes recolored from purple/cyan to the accent (`#2f81f7` / `#7db3ff`).
- Horizon default aligned: `currentDTE` now initializes to `'1m'` to match the ask-bar `<select>`.
- **Realistic, horizon-aware stop/targets.** The structure window now scales to the chosen horizon (`horizonCandles`): 0DTE reads intraday bars (`h1d`), 1W/1M a handful of recent daily bars, 1Y ~170 daily bars — instead of a fixed ~60-bar daily window for every horizon. A `clampLevels` guard keeps the stop within a sensible %-band per horizon (e.g. 0DTE ~0.3–1.4%, 1M ~3–7%, 1Y ~12–28%), scaling the whole setup around entry so R:R is preserved. The horizon selector now actually re-reads the levels (previously it only affected a fallback). `HZ_WIN`/`HZ_RISK` configs.

## 2026-06-25 (session 5)
- **Dashboard is now an AI Copilot (conversational).** Replaced the workspace/Focus render with a chat: `askCopilot(text)` resolves a ticker from the question, runs the live analysis, and appends an answer card — verdict, an embedded **TradingView** chart, and **entry/stop/target as ticks** up/down from current price (price as a small subtitle), R/R in ticks, rationale, and follow-up chips (`cpExplainStop`, `cpBacktest`, `cpAIdeep`, compare). `loadTicker` now routes into the conversation; legacy `renderDash`/`load` are guarded/disabled (no `#main`). Functions: `cpInit/cpSend/cpChip/cpSetHorizon/resolveTicker/mountTVInto`.
- (Earlier this session) explored 3 + 3 dashboard concepts as visual mockups; user chose Focus, then AI Copilot.

## 2026-06-25 (session 4)
- **Rebuilt the dashboard (post-launch) from scratch** as an asymmetric trading-terminal workspace (`.wk` namespace in `renderDash`). 12-col grid: command header → dominant chart (spans 2 rows) + elevated Trade Plan + AI Conviction → metric tiles → Why / Indicators / Strategies / Feedback. Premium dark panels, thin borders, depth shadows, accent-ringed plan, hover lift. All functional IDs preserved.

## 2026-06-25 (session 3)
- **Cross-user shared learning** — `api/learn.js` (Vercel serverless + KV/Upstash) pools the AI's self-test learning across ALL users. Client syncs on load (`syncSharedMemory`), posts each test (`postShared`), merges pooled model into `AI_MEMORY` so dashboard confidence reflects everyone; falls back to localStorage when the backend isn't deployed (`SHARED_OK`). Setup in `DEPLOY_BACKEND.md`.
- **Readable level chart** — rewrote the AI Levels overlay: faint risk/reward zones, labeled support/resistance, and dodged color-coded price chips (entry/stop/TP1/TP2) so the setup reads instantly.
- **Black-minimal Bloomberg design system** — pure black (`#050505`), dark-gray surfaces, white type, ONE accent (`#2f81f7`). Collapsed the blue/cyan/purple gradients to the single accent, removed glowing orbs / ambient blobs (one faint top glow), solid buttons, tighter radii.
- **Realistic terminal hero** — replaced the tilted glass panel + floating cards with a data-first bento: candlestick chart (with entry/stop/target lines), watchlist, volume profile, AI probability, setup score, risk/reward, market sentiment.

## 2026-06-25 (session 2)
- **News tab** — added a `News` nav tab + glass news grid (macro + sector headlines with plain-English impact), labeled as an illustrative sample feed; tickers are clickable → load on dashboard. (`renderNewsTab`, `newsOpen`)
- **Draw the setup on the chart** — the annotated **AI Levels** canvas ("Setup & Levels") is now the **default** chart view (TradingView = toggle), and `drawCanvasChart` draws labeled **support/resistance** lines under the entry/stop/TP. (Note: can't draw on the TradingView free embed — sandboxed iframe.)
- **Persistent AI Lab learning** — self-test history saved in `AI_MEMORY.log` (localStorage) and re-rendered on load (`renderAILearnLog`); backtest track record `btHistory` persisted (`BT_HIST_KEY`). Learned confidence already feeds dashboard level weighting via `classifySetup`/`stratConf`; now it accumulates across sessions.
- **Serious tone pass** — calmed landing motion (no card bob, less 3D tilt, lower orb opacity, de-animated primary button); app de-arcaded: "Directional bias — Long/Short" instead of "⬆ BULLISH GO LONG", emoji stripped from chart controls / pressure toggle / feedback.

## 2026-06-25 (session 1)
- **Declutter dashboard into a trader reading order** — main view now leads with the actionable content (price → verdict → trade plan → chart → "Why" analysis → feedback) via flex `order`; removed the redundant Watchlist card; de-emoji'd chart toggle / AI buttons; direction banner moved to the new palette. (`5f8c879`)
- **Align app shell to landing** — glass nav (blurred charcoal, gradient-underline tabs, bigger calm labels), ghost-glass nav buttons with line icons (no emoji), emerald LIVE pill; dropped the 3-column layout to a single focused 1180px column (sidebars hidden); glassy command controls; slim glass "Connect AI" strip replacing the unstyled banner. (`3c98e24`)
- Added permanent project docs: `PROJECT_CONTEXT.md`, `ARCHITECTURE.md`, `DESIGN_SYSTEM.md`, `TODO.md`, `CHANGELOG.md`, and `CLAUDE.md` (instructs future sessions to keep them current).

## 2026-06-24
- **Rebuild landing from first principles** — bespoke, asymmetric, editorial composition: animated orb background, parallax hero with 3D dashboard panel + count-up stats, alternating feature showcase rows with animated product mocks, metrics band, oversized "how it works" numerals, elevated pricing, glowing final CTA, watermark footer. Scroll-reveal + count-up motion. (`3bd7645`)
- **Premium fintech SaaS redesign + first landing page** — charcoal + blue/cyan/purple glass design system; marketing landing (hero/stats/features/pricing/footer) with Launch-App into the dashboard; reskinned app chrome. (`8576c29`)
- **Gold pro-terminal theme + TradingView primary chart** (theme later replaced) — embedded TradingView Advanced Chart as the dashboard's primary chart with a Pro Chart / AI Levels toggle; live updates stopped rebuilding the DOM so the widget persists. (`33280b7`)

## 2026-06-23
- **Polish UI** — roomier layout, organized/grouped nav, plain-language indicator labels with tooltips. (`59f4681`)
- **Fix AI Lab training feedback** — self-test buttons now show live progress, disable while running, and report a clear result / rate-limit warning. (`f5a805f`)
- **Make repo deploy-ready for Vercel** — moved `index.html` to repo root, added `.vercelignore`. (`6f4ff23`)
- **Add local preview server** — `.claude/serve.ps1` + `launch.json` (no Node/Python needed). (`265388e`)
- **Make the main chart stream live** — 15s lightweight price poll, ticking price, pulsing live-price dot/line. (`c9f4b78`)
- **Add AI strategy coach to Backtest** — pre-guess AI read of the assigned strategy + structure-based levels. (`6a64e66`)
- **Make entry/stop/TP structure-based and accurate** — swing levels + ATR stops + `normTrade` ordering/min-R:R. (`6184a69`)
- **Remove Strategy Lab tab** — kept the shared strategy engine used by Dashboard + AI Lab. (`6d8c19c`)
- Imported from claude.ai, removed duplicate HTML/zip, initial commit. (`cd6b184`, `8c96c16`)
