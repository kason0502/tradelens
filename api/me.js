// Verify a completed Stripe Checkout Session (from the success redirect) →
// is this an active/paid subscriber? The frontend calls this once on return
// from Stripe and caches the result locally to unlock access.
//
//   GET /api/me?session_id=cs_test_...  →  { active, email }
//
// Env: STRIPE_SECRET_KEY (same key as checkout). Missing → 503.

const KEY = process.env.STRIPE_SECRET_KEY;

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (!KEY) return res.status(503).json({ active: false, error: 'Stripe not configured' });
  const sid = (req.query && req.query.session_id) || '';
  if (!sid) return res.status(400).json({ active: false });
  try {
    const r = await fetch('https://api.stripe.com/v1/checkout/sessions/' + encodeURIComponent(sid), {
      headers: { Authorization: 'Bearer ' + KEY },
    });
    const d = await r.json();
    if (!r.ok) return res.status(500).json({ active: false });
    const active = d.payment_status === 'paid' || d.status === 'complete';
    const email = d.customer_email || (d.customer_details && d.customer_details.email) || '';
    return res.status(200).json({ active, email });
  } catch (e) {
    return res.status(500).json({ active: false });
  }
};
