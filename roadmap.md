# STRATA — Development Roadmap

> Last updated: 2026-07-01
> Owner: @kason0502 | Build system: Hermes Agent (autonomous)

## Vision
Transform STRATA from a validated trading signal platform into a premium, institutional-grade futures trading ecosystem that rivals Bloomberg Terminal + TradingView + LuxAlgo — but original, AI-driven, and built for the independent trader.

---

## Phase 1: Foundation Hardening (Current → Week 2)
**Goal:** Stabilize what exists, close security gaps, prepare for real payments.

### 1.1 Security & Payment Prerequisites
- [ ] Fix `api/me.js` re-grant loophole (server-side subscription verification)
- [ ] Build `api/stripe-webhook.js` for subscription lifecycle (renewal, cancel, disputes)
- [ ] Server-side tier entitlement (replace client-side localStorage gating)
- [ ] Rate limiting on all API endpoints
- [ ] Input sanitization audit on api/*.js

### 1.2 Code Quality & Cleanup
- [ ] Remove dead stock-era code (~40% of JS is unreferenced)
- [ ] Extract shared candlestick renderer (DRY: `proofChartSVG`, `predictChartSVG`, `annotatedChartHTML`)
- [ ] Fix the two competing `.bt-stat` CSS definitions
- [ ] Replace remaining emoji with SVG line icons
- [ ] Accessibility audit: clickable divs → buttons, focus rings, ARIA
- [ ] Mobile responsiveness pass (≤480px verified on all tabs)

### 1.3 Performance
- [ ] Profile `#fxCanvas` on low-end devices (aurora + constellation + wave ribbons)
- [ ] Remove `?t=Date.now()` cache-busters on results fetches
- [ ] Lazy-mount TradingView widgets (only when tab visible)
- [ ] Audit fetch deduplication (recently improved, verify)

---

## Phase 2: Premium Visual Overhaul (Weeks 2–4)
**Goal:** Make every pixel scream institutional quality.

### 2.1 Layout System
- [ ] Implement dockable/resizable panel system (trader workspaces)
- [ ] Top command bar: search + notifications + settings + user profile
- [ ] Right rail: AI sentiment gauge + economic calendar + strategy performance
- [ ] Bottom panel row: market breadth donut + top performers + risk status
- [ ] Keyboard shortcuts system (Ctrl+K command palette, tab switching)

### 2.2 Data Display
- [ ] Order flow visualization (bid/ask depth, time & sales style)
- [ ] Volatility/timing heatmap (hour × day-of-week from real intraday bars)
- [ ] Heat-mapped market matrix (correlation + relative performance)
- [ ] Real-time P&L ticker with position tracking
- [ ] Multi-timeframe candle sync (1m/5m/15m/1h/4h/D)

### 2.3 Chart Enhancements
- [ ] Draw PO3 box/sweep on actual candle chart (not just schematic)
- [ ] Chart timeframe tabs backed by real data per interval
- [ ] Crosshair/symbol sync across Split panes
- [ ] Custom indicator overlays (Bollinger, Ichimoku, VWAP, volume profile)
- [ ] Chart drawing tools (trendlines, fibs, pitchfork)

### 2.4 Animation & Polish
- [ ] Panel entrance micro-interactions (spring-based, not linear)
- [ ] Value-change flash animations on all numeric displays
- [ ] Skeleton loaders on every data-dependent component
- [ ] Loading states: shimmer → data reveal transitions
- [ ] Subtle parallax depth on panel hover

---

## Phase 3: AI Agent Intelligence (Weeks 3–5)
**Goal:** Make STRATA's AI genuinely useful, not decorative.

### 3.1 Signal Intelligence
- [ ] Website futures signal → long + short (match trader app capability)
- [ ] Close-aware `buySetup` boolean (confirmed only on closed bars)
- [ ] Multi-timeframe signal confluence (daily + hourly + 15m agreement)
- [ ] Signal quality scoring (feature-based edge estimation)
- [ ] Data-freshness chip on signal card ("as of HH:MM:SS · refreshed Ns ago")

### 3.2 AI Market Analysis
- [ ] Natural language market briefing (morning, mid-session, close)
- [ ] Economic calendar integration (FOMC/CPI/NFP with real dates)
- [ ] Cross-market correlation alerts (CL↔ES divergence, etc.)
- [ ] Regime detection dashboard (trending/ranging/volatile with confidence)
- [ ] AI-generated daily trading plan based on signal + regime + calendar

### 3.3 Learning System
- [ ] Monte Carlo simulation on strategy results
- [ ] Walk-forward validation framework
- [ ] Bootstrap confidence intervals on all edge metrics
- [ ] Pool logistic model cross-user (extend api/learn.js)
- [ ] Strategy improvement suggestions from AI analysis

---

## Phase 4: Backtesting Power (Weeks 4–6)
**Goal:** Institutional-grade backtesting that proves the edge.

### 4.1 In-Browser Backtester
- [ ] Fold costs (slippage + commission) into JavaScript sim
- [ ] Per-symbol real backtests (each market gets its own verified PF)
- [ ] Candlestick visualization on live-runner trades
- [ ] Cache historical OHLC per (symbol, window)
- [ ] Multi-strategy comparison mode

### 4.2 Statistical Rigor
- [ ] t-test significance on strategy returns
- [ ] Monte Carlo drawdown analysis (1000+ paths)
- [ ] Walk-forward optimization with rolling windows
- [ ] Regime-conditional performance breakdown
- [ ] Benchmark comparison (buy-and-hold, random entries)

### 4.3 Reporting
- [ ] PDF export of backtest results
- [ ] Shareable backtest result links
- [ ] Tear sheet generation (Sharpe, Sortino, Calmar, max DD)
- [ ] Monthly/yearly return heatmap
- [ ] Trade-by-trade annotation view

---

## Phase 5: Subscription & Monetization (Weeks 5–7)
**Goal:** Real revenue from real value.

### 5.1 Payment Infrastructure
- [ ] Stripe webhook for subscription lifecycle
- [ ] Multi-device login (email + magic link or OAuth)
- [ ] Server-side entitlement verification
- [ ] Subscription management portal (pause, cancel, upgrade)
- [ ] Usage analytics (which features drive retention)

### 5.2 Premium Features
- [ ] Server-side alerts (email/push on signal flip) — THE subscription wedge
- [ ] Live forward track record (server-side signal logging since launch)
- [ ] Advanced backtesting (Monte Carlo, walk-forward) — Plus tier
- [ ] Custom indicator builder — Pro tier
- [ ] API access for algorithmic traders — Pro tier

### 5.3 Onboarding & Retention
- [ ] Interactive onboarding tour (first-time user experience)
- [ ] Welcome email sequence (drip campaign for Plus/Pro features)
- [ ] Weekly edge report email (automated from AI analysis)
- [ ] Trading journal with CSV export (reactivate dead code)
- [ ] Achievement/streak system for consistent use

---

## Phase 6: Production Hardening (Weeks 7–8)
**Goal:** Ship it for real users.

### 6.1 Infrastructure
- [ ] CDN for static assets (images, results.json)
- [ ] Error monitoring (Sentry or similar)
- [ ] Uptime monitoring + status page
- [ ] API rate limiting per tier
- [ ] GDPR compliance (data export, deletion)

### 6.2 Testing
- [ ] End-to-end browser tests (Playwright/Puppeteer)
- [ ] Data pipeline validation (Yahoo proxy, fallback chain)
- [ ] Payment flow testing (Stripe test mode → production)
- [ ] Performance benchmarks (Lighthouse scores)
- [ ] Cross-browser testing (Chrome, Firefox, Safari, mobile)

### 6.3 Launch
- [ ] Production Stripe keys deployed
- [ ] Vercel KV enabled for shared learning
- [ ] Custom domain + SSL
- [ ] SEO meta tags + Open Graph
- [ ] Launch landing page with social proof

---

## Continuous (Always Running)
- Hermes agents running research, code review, and QA automatically
- Skills updated after every successful pattern
- Trading edge research (new strategies, new timeframes)
- UI polish based on user feedback
- Performance monitoring and optimization

---

## Success Metrics
| Metric | Target |
|--------|--------|
| Lighthouse Performance | ≥90 |
| Time to First Signal | <3s |
| Backtest Statistical Power | ≥100 trades per market |
| Active Subscribers | 50+ by month 3 |
| Signal Accuracy (forward) | Track and publish |
| Mobile Usability | Fully functional ≤375px |
| Uptime | 99.5%+ |
