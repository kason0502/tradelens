# TradeLens Pro — Changelog

> Living doc. Add an entry (newest first) each session that ships changes.
> Dates are YYYY-MM-DD. Mirrors git history; group by session/day.

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
