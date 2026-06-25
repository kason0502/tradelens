# TradeLens Pro — TODO

> Living doc. Keep prioritized; check items off and add new ones each session.
> Last updated: 2026-06-25

## Now / next (highest value)
- [ ] **Kill level redundancy on the dashboard.** Entry/stop/TP currently appear in the direction banner *and* the trade-setup card *and* the chart legend. Pick ONE source of truth (the setup card) and trim the rest.
- [ ] **Polish the inner tabs** to match the landing/shell. Screener, Backtest, AI Lab, Pro Traders, Feedback still use denser legacy styling and some emoji (feedback box 💰📉⏳, chart controls 🕯📈📊⦿). They inherit the blue tokens but aren't hand-polished.
- [ ] **Consolidate the metrics strip vs the Indicators card** — RSI / 20-day avg / range position / 52w hi-lo are shown in both. Keep one quick-glance set + one detail set without duplication.

## Soon
- [ ] **Nav consolidation:** 9 top tabs → ~4 primary (Terminal · Screener · Backtest · AI Lab) + a "More" menu and a utility cluster (Account/Alerts/AI key). Fold Pro Traders / AI Chat / Feedback.
- [ ] Replace remaining emoji across the app with line icons.
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
