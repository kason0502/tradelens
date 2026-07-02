# STRATA — TODO

> Living doc. Keep prioritized; check items off and add new ones each session.
> Last updated: 2026-07-01 (pipeline run 2: evidence + visual system)

## Done (2026-07-01 — pipeline run 2: backtester-backed info + STRATA visual system)
- [x] **Generalization artifact** (`results-generalization.json`, 8 markets, frozen rule, reproducible generator) — wired into the edge card (FUT_PF hardcodes DELETED, both ES windows shown), a Backtester generalization table, Matrix evidence lines, the app rail `#genEv`, and the landing big-stats band.
- [x] **"Inside the trades" analysis card** — yearly returns, drawdown periods w/ recovery, exit-reason breakdown (stop fired 0/59 — computed), expectancy/streaks, hold histogram, time-in-market, rolling PF.
- [x] **Hourly verdict can never print green** (forced amber "exploration only"); saved-run tf tagging; "1hy" + "daily bars" bugs fixed; synced saved-run rows clickable (✕ local-only).
- [x] **Fetch dedupe** (results.json ×2 gone; fetchLivePrice 5s memo) — was ~39 proxy hits/load.
- [x] **Visual system:** tabular-nums + U+2212 + `.nu` units · `strataChart` (time-scaled equity — deleted both old renderers) · unified tile spec · `.ct-glyph` strata motif ×3 + layered landing dividers · app long-only stat default + shorts toggle · ≤520px bottom-dock nav (root-cause of the 267px column).

## OWNER FEEDBACK BACKLOG (2026-07-01 — pipeline wave 3 in progress)
**Wave A (fixes/upgrades):** PO3 card: explain Acc/Manip/Dist plainly + more real data · expand edge card further · compact Futures layout (less scrolling) · Matrix: more per-market info · Playbook: professional diagram + real stats · Split View: accessible from other tabs · Strength: new-trader readability · Risk Calc: make genuinely useful · Backtester: honest hold-time expectation-setting (~27d avg; no shorter edge exists yet) · Learn: refresh to current product · **ABOLISH AI Chat tab + Connect-AI footer** · deluxe nav feel both surfaces · Live: fix ⚡ Edge Finder · fastest-honest refresh cadence + "updated Xs ago" · per-marker WHY + take/skip guidance · indicator stats from generalization artifact · fix top-left logo (use owner's logo.png) · symbol search + custom watchlist.
**Wave B (new features, architect-designed):** PRO "Trade Planner" tab (live indicator → strategy match → entry/SL/TP from real structure + artifact stats, educational framing) · "Market Structure" tab (auto FVG/liquidity-zone detection, NO trade suggestions; users define/describe OWN strategies + paper-track live with SL/TP hit detection + % P&L + history; dead Journal engine may revive for tracking).

## Next (wave 3 run 1 discoveries — honesty risks in dead code)
- [ ] **Dead alerts system:** `#moAlert` modal + `addAlertModal`/`addAlert2`/`renderAlerts` have NO callers — yet `TIER_FEATS` Plus copy still sells "alerts". Wire it up or remove it and scrub the tier copy.
- [ ] **Dead stock-era backtest game** (`initBacktestTab`/`dealBacktest`, ~2747–2997) contains stale "Connect Claude" strings pointing at the deleted button — prune when next in the area.
- [ ] **`#tab-ailab` referenced by guarded JS but has no pane** — the AI self-learning block is fully dead; candidate for the next dead-code sweep.

## Next (pipeline run 2 leftovers)
- [ ] **`btViewSaved` unguarded `${r.bars}`** (index.html ~5696) — "undefined daily bars" if a record ever lacks `bars`; add `r.bars||'—'`.
- [ ] **serve.ps1 directory URLs** — `/trader/app/` 404s locally (only `/` maps to index.html); links use the full path so it works, but a dir→index fallback would make the documented URL valid.
- [ ] **App chart markers still plot short trades** while tiles/curve are long-only by default — legend discloses it; consider dimming short markers when the shorts toggle is off.
- [ ] **Two competing `.bt-stat` definitions** (~426 sim-trainer vs ~1131 backtester) share a class name — rules leak across; rename one when next touched.
- [ ] **`?t=Date.now()` cache-busters** on results fetches defeat HTTP caching on Vercel — consider a version param or plain URLs.
- [ ] **App rail note** still says "validated by the Python backtester" generically — name the ES window.
- [ ] **App full `strataChart` port** (rail sparkline stays compact by design; a bigger app chart could adopt the full frame).
- [ ] **Roll-adjusted continuous futures data** would clean up the CL/GC splice caveat (paid data).
- [ ] **Daily-rule improvements** can no longer use the 8-market daily runs as holdout (consumed as evidence) — only the ES-daily incremental-holdout discipline remains.

## ⚠️ HARD PRECONDITIONS before `PAY.testMode=false` (going live on Stripe)
- [ ] **`api/me.js` re-grant loophole:** any historic `session_id` re-grants 31 days with no subscription-status check — a canceled subscriber can bookmark the success URL and re-unlock forever. Needs `api/stripe-webhook.js` + server-verified entitlement.
- [ ] **Client-side tier gating is bypassable** (`localStorage tlpro_account_v1 {"tier":2}` unlocks everything incl. the app's #proGate) — acceptable in test mode ONLY; server-side entitlement check required for real billing.
- [ ] **Plus "setup alerts" copy vs reality:** alerts exist only in-page; don't bill for server-side alerts until the cron exists.

## Done (2026-07-01 — five-agent pipeline run: Pro access + visuals + honesty)
- [x] **Pro can reach the app from the site** — snav "STRATA Live · PRO" link + account-chip/paywall anchors (full `/trader/app/index.html` path; bare `/trader/app/` 404s locally).
- [x] **Stripe-return race** — `payHydrate` reloads after grant; duplicate call removed.
- [x] **Tier copy honesty ×3** — "dedicated live terminal (web)"; cut Priority-data/synced claims.
- [x] **Flat `.card` retheme** (one chrome language) · **payLock premium + blurred real PO3 preview** · **skeleton loaders** (Futures) · **emoji→SVG chrome** · **acct-chip accent tokens** · **mobile ≤480 overflow fixed both surfaces** (incl. the QA-caught `.fut-scan` 2×2 regression) · **app boot fast-path** (`tlpro_boot_seen_v1`).
- [x] **Hero honesty complete** (all 5 static tiles tagged "example"; watchlist seeds "—") · **EDGE HOLDS graded on longs only**.
- [x] **Edge research round 2: NO EDGE** — GC compression / CL-GC time-of-day / daily-filter pass all dead in-sample; daily system proven stop-spec-insensitive; GC/CL hourly holdouts intact.

## Next (pipeline leftovers — small)
- [ ] **Matrix "↻ Refresh"** (`#mxRefresh`) still emoji — same SVG swap as the futures button.
- [ ] **App rail "★ LONG/SHORT SIGNAL"** text stars → SVG (only the toast was swapped).
- [ ] **Paywall greens** (`.pay-badge`/`.pt-cur`/`.pt-feats li::before`) still use P&L green — switch to accent tokens (same as the chip fix).
- [ ] **`#futBody` at phone widths** renders ~267px in ~363px available (unused right gutter) — investigate next polish pass.
- [ ] **`.po3-seg` labels clip <400px** inside the blurred teaser.
- [ ] **`moAI` modal ✨ emoji** (~1906) → SVG.
- [ ] **Skeleton adoption** at the other `loading-label` call sites (Matrix/Strength/Backtester) via `skelCard`.
- [ ] **Edge research next avenue (no holdout cost):** run the frozen daily rule on YM/RTY/GC/CL daily as generalization evidence; per-market real PFs would also replace the remaining hardcoded NQ/SPY/QQQ constants.

## Done (2026-07-01 — three-agent pass: critic round 4 + edge research + fixes)
- [x] **Built `strata-debugger` + `edge-hunter` subagents** (`.claude/agents/`) — the fix-and-verify robot and the gated strategy-research robot.
- [x] **Hourly edge research: NO EDGE** — 40 configs / 4 families on ~2y of ES 60-min bars; in-sample PF 1.58 → holdout PF 0.92. Post-mortem in CHANGELOG. ⚠️ The 2025-09→2026-07 hourly holdout is **burned** for these families — don't re-test variants against it and call it OOS.
- [x] **Critic round 4 honesty fixes** — Free-tier copy (no phantom "long & short"), hero "validated on ES & NQ" scoping, ES PF "(full sample)" relabel, hourly-mode "data explorer" caveat, hero bento "example" tags, buy-&-hold yardstick on the Backtester, snav `title`/`aria-label`.
- [x] **Fresh-browser TDZ init crash fixed** (`AI_MEMORY` before `TF_BUCKETS` → whole init aborted for new visitors).
- [x] **App: stale long-only PO3 copy removed; Longs/Shorts stat split + "shorts not OOS-tested" disclosure; Legend softened.**

## Next (from critic round 4 — not yet done)
- [ ] **Lock icons on gated nav tabs** — Free users currently discover the paywall by click-surprise; mark Plus/Pro tabs in the sidebar itself.
- [ ] **Verify Plus "alerts" claim before going live on Stripe** — `TIER_FEATS` sells alerts; in-app banner/notification exists only while the page is open. Don't bill for server-side alerts until they exist.
- [ ] **Split the app's EDGE HOLDS verdict by direction** (disclosure shipped; the badge itself still grades the combined record — on ES daily the unvalidated shorts drag PF below 1).
- [ ] **Downgrade the in-browser hourly verdict wording** — an hourly run can still print a green "edge holds" (gross of costs) above the new caveat.
- [ ] **Edge card: add a "YM/RTY/CL/GC pattern-only" note** to close the loop with the Matrix flags.
- [ ] **Data-freshness chip on the signal card** ("as of HH:MM:SS · refreshed Ns ago" + a visible warning when running on fallback proxies instead of `/api/yf`).
- [ ] **Wire the hero bento tiles to the real engine** (labeled "example" for now; `winProb`/`edgeFromProb` exist in legacy code).
- [ ] **Reactivate the Journal for futures paper-trades** (real $ P&L, CSV export) — the accountability hook that converts free → Plus; old engine exists as dead code.

## Done (session 52 — new indicator badges + PO3 market-cycle zones)
- [x] **New bull/bear indicator badges** wired into both surfaces — root `bull-ind.png` / `bear-ind.png` (one source of truth; root so Vercel serves them). Fixed the **broken** STRATA Live marker refs (old `/trader/bull indicator.png` files were deleted) + the Legend.
- [x] **PO3 zone engine + card on the site** — Accumulation/Manipulation/Distribution read from real daily structure, with a phase strip, SVG schematic, directional badge, description, range/equilibrium, and a phase-specific plan (`po3Analyze`/`po3CardHTML` in the Futures tab).
- [x] **PO3 card in the STRATA Live app** — mirrored engine in a new rail card (`renderPO3`).
- [x] **`serve.ps1` honors `PORT`** + `launch.json` `autoPort` — multiple preview sessions no longer collide on 8777.

## Next (PO3 follow-ups)
- [ ] **Verify live in a real browser** — the preview sandbox can't load the TradingView/Chart.js CDNs, so the full Futures tab doesn't init there; the PO3 engine + card were verified directly, but eyeball the live ES read once. (Per CLAUDE.md: this page can't be auto-screenshotted.)
- [ ] **Tune the PO3 thresholds** on real history if the phase calls feel off (sweep buffer `0.1×ATR`, expansion `0.3×ATR`, compression `≤6.5×ATR`). Consider a small backtest of "enter on manipulation reclaim" to put an honest number on the zone.
- [ ] **Show the PO3 zone on the Market Matrix** (a per-market phase chip) so the cycle read spans all six futures, not just the selected one.
- [ ] **Draw the live PO3 box/sweep on the actual candle chart** (not just the schematic) — range hi/lo lines + the sweep marker on `futCandleSVG` / the app canvas.

## Open (sessions 53–62 — carried forward)
- [ ] **Volatility / timing heatmap** — a grid of realized volatility & average move by hour-of-day × day-of-week (from real intraday bars), showing when the biggest moves happen. New "Timing" panel/tab, Plus tier. (Requested, not built yet.)
- [ ] **Website Futures signal → long + short** — the trader app now shorts downtrends; give `futSignal`/`paintFutures` on the main site the same treatment (it still says "No trade — downtrend").
- [ ] **Go live on payments/storage** — create two Stripe products ($20/$50), set `STRIPE_SECRET_KEY` + `STRIPE_PRICE_PLUS` + `STRIPE_PRICE_PRO` in Vercel, enable Vercel KV, flip `PAY.testMode=false`. See `DEPLOY_PAYWALL.md`.
- [ ] **Multi-device login + Stripe webhook** — v1 remembers the tier per browser after checkout; add `api/auth.js` + a users table and `api/stripe-webhook.js` for real account portability + renewal/cancel sync.
- [ ] **App still has stock-era dead code** (Pro Traders sample data, movers/screener universes, backtester random-ticker) — prune to pure futures if wanted.

## Done (sessions 53–62)
- [x] New bull/bear **indicator badges** at root (`bull-ind/bear-ind.png`); fixed the app's broken marker refs.
- [x] **PO3 cycle zone** + **12-factor edge bias stack** on both surfaces (site card + app rail).
- [x] **Validated-signal markers** in the app (real backtest entries/exits, click for detail), bigger, direction-aware; replay **speed control**; subtle marker bounce.
- [x] Boot intro (dim bull, steady glow, ready for a looping `/logo.mp4`); background bull **eye→edge glow** every ~10s.
- [x] Landing **remodeled to futures-only**; removed **AI self-learning** copy; pricing = the 3 real tiers; faint bg bull.
- [x] **3-tier membership** (Free / Plus $20 / Pro $50) with gating, test mode, Stripe + KV backend code, and the trader-app Pro gate.
- [x] **Backtester**: Hourly short-hold timeframe, strategy explainer, signal timeline; server-side saved backtests.
- [x] **App trades downtrends** (long + short).

## Done (session 37 — trader-critic robot + its quick wins)
- [x] **Built `futures-trader-critic` subagent** (`.claude/agents/`) — reusable site-review robot (flaws + monetization ideas through a trader's eyes).
- [x] **Fixed headline day-change** to use the close series in `fetchQuote` (was the proxy prev-close bug).
- [x] **Matrix: validated vs pattern-only** — ES/NQ validated; YM/RTY/CL/GC badged + excluded from the buy count.
- [x] **Inline position size** in the Futures plan + persisted account settings (`tlpro_acct`) synced with the Risk Calc.
- [x] **Market-state + timestamp** on the signal card; **swapped 🟢 emoji** for a `.live-pip` dot.

## Done (session 42 — critic round 3 quick wins)
- [x] **Profit-factor contradiction fixed** — ES tile derives from results.json live (`futPfReal`); constant fallback = 1.99.
- [x] **results.json config cleaned** — futures_trend_pullback + MES point_value 5; dropped dead options/ORB fields.
- [x] **Contract multiplier stated** (MES $5/pt) across the Backtester.
- [x] **Win-rate tile contextualized** ("low by design").
- [x] **Forming vs confirmed BUY banner** (amber while the bar's open, green on the close).

## Next (the wedge — needs a backend)
- [ ] **Server-side alerts (email/push)** — Vercel cron + `futSignal` on closed bars → notify on a fresh BUY SETUP. Subscriber list in Vercel KV (reuse the `api/learn.js` pattern). The one feature that justifies a subscription.
- [ ] **Live forward track record** — log signal flips server-side since launch; show a live curve next to the backtest.
- [ ] **Per-symbol real backtests** so each market's PF/n/drawdown is real (removes the remaining hard-coded NQ/SPY/QQQ constants).
- [ ] **Close-aware `buySetup` boolean** (currently the label/banner handle forming, but the boolean still evaluates intraday).
- [ ] **Dedupe the sentiment gauge** (ES≈SPY, NQ≈QQQ → really 2 signals) or pull the Matrix's 6 distinct markets.

## Done (session 41 — trade-math fix + Futures right rail)
- [x] **Fixed trade example math** — show points + implied $/pt so P&L reconciles; stop excluded from chart scaling (no more squished candles).
- [x] **Futures main + right rail** with the AI Market Sentiment gauge (real breadth) + Strategy Performance, toward the mockup.

## Next (finish the mockup — real-data pieces only)
- [ ] **Bottom panel row:** Market Breadth donut (% above 200-day, real from Matrix), Top Performers (real day %), Risk Status (from ATR/vol). All derivable without faking.
- [ ] **Recent Trades table on the dashboard** — show the backtest's most recent trades until a live journal exists.
- [ ] **Top account/search bar** above the main column (cosmetic).
- [ ] **Skip unless real:** economic calendar (needs a feed), journal-streak ring (needs the journal).

## Done (session 40 — candlestick trade replay + in-browser backtester)
- [x] **Candlestick trade viz** — fetch real OHLC around any backtest trade (proxy period1/period2) + Entry/Stop/Take-profit lines; click-to-replay.
- [x] **In-browser backtest runner** — run the rule live on real data (ES/NQ/YM/RTY/CL/GC/SPY/QQQ, 5y/10y/max) → stats + equity + verdict.

## Next (backtester follow-ups)
- [ ] **Candlestick viz on live-runner trades too** (candles already fetched in `_btLiveCandles` — wire a featured trade + log for `btSimulate` output).
- [ ] **Fold costs into the in-browser sim** (slippage + commission) so its numbers are comparable to the Python engine, not just gross.
- [ ] **Cache historical OHLC** per (symbol, window) to avoid refetching when replaying trades.

## Done (session 39 — Backtester tab + backtest emphasis)
- [x] **Backtester tab** — real stats grid, equity curve, a real trade example (click-to-replay), full 59-trade log, from `results.json`.
- [x] **Strategy Performance card** on the Futures tab (backtest return/win/PF/trades/expectancy) + link to the Backtester.
- [x] **Instrument cards restyled** larger/left-aligned toward the reference mockup.

## Next (finish matching the reference mockup — bigger lift)
- [ ] **Top account bar** (search + notifications + settings + user) above the main column.
- [ ] **Right rail panels:** sentiment gauge (derive from the live signal, real), economic calendar (NEEDS a real feed — avoid faking), strategy-performance (done, could move to the rail).
- [ ] **Bottom dashboard panels** (AI Signal / Market Breadth donut / Top Performers / Risk Status / Journal streak) — Market Breadth + Top Performers are real (from Matrix data); Journal-streak needs the journal feature.
- [ ] **Recent Trades table on the dashboard** — real once the live journal exists; until then it can show the backtest's recent trades.
- [ ] **Chart timeframe tabs (1D/5D/1M…)** — only if backed by real data per timeframe (don't add dead chrome).

## Done (session 38 — critic round 2)
- [x] **Priority tabs bigger + nav regrouped** (Trade spine: Futures/Matrix/Playbook = `.snav-pri`).
- [x] **`marketState()` Globex hours for futures** (fixed the cash-hours regression).
- [x] **Confirmed-vs-forming** signal label (daily-close honesty).
- [x] **Charts cash-index caption** on-screen.
- [x] **Edge scoreboard** clarified as OOS runs w/ pointer to trade count + period.
- [x] **Mobile**: `.fut-scan` 2×2 + drop `.fs-px` float under 520px.

## Next (highest-value from the critic — need a backend or bigger lift)
- [ ] **Alerts that fire when the app is closed** (email/push via a Vercel cron hitting `/api/yf` + `futSignal`). The robot's #1 "worth money" idea — the real wedge for a ~6-trade/year system. Needs `api/cron-alert.js` + an email/push provider + subscriber storage.
- [ ] **Server-side forward live-edge track record / journal** (grade live `futSignal` flips since launch; show real $ P&L). Partial in-file version possible but only logs while the app is open.
- [ ] **Per-symbol edge scoreboard from real `results.json`** (needs a backtester run per symbol so each PF carries its own n-trades/period/drawdown; currently one run + hard-coded `FUT_PF`).
- [ ] **Close-aware `buySetup`**: only flip to confirmed on the last *closed* daily bar (currently labelled forming/confirmed, but the boolean still evaluates intraday).

## Done (session 34 — Split expansion + Learn + Strength + animated backdrop)
- [x] **Animated logo watermark** behind the app (`.bg-logo`, accent-tinted, mood-flipping, reduced-motion-safe) + tab-switch entrance anim.
- [x] **Split View expanded** — 5 module types (chart/signal/grid/sessions/notes), 1/2/3/4 layouts, localStorage persistence, live-tick timer.
- [x] **Learn tab** — visual academy with SVG diagrams (candle anatomy, long/short, tick value, MA trend, leverage, the strategy).
- [x] **Relative Strength tab** — multi-market normalized overlay + leaderboard, selectable window.

## Next (visual / new-tab follow-ups)
- [ ] **Crosshair/symbol sync across Split panes** (TradingView iframes can't share a crosshair; could at least sync the symbol across chart panes).
- [ ] **Strength: let the user pick which markets to overlay** (currently all six) + add a relative-to-ES mode.
- [ ] **Learn: add an interactive candle** (hover a real candle to see its OHLC) and a quick quiz to reinforce.
- [ ] **Verify the logo watermark contrast** on a real monitor — tune opacity if it's too faint or too busy behind dense tabs.

## Done (session 33 — playbook diagram + Matrix/Charts/Split View)
- [x] **Playbook setup diagram** (`playbookDiagramSVG`) — annotated schematic: uptrend → pullback (buy zone) → entry → ride → exit, with a phase legend.
- [x] **Market Matrix** tab — live grid (ES/NQ/YM/RTY/CL/GC) w/ sparkline + signal + breadth header; cards open the Charts tab.
- [x] **Charts** tab — TradingView symbol lookup (search + futures chips), drawing tools enabled.
- [x] **Split View** tab — 1/2/4-pane workspace; each pane = a live chart or a live signal card.

## Next (new tabs follow-ups)
- [ ] **Persist Split View / Charts state** to localStorage (layout, per-pane symbols, last chart symbol) so it survives reload.
- [ ] **Matrix auto-refresh** on an interval while the tab is open (bgIdle-gated), like the other pollers.
- [ ] **Add CL/GC to the validated edge** in the backtester so the Matrix signal carries the same proven OOS profit factors (currently only ES/NQ/SPY/QQQ are validated).
- [ ] **Split panes: more module types** (Risk Calc, Sessions) — needs the fixed-ID renderers parameterized to a target element.

## Done (session 32 — candles + futures toolkit)
- [x] **Candlestick price chart** (`futCandleSVG`) replaces the line — real OHLC + 10/50-day MAs + price axis.
- [x] **Playbook tab** — the system's rules + a live ES pre-trade checklist (`renderPlaybookTab`).
- [x] **Risk Calculator tab** — position sizing from real CME contract specs (`renderCalc`/`FUT_SPECS`); pre-fills from live ES.
- [x] **Session Clock tab** — live global sessions, DST-correct, London–NY overlap highlight (`renderSessions`/`_tzNow`).

## Next (futures toolkit follow-ups)
- [ ] **Auto-refresh the futures scan** on an interval while the tab is open (still manual via ↻ Refresh).
- [ ] **Calculator: contract auto-detect** — when a contract is picked, default entry/stop from that market's live quote (only ES is pre-filled today).
- [ ] **Add CL/GC to the scan strip** once validated in the backtester (specs already in the calculator).

## Done (session 29 — STRATA refocused on futures)
- [x] **Futures terminal is the new default tab** — live validated trend-pullback signal on ES (signal card + daily chart w/ 10/50-day MAs + plain trade plan + validated-edge card). Stocks dashboard moved to a "Stocks" tab. Shell kept.

## Done (session 30 — futures terminal v2)
- [x] **Multi-market scan strip** (ES/NQ/SPY/QQQ) = selector + at-a-glance signal alert.
- [x] **BUY-SETUP alerts** (banner + opt-in browser notification).
- [x] **Edge card wired to `backtester/results.json`** (latest run line).
- [x] **Removed options-focused 0DTE Lab tab**; logo retheme → "Futures Terminal".

## Done (session 31 — purely futures)
- [x] **Removed all stock/options tabs from the nav** (Futures · AI Chat · Feedback only); hid the stock movers ticker.
- [x] **Pruned dead options JS** (renderOptLab/paintOptLab/optEquitySVG/optLabToggleAuto).

## Next (futures terminal)
- [ ] **Delete the unreachable stock tab panes** from the HTML (and their now-dead render fns: renderMovers/renderScreener/renderStrategy/renderTraders/renderPerformance/renderJournal/AI-Lab) for a smaller file. They're hidden now but still in the DOM.
- [ ] **Commodities/metals** (CL, GC) once validated in the backtester.
- [ ] **Auto-refresh the scan** on an interval while the Futures tab is open.
- [ ] **Prune now-unused CSS** (`.opt-*`) and stock-era styles.

## Done (session 23 — 0DTE options backtester + STRATA 0DTE Lab)
- [x] Standalone honesty-first Python 0DTE backtester in `/backtester` (pessimistic fills, no look-ahead, next-bar exec, fragility report, swappable modules, tests, SPY ORB strategy).
- [x] STRATA **0DTE Lab** tab renders `results.json` (scoreboard, equity curve, fragility verdict, time-of-day, trade log); synthetic sample fallback with a SAMPLE banner.

## Next (0DTE backtester — to make it produce REAL numbers)
- [ ] **Wire the real feed:** subscribe ThetaData (or Polygon/Databento), run Theta Terminal, verify `providers.ThetaDataProvider` field mapping against your tier (greeks!), set `config.json` → `python run_backtest.py`.
- [ ] **Intrabar path risk (biggest optimism):** minute bars can credit a TP that intrabar would've hit the stop first — add pessimistic intrabar ordering or finer data (see `ASSUMPTIONS.md` #3).
- [ ] **Real holiday calendar** (currently Mon–Fri) and **out-of-sample split** to avoid curve-fitting.
- [ ] **Costs realism:** model size/liquidity (quoted size), partial fills, latency beyond next-minute.

## Done (session 22 — scorecard + dollars + level rebalance)
- [x] **Dashboard setup scorecard** — probability/confidence/sample/win-rate/R:R/EV grid + approve-or-skip recommendation banner.
- [x] **AI Lab "profit in dollars" panel** — $ result of 1 contract / $100-risk, worked math, + always-on "low win rate can still win" principle.
- [x] **Fixed tight-stop bug** — stops now beyond major swings with a ≥1.1×ATR floor (was anchoring to minor wiggles → ~14% win rate); targets take the nearest reachable real pivot. Loosened `FWD_CAP` so slow winners aren't truncated.

## Next (push expectancy from breakeven → positive, honestly)
- [ ] **Selectivity / entry quality:** the engine takes every setup in self-tests (→ ~breakeven). Consider only *counting/approving* with-trend + high-feature setups; or wait-for-pullback entries instead of market-at-close. Avoid overfitting.
- [ ] **Intraday calibration:** 5-min self-tests still win-rate-low (~17%); intraday stops/targets likely need vol-relative tuning distinct from daily.
- [ ] **Costs:** fold a small slippage/commission into self-test R so the EV shown is net, not gross.

## Done (session 21 — stops/targets on real structure)
- [x] **Rebuilt `structureLevels`** to anchor stop/target on genuine pivots (`structurePivots`, 2 scales), prefer real structure over arithmetic, honor the horizon band by *choosing among real pivots*, and **flag** when a level isn't on structure.
- [x] **Clamp is now last-resort** — only scales when a level isn't a real pivot (or is wildly wide); real structural levels are left exactly in place.
- [x] **Plan labels say where levels come from** ("real liquidity" / "real structure" / honest "fitted to the horizon") + comments clarify probability/EV never moves the levels.

## Done (session 20 — probabilistic edge engine)
- [x] **Online logistic win-probability model per timeframe** (`AI_MEMORY.model[bucket]`) trained from every self-test on a real-indicator feature vector; direction-relative so one model serves longs/shorts.
- [x] **Expected value + ¼-Kelly size on the dashboard** (edge block: EV in R, win %, suggested size + verdict) — the +EV reframe.
- [x] **Calibration tracking (Brier) + explainable factor weights** in the AI Lab model panel.

## Next (extend the probabilistic engine)
- [ ] **Feed it more features** (volume surge, gap, MA50/200 cross, distance-to-structure) — keep the vector small + explainable; watch for overfitting at low samples.
- [ ] **Active learning:** bias auto-train toward setups where predicted p≈0.5 (max uncertainty) instead of pure random.
- [ ] **Pool the model cross-user** (`api/learn.js`) — currently the logistic weights + Brier are local per device.
- [ ] **Let the EV gate the verdict everywhere** (screener/strategy candidates could rank by EV, not just sentiment).

## Done (session 19 — dashboard ↔ AI Lab per-timeframe link)
- [x] **Dashboard plan shows the AI Lab model driving it** — "AI Lab · {style} model" strip (tests, win%, edge, learned construction) + a "{style} style" header tag; Intraday/Swing/Position each pull their own learned model.
- [x] **"Sharpen {model} ↗" button** (`cpTuneBucket`) — train the swing/position/intraday model from the dashboard in one click.
- [x] **Swing vs Position differentiated** — per-bucket forward-holding cap (`FWD_CAP`) so each learns setups that resolve in its own horizon (were identical apart from the label).

## Done (session 18 — per-timeframe self-learning)
- [x] **Self-learning is timeframe-aware** — Intraday / Swing / Position buckets, each with its own genome population + per-strategy edge (`byTF`). Intraday trains on real 5-/1-min data; swing/position on daily.
- [x] **Dashboard uses the bucket matching the horizon** (`renderDash` → `tfBucket(currentDTE)`), so shorter and longer setups each draw on what was learned for that timeframe.
- [x] **User chooses which timeframe to study** — AI Lab timeframe selector; per-bucket scoreboard/leaderboard/construction/recent-form; console tags each trade's timeframe; auto-learn rotates all three buckets.

## Next (per-timeframe follow-ups)
- [ ] **Position bucket could read weekly bars** for longer structure — deferred: it adds a fetch per position render (rate-limit risk) and daily-over-~10-months is a decent proxy. The `FWD_CAP` split (session 19) already differentiates swing vs position cheaply.
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
