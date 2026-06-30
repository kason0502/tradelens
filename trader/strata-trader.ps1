<#
  STRATA Trader — standalone futures backtester + live trade-setup tool.
  Runs the validated daily trend-pullback strategy on real Yahoo data, prints
  every trade as it finds them, shows the full stats, then tells you the CURRENT
  setup (where to enter / where to exit). No installs — pure PowerShell.

  USAGE (from this folder):
    powershell -ExecutionPolicy Bypass -File strata-trader.ps1
    powershell -ExecutionPolicy Bypass -File strata-trader.ps1 -Symbol NQ=F -Years 10
    powershell -ExecutionPolicy Bypass -File strata-trader.ps1 -All        # scan every market's live signal
    powershell -ExecutionPolicy Bypass -File strata-trader.ps1 -Watch       # re-check the live signal on a timer
  Or just double-click run.bat.

  The rule (same edge as the STRATA app):
    - Only LONG, only while price is ABOVE its 50-day average (uptrend).
    - ENTER when price pulls back to the 10-day average and the day turns up.
    - EXIT when a daily close falls back below the 50-day average (trend break).
    - Hard stop at -10%. No fixed target — winners run.

  NOT financial advice. This tells you the levels; it does NOT place orders.
#>
[CmdletBinding()]
param(
  [string]$Symbol = "ES=F",
  [int]$Years = 10,
  [double]$Account = 10000,
  [double]$RiskPct = 1,
  [switch]$All,
  [switch]$Watch,
  [int]$WatchMins = 30
)

$ErrorActionPreference = "Stop"
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

# Per-point dollar value of the MICRO contract for each market (what the app models).
$PointVal = @{ "ES=F"=5; "NQ=F"=2; "YM=F"=0.5; "RTY=F"=5; "CL=F"=100; "GC=F"=10; "SPY"=1; "QQQ"=1 }
$Names = @{ "ES=F"="S&P 500 (MES)"; "NQ=F"="Nasdaq 100 (MNQ)"; "YM=F"="Dow (MYM)"; "RTY=F"="Russell 2000 (M2K)"; "CL=F"="Crude Oil (MCL)"; "GC=F"="Gold (MGC)"; "SPY"="S&P 500 ETF"; "QQQ"="Nasdaq 100 ETF" }

function Write-Rule { param([string]$ch="-") Write-Host ($ch * 64) -ForegroundColor DarkGray }
function Hd { param([string]$t) Write-Host ""; Write-Host "  $t" -ForegroundColor Cyan; Write-Rule }

# ── Fetch real daily OHLC from Yahoo (server-side, no CORS) ──
function Get-Daily {
  param([string]$Sym, [int]$Yrs)
  $url = "https://query1.finance.yahoo.com/v8/finance/chart/$Sym`?interval=1d&range=${Yrs}y"
  $resp = Invoke-WebRequest -Uri $url -Headers @{ "User-Agent" = "Mozilla/5.0" } -UseBasicParsing -TimeoutSec 25
  $data = $resp.Content | ConvertFrom-Json
  $r = $data.chart.result[0]
  $ts = $r.timestamp
  $q = $r.indicators.quote[0]
  $bars = New-Object System.Collections.Generic.List[object]
  for ($i = 0; $i -lt $ts.Count; $i++) {
    $c = $q.close[$i]
    if ($null -eq $c) { continue }
    $o = if ($null -ne $q.open[$i]) { [double]$q.open[$i] } else { [double]$c }
    $h = if ($null -ne $q.high[$i]) { [double]$q.high[$i] } else { [double]$c }
    $l = if ($null -ne $q.low[$i])  { [double]$q.low[$i]  } else { [double]$c }
    $bars.Add([pscustomobject]@{
      Date = [DateTimeOffset]::FromUnixTimeSeconds([long]$ts[$i]).DateTime.ToString("yyyy-MM-dd")
      O = $o; H = $h; L = $l; C = [double]$c
    })
  }
  return $bars
}

function SMA { param($arr, [int]$n, [int]$i)
  if ($i -lt $n - 1) { return $null }
  $s = 0.0; for ($j = $i - $n + 1; $j -le $i; $j++) { $s += $arr[$j] }
  return $s / $n
}

# ── Backtest: walk the bars, print each trade as it's found ──
function Run-Backtest {
  param($bars, [bool]$Verbose = $true)
  $closes = @($bars | ForEach-Object { $_.C })
  $n = $closes.Count
  $trades = New-Object System.Collections.Generic.List[object]
  $pos = $null
  if ($Verbose) { Write-Host ("  {0,-12} {1,-12} {2,10} {3,10} {4,8}  {5}" -f "Entered","Exited","Entry","Exit","Move","Why it exited") -ForegroundColor DarkGray }
  for ($i = 50; $i -lt $n; $i++) {
    $s50 = SMA $closes 50 $i
    $s10 = SMA $closes 10 $i
    if ($null -eq $s50 -or $null -eq $s10) { continue }
    $price = $closes[$i]
    if ($null -eq $pos) {
      $uptrend = $price -gt $s50
      $lo3 = [math]::Min([math]::Min($bars[$i].L, $bars[$i-1].L), $bars[$i-2].L)
      $pulled = ($lo3 -le $s10) -or ($price -le $s10)
      $turn = $price -gt $closes[$i-1]
      if ($uptrend -and $pulled -and $turn) {
        $pos = [pscustomobject]@{ Date = $bars[$i].Date; Entry = $price; Stop = $price * 0.90 }
      }
    } else {
      $exit = $null; $reason = $null
      if ($bars[$i].L -le $pos.Stop) { $exit = $pos.Stop; $reason = "hard stop -10%" }
      elseif ($price -lt $s50)       { $exit = $price;    $reason = "trend break (close < 50-day)" }
      if ($null -ne $exit) {
        $pct = ($exit - $pos.Entry) / $pos.Entry * 100
        $t = [pscustomobject]@{ EntryDate=$pos.Date; ExitDate=$bars[$i].Date; Entry=$pos.Entry; Exit=$exit; Pct=$pct; Reason=$reason }
        $trades.Add($t)
        if ($Verbose) {
          $col = if ($pct -ge 0) { "Green" } else { "Red" }
          Write-Host ("  {0,-12} {1,-12} {2,10:N2} {3,10:N2} {4,7:N1}%  {5}" -f $t.EntryDate,$t.ExitDate,$t.Entry,$t.Exit,$t.Pct,$t.Reason) -ForegroundColor $col
        }
        $pos = $null
      }
    }
  }
  return ,$trades
}

function Show-Stats {
  param($trades, [string]$Sym)
  if ($trades.Count -eq 0) { Write-Host "  No trades triggered in this window." -ForegroundColor Yellow; return }
  $rs = @($trades | ForEach-Object { $_.Pct })
  $wins = @($rs | Where-Object { $_ -gt 0 })
  $losses = @($rs | Where-Object { $_ -le 0 })
  $gW = ($wins | Measure-Object -Sum).Sum;  if ($null -eq $gW) { $gW = 0 }
  $gL = [math]::Abs((($losses | Measure-Object -Sum).Sum)); if ($null -eq $gL) { $gL = 0 }
  $pf = if ($gL -gt 0) { $gW / $gL } else { [double]::PositiveInfinity }
  $winRate = if ($rs.Count) { $wins.Count / $rs.Count * 100 } else { 0 }
  $eq = 1.0; $curve = @(1.0); foreach ($r in $rs) { $eq *= (1 + $r/100); $curve += $eq }
  $peak = $curve[0]; $dd = 0.0; foreach ($v in $curve) { if ($v -gt $peak) { $peak = $v }; $d = ($v-$peak)/$peak*100; if ($d -lt $dd) { $dd = $d } }
  $avg = ($rs | Measure-Object -Average).Average
  $best = ($rs | Measure-Object -Maximum).Maximum
  $worst = ($rs | Measure-Object -Minimum).Minimum

  $pv = if ($PointVal.ContainsKey($Sym)) { $PointVal[$Sym] } else { 5 }
  $usd = 0.0; foreach ($t in $trades) { $usd += ($t.Exit - $t.Entry) * $pv }

  Hd "RESULTS"
  $retCol = if (($eq-1) -ge 0) { "Green" } else { "Red" }
  $pfCol  = if ($pf -ge 1)     { "Green" } else { "Red" }
  Write-Host ("  Trades         {0}" -f $trades.Count)
  Write-Host ("  Win rate       {0:N1}%   (low by design - wins are bigger)" -f $winRate)
  Write-Host ("  Profit factor  {0:N2}" -f $pf) -ForegroundColor $pfCol
  Write-Host ("  Total return   {0:+0.0;-0.0}%   (compounding 1 unit/trade, gross of costs)" -f (($eq-1)*100)) -ForegroundColor $retCol
  Write-Host ("  Net P&L        {0:+$#,0;-$#,0}   (1 micro, `$$pv/point)" -f $usd) -ForegroundColor $retCol
  Write-Host ("  Avg trade      {0:+0.00;-0.00}%" -f $avg)
  Write-Host ("  Best / Worst   {0:+0.0;-0.0}%  /  {1:+0.0;-0.0}%" -f $best,$worst)
  Write-Host ("  Max drawdown   {0:N1}%" -f $dd) -ForegroundColor Red
  $verdict = if ($pf -ge 1.3 -and ($eq-1) -gt 0) { "EDGE HOLDS" } elseif ($pf -ge 1) { "marginal edge" } else { "no edge in this window" }
  $vCol = if ($pf -ge 1.3 -and ($eq-1) -gt 0) { "Green" } elseif ($pf -ge 1) { "Yellow" } else { "Red" }
  Write-Host ("  Verdict        {0}" -f $verdict) -ForegroundColor $vCol
}

# ── Current live setup: where to enter / where to exit ──
function Show-Signal {
  param($bars, [string]$Sym, [double]$Account, [double]$RiskPct, [bool]$Heading = $true)
  $closes = @($bars | ForEach-Object { $_.C })
  $n = $closes.Count
  if ($n -lt 51) { Write-Host "  Not enough data." -ForegroundColor Yellow; return }
  $i = $n - 1
  $price = $closes[$i]
  $s50 = SMA $closes 50 $i
  $s10 = SMA $closes 10 $i
  $uptrend = $price -gt $s50
  $lo3 = [math]::Min([math]::Min($bars[$i].L, $bars[$i-1].L), $bars[$i-2].L)
  $pulled = ($lo3 -le $s10) -or ($price -le $s10)
  $turn = $price -gt $closes[$i-1]
  $buy = $uptrend -and $pulled -and $turn

  $name = if ($Names.ContainsKey($Sym)) { $Names[$Sym] } else { $Sym }
  if ($Heading) { Hd "LIVE SETUP - $Sym  ($name)" }

  if (-not $uptrend) {
    Write-Host ("  {0}  NO TRADE - downtrend (below 50-day). Stand aside." -f $Sym) -ForegroundColor Red
    Write-Host ("     last close {0:N2}   50-day {1:N2}" -f $price,$s50) -ForegroundColor DarkGray
    return
  }
  $hardStop = $price * 0.90
  $exitLvl = [math]::Max($s50, $hardStop)
  $stopDist = $price - $exitLvl
  $pv = if ($PointVal.ContainsKey($Sym)) { $PointVal[$Sym] } else { 5 }
  $riskD = $Account * $RiskPct / 100
  $contracts = if ($stopDist -gt 0) { [math]::Floor($riskD / ($stopDist * $pv)) } else { 0 }

  if ($buy) {
    Write-Host ("  {0}  *** BUY SETUP ***  uptrend + pullback + turning up" -f $Sym) -ForegroundColor Green
  } elseif ($pulled) {
    Write-Host ("  {0}  WATCH - pulled back, waiting for a green (up) day to trigger" -f $Sym) -ForegroundColor Yellow
  } else {
    Write-Host ("  {0}  UPTREND - no entry yet (not pulled back to the 10-day)" -f $Sym) -ForegroundColor Cyan
  }
  Write-Host ""
  Write-Host ("     ENTER       {0:N2}   {1}" -f $price, $(if($buy){"buy now / next open"}else{"on a dip to the 10-day ($('{0:N2}' -f $s10)) that turns up"})) -ForegroundColor White
  Write-Host ("     EXIT (trend) {0:N2}   sell on a daily close below the 50-day average" -f $s50) -ForegroundColor White
  Write-Host ("     HARD STOP    {0:N2}   -10% safety net" -f $hardStop) -ForegroundColor White
  Write-Host ("     TARGET       none - ride the trend; exits dynamically on the trend break") -ForegroundColor DarkGray
  if ($contracts -gt 0) {
    Write-Host ("     SIZE         {0} micro contract(s)  (risking {1}% of `${2:N0} = ~`${3:N0} to the stop)" -f $contracts,$RiskPct,$Account,($contracts*$stopDist*$pv)) -ForegroundColor DarkGray
  }
}

# ════════════════════════ MAIN ════════════════════════
Clear-Host
Write-Host ""
Write-Host "  S T R A T A   T R A D E R" -ForegroundColor Green
Write-Host "  Daily trend-pullback - futures backtest + live setups" -ForegroundColor DarkGray
Write-Host "  (educational; not financial advice; does NOT place orders)" -ForegroundColor DarkGray

$markets = if ($All) { @("ES=F","NQ=F","YM=F","RTY=F","CL=F","GC=F") } else { @($Symbol) }

if ($All) {
  Hd "LIVE SETUPS - all markets"
  foreach ($m in $markets) {
    try { $bars = Get-Daily $m 2; Show-Signal $bars $m $Account $RiskPct $false; Write-Host "" }
    catch { Write-Host ("  {0}  data unavailable ({1})" -f $m, $_.Exception.Message) -ForegroundColor DarkGray }
  }
  Write-Host "  Tip: run without -All for a full backtest of one market." -ForegroundColor DarkGray
  return
}

do {
  try {
    Hd "BACKTEST - $Symbol, last $Years years (trades as they happen)"
    $bars = Get-Daily $Symbol $Years
    Write-Host ("  Loaded {0} daily bars ({1} -> {2})." -f $bars.Count, $bars[0].Date, $bars[$bars.Count-1].Date) -ForegroundColor DarkGray
    Write-Host ""
    $trades = Run-Backtest $bars $true
    Show-Stats $trades $Symbol
    Show-Signal $bars $Symbol $Account $RiskPct $true
  } catch {
    Write-Host ("  ERROR: {0}" -f $_.Exception.Message) -ForegroundColor Red
    Write-Host "  (Yahoo may be rate-limiting - wait a moment and retry.)" -ForegroundColor DarkGray
  }
  if ($Watch) {
    Write-Host ""
    Write-Host ("  Watching - re-checking in $WatchMins min. Ctrl+C to stop." -f $WatchMins) -ForegroundColor DarkGray
    Start-Sleep -Seconds ($WatchMins * 60)
  }
} while ($Watch)

Write-Host ""
