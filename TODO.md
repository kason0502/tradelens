# STRATA — TODO

> Living doc. Keep prioritized; check items off and add new ones each session.
> Last updated: 2026-06-27 (session 18)

## Done (session 18 — per-timeframe self-learning)
- [x] **Self-learning is timeframe-aware** — Intraday / Swing / Position buckets, each with its own genome population + per-strategy edge (`byTF`). Intraday trains on real 5-/1-min data; swing/position on daily.
- [x] **Dashboard uses the bucket matching the horizon** (`renderDash` → `tfBucket(currentDTE)`), so shorter and longer setups each draw on what was learned for that timeframe.
- [x] **User chooses which timeframe to study** — AI Lab timeframe selector; per-bucket scoreboard/leaderboard/construction/recent-form; console tags each trade's timeframe; auto-learn rotates all three buckets.

## Next (per-timeframe follow-ups)
- [ ] **Position bucket could read weekly bars** (currently daily, same as swing) for genuinely longer structure.
- [ ] **Shared-pool is still global per strategy** — `byTF` buckets are local-only. Extend `api/learn.js` to pool per-timeframe if cross-user intraday learning is wanted.
- [ ] **Intraday training cost** — each intraday self-test is one `fetchBacktestSeries('5m')` call; if rate-limits bite, cache a few symbols' intraday series for the session.

## Done (session 17 — timeframe-true levels + AI Lab → live prediction)
- [x] **Short timeframes no longer target monthly lows / record highs** — `structCandles` reads near-term structure per horizon; intraday uses real live 1-minute bars (`h1d`) with a near-term daily fallback (never a full year).
- [x] **Wired `clampLevels`** (was dead code) so every horizon's stop/target respects its realistic risk band (`HZ_RISK`), R:R preserved; chart zones scale with it.
- [x] **Honest horizon selector** — relabelled (`Intraday · 1-min`, `1 Month`, …), defaulted to Intraday, friendly panel labels + a "live 1-min structure / using recent bars" tag.
- [x] **AI Lab now refreshes the live prediction** — `aiSelfBacktest`/`resetAIMemory` were calling the disabled legacy `load()`; switched to `renderDash()`. Added a "Recent form" tile (last-10 expectancy/win, ▲/▼).

## ~~Next (intraday learning — the remaining gap)~~ — DONE in session 18
- [x] **Self-learning is timeframe-aware** — genomes + strategy edge are bucketed per timeframe; intraday trains on real intraday series (`fetchBacktestSeries`); the dashboard reads the bucket matching the horizon.

## Done (session 9 — reactive theme + bull/bear + bull logo + index strip)
- [x] **Sentiment-reactive UI** — whole site (accent, nav, background) flips red when the read is bearish (`setMood`, `--ac-rgb`, `body.bearish`, `FX_MOOD`).
- [x] **Original bull + bear mascots** in the dashboard AI-read panel; **new bull-head logo**.
- [x] **Index strip** (S&P/Nasdaq/Dow/VIX) on the dashboard.

## Done (session 15 — ticker-only ask bar + self-running AI)
- [x] **Dashboard ask bar → ticker-only** (uppercase/strip A–Z, reworded placeholder).
- [x] **AI auto-learning** — idle trickle (`aiAutoLearnOnce`, every 60s behind `bgIdle`), Pause/Resume toggle + status in AI Lab, posts to the shared pool. (Closes the old "AI auto-learning" TODO from session 6.)

## Done (session 16k — regime-aware learning)
- [x] **Regime-aware self-learning** — strategies bucket expectancy by uptrend/downtrend/range/high-vol; selection weights by current-regime expectancy; AI Lab regime matrix + dashboard/proof-window regime tags.
- [x] **Fixed** AI-chat "What I can explain" chips (were unevaluated `${}.map()` in static HTML).

## Premium polish backlog (standing self-critique — prioritized, ongoing)
> Per the user's directive to continuously refine toward a TradingView/Bloomberg bar. Fix top items each session.
- [ ] **Reusable candlestick renderer.** `proofChartSVG`, `predictChartSVG`, `annotatedChartHTML` duplicate ~40 lines of scaling/axis/candle code — extract a shared `drawCandles({candles,levels,...})` helper (DRY; lower regression surface).
- [ ] **AI-read panel is very tall** (conviction + mood beast + coach notebook + bull/bear + checklist + signals). Tighten hierarchy / consider collapsing the checklist or signals into a compact toggle.
- [ ] **Dead code sweep:** `dashWhy` (button removed), `other` var, schematic `strategyDiagram`/`STRAT_DIAGRAMS` (fallback-only), legacy `renderDash(ticker,q,a)`/`.wk`/`runScan`/`SCAN_DATA`. Prune safely.
- [ ] **A11y:** clickable `<div onclick>` rows (AI console, etc.) need `role="button"`/`tabindex`/keydown; check focus rings + contrast on muted text.
- [ ] **Responsiveness:** audit dashboard + new SVG charts at mobile/tablet widths (charts are width:100% but label gutters may crowd <420px); verify the sidebar icon-rail tap targets.
- [ ] **Loading polish:** consider skeleton shimmer in the metrics/AI-read panels (not just grid dim).
- [ ] **Micro-interactions:** intentional, subtle panel entrance + value-change flashes (price already tweens) — make them feel designed, not default.
- [ ] **Empty states** for every tab when data feed fails (Movers/Screener/Strategy candidates have them; double-check News/Pro Traders/Performance).

## Done (session 16i — premium polish pass 1)
- [x] Trade plan in $/% (killed "ticks" clutter) · orphan blue → neutral · cohesive grid loading state · trimmed Compare button · Escape-to-close modals.

## Done (session 16h — dashboard predicts from now + inline chart)
- [x] **Entry re-anchored to current price** so the plan is a forward prediction, not a partway-through setup.
- [x] **Inline prediction chart** in the Trade Plan (`predictChartSVG`): candles → "now" divider → reward/risk projection cone + labeled levels; removed the "See chart" button.

## Done (session 16g — proof windows / "show the receipts")
- [x] **Reusable proof modal** (`#moWhy`/`openWhy`) — chart + reasoning behind a claim.
- [x] **AI Lab: click any console trade → chart replay (decision divider) + why + conf delta** (`aiWhy`/`proofChartSVG`/`setupWhy`; `simulateSetup` stores a candle `snap`).
- [x] **Dashboard "See the chart & reasoning ↗"** (`dashWhy`) → live candlestick + coach read.

## Next (extend the proof pattern)
- [ ] Add "why ↗" windows to more surfaces: Screener/Movers rows, Strategy candidates, News impact tags, Pro Traders calls — each opening a chart + reasoning.
- [ ] Pooled (shared-backend) console entries have no local `snap` — optionally re-fetch + reconstruct the window by stored date so their charts work too.

## Done (session 16f — candlesticks + real learning + console + timeframe bias)
- [x] **Real candlestick chart with a left price axis** in the Strategy tab (`annotatedChartHTML`).
- [x] **Outcome-based self-learning** — `simulateSetup` walks entry/stop/target forward; win only if target beats stop (in R). `applyLearning` records conf before→after.
- [x] **Live AI learning console** (`renderAIConsole`/`#aiConsole`) streaming each trade + confidence delta.
- [x] **Timeframe-aware bull/bear bias** (`HZ_LOOKBACK` windows `analyze`).

## Done (session 16e — real strategy charts + verdict removed)
- [x] **Strategy charts use real data** — `loadRealStrategyChart`/`annotatedChartHTML` draw the setup on a ticker's actual chart with labeled support/resistance/20-MA/entry/stop/targets + swing markers + thought process; ticker editable; schematic kept as fallback.
- [x] **Removed "Would AI take this trade?"** verdict (a bearish read is a valid short).

## Done (session 16d — AI coach / human-mentor read)
- [x] **Mentor narration + "Would AI take it?" verdict + Bull-vs-Bear + conviction checklist** in the dashboard AI-read panel (`coachRead`/`coachReadHTML`), all from the real engine.
- [x] **Condition-aware indicator tooltips** on the Key-metrics tiles.

## Next (the "AI mentor" wishlist — sequenced)
- [ ] **Per-candle "why"** (#2/#8/#13): click a candle → explain it from its real OHLC/volume/structure (engulfing, gap, volume spike, position vs MA). Needs candle-click hooks on the custom canvas. NO fabricated news/flow unless a real feed is wired.
- [ ] **Replay mode** (#6): step through a historical day candle-by-candle with the coach read, future hidden. Builds on the Backtest engine.
- [ ] **Market personality** (#4): "mood/fear/greed/momentum/health" panel from VIX + breadth + index structure (real data).
- [ ] **Richer coach via Claude**: when a key is connected, let `callClaude` write the narrative for an even more natural voice (keep the rule-based version as the offline default).
- [ ] **Sector heat-map** (#11): lower priority; needs sector data + heavier viz.

## Done (session 16c — self-grading trade journal)
- [x] **Journal tab** — "+ Track this setup" on the dashboard logs a plan; a background poller grades it pending→open→win/loss in R from live price. Scoreboard + live progress bars + history.

## Next (Journal follow-ups)
- [ ] Grade the **currently-viewed** ticker on each `liveTick` too (instant updates without waiting for the 45s poller).
- [ ] Optional: feed resolved Journal R-results into the AI/feedback weighting, and let the AI coach review your live journal (not just backtest history).
- [ ] Optional: position-size each tracked setup ($ risk → shares) so the journal can show $ P&L, not just R.

## Done (session 16 — Strategy tab)
- [x] **New Strategy tab** — day-by-day playbook (weekday themes), a date-computed event calendar (OPEX/witching/NFP/month-end), and live candidate scans that reuse the screener engine. Today auto-highlighted.

## Next (Strategy tab follow-ups)
- [ ] Wire FOMC/CPI/PCE **actual dates** (needs an economic-calendar source) so they can carry real TODAY/THIS-WEEK badges instead of the generic "check a calendar" note.
- [ ] Optional: let each day's candidate scan also derive a one-line entry/stop/target via the dashboard engine, not just a verdict chip.

## Done (session 15 — more info in every tab)
- [x] **News** breadth summary + legend · **Pro Traders** legend + 2 desk members · **Backtest** equity curve + per-strategy mastery + legend · **Performance** risk/edge metrics (profit factor, avg win/loss, expectancy, discipline) + legend · **AI Chat** topic reference · **Alerts** legend + active count · **Feedback** legend.

## Next (more info — optional follow-ups)
- [ ] **Pro Traders per-ticker desk-vs-STRATA agreement** (compare desk lean to STRATA's learned sentiment) — deferred (needs a fetch/analyze per name).
- [ ] **Movers/Screener legends** for full consistency (they already have breadth stats + descriptive headers, so low priority).
- [ ] **Wire a live newswire** (still a sample feed; needs a provider key).
- [ ] **Lean closer to the reference dashboard layout** if wanted (watchlist + chart + Key Levels + Technical Indicators side-by-side; the index strip is a first step).

## Done (session 8 — emerald + premium nav + landing fix)
- [x] **Emerald-green rebrand** (accent `#22c55e`, brand + bullish) to match the reference.
- [x] **Premium animated nav** — floating glass rail, gliding active pill (spring), magnetic hover, cursor glow, spring icons (`initPremiumNav`).
- [x] **Landing bleed-through fixed** — `#landing` opaque again; `#fxCanvas` behind the app only; landing gets its own green aurora orbs.

## Now / next (highest value)
- [ ] **(Optional) lean further into the reference layout:** index-chips row (SPX/NDX/DJI/VIX), and a classic watchlist+chart+indicators dashboard composition if the user wants the dashboard itself to mirror the picture more literally.
- [ ] **Apply the data-quality fix to the dashboard too.** Movers/Screener now recompute day-% from the price series (the proxy prev-close is often wrong), but the **dashboard header** still shows the raw `q.pct`/`q.change` from `fetchQuote` (can read e.g. "+36%" on AAPL). Move the series-based recompute into `fetchQuote` so every consumer benefits.
- [ ] **Background perf check.** `#fxCanvas` runs a full-screen rAF (aurora gradients + O(n²) constellation links). It pauses when hidden and respects reduced-motion, but profile on a low-end laptop; if needed, cap particle count / pre-render the aurora.
- [ ] **Apply the dashboard's `dash-` look to the inner tabs.** Dashboard, the sidebar, movers, Pro Traders (consensus) and Backtest (scoreboard) are on the new flat look; Screener / AI Lab / News / Feedback / the Backtest arena+playbook still use older `.card` chrome. Strategy emoji 📈🚀📉🪃↔️ still linger in LAB_STRATEGIES/PLAYBOOK, and the Pro Traders filter row still has 🟢🔴.
- [ ] **Deepen Backtest / Pro Traders further** if wanted: Backtest could add an equity curve + per-strategy mastery breakdown (Performance tab already has some of this); Pro Traders could add more desk members and a per-ticker "desk vs STRATA" agreement check.
- [ ] **Dashboard polish.** Each panel re-renders on every ask; the TradingView widget only remounts on ticker change (good). Consider: lazy-mount TV until the tab is visible, persist last ticker, and when a Claude key is connected lead the AI-read panel with a natural-language answer. Tick distances are large by design (1 tick = $0.01) — confirm ticks vs points/$ with the user.
- [ ] **Dead code:** legacy `renderDash`/`.wk`/`.fc`/`.cp` remnants and the old ticker-row/dte-row CSS are unused — safe to prune. (The `.cp-*` chat CSS was removed in session 6; the disabled legacy `renderDash`/`.wk` workspace JS still lingers.)
- [ ] **Deploy the shared-learning backend** — code is ready (`api/learn.js`); follow `DEPLOY_BACKEND.md` (push to GitHub → Vercel → add KV). Until then it's local-only.

## Done (session 6)
- [x] **Dashboard rebuilt as a real panel terminal** (ask bar + header + chart/plan/AI-read/metrics/signals panels), replacing the conversational chat. `renderDash` reuses the analysis engine.
- [x] **Single source of truth for levels** — entry/stop/TP now live only in the Trade Plan panel (no more banner + card + chip triplication).
- [x] **Landing flattened to black-minimal** — logo, buttons, bullet icons, bars, metrics band, pricing card, final CTA, and showcase charts no longer use blue→cyan→purple gradients or glow.
- [ ] **Live news** — News tab is a static sample feed; wire a real newswire (needs a provider API key).
- [ ] **AI auto-learning** — optional background trickle of self-tests so confidence builds without manual training (persistence + sharing are done; auto-train is not).

## Done (session 7 — STRATA rebrand + pro shell + "wow" pass)
- [x] **Rebrand → STRATA** (name, logo, all chrome/copy).
- [x] **Sidebar nav** (`.appnav`, grouped) replaced the top nav; **removed the top AI button** (moved to footer).
- [x] **Animated "living market" background** (`#fxCanvas`) site-wide.
- [x] **Movers banner** (`.appbar`) + **High Volume tab** with real-data sortable cards + breadth header.
- [x] **Live Screener** (real `analyze` scan, sortable filters, breadth stats, results table).
- [x] **Performance** equity curve + best-streak; **Pro Traders** desk-consensus; **Backtest** scoreboard + "Surprise me".
- [x] **Data-quality:** recompute day-% from the price series in movers/screener (kills the "+36%" artifact there).

## Soon
- [ ] **Mobile sidebar:** under 1080/640px it collapses to an icon rail — verify tap targets / consider a slide-over drawer for phones.
- [ ] Replace remaining emoji across the app with line icons (strategy icons, Pro Traders filter row, ✅/❌ verdicts).
- [ ] Re-style the modals (`#moAcct`, `#moAlert`, `#moAI`) to full glass/landing language.

## Deploy / infra
- [ ] Add a GitHub remote and push (`git remote add origin … && git push -u origin main`).
- [ ] (Optional) Vercel serverless `/api/claude` proxy so hosted visitors get AI without their own key — note: bills the owner's key for everyone; only for private deploys.
- [ ] (Optional) `README.md` for the GitHub repo.

## Nice to have
- [ ] News: it was removed from the dashboard's old left rail — decide where live news lives (its own tab? a collapsible panel?).
- [ ] Watchlist persistence (localStorage) + live price chips.
- [ ] Mobile pass on the dashboard (landing is responsive; app less so).

## Done (recent — see CHANGELOG.md for full history)
- [x] Premium landing page rebuilt from first principles (editorial, asymmetric, animated).
- [x] App shell aligned to landing (glass nav, single column, line icons).
- [x] Dashboard reordered into trader reading order; Watchlist removed.
- [x] TradingView primary chart + AI Levels toggle.
- [x] Structure+ATR accurate entry/stop/TP; live streaming price; AI Lab feedback fix.
- [x] Deploy-ready for Vercel (index.html at root).
