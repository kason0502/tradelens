# STRATA — Project Context

> Living doc. Update at the end of any session that changes scope, status, or direction.
> Last updated: 2026-06-26 (session 15). Dashboard ask bar is now ticker-only; AI self-learning runs automatically in the background (idle trickle + Pause/Resume in AI Lab). Earlier: renamed TradeLens Pro → STRATA; hosted on GitHub→Vercel with a server-side data + AI proxy (see "Server, data & hosting" below).

## What this is
STRATA (formerly TradeLens Pro) is a **single-file** web app (`index.html`, no build step, no framework) that combines:
1. A **premium marketing landing page** (shown first), and
2. A **trading-analysis dashboard** ("the app") behind a *Launch App* button.

It pulls **real market data**, derives structure-based trade plans (entry / stop / targets), embeds professional charts, and offers AI analysis. Educational tool — not financial advice.

## Who it's for
Serious independent retail traders. Voice/feel: precise, institutional, trustworthy, data-driven — not flashy marketing.

## Current state (2026-06-26, session 13)
- **Reliable market data via a server-side proxy** (`/api/yf?url=…`): fetches Yahoo/Stooq server-side so there's no browser-CORS and no public-proxy rate-limiting. Two implementations: `.claude/serve.ps1` handles it **locally** (pure PowerShell, no Node), and `api/yf.js` is the **Vercel serverless** equivalent for a public deploy. The client (`raceAttempts`) calls `/api/yf` first and only falls back to public CORS proxies if absent. Background pollers throttled + stand down during a user lookup (`bgIdle`, `window.__userFetch`). → To host it for everyone, see **`DEPLOY.md`** (push to GitHub → Vercel).
- **Brand = the user's own images** (transparent PNGs): `logo.png` (low-poly bull-head, in the nav — no box), `bull.png`/`bear.png` (low-poly mascots in the dashboard AI-read panel, swapped by sentiment with a green/red glow).
- **Sentiment-reactive theme:** the whole UI flips **red when the read is bearish** (`setMood`, `--ac-rgb`, `body.bearish`, `FX_MOOD`) and green otherwise.
- Dashboard is loaded with info: index strip (S&P/Nasdaq/Dow/VIX), 9 indicator tiles (RSI/MACD/MA-cross/ATR/…), an **options Greeks** panel (Black–Scholes delta/gamma/theta/vega), a "What the AI sees" checklist, and a **persistent watchlist** (add/remove/live).
- **Accent is emerald green** (`#22c55e`, brand + bullish; was blue) to match a reference dashboard the user supplied. The nav is a **premium animated floating glass rail** (gliding active pill, magnetic hover, cursor glow, spring icons — `initPremiumNav`). The landing is opaque again (no more app bleed-through); the animated `#fxCanvas` background now lives behind the app only.
- **Branded STRATA.** App chrome moved to a **left sidebar** (`.appnav`, grouped Terminal/Research/Assistant) — the top nav bar is gone; the top "✨ AI" button is gone (connect-AI lives in the sidebar footer). A streaming **movers banner** (`.appbar`) sits at the top of the app, and a new **High Volume** tab (`#tab-movers`) lists the day's most active / biggest movers from real data. Pro Traders gained a desk-consensus panel; Backtest gained a session scoreboard + "Surprise me".
- Fully working single page. Landing + app both live.
- Visual language: **Bloomberg/terminal minimal** — pure black (`#050505`), dark-gray surfaces, white type, ONE accent (`#2f81f7`); no gradients/glowing blobs (the landing's residual blue/cyan/purple gradients + glow were flattened in session 6). Landing hero is a realistic terminal **bento** (candles/watchlist/volume profile/AI probability/etc.).
- **The dashboard (post-launch) is a real panel terminal** (rebuilt from the session-5 AI Copilot chat). A slim **ask bar** (search + horizon + ticker chips) drives `renderDash`, which fills fixed panels: ticker header (live price + conviction), wide **TradingView** chart, a single Trade Plan (entry/stop/target — price primary, tick-distance secondary, R:R), an AI-read conviction panel, a key-metrics strip, and a live-signals panel. `loadTicker` (News/Screener/etc.) routes here. The old `.cp-*` chat and the older legacy `renderDash`/`.wk` workspace are gone/disabled.
- **Shared cross-user learning** exists: `api/learn.js` (Vercel serverless + KV) pools the AI's self-test learning across all users; falls back to per-device localStorage when not deployed (`DEPLOY_BACKEND.md`).
- Other tabs: Screener, News (sample feed), Pro Traders, Backtest, Performance, AI Lab (persistent learning), AI Chat, Alerts, Feedback — still on older `.card` styling.
- Repo is git-tracked (`main`) and **on GitHub at `kason0502/tradelens`**, deployed via Vercel (`index.html` homepage, `api/yf.js`/`api/claude.js`/`api/learn.js` serverless, brand PNGs tracked, `.vercelignore` excludes `.claude` + `*.md`). See the "Server, data & hosting" section + **`DEPLOY.md`**.

## How to run / preview
- No Node/Python on this machine. Use the bundled PowerShell server (**which is also the `/api/yf` data proxy** — that's what makes data load reliably):
  - Preview config `tradelens` → `.claude/serve.ps1` serves the repo root at `http://localhost:8777`.
  - In Claude Code: `preview_start` with name `tradelens`. **Restart the preview after editing `serve.ps1`.**
  - Always open via `http://localhost:8777` (through the server) — opening `index.html` as a bare file has no proxy and falls back to flaky public proxies.
- **To host it for everyone (so the server runs in the cloud, not just locally):** see `DEPLOY.md` (GitHub → Vercel; `api/yf.js` runs the proxy server-side for all visitors).
- ⚠️ The **screenshot tool cannot capture this page** (live TradingView iframe + offscreen tab pauses CSS animations → timeout). Verify with `preview_eval` / computed styles / console logs instead, and ask the user to view in a real browser.

## Server, data & hosting (how the server works + GitHub/Vercel)

### Why a server at all
Browsers can't fetch stock data straight from Yahoo (CORS blocks it). The app used to bounce requests through flaky free public CORS proxies → "nothing loads". The fix is a **server-side proxy**: the *server* fetches Yahoo (servers aren't bound by CORS), so data loads fast and reliably. There are two server functions:
- **`/api/yf?url=…`** — market-data proxy (Yahoo/Stooq). The reason stocks load.
- **`/api/claude`** — Claude (Anthropic) proxy. Lets the owner's key power AI for every visitor.

### Same code, two homes
- **Local dev:** `.claude/serve.ps1` is the preview server AND the `/api/yf` proxy (pure PowerShell `Invoke-WebRequest`, no Node). `/api/claude` does NOT exist locally (PowerShell only does `/api/yf`), so locally AI is bring-your-own-key. **Restart the preview after editing `serve.ps1`.** Always open via `http://localhost:8777`.
- **Deployed (Vercel):** `api/yf.js` and `api/claude.js` are serverless functions that do the same thing in the cloud for **every visitor**. `vercel.json` gives `api/claude.js` a 30s timeout.
- **Client fallback chain** (`raceAttempts` in `index.html`): try `/api/yf` first (`_yfProxyOK`); if absent (bare file / plain static host), race the public CORS proxies in parallel. Background pollers throttle + stand down during a user lookup (`bgIdle`, `window.__userFetch`).

### GitHub + Vercel
- **Repo:** `https://github.com/kason0502/tradelens` (`origin/main`). Connected via `git remote add origin …`.
- **History note:** the GitHub repo had been updated by *manual file uploads* ("Add files via upload"), so it diverged from the local git history and was **missing files** (the PNGs, `api/yf.js`, `api/learn.js`). Reconciled in session 14 by **merging** `origin/main` into the complete local project with `-X ours` (keep local files) + `--allow-unrelated-histories`, then a normal push. Local and GitHub are now in sync.
- **Deploy flow:** push to GitHub → **Vercel auto-redeploys** in ~30s. `index.html` at root is the homepage; `api/*.js` become functions. `.vercelignore` keeps `.claude` + `*.md` out of the build.
- **AI for everyone:** the owner set **`ANTHROPIC_API_KEY`** (encrypted) in Vercel env vars; once `api/claude.js` is deployed, the app probes `/api/claude` on load and gives all visitors AI with no key prompt (this bills the owner's key). Optional: Vercel KV for pooled learning (`api/learn.js`, see `DEPLOY_BACKEND.md`).
- **Pushing updates:** normal `git add -A && git commit -m "…" && git push` (first time needed `git push --set-upstream origin main` to set tracking). Full step-by-step in **`DEPLOY.md`**.

## Key product decisions
- **Real data only** — never simulate/fake prices. If a feed fails, show an honest error.
- **One accent (`#2f81f7`), used sparingly.** Green/red are reserved for up/down (P&L) only. No big gradients or glowing blobs.
- **AI is optional.** Works on a built-in rule engine without a key; richer with a Claude API key. Self-test learning is **pooled across users** when the backend is deployed.
- Levels come from **real chart structure + ATR**, never arbitrary percentages — and in the Copilot they're shown **as ticks** (distance from current price), per user preference, not absolute prices.
- Charts in the Copilot are the **real TradingView** widget (user preference over the custom canvas).

## Known constraints / gotchas
- **Data reliability is solved by the `/api/yf` proxy** (local PowerShell or deployed Vercel). The public CORS proxies are now only a *fallback* (used when the page is opened as a bare file with no server) — flaky/rate-limited. `raceAttempts` fires proxies in parallel (first valid wins), so even the fallback fails fast instead of hanging.
- TradingView widget needs internet; shows a fallback message pointing to "AI Levels" if blocked.
- `/api/claude` exists (`api/claude.js`) but only runs when **deployed** (Vercel reads `ANTHROPIC_API_KEY`); the **local** PowerShell server doesn't run it, so locally AI is bring-your-own-key.
- Commits warn `LF will be replaced by CRLF` — harmless (Windows).

## The doc set (keep all current)
- `PROJECT_CONTEXT.md` — this file: what/why/status.
- `ARCHITECTURE.md` — code structure, key functions, data flow.
- `DESIGN_SYSTEM.md` — tokens, colors, components, conventions.
- `TODO.md` — prioritized outstanding work.
- `CHANGELOG.md` — notable changes, newest first.
