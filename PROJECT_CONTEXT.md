# TradeLens Pro — Project Context

> Living doc. Update at the end of any session that changes scope, status, or direction.
> Last updated: 2026-06-25

## What this is
TradeLens Pro is a **single-file** web app (`index.html`, no build step, no framework) that combines:
1. A **premium marketing landing page** (shown first), and
2. A **trading-analysis dashboard** ("the app") behind a *Launch App* button.

It pulls **real market data**, derives structure-based trade plans (entry / stop / targets), embeds professional charts, and offers AI analysis. Educational tool — not financial advice.

## Who it's for
Serious independent retail traders. Voice/feel: precise, institutional, trustworthy, data-driven — not flashy marketing.

## Current state (2026-06-25)
- Fully working single page. Landing + dashboard both live.
- Visual language: **premium fintech glass** — charcoal + electric blue/cyan/purple. Landing is bespoke/editorial; the app shell has been aligned to it.
- Main dashboard chart = embedded **TradingView** widget (with an "AI Levels" custom-canvas toggle).
- Repo is git-tracked (`main`), **no remote yet**. Deploy-ready for Vercel (`index.html` at root, `.vercelignore` excludes `.claude`).

## How to run / preview
- No Node/Python on this machine. Use the bundled static server:
  - Preview config `tradelens` → `.claude/serve.ps1` serves the repo root at `http://localhost:8777`.
  - In Claude Code: `preview_start` with name `tradelens`.
- ⚠️ The **screenshot tool cannot capture this page** (live TradingView iframe + offscreen tab pauses CSS animations → timeout). Verify with `preview_eval` / computed styles / console logs instead, and ask the user to view in a real browser.

## Key product decisions
- **Real data only** — never simulate/fake prices. If a feed fails, show an honest error.
- **Green/red are reserved for up/down (P&L) only.** Brand/UI accent is electric blue. (Earlier a gold "pro-terminal" theme existed; it was replaced.)
- **AI is optional.** Works on a built-in rule engine without a key; richer with a Claude API key.
- Levels come from **real chart structure + ATR**, never arbitrary percentages.

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
