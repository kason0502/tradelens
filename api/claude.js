// Server-side Claude (Anthropic) proxy for STRATA.
//
//   POST /api/claude   body { system, prompt, max_tokens }   → { text }
//
// The Anthropic API key lives in a server env var (ANTHROPIC_API_KEY), so when the
// app is deployed every visitor gets the AI features WITHOUT pasting their own key —
// the app probes this endpoint on load and flips into "server proxy" mode.
//
//   ⚠️  This bills YOUR Anthropic key for every visitor's AI request. That's the
//       trade-off of a shared proxy. Leave the env var unset to keep AI as
//       bring-your-own-key (the endpoint then returns 503 and the app falls back).
//
// Set in Vercel → Project → Settings → Environment Variables:
//   ANTHROPIC_API_KEY = sk-ant-...      (required)
//   ANTHROPIC_MODEL   = claude-sonnet-4-6   (optional override)

const KEY = process.env.ANTHROPIC_API_KEY || process.env.CLAUDE_API_KEY;
const MODEL = process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-6';

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });
  if (!KEY) return res.status(503).json({ error: 'AI not configured (set ANTHROPIC_API_KEY in Vercel)' });

  try {
    let b = req.body;
    if (typeof b === 'string') { try { b = JSON.parse(b); } catch { b = {}; } }
    b = b || {};

    const prompt = String(b.prompt || '').slice(0, 12000);
    const system = String(b.system || '').slice(0, 8000);
    let maxTokens = parseInt(b.max_tokens, 10) || 1024;
    if (maxTokens > 2048) maxTokens = 2048;
    if (!prompt) return res.status(400).json({ error: 'missing prompt' });

    // The app pings with prompt:"ping" on load just to detect the proxy — answer
    // that cheaply so a page load never costs an Anthropic call.
    if (prompt === 'ping') return res.status(200).json({ text: 'pong' });

    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: maxTokens,
        system: system || undefined,
        messages: [{ role: 'user', content: prompt }],
      }),
    });
    const data = await r.json();
    if (!r.ok) {
      return res.status(r.status).json({ error: (data && data.error && data.error.message) || ('Anthropic ' + r.status) });
    }
    const text = (data.content || []).map(c => c.text || '').join('').trim();
    return res.status(200).json({ text });
  } catch (e) {
    return res.status(502).json({ error: String((e && e.message) || e) });
  }
};
