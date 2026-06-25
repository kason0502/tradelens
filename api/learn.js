// Shared AI-learning store for TradeLens.
// A Vercel serverless function backed by Vercel KV / Upstash Redis (REST).
//
//   GET  /api/learn   → returns the pooled memory {strats, trials, wins, log}
//   POST /api/learn   → body {key, win, pnl, tk, name, dir}; merges one
//                       self-test result into the pooled memory, returns it
//
// Requires the Vercel KV (Upstash) integration — it sets KV_REST_API_URL and
// KV_REST_API_TOKEN automatically. Without them the endpoint returns 503 and
// the app falls back to per-device localStorage learning. See DEPLOY_BACKEND.md.

const KV_URL = process.env.KV_REST_API_URL;
const KV_TOK = process.env.KV_REST_API_TOKEN;
const KEY = 'tlpro:shared_memory_v1';

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
function blank() { return { strats: {}, trials: 0, wins: 0, log: [] }; }
function s(v, n) { return String(v == null ? '' : v).slice(0, n); }

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (!KV_URL || !KV_TOK) return res.status(503).json({ error: 'shared store not configured' });

  try {
    let mem = (await kvGet()) || blank();
    if (req.method === 'POST') {
      let b = req.body;
      if (typeof b === 'string') { try { b = JSON.parse(b); } catch { b = {}; } }
      b = b || {};
      const k = s(b.key, 40);
      if (k) {
        if (!mem.strats[k]) mem.strats[k] = { wins: 0, losses: 0, pnl: 0 };
        if (b.win) mem.strats[k].wins++; else mem.strats[k].losses++;
        mem.strats[k].pnl += Number(b.pnl) || 0;
        mem.trials++; if (b.win) mem.wins++;
        mem.log.unshift({
          tk: s(b.tk, 6), name: s(b.name, 40),
          dir: b.dir === 'short' ? 'short' : 'long',
          win: !!b.win, pnl: Math.round((Number(b.pnl) || 0) * 10) / 10, when: Date.now(),
        });
        if (mem.log.length > 60) mem.log.length = 60;
        await kvSet(mem);
      }
    }
    return res.status(200).json(mem);
  } catch (e) {
    return res.status(500).json({ error: String(e && e.message || e) });
  }
};
