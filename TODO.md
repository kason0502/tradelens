# STRATA — TODO

> Living doc. Keep prioritized; check items off and add new ones each session.
> Last updated: 2026-06-26 (session 9)

## Done (session 9 — reactive theme + bull/bear + bull logo + index strip)
- [x] **Sentiment-reactive UI** — whole site (accent, nav, background) flips red when the read is bearish (`setMood`, `--ac-rgb`, `body.bearish`, `FX_MOOD`).
- [x] **Original bull + bear mascots** in the dashboard AI-read panel; **new bull-head logo**.
- [x] **Index strip** (S&P/Nasdaq/Dow/VIX) on the dashboard.

## Done (session 15 — ticker-only ask bar + self-running AI)
- [x] **Dashboard ask bar → ticker-only** (uppercase/strip A–Z, reworded placeholder).
- [x] **AI auto-learning** — idle trickle (`aiAutoLearnOnce`, every 60s behind `bgIdle`), Pause/Resume toggle + status in AI Lab, posts to the shared pool. (Closes the old "AI auto-learning" TODO from session 6.)

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
