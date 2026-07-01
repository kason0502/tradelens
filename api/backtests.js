// Shared saved-backtests store for STRATA (server-side, cross-device).
// Vercel KV / Upstash Redis over REST — same pattern as api/learn.js.
//
//   GET  /api/backtests  → { runs: [...] }   (newest first)
//   POST /api/backtests  → body { run: {...} }; prepends it → { ok, count }
//
// Requires the Vercel KV integration (sets KV_REST_API_URL + KV_REST_API_TOKEN).
// Without them the endpoint returns 503 and the app falls back to per-device
// localStorage. See DEPLOY_PAYWALL.md / DEPLOY_BACKEND.md.

const KV_URL = process.env.KV_REST_API_URL;
const KV_TOK = process.env.KV_REST_API_TOKEN;
const KEY = 'tlpro:backtests_v1';

async function kvGet() {
  const r = await fetch(`${KV_URL}/get/${KEY}`, { headers: { Authorization: `Bearer ${KV_TOK}` } });
  const j = await r.json();
  if (!j || j.result == null) return null;
  try { return typeof j.result === 'string' ? JSON.parse(j.result) : j.result; } catch { return null; }
}
async function kvSet(val) {
  await fetch(`${KV_URL}/set/${KEY}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOK}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(val),
  });
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (!KV_URL || !KV_TOK) return res.status(503).json({ error: 'shared store not configured' });

  try {
    let runs = (await kvGet()) || [];
    if (!Array.isArray(runs)) runs = [];
    if (req.method === 'POST') {
      let b = req.body;
      if (typeof b === 'string') { try { b = JSON.parse(b); } catch { b = {}; } }
      b = b || {};
      const run = b.run || b;
      if (run && run.m) {
        runs.unshift(run);
        if (runs.length > 200) runs.length = 200;
        await kvSet(runs);
      }
      return res.status(200).json({ ok: true, count: runs.length });
    }
    return res.status(200).json({ runs });
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
