// Creates a Stripe Checkout Session (subscription) and returns its hosted URL.
// Use a Stripe TEST secret key (sk_test_...) to test the whole flow with fake
// cards — NO real money moves until you switch to a live key. See DEPLOY_PAYWALL.md.
//
//   POST /api/checkout   body { email }  →  { url }   (redirect the browser there)
//
// Env: STRIPE_SECRET_KEY, STRIPE_PRICE_ID (a recurring Price id). Missing → 503,
// and the frontend stays in local test mode.

const KEY = process.env.STRIPE_SECRET_KEY;
// Per-tier recurring Price ids. STRIPE_PRICE_PLUS = $20 plan, STRIPE_PRICE_PRO = $50
// plan. STRIPE_PRICE_ID stays supported as a fallback for a single-plan setup.
const PRICE_PLUS = process.env.STRIPE_PRICE_PLUS || process.env.STRIPE_PRICE_ID;
const PRICE_PRO = process.env.STRIPE_PRICE_PRO || process.env.STRIPE_PRICE_ID;

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });
  let b = req.body;
  if (typeof b === 'string') { try { b = JSON.parse(b); } catch { b = {}; } }
  b = b || {};
  const tier = String(b.tier) === '2' ? 2 : 1;
  const price = tier === 2 ? PRICE_PRO : PRICE_PLUS;
  if (!KEY || !price) return res.status(503).json({ error: 'Stripe not configured — see DEPLOY_PAYWALL.md' });
  const email = String(b.email || '').slice(0, 120);
  const origin = req.headers.origin || ('https://' + (req.headers.host || ''));

  const f = new URLSearchParams();
  f.set('mode', 'subscription');
  f.set('line_items[0][price]', price);
  f.set('line_items[0][quantity]', '1');
  f.set('metadata[tier]', String(tier));            // so /api/me can return the plan
  f.set('subscription_data[metadata][tier]', String(tier));
  f.set('success_url', origin + '/?pro=success&session_id={CHECKOUT_SESSION_ID}');
  f.set('cancel_url', origin + '/?pro=cancel');
  f.set('allow_promotion_codes', 'true');
  if (email) f.set('customer_email', email);

  try {
    const r = await fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: f,
    });
    const d = await r.json();
    if (!r.ok) return res.status(500).json({ error: (d.error && d.error.message) || 'stripe error' });
    return res.status(200).json({ url: d.url });
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
