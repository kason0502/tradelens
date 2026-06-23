// api/claude.js — server-side proxy. The API key NEVER reaches the browser.
// Runs on Vercel/Netlify (Node serverless). Reads the key from an env variable.

// --- simple in-memory rate limit (per server instance) ---
const HITS = new Map();
const WINDOW_MS = 60_000;   // 1 minute
const MAX_PER_WINDOW = 20;  // max requests per IP per minute — tune to taste

function rateLimited(ip) {
  const now = Date.now();
  const arr = (HITS.get(ip) || []).filter(t => now - t < WINDOW_MS);
  arr.push(now);
  HITS.set(ip, arr);
  return arr.length > MAX_PER_WINDOW;
}

export default async function handler(req, res) {
  // CORS (lock origin down to your own domain in production)
  res.setHeader('Access-Control-Allow-Origin', process.env.ALLOWED_ORIGIN || '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });

  const ip = (req.headers['x-forwarded-for'] || 'anon').split(',')[0].trim();
  if (rateLimited(ip)) return res.status(429).json({ error: 'Rate limit — slow down a moment.' });

  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return res.status(500).json({ error: 'Server missing ANTHROPIC_API_KEY' });

  try {
    const { system, prompt, max_tokens } = req.body || {};
    if (!prompt) return res.status(400).json({ error: 'Missing prompt' });

    // Guard against abuse: cap tokens and prompt length.
    const cappedTokens = Math.min(Math.max(parseInt(max_tokens || 800, 10), 16), 1500);
    const safePrompt = String(prompt).slice(0, 6000);
    const safeSystem = String(system || '').slice(0, 4000);

    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': key,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6',
        max_tokens: cappedTokens,
        system: safeSystem,
        messages: [{ role: 'user', content: safePrompt }],
      }),
    });

    const data = await r.json();
    if (!r.ok) return res.status(r.status).json({ error: data?.error?.message || 'Claude error' });

    const text = (data.content || []).map(b => (b.type === 'text' ? b.text : '')).join('').trim();
    return res.status(200).json({ text });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
