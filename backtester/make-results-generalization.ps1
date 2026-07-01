# Generates backtester/results-generalization.json
# Frozen daily trend-pullback rule, faithful port of backtester/src/strategy.py detect_pullback
# + engine.py run_swing (verified: reproduces the published ES results.json trades to the penny).
# Data: Yahoo daily via the local STRATA proxy (preview must be running on :8777).
$ErrorActionPreference = 'Stop'
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

$repo = 'C:\Users\donna\Desktop\tradelens'
$now  = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

function Get-Candles($sym) {
  $yurl = "https://query1.finance.yahoo.com/v8/finance/chart/$sym`?interval=1d&period1=0&period2=$now"
  $u = 'http://localhost:8777/api/yf?url=' + [uri]::EscapeDataString($yurl)
  $raw = (Invoke-WebRequest -UseBasicParsing -Uri $u -TimeoutSec 60).Content
  $j = $raw | ConvertFrom-Json
  $res = $j.chart.result[0]
  $q = $res.indicators.quote[0]
  $ts = $res.timestamp
  $out = New-Object System.Collections.Generic.List[object]
  for ($i=0; $i -lt $ts.Count; $i++) {
    $c = $q.close[$i]
    if ($null -eq $c -or $null -eq $ts[$i]) { continue }
    $o = $q.open[$i];  if ($null -eq $o) { $o = $c }
    $h = $q.high[$i];  if ($null -eq $h) { $h = $c }
    $l = $q.low[$i];   if ($null -eq $l) { $l = $c }
    $out.Add([pscustomobject]@{ t=[long]$ts[$i]; o=[double]$o; h=[double]$h; l=[double]$l; c=[double]$c })
  }
  return $out
}

function Run-Sim($candles, [double]$costPts) {
  # Signal on the CLOSED bar: close>SMA50 AND low<=SMA10 AND close>prevClose (SMAs include the signal bar,
  # exactly like pandas tail(n).mean()). Entry at NEXT bar open. Exit signal close<SMA50 -> next bar open.
  # -10% hard stop, pessimistic intrabar (stop-first; gap-through fills at the open). Cost per round trip in points.
  $n = $candles.Count
  # cumulative sums for O(1) SMAs
  $cum = New-Object double[] ($n+1)
  for ($i=0; $i -lt $n; $i++) { $cum[$i+1] = $cum[$i] + $candles[$i].c }
  $trades = New-Object System.Collections.Generic.List[object]
  $pos = $null; $pe = $false; $px = $null
  for ($i=0; $i -lt $n; $i++) {
    $b = $candles[$i]; $isLast = ($i -eq $n-1)
    if ($px -and $pos) {
      $trades.Add([pscustomobject]@{ e=$pos.entry; x=$b.o; et=$pos.t; xt=$b.t; r=$px; pts=($b.o-$pos.entry)-$costPts })
      $pos = $null; $px = $null
    }
    if ($pe -and (-not $pos) -and (-not $isLast)) {
      $pos = @{ entry=$b.o; t=$b.t; stop=$b.o*0.90 }; $pe = $false
    } elseif ($pe) { $pe = $false }
    if ($pos -and $b.l -le $pos.stop) {
      $fill = [Math]::Min($b.o, $pos.stop)
      $trades.Add([pscustomobject]@{ e=$pos.entry; x=$fill; et=$pos.t; xt=$b.t; r='hard_stop'; pts=($fill-$pos.entry)-$costPts })
      $pos = $null; $px = $null
    }
    if ($isLast) {
      if ($pos) { $trades.Add([pscustomobject]@{ e=$pos.entry; x=$b.c; et=$pos.t; xt=$b.t; r='end_of_data'; pts=($b.c-$pos.entry)-$costPts }); $pos = $null }
      break
    }
    if ($i -ge 49) {
      $s50 = ($cum[$i+1]-$cum[$i-49])/50.0
      $s10 = ($cum[$i+1]-$cum[$i-9])/10.0
      if ($pos) {
        if ($b.c -lt $s50) { $px = 'trend_break' }
      } elseif ($i -ge 50 -and $b.c -gt $s50 -and $b.l -le $s10 -and $b.c -gt $candles[$i-1].c) {
        $pe = $true
      }
    }
  }
  return $trades
}

function Get-Stats($trades, [double]$pv, [double]$ddBase = 10000.0) {
  $n = $trades.Count
  if ($n -eq 0) { return $null }
  $pts = @($trades | ForEach-Object { $_.pts })
  $usd = @($pts | ForEach-Object { $_ * $pv })
  $wins = @($usd | Where-Object { $_ -gt 0 })
  $gW = ($wins | Measure-Object -Sum).Sum; if ($null -eq $gW) { $gW = 0.0 }
  $gL = [Math]::Abs((($usd | Where-Object { $_ -le 0 }) | Measure-Object -Sum).Sum)
  $meanPts = ($pts | Measure-Object -Average).Average
  $var = 0.0; foreach ($p in $pts) { $var += ($p-$meanPts)*($p-$meanPts) }
  $sd = [Math]::Sqrt($var / [Math]::Max(1,($n-1)))
  $t = 0.0; if ($sd -gt 0) { $t = $meanPts/$sd*[Math]::Sqrt($n) }
  $eq = $ddBase; $pk = $ddBase; $dd = 0.0
  foreach ($v in $usd) { $eq += $v; if ($eq -gt $pk) { $pk = $eq }; $d = ($eq-$pk)/$pk*100.0; if ($d -lt $dd) { $dd = $d } }
  $hold = 0.0; foreach ($tr in $trades) { $hold += ($tr.xt-$tr.et)/86400.0 }; $hold = $hold/$n
  $pf = $null; if ($gL -gt 0) { $pf = [Math]::Round($gW/$gL,3) }
  return [pscustomobject]@{
    n=$n; win_rate_pct=[Math]::Round($wins.Count/$n*100,1); profit_factor=$pf
    net_expectancy_pts=[Math]::Round($meanPts,3); net_expectancy_usd=[Math]::Round($meanPts*$pv,2)
    strategy_usd=[Math]::Round(($usd | Measure-Object -Sum).Sum,2)
    max_dd_pct=[Math]::Round($dd,2); avg_hold_days=[Math]::Round($hold,1)
    best_trade_usd=[Math]::Round(($usd | Measure-Object -Maximum).Maximum,2)
    worst_trade_usd=[Math]::Round(($usd | Measure-Object -Minimum).Minimum,2)
    t_stat=[Math]::Round($t,2)
  }
}

$markets = @(
  @{ sym='ES=F';  label='S&P 500 (E-mini)';    micro='MES'; pv=5.0;   cost=1.02;  tuned='ES';
     costDesc='2 ticks (0.50 pt) spread+slippage RT + $2.60 commission RT = ~1.0 ES pt';
     note='Design market. In-sample baseline over max history (2000-09+); the published site number (PF 1.99, 59 trades) is the most recent 10y window of these same trades. Full 26y is weaker (PF ~1.5) - the site should state its window.'; withTrades=$true },
  @{ sym='NQ=F';  label='Nasdaq-100 (E-mini)'; micro='MNQ'; pv=2.0;   cost=1.80;  tuned='prior-generalization';
     costDesc='2 ticks (0.50 pt) spread+slippage RT + $2.60 commission RT';
     note='Prior generalization market (rule never tuned on it, but NQ results were cited before). Strongest market in the set.'; withTrades=$true },
  @{ sym='YM=F';  label='Dow (E-mini)';        micro='MYM'; pv=0.5;   cost=7.2;   tuned='untuned';
     costDesc='2 ticks (2 pts) spread+slippage RT + $2.60 commission RT';
     note='First-ever run on this market with the frozen rule.'; withTrades=$true },
  @{ sym='RTY=F'; label='Russell 2000 (E-mini)'; micro='M2K'; pv=5.0; cost=0.72;  tuned='untuned';
     costDesc='2 ticks (0.2 pt) spread+slippage RT + $2.60 commission RT';
     note='Only ~9y of Yahoo history (RTY listed 2017). FRAGILE: the single best trade (Nov 2020 - Mar 2021, +$3,098) exceeds the entire net profit - remove it and the strategy is net negative on RTY.'; withTrades=$true },
  @{ sym='GC=F';  label='Gold';                micro='MGC'; pv=10.0;  cost=0.66;  tuned='untuned';
     costDesc='4 ticks (0.4 pt) spread+slippage RT (metals micros run wider) + $2.60 commission RT';
     note='First-ever run. Caveat: Yahoo GC=F is an unadjusted spliced front-month series; multi-week holds cross contract rolls, so simulated P&L includes roll gaps a real (rolled) position would trade at the calendar spread instead. One malformed Yahoo bar (2009-11-23, high<low by 1.3 pts) - immaterial. A large share of the net came from the 2024-2026 gold run.'; withTrades=$true },
  @{ sym='CL=F';  label='Crude Oil (WTI)';     micro='MCL'; pv=100.0; cost=0.066; tuned='untuned';
     costDesc='4 ticks ($0.04) spread+slippage RT + $2.60 commission RT';
     note='First-ever run. VERDICT DOWNGRADED to marginal by judgment despite PF>=1.3: CL has the worst unadjusted roll-splice distortion (contango bleed), t-stat only ~1.1, and the top two trades (both 2026) carry ~53% of the net. The rule was FLAT through the April 2020 negative-price event (real Yahoo prints, low -40.32 on 2020-04-20) - the trend filter kept it out.'; withTrades=$true },
  @{ sym='SPY';   label='S&P 500 ETF';         micro='SPY x1 share'; pv=1.0; cost=0.03; tuned='prior-generalization';
     costDesc='$0.02 spread+slippage RT + ~$0.01 fees per share';
     note='Per 1 share; USD figures are per share. Same underlying market as ES - a correlated confirmation, not independent generalization. Replaces the previously hardcoded, unreproducible SPY 1.41. max_dd_pct is measured against a single-share cost basis at the series START (1993, ~$44), so the percentage reads large; judge scale by the USD fields.'; withTrades=$false },
  @{ sym='QQQ';   label='Nasdaq-100 ETF';      micro='QQQ x1 share'; pv=1.0; cost=0.03; tuned='prior-generalization';
     costDesc='$0.02 spread+slippage RT + ~$0.01 fees per share';
     note='Per 1 share; USD figures are per share. Same underlying as NQ - correlated confirmation. Replaces the previously hardcoded, unreproducible QQQ 1.32. max_dd_pct is measured against a single-share cost basis at the series START (1999, ~$51), so the percentage reads large; judge scale by the USD fields.'; withTrades=$false }
)

$entries = @()
foreach ($m in $markets) {
  Write-Host ("Running {0} ..." -f $m.sym)
  $candles = Get-Candles $m.sym
  $bad  = @($candles | Where-Object { $_.h -lt $_.l -or $_.l -le 0 -or $_.o -le 0 }).Count
  $tr   = Run-Sim $candles $m.cost
  $first = $candles[0]; $last = $candles[$candles.Count-1]
  $ddBase = 10000.0; if ($m.pv -eq 1.0) { $ddBase = $first.c }   # ETF rows: drawdown vs a 1-share cost basis
  $st   = Get-Stats $tr $m.pv $ddBase
  $st2  = Get-Stats (Run-Sim $candles ($m.cost*2)) $m.pv $ddBase
  $bh = [Math]::Round(($last.c - $first.c) * $m.pv, 2)
  # verdict: objective criteria, with the CL judgment override documented in its note
  $fragile = (($st.strategy_usd - $st.best_trade_usd) -le 0)
  if ($m.sym -eq 'ES=F') { $verdict = 'edge holds (in-sample baseline)' }
  elseif ($st.profit_factor -ge 1.3 -and $st.n -ge 30 -and $st2.profit_factor -gt 1.0 -and -not $fragile -and $m.sym -ne 'CL=F') { $verdict = 'edge generalizes' }
  elseif ($st.profit_factor -ge 1.1) { $verdict = 'marginal' }
  else { $verdict = 'does not generalize' }
  $d = { param($ts) [DateTimeOffset]::FromUnixTimeSeconds($ts).UtcDateTime.ToString('yyyy-MM-dd') }
  $tradeList = $null
  if ($m.withTrades) {
    $tradeList = @($tr | ForEach-Object {
      [pscustomobject]@{ entry=(& $d $_.et); exit=(& $d $_.xt); pts=[Math]::Round($_.pts,3); usd=[Math]::Round($_.pts*$m.pv,2); reason=$_.r }
    })
  }
  $entries += [pscustomobject]@{
    sym=$m.sym; label=$m.label; micro=$m.micro; point_value=$m.pv
    cost_rt=[pscustomobject]@{ points=$m.cost; usd=[Math]::Round($m.cost*$m.pv,2); model=$m.costDesc }
    period=[pscustomobject]@{ from=(& $d $first.t); to=(& $d $last.t) }
    bars=$candles.Count; bad_bars=$bad
    n_trades=$st.n; win_rate_pct=$st.win_rate_pct; profit_factor=$st.profit_factor
    net_expectancy_pts=$st.net_expectancy_pts; net_expectancy_usd=$st.net_expectancy_usd
    max_dd_pct=$st.max_dd_pct; avg_hold_days=$st.avg_hold_days
    best_trade_usd=$st.best_trade_usd; worst_trade_usd=$st.worst_trade_usd; t_stat=$st.t_stat
    pf_2x_costs=$st2.profit_factor
    buyhold_usd=$bh; strategy_usd=$st.strategy_usd
    verdict=$verdict; tuned=$m.tuned; note=$m.note
    trades=$tradeList
  }
  Write-Host ("  n={0} pf={1} win={2}% t={3} best={4} worst={5} strat={6} bh={7} verdict={8}" -f `
    $st.n,$st.profit_factor,$st.win_rate_pct,$st.t_stat,$st.best_trade_usd,$st.worst_trade_usd,$st.strategy_usd,$bh,$verdict)
}

$out = [pscustomobject]@{
  schema_version = 1
  generated_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
  method = 'FROZEN daily trend-pullback rule, zero tuning, run identically on every market. LONG when (a) close > 50-day SMA, (b) the day''s low touched at/below the 10-day SMA, (c) close > previous close - all judged on the CLOSED daily bar (SMAs include the signal bar, matching the published Python engine); ENTER at the NEXT day''s open. EXIT signal on a daily close < 50-day SMA, filled at the NEXT day''s open. -10% hard-stop backstop, pessimistic intrabar (if the day''s low touches the stop it fills at the stop, or at the open if it gapped through). One position at a time, long only, all-session Globex daily bars (Yahoo). Costs are deducted per round trip on every trade (see each market''s cost_rt; micro-contract scale: 2 ticks spread+slippage RT for index micros, 4 ticks for MGC/MCL, + $2.60 commission RT). Max drawdown is peak-to-trough on a $10,000 account trading 1 micro contract (ETF rows: vs a 1-share cost basis), closed-trade equity, non-compounding. Buy-and-hold = (last close - first close) x point value over the same span, same micro. Data caveat: Yahoo =F series are unadjusted spliced front-month contracts - long holds cross rolls (worst for CL/GC carry); ETF rows (SPY/QQQ) are per 1 share and are correlated confirmations of ES/NQ, not independent markets. VERIFICATION: this simulator reproduces the published backtester/results.json ES run (2016-06-29 window, published cost model) trade-for-trade - n=59, win 32.2%, best +$5258.75, worst -$731.25 exactly.'
  holdout_status = 'This run consumed NO holdouts: the rule was frozen long before (tuned only on ES) and YM/RTY/GC/CL had never been tested with it. ES is in-sample/full-sample, NOT out-of-sample. NQ/SPY/QQQ are prior-generalization markets re-run under one consistent methodology.'
  markets = $entries
}

$json = $out | ConvertTo-Json -Depth 8 -Compress
$path = Join-Path $repo 'backtester\results-generalization.json'
[IO.File]::WriteAllText($path, $json, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Wrote $path ($([IO.FileInfo]::new($path).Length) bytes)"



