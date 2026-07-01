# STRATA Pro — paywall, accounts & server storage setup

STRATA now has a **Pro paywall** in front of "Launch App", plus **server-side
saved backtests**. Both work in two modes:

- **Test mode (default, on right now):** no backend, no money. You can exercise
  the entire paid flow immediately.
- **Live mode:** real Stripe Checkout (test *or* live keys) + Vercel KV storage.

Nothing here ever charges a real card on its own. Even "live" starts with Stripe
**test** keys, where the only cards that work are fake test cards.

---

## 1. Test it right now (no setup, no money)

`index.html` ships with `PAY.testMode = true`. On the landing page:

1. Click **Launch App** → the **STRATA PRO** paywall appears.
2. Either:
   - type any email and click **Subscribe** → a *simulated* subscription unlocks
     the app (30-day local pass), **or**
   - enter the code **`STRATA-TEST`** in the "Access / test code" box → **Unlock**.
3. You're in. A **PRO** chip shows top-right; **sign out** clears it and the gate
   returns.

This proves the whole gated experience without a backend or a cent. Saved
backtests persist in your browser (localStorage) in this mode.

---

## 2. Go live with real Stripe test checkout (still fake money)

This uses Stripe's **test mode** — a real hosted checkout page where only test
cards work (e.g. `4242 4242 4242 4242`, any future expiry, any CVC/ZIP). No real
charges.

### a. Create the Stripe product (2 min)
1. Make a free account at <https://stripe.com> and stay in **Test mode** (toggle
   top-right of the Stripe dashboard).
2. **Products → Add product** → name it "STRATA Pro", add a **recurring** price
   (e.g. $29 / month). Save.
3. Copy the **Price ID** (looks like `price_1AbC…`).
4. **Developers → API keys** → copy the **Secret key** (`sk_test_…`).

### b. Add the keys to Vercel (you do this — never paste keys into chat)
In your Vercel project → **Settings → Environment Variables**, add:

| Name                | Value                    |
|---------------------|--------------------------|
| `STRIPE_SECRET_KEY` | `sk_test_…` (your test secret key) |
| `STRIPE_PRICE_ID`   | `price_…` (the recurring price)    |

Redeploy (Vercel does this automatically on the next push, or hit **Redeploy**).

### c. Flip the app to live mode
In `index.html`, find the `PAY` config near `launchApp` and set:

```js
const PAY = { testMode:false, price:'$29', … };
```

Now **Subscribe** sends the user to Stripe's hosted checkout. Pay with the test
card `4242 4242 4242 4242`. On success Stripe returns to
`/?pro=success&session_id=…`; the app calls `/api/me` to confirm the session and
unlocks Pro.

### d. Actually go live (real money) — only when ready
Swap the test keys for **live** keys (`sk_live_…` + a live `price_…`) in Vercel.
That's the only change. **Do this consciously — live keys charge real cards.**

---

## 3. Server-side saved backtests (shared across devices)

Enable **Vercel KV** (Upstash) — same integration `api/learn.js` already uses:

1. Vercel project → **Storage → Create → KV** (Upstash Redis). Connect it to the
   project. Vercel injects `KV_REST_API_URL` and `KV_REST_API_TOKEN` automatically.
2. Redeploy.

Now `api/backtests.js` persists every run server-side. The Backtester tab shows
"synced across your devices"; runs appear on any device/browser. Until KV exists,
`/api/backtests` returns 503 and the app silently falls back to localStorage.

---

## Files
- `api/checkout.js` — creates the Stripe Checkout Session (subscription).
- `api/me.js` — verifies the returned session → active subscriber?
- `api/backtests.js` — KV-backed shared backtest store (GET/POST).
- `index.html` — `PAY` config + paywall modal + gate on `launchApp`.

## Honest limits of v1
- Access is **remembered per browser** after a successful subscription (cached
  locally after `/api/me` confirms). A full **multi-device login** (accounts +
  passwords + sessions) is a further step — say the word and it's a follow-up:
  add `api/auth.js` + a users table in KV, and check the session on load instead
  of a local flag.
- Recurring **renewal/cancellation** is not yet reconciled by a webhook; add
  `api/stripe-webhook.js` (listening for `customer.subscription.*`) to keep
  status perfectly in sync for production billing.
