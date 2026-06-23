# Deploy TradeLens Pro as a public website (your key, server-side)

Your Anthropic API key lives **on the server**, in an environment variable.
Visitors use the site; the server calls Claude. The key is never in the page,
so it can't be stolen from the browser. The included `/api/claude` proxy also
rate-limits requests so visitors can't drain your credit.

```
Visitor browser  ──►  /api/claude (your server, holds the key)  ──►  Anthropic
   (no key)                      (key in env var)                     (Claude)
```

---

## 0. Rotate your key first

If you ever pasted your key anywhere public (chat, screenshot, commit),
treat it as compromised:
**console.anthropic.com → API Keys → revoke the old key → create a new one.**
You'll paste the NEW key into your host's env settings (never into code).

---

## Option A — Vercel (recommended, free tier, ~10 min)

### Files in this folder
```
index.html        ← the whole app
api/claude.js     ← serverless proxy (holds the key server-side)
vercel.json       ← config
package.json
```

### Steps
1. Install the CLI and log in:
   ```
   npm i -g vercel
   vercel login
   ```
2. From inside this folder, run:
   ```
   vercel
   ```
   Accept the defaults. This creates a preview deployment.
3. Add your key as an environment variable (NOT in any file):
   ```
   vercel env add ANTHROPIC_API_KEY
   ```
   Paste your `sk-ant-...` key when prompted. Choose **Production** (and
   Preview/Development if you want `vercel dev` to work too).
   Optionally lock the origin down:
   ```
   vercel env add ALLOWED_ORIGIN
   ```
   e.g. `https://your-app.vercel.app`
4. Ship it:
   ```
   vercel --prod
   ```
5. Open the URL it prints. The site auto-detects the proxy — the “Connect AI”
   banner disappears and every ✨ AI feature works with **no key needed by
   visitors**. Done.

> Prefer the dashboard? Push this folder to a GitHub repo, click “Import
> Project” at vercel.com, and add `ANTHROPIC_API_KEY` under
> Settings → Environment Variables. Same result, no CLI.

---

## Option B — Cloudflare Pages + Pages Function

1. Rename `api/claude.js` to `functions/api/claude.js` and adapt the handler
   to Cloudflare's `onRequestPost({ request, env })` signature (the body is
   the same fetch to Anthropic; read the key from `env.ANTHROPIC_API_KEY`).
2. In the Cloudflare dashboard: Pages → your project → Settings → Environment
   variables → add `ANTHROPIC_API_KEY`.
3. Deploy. Same browser-never-sees-the-key guarantee.

(Ask and I'll generate the exact Cloudflare version of the function.)

---

## Option C — Netlify

1. Move `api/claude.js` to `netlify/functions/claude.js` and export a
   `handler(event)` instead of `(req,res)`.
2. netlify.toml: redirect `/api/claude` → `/.netlify/functions/claude`.
3. Site settings → Environment variables → add `ANTHROPIC_API_KEY`.

(Ask and I'll generate the exact Netlify version.)

---

## Local testing

```
vercel dev
```
Runs the proxy + site at http://localhost:3000 using the env var you set for
the Development environment. Without the proxy running, the app falls back to
the in-tab key field so you can still test with your own key locally.

---

## Cost & safety controls (already built in)

- **Rate limit:** `api/claude.js` caps requests per IP per minute
  (`MAX_PER_WINDOW`, default 20). Raise/lower it to taste.
- **Token cap:** server clamps `max_tokens` to ≤1500 and trims long prompts.
- **Origin lock:** set `ALLOWED_ORIGIN` to your domain so other sites can't
  call your proxy.
- **Monitor spend:** watch usage at console.anthropic.com and set a billing
  budget/alert. Each call is a fraction of a cent, but a public URL means
  strangers can trigger calls — the rate limit + origin lock keep that sane.
- For a real public launch, consider adding auth (e.g. a login or a simple
  shared password) so only your users can hit the proxy.

---

## What the app does once AI is connected

- Dashboard: “✨ AI deep-read” of any ticker’s direction
- AI Chat: real Claude mentoring with your live dashboard context
- Strategy Lab: animated strategy walkthroughs + “find this setup live”
- Backtest: practice trades with strategy application
- My Performance: AI coach reviews your track record
- Sidebar: “✨ summarize today” market digest

All of it is **educational, not financial advice.**
