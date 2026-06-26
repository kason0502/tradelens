# STRATA — Project Context

> Living doc. Update at the end of any session that changes scope, status, or direction.
> Last updated: 2026-06-26 (session 7). **The product was renamed TradeLens Pro → STRATA** ("Structure Terminal").

## What this is
STRATA (formerly TradeLens Pro) is a **single-file** web app (`index.html`, no build step, no framework) that combines:
1. A **premium marketing landing page** (shown first), and
2. A **trading-analysis dashboard** ("the app") behind a *Launch App* button.

It pulls **real market data**, derives structure-based trade plans (entry / stop / targets), embeds professional charts, and offers AI analysis. Educational tool — not financial advice.

## Who it's for
Serious independent retail traders. Voice/feel: precise, institutional, trustworthy, data-driven — not flashy marketing.

## Current state (2026-06-26, session 8)
- **Accent is emerald green** (`#22c55e`, brand + bullish; was blue) to match a reference dashboard the user supplied. The nav is a **premium animated floating glass rail** (gliding active pill, magnetic hover, cursor glow, spring icons — `initPremiumNav`). The landing is opaque again (no more app bleed-through); the animated `#fxCanvas` background now lives behind the app only.
- **Branded STRATA.** App chrome moved to a **left sidebar** (`.appnav`, grouped Terminal/Research/Assistant) — the top nav bar is gone; the top "✨ AI" button is gone (connect-AI lives in the sidebar footer). A streaming **movers banner** (`.appbar`) sits at the top of the app, and a new **High Volume** tab (`#tab-movers`) lists the day's most active / biggest movers from real data. Pro Traders gained a desk-consensus panel; Backtest gained a session scoreboard + "Surprise me".
- Fully working single page. Landing + app both live.
- Visual language: **Bloomberg/terminal minimal** — pure black (`#050505`), dark-gray surfaces, white type, ONE accent (`#2f81f7`); no gradients/glowing blobs (the landing's residual blue/cyan/purple gradients + glow were flattened in session 6). Landing hero is a realistic terminal **bento** (candles/watchlist/volume profile/AI probability/etc.).
- **The dashboard (post-launch) is a real panel terminal** (rebuilt from the session-5 AI Copilot chat). A slim **ask bar** (search + horizon + ticker chips) drives `renderDash`, which fills fixed panels: ticker header (live price + conviction), wide **TradingView** chart, a single Trade Plan (entry/stop/target — price primary, tick-distance secondary, R:R), an AI-read conviction panel, a key-metrics strip, and a live-signals panel. `loadTicker` (News/Screener/etc.) routes here. The old `.cp-*` chat and the older legacy `renderDash`/`.wk` workspace are gone/disabled.
- **Shared cross-user learning** exists: `api/learn.js` (Vercel serverless + KV) pools the AI's self-test learning across all users; falls back to per-device localStorage when not deployed (`DEPLOY_BACKEND.md`).
- Other tabs: Screener, News (sample feed), Pro Traders, Backtest, Performance, AI Lab (persistent learning), AI Chat, Alerts, Feedback — still on older `.card` styling.
- Repo is git-tracked (`main`), **no remote yet**. Deploy-ready for Vercel (`index.html` at root, `api/` serverless, `.vercelignore` excludes `.claude` + `*.md`).

## How to run / preview
- No Node/Python on this machine. Use the bundled static server:
  - Preview config `tradelens` → `.claude/serve.ps1` serves the repo root at `http://localhost:8777`.
  - In Claude Code: `preview_start` with name `tradelens`.
- ⚠️ The **screenshot tool cannot capture this page** (live TradingView iframe + offscreen tab pauses CSS animations → timeout). Verify with `preview_eval` / computed styles / console logs instead, and ask the user to view in a real browser.

## Key product decisions
- **Real data only** — never simulate/fake prices. If a feed fails, show an honest error.
- **One accent (`#2f81f7`), used sparingly.** Green/red are reserved for up/down (P&L) only. No big gradients or glowing blobs.
- **AI is optional.** Works on a built-in rule engine without a key; richer with a Claude API key. Self-test learning is **pooled across users** when the backend is deployed.
- Levels come from **real chart structure + ATR**, never arbitrary percentages — and in the Copilot they're shown **as ticks** (distance from current price), per user preference, not absolute prices.
- Charts in the Copilot are the **real TradingView** widget (user preference over the custom canvas).

## Known constraints / gotchas
- Free CORS proxies (corsproxy.io, allorigins, codetabs, etc.) are flaky / rate-limited; failures are silent-with-retry by design.
- TradingView widget needs internet; shows a fallback message pointing to "AI Levels" if blocked.
- No `/api/claude` server proxy exists in the repo, so on a public deploy each visitor must paste their own Anthropic key for AI features.
- Commits warn `LF will be replaced by CRLF` — harmless (Windows).

## The doc set (keep all current)
- `PROJECT_CONTEXT.md` — this file: what/why/status.
- `ARCHITECTURE.md` — code structure, key functions, data flow.
- `DESIGN_SYSTEM.md` — tokens, colors, components, conventions.
- `TODO.md` — prioritized outstanding work.
- `CHANGELOG.md` — notable changes, newest first.
