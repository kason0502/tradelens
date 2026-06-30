# Static file server + market-data proxy for STRATA (no Node/Python needed).
#
#   /api/yf?url=<encoded Yahoo or Stooq URL>
#       → fetched SERVER-SIDE by PowerShell (no browser CORS, no public proxies),
#         so stock data loads reliably. The app calls this first and only falls
#         back to flaky public CORS proxies if this route isn't available.
#
# Everything else is served as a normal static file from the repo root.

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

$port = if ($env:PORT) { [int]$env:PORT } else { 8777 }   # honor PORT (preview autoPort); default 8777
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Start()
Write-Host "Serving $root at http://localhost:$port/  (+ /api/yf live-data proxy)"

while ($listener.IsListening) {
  try {
    $ctx = $listener.GetContext()
    $req = $ctx.Request
    $res = $ctx.Response

    # ── market-data proxy ──────────────────────────────────────────────
    if ($req.Url.LocalPath -eq '/api/yf') {
      $res.AddHeader('Access-Control-Allow-Origin', '*')
      $res.AddHeader('Cache-Control', 'no-store')
      $target = $req.QueryString['url']
      $ok = $false
      if ($target) {
        try { $target = [System.Uri]::UnescapeDataString($target) } catch { }
        # only the data hosts the app uses — not an open proxy
        if ($target -match '^https://(query[12]\.finance\.yahoo\.com|stooq\.com)/') {
          try {
            $r = Invoke-WebRequest -Uri $target -UseBasicParsing -TimeoutSec 12 `
                  -Headers @{ 'User-Agent' = 'Mozilla/5.0 (compatible; STRATA/1.0)'; 'Accept' = 'application/json,text/csv,*/*' }
            $bytes = [System.Text.Encoding]::UTF8.GetBytes([string]$r.Content)
            $res.ContentType = 'application/json; charset=utf-8'
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $ok = $true
          } catch { }
        }
      }
      if (-not $ok) { $res.StatusCode = 502 }
      $res.Close()
      continue
    }

    # ── static files ───────────────────────────────────────────────────
    $path = [System.Uri]::UnescapeDataString($req.Url.LocalPath).TrimStart('/')
    if ([string]::IsNullOrEmpty($path)) { $path = 'index.html' }
    $file = Join-Path $root $path
    if (Test-Path $file -PathType Leaf) {
      $bytes = [System.IO.File]::ReadAllBytes($file)
      $ext = [System.IO.Path]::GetExtension($file).ToLower()
      switch ($ext) {
        '.html' { $res.ContentType = 'text/html; charset=utf-8' }
        '.js'   { $res.ContentType = 'application/javascript' }
        '.css'  { $res.ContentType = 'text/css' }
        '.json' { $res.ContentType = 'application/json' }
        '.png'  { $res.ContentType = 'image/png' }
        '.jpg'  { $res.ContentType = 'image/jpeg' }
        '.jpeg' { $res.ContentType = 'image/jpeg' }
        '.webp' { $res.ContentType = 'image/webp' }
        '.svg'  { $res.ContentType = 'image/svg+xml' }
        default { $res.ContentType = 'application/octet-stream' }
      }
      $res.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
      $res.StatusCode = 404
    }
    $res.Close()
  } catch { }
}
