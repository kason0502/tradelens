// Server-side market-data proxy for STRATA.
//
//   GET /api/yf?url=<url-encoded Yahoo/Stooq URL>  → returns that source's response
//
// This runs SERVER-SIDE on Vercel, so there is no browser CORS restriction and no
// per-user rate limiting — which is what makes stock data load reliably once the
// app is deployed. When you run the bare index.html locally there is no serverless
// runtime, so this 404s and the client falls back to the public CORS proxies
// (flaky). In short: deploy to Vercel and data loads reliably. See DEPLOY.md.

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Cache-Control', 's-maxage=8, stale-while-revalidate=24');
  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    let url = req.query && req.query.url;
    if (Array.isArray(url)) url = url[0];
    if (!url) return res.status(400).json({ error: 'missing url param' });
    url = decodeURIComponent(url);

    // Only allow the market-data hosts the app uses — don't be an open proxy.
    if (!/^https:\/\/(query[12]\.finance\.yahoo\.com|stooq\.com)\//i.test(url)) {
      return res.status(400).json({ error: 'host not allowed' });
    }

    const upstream = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; STRATA/1.0)',
        'Accept': 'application/json,text/csv,text/plain,*/*',
      },
    });
    const body = await upstream.text();
    res.setHeader('Content-Type', upstream.headers.get('content-type') || 'application/json');
    return res.status(upstream.status).send(body);
  } catch (e) {
    return res.status(502).json({ error: String((e && e.message) || e) });
  }
};
