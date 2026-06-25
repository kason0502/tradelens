# TradeLens Pro — TODO

> Living doc. Keep prioritized; check items off and add new ones each session.
> Last updated: 2026-06-25 (session 3)

## Now / next (highest value)
- [ ] **Copilot polish.** Each answer card mounts its own TradingView iframe — cap the thread (e.g. keep last ~5) or lazy-mount to limit weight. Consider: persist conversation, voice of follow-ups, and when a Claude key is connected, lead with a natural-language answer (not just the rule-based verdict). Tick numbers are large by design (1 tick = $0.01) — confirm the user wants ticks vs points/$ distance.
- [ ] **Dead code:** legacy `renderDash`/`.wk`/`.fc` and the old ticker-row/dte-row CSS are now unused — safe to prune later.
- [ ] **Apply a consistent look to the inner tabs.** The main Dashboard view was rebuilt as the `.wk` terminal workspace; Screener / Backtest / AI Lab / Pro Traders / News / Feedback still use the older `.card` styling and don't match the new panel system yet.
- [ ] **Bring the rest of the landing to black-minimal.** Hero + design tokens are done, but the other sections still use the older gradient/glow styling: feature rows (`.lx-feat` gradient icon tiles), metrics band (`.lx-band` blue radial), steps (`.lx-step` gradient numerals), pricing (`.lx-plan.hot` blue glow), and the final CTA (`.lx-final` big gradient slab). Flatten to dark surfaces + thin borders + single accent so every section matches the new hero.
- [ ] **Deploy the shared-learning backend** — code is ready (`api/learn.js`); follow `DEPLOY_BACKEND.md` (push to GitHub → Vercel → add KV). Until then it's local-only.
- [ ] **Kill level redundancy on the dashboard.** Entry/stop/TP still appear in the direction banner *and* the trade-setup card *and* the chart chips. Pick ONE source of truth.
- [ ] **Polish the inner tabs** to black-minimal (Screener, Backtest, AI Lab, Pro Traders, Feedback still use denser legacy styling; strategy icons 📈🚀📉🪃↔️ remain in LAB_STRATEGIES/PLAYBOOK).
- [ ] **Consolidate the metrics strip vs the Indicators card** (duplicated values).
- [ ] **Live news** — News tab is a static sample feed; wire a real newswire (needs a provider API key).
- [ ] **AI auto-learning** — optional background trickle of self-tests so confidence builds without manual training (persistence + sharing are done; auto-train is not).

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
