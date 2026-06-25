# TradeLens Pro — Project Context

> Living doc. Update at the end of any session that changes scope, status, or direction.
> Last updated: 2026-06-25 (session 5)

## What this is
TradeLens Pro is a **single-file** web app (`index.html`, no build step, no framework) that combines:
1. A **premium marketing landing page** (shown first), and
2. A **trading-analysis dashboard** ("the app") behind a *Launch App* button.

It pulls **real market data**, derives structure-based trade plans (entry / stop / targets), embeds professional charts, and offers AI analysis. Educational tool — not financial advice.

## Who it's for
Serious independent retail traders. Voice/feel: precise, institutional, trustworthy, data-driven — not flashy marketing.

## Current state (2026-06-25, session 5)
- Fully working single page. Landing + app both live.
- Visual language: **Bloomberg/terminal minimal** — pure black (`#050505`), dark-gray surfaces, white type, ONE accent (`#2f81f7`); no big gradients/glowing blobs. (Evolved from an earlier blue/cyan/purple glass look, and before that a gold theme.) Landing hero is a realistic terminal **bento** (candles/watchlist/volume profile/AI probability/etc.).
- **The dashboard (post-launch) is now an AI Copilot** — a conversation. Ask in plain language ("is NVDA a buy?") → an answer card with a verdict, an embedded **TradingView** chart, and entry/stop/target shown **as ticks** up/down from current price (1 tick = $0.01; price as subtitle), R/R in ticks, rationale, and follow-up chips. The dashboard went through several rebuilds this session (terminal workspace → Focus → Copilot); Copilot is current. Legacy `renderDash`/`load` are disabled (guarded on missing `#main`).
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
