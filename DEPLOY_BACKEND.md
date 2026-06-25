# Enabling shared (cross-user) AI learning

By default the AI's learning is saved per-browser (localStorage). To pool it
across **everyone** who uses the site, deploy the included serverless endpoint
`api/learn.js` with a key-value store. ~5 minutes on Vercel, free tier.

## What it does
- `api/learn.js` is a Vercel serverless function.
  - `GET /api/learn` → returns the pooled model (`strats`, `trials`, `wins`, `log`).
  - `POST /api/learn` → merges one self-test result into the pool.
- The app probes `/api/learn` on load (`syncSharedMemory`). If it answers, the
  AI Lab switches to **global** learning: every self-test anyone runs updates the
  shared model, and that pooled confidence drives the dashboard's strategy pick
  and entry/stop/targets for all users. If it's not there, the app silently falls
  back to per-device localStorage — nothing breaks.

## Setup (Vercel + KV)
1. Push this repo to GitHub and import it into **Vercel** (Framework preset:
   *Other*; no build command). `index.html` serves at `/`, and `api/learn.js`
   is auto-detected as a serverless function.
2. In the Vercel project → **Storage** → **Create Database** → **KV** (Upstash
   Redis). Connect it to the project. Vercel injects these env vars
   automatically: `KV_REST_API_URL` and `KV_REST_API_TOKEN`.
3. **Redeploy** (Vercel does this when you connect the store). Done — visit the
   site, open **AI Lab**, and it should say *"pooled across everyone."*

No env vars / no KV connected → the endpoint returns `503` and the app stays in
local mode. So it's safe to deploy before you set up the store.

## Notes / limits
- The store key is `tlpro:shared_memory_v1` (a single JSON blob). Fine for this
  scale; for very high traffic you'd shard or use atomic counters.
- The endpoint is open (no auth) and rate-limited only by Vercel. For a public
  launch, add a simple write throttle or a shared secret header if you see abuse.
- This is the same pattern you'd use to later add a real news feed or accounts.
