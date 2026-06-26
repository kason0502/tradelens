# STRATA — Host it so the server runs for everyone

Locally, the market-data proxy (`/api/yf`) runs from `.claude/serve.ps1` on **your
machine only**. To make that server run **for everyone who visits** — reachable from
any phone or computer, no PC of yours needed — host the project on **Vercel** (free).
Vercel runs `api/yf.js` (and `api/learn.js`) as cloud functions, so the same reliable
data path works for every visitor automatically.

You do **not** need Node or Python for this. The work happens in your browser (GitHub)
and on Vercel's servers. The app already calls `/api/yf` first, so once it's hosted,
data just loads — nothing else to wire up.

## One-time setup (~5 minutes)

1. **GitHub account** — free at github.com if you don't already have one.

2. **Create an empty repo:** github.com → *New repository* → name it `strata`
   (Public or Private, your call) → *Create*. Don't add a README/.gitignore —
   the project already has them.

3. **Push this project to it.** In a terminal in the project folder:
   ```
   git remote add origin https://github.com/<your-username>/strata.git
   git push -u origin main
   ```
   The first push asks you to sign in to GitHub — a browser window opens, approve it.

4. **Connect Vercel:**
   - vercel.com → *Sign Up* → **Continue with GitHub** (free "Hobby" plan).
   - *Add New… → Project* → pick your `strata` repo → **Deploy**.
   - Leave all settings default — it auto-detects the static page + the `api/` functions.

5. **Done.** Vercel gives you a URL like `https://strata-xxxx.vercel.app`. Open it on
   any device — stock data loads server-side via `/api/yf`, reliably, for anyone.
   (Add a custom domain later in the Vercel dashboard if you want.)

## Pushing updates to the live site
Whenever you change something and want it live:
```
git add -A
git commit -m "your message"
git push
```
Vercel redeploys automatically in a few seconds.

## Optional extras
- **Pool the AI's self-test learning across all users:** add Vercel's **KV (Upstash)**
  integration from the Vercel dashboard — it sets the env vars `api/learn.js` reads.
  Without it, learning is per-device (localStorage). See `DEPLOY_BACKEND.md`.
- **Claude AI features:** each visitor still pastes their own Anthropic key (the
  ✨ Connect AI button). A single shared key would bill you for everyone, so it's off
  by default.

## What deploys where
| File | Role |
|---|---|
| `index.html` | the entire app (served as the homepage) |
| `api/yf.js` | **server-side market-data proxy** — makes stock data load reliably for all visitors |
| `api/learn.js` | shared AI-learning store (optional; needs KV) |
| `logo.png` / `bull.png` / `bear.png` | brand + mascots |
| `.claude/serve.ps1` | the **local** dev server + proxy — NOT deployed |
| `.vercelignore` | keeps `.claude` and the `*.md` docs out of the deployed build |
