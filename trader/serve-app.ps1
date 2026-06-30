# STRATA Live — local server + market-data proxy for the desktop web app.
# Serves trader/app/* and the repo PNGs, and proxies Yahoo/Stooq server-side
# (no CORS, no public proxies). No installs. Port 8799 (separate from the dev server).
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add('http://localhost:8799/')
try { $listener.Start() } catch { Write-Host "STRATA Live server already running (or port 8799 busy). This window can close."; return }
Write-Host "STRATA Live serving $root at http://localhost:8799/  (Ctrl+C to stop)"

while ($listener.IsListening) {
  try {
    $ctx = $listener.GetContext(); $req = $ctx.Request; $res = $ctx.Response
    # ── market-data proxy ──
    if ($req.Url.LocalPath -eq '/api/yf') {
      $res.AddHeader('Access-Control-Allow-Origin','*'); $res.AddHeader('Cache-Control','no-store')
      $target = $req.QueryString['url']; $ok = $false
      if ($target) {
        try { $target = [System.Uri]::UnescapeDataString($target) } catch {}
        if ($target -match '^https://(query[12]\.finance\.yahoo\.com|stooq\.com)/') {
          try {
            $r = Invoke-WebRequest -Uri $target -UseBasicParsing -TimeoutSec 12 -Headers @{ 'User-Agent'='Mozilla/5.0 (compatible; STRATA/1.0)'; 'Accept'='application/json,text/csv,*/*' }
            $bytes = [System.Text.Encoding]::UTF8.GetBytes([string]$r.Content)
            $res.ContentType = 'application/json; charset=utf-8'
            $res.OutputStream.Write($bytes,0,$bytes.Length); $ok = $true
          } catch {}
        }
      }
      if (-not $ok) { $res.StatusCode = 502 }
      $res.Close(); continue
    }
    # ── static files ──
    $path = [System.Uri]::UnescapeDataString($req.Url.LocalPath).TrimStart('/')
    if ([string]::IsNullOrEmpty($path)) { $path = 'trader/app/index.html' }
    $file = Join-Path $root $path
    if (Test-Path $file -PathType Leaf) {
      $bytes = [System.IO.File]::ReadAllBytes($file)
      switch ([System.IO.Path]::GetExtension($file).ToLower()) {
        '.html' { $res.ContentType = 'text/html; charset=utf-8' }
        '.js'   { $res.ContentType = 'application/javascript' }
        '.css'  { $res.ContentType = 'text/css' }
        '.png'  { $res.ContentType = 'image/png' }
        '.svg'  { $res.ContentType = 'image/svg+xml' }
        default { $res.ContentType = 'application/octet-stream' }
      }
      $res.OutputStream.Write($bytes,0,$bytes.Length)
    } else { $res.StatusCode = 404 }
    $res.Close()
  } catch {}
}
