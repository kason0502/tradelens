<#
  STRATA Live - a desktop charting app (PowerShell + WinForms, no installs).
  Reacts to live futures candles with the trend-pullback strategy, drops your
  bull.png on BUY signals / bear.png on downtrend-exit signals, and shows the
  current entry / exit / stop. Switch timeframe (Daily ~weeks hold, or a LOWER
  timeframe ~couple-days hold); the Backtest button tells you whether the edge
  holds on that timeframe - if it doesn't, try another and re-backtest.

  RUN:  double-click run-live.bat   (or)
        powershell -ExecutionPolicy Bypass -File strata-live.ps1
  TEST: powershell -ExecutionPolicy Bypass -File strata-live.ps1 -NoUI -Interval 1h

  Educational only - not financial advice. Shows levels; does NOT place orders.
#>
[CmdletBinding()]
param(
  [string]$Symbol = "ES=F",
  [ValidateSet("1d","1h")] [string]$Interval = "1d",
  [double]$Account = 25000,
  [double]$RiskPct = 1,
  [switch]$NoUI
)
$ErrorActionPreference = "Stop"
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}
$ROOT = Split-Path -Parent $PSScriptRoot   # repo root (this script lives in /trader)
if (-not $ROOT) { $ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent }

$PointVal = @{ "ES=F"=5; "NQ=F"=2; "YM=F"=0.5; "RTY=F"=5; "CL=F"=100; "GC=F"=10; "SPY"=1; "QQQ"=1 }
# Per-timeframe config: the SMA pair + the Yahoo range + a plain hold-time label.
$TF = @{
  "1d" = @{ range="5y";  trend=50; pull=10; hold="~weeks (swing)";      label="Daily" }
  "1h" = @{ range="180d"; trend=50; pull=10; hold="~hours-to-days (short)"; label="Hourly" }
}

# -- Data --
function Get-Series {
  param([string]$Sym,[string]$Intv)
  $range = $TF[$Intv].range
  $url = "https://query1.finance.yahoo.com/v8/finance/chart/$Sym`?interval=$Intv&range=$range"
  $resp = Invoke-WebRequest -Uri $url -Headers @{ "User-Agent"="Mozilla/5.0" } -UseBasicParsing -TimeoutSec 25
  $data = $resp.Content | ConvertFrom-Json
  $r = $data.chart.result[0]; $ts = $r.timestamp; $q = $r.indicators.quote[0]
  $bars = New-Object System.Collections.Generic.List[object]
  for ($i=0; $i -lt $ts.Count; $i++) {
    $c = $q.close[$i]; if ($null -eq $c) { continue }
    $o = if ($null -ne $q.open[$i]) { [double]$q.open[$i] } else { [double]$c }
    $h = if ($null -ne $q.high[$i]) { [double]$q.high[$i] } else { [double]$c }
    $l = if ($null -ne $q.low[$i])  { [double]$q.low[$i]  } else { [double]$c }
    $dt = [DateTimeOffset]::FromUnixTimeSeconds([long]$ts[$i]).LocalDateTime
    $bars.Add([pscustomobject]@{ T=$dt; O=$o; H=$h; L=$l; C=[double]$c })
  }
  return ,$bars
}
function SMASeries { param($vals,[int]$n)
  $out = New-Object 'double[]' $vals.Count
  $sum = 0.0
  for ($i=0; $i -lt $vals.Count; $i++) {
    $sum += $vals[$i]; if ($i -ge $n) { $sum -= $vals[$i-$n] }
    $out[$i] = if ($i -ge $n-1) { $sum/$n } else { [double]::NaN }
  }
  return ,$out
}

# -- Strategy: tag each bar, run the backtest, read the current signal --
function Analyze {
  param($bars,[string]$Intv)
  $cfg = $TF[$Intv]
  $closes = @($bars | ForEach-Object { $_.C })
  $n = $closes.Count
  $s50 = SMASeries $closes $cfg.trend
  $s10 = SMASeries $closes $cfg.pull
  $sig = New-Object 'string[]' $n       # "" | "buy" | "down"
  $trades = New-Object System.Collections.Generic.List[object]
  $pos = $null
  for ($i=0; $i -lt $n; $i++) {
    $sig[$i] = ""
    if ([double]::IsNaN($s50[$i]) -or [double]::IsNaN($s10[$i]) -or $i -lt 2) { continue }
    $price = $closes[$i]; $up = $price -gt $s50[$i]
    if (-not $up) { $sig[$i] = "down" }
    if ($null -eq $pos) {
      $lo3 = [math]::Min([math]::Min($bars[$i].L,$bars[$i-1].L),$bars[$i-2].L)
      $pulled = ($lo3 -le $s10[$i]) -or ($price -le $s10[$i])
      $turn = $price -gt $closes[$i-1]
      if ($up -and $pulled -and $turn) { $sig[$i]="buy"; $pos = [pscustomobject]@{ i=$i; Entry=$price; Stop=$price*0.90 } }
    } else {
      $exit=$null;$reason=$null
      if ($bars[$i].L -le $pos.Stop) { $exit=$pos.Stop;$reason="hard stop -10%" }
      elseif ($price -lt $s50[$i])   { $exit=$price;$reason="trend break" }
      if ($null -ne $exit) {
        $pct = ($exit-$pos.Entry)/$pos.Entry*100
        $hbars = $i - $pos.i
        $trades.Add([pscustomobject]@{ i0=$pos.i; i1=$i; Entry=$pos.Entry; Exit=$exit; Pct=$pct; Reason=$reason; Bars=$hbars })
        $sig[$i]="down"; $pos=$null
      }
    }
  }
  return [pscustomobject]@{ closes=$closes; s50=$s50; s10=$s10; sig=$sig; trades=$trades; openPos=$pos }
}

function Hold-Label { param([string]$Intv,$avgBars)
  if ($Intv -eq "1h") { $hrs=[math]::Round($avgBars); return ("~{0} trading hours (~{1:N0} days)" -f $hrs, ($hrs/6.5)) }
  return ("~{0:N0} days" -f $avgBars)
}

function Backtest-Text {
  param($a,[string]$Sym,[string]$Intv)
  $tr = $a.trades
  if ($tr.Count -eq 0) { return "No trades triggered on the $($TF[$Intv].label) timeframe." }
  $rs = @($tr | ForEach-Object { $_.Pct })
  $wins=@($rs|Where-Object{$_ -gt 0}); $losses=@($rs|Where-Object{$_ -le 0})
  $gW=($wins|Measure-Object -Sum).Sum; if($null -eq $gW){$gW=0}
  $gL=[math]::Abs(($losses|Measure-Object -Sum).Sum); if($null -eq $gL){$gL=0}
  $pf= if($gL -gt 0){$gW/$gL}else{[double]::PositiveInfinity}
  $wr= if($rs.Count){$wins.Count/$rs.Count*100}else{0}
  $eq=1.0;$curve=@(1.0); foreach($r in $rs){$eq*=(1+$r/100);$curve+=$eq}
  $peak=$curve[0];$dd=0.0; foreach($v in $curve){if($v -gt $peak){$peak=$v};$d=($v-$peak)/$peak*100;if($d -lt $dd){$dd=$d}}
  $avgBars=($tr|ForEach-Object{$_.Bars}|Measure-Object -Average).Average
  $verdict= if($pf -ge 1.3 -and ($eq-1) -gt 0){"EDGE HOLDS"}elseif($pf -ge 1){"MARGINAL - consider another timeframe"}else{"NO EDGE here - re-backtest a different timeframe"}
  $pfTxt = if([double]::IsInfinity($pf)){"inf"}else{("{0:N2}" -f $pf)}
  return @"
$($TF[$Intv].label) backtest | $Sym
  Trades            $($tr.Count)
  Win rate          $("{0:N1}" -f $wr)%   (low by design)
  Profit factor     $pfTxt
  Total return      $("{0:+0.0;-0.0}" -f (($eq-1)*100))%   (gross of costs)
  Avg hold          $(Hold-Label $Intv $avgBars)
  Max drawdown      $("{0:N1}" -f $dd)%
  VERDICT           $verdict
"@
}

function Signal-Info {
  param($a,[string]$Sym,[string]$Intv,[double]$Account,[double]$RiskPct)
  $closes=$a.closes; $n=$closes.Count; $i=$n-1
  $price=$closes[$i]; $s50=$a.s50[$i]; $s10=$a.s10[$i]
  if ([double]::IsNaN($s50)) { return "Not enough bars." }
  $up = $price -gt $s50
  if (-not $up) { return ("$Sym  NO TRADE - downtrend (last {0:N2} < 50-period {1:N2}). Stand aside." -f $price,$s50) }
  $lo3=[math]::Min([math]::Min($a.s10[$i],$price),$price)  # placeholder; recompute via bars in caller
  $state = if ($a.sig[$i] -eq "buy") { "*** BUY SIGNAL ***" } elseif ($price -le $s10) { "WATCH - pulled back, need an up bar" } else { "UPTREND - no entry yet" }
  $hard=$price*0.90; $exitLvl=[math]::Max($s50,$hard); $dist=$price-$exitLvl
  $pv = if($PointVal.ContainsKey($Sym)){$PointVal[$Sym]}else{5}
  $riskD=$Account*$RiskPct/100; $ct= if($dist -gt 0){[math]::Floor($riskD/($dist*$pv))}else{0}
  return @"
$Sym  $state
  ENTER       $("{0:N2}" -f $price)   $(if($a.sig[$i] -eq 'buy'){'now / next bar'}else{'on a pullback to the 10-period that turns up'})
  EXIT        $("{0:N2}" -f $s50)   close below the 50-period average (trend break)
  HARD STOP   $("{0:N2}" -f $hard)   -10%
  TARGET      none - ride the trend
  SIZE        $ct micro ($($pv)/pt) at $RiskPct% of `$$([int]$Account)
"@
}

# ================ HEADLESS (for testing / quick check) ================
if ($NoUI) {
  Write-Host "STRATA Live (headless) - $Symbol $Interval" -ForegroundColor Green
  $bars = Get-Series $Symbol $Interval
  Write-Host ("Loaded {0} {1} bars." -f $bars.Count, $Interval) -ForegroundColor DarkGray
  $a = Analyze $bars $Interval
  Write-Host ""; Write-Host (Backtest-Text $a $Symbol $Interval)
  Write-Host ""; Write-Host (Signal-Info $a $Symbol $Interval $Account $RiskPct) -ForegroundColor Cyan
  Write-Host ("`nBuy signals on chart: {0} | downtrend/exit marks: {1}" -f (@($a.sig|Where-Object{$_ -eq 'buy'}).Count), (@($a.sig|Where-Object{$_ -eq 'down'}).Count)) -ForegroundColor DarkGray
  return
}

# ============================ GUI ============================
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$script:Symbol=$Symbol; $script:Interval=$Interval; $script:Data=$null
$bullImg=$null; $bearImg=$null
try { if (Test-Path "$ROOT\bull.png") { $bullImg=[System.Drawing.Image]::FromFile("$ROOT\bull.png") } } catch {}
try { if (Test-Path "$ROOT\bear.png") { $bearImg=[System.Drawing.Image]::FromFile("$ROOT\bear.png") } } catch {}

$BG=[System.Drawing.Color]::FromArgb(12,12,14)
$GREEN=[System.Drawing.Color]::FromArgb(38,194,129)
$RED=[System.Drawing.Color]::FromArgb(240,68,90)
$AMBER=[System.Drawing.Color]::FromArgb(255,201,77)
$INK=[System.Drawing.Color]::FromArgb(232,234,237)
$MUT=[System.Drawing.Color]::FromArgb(120,124,132)

$form=New-Object System.Windows.Forms.Form
$form.Text="STRATA Live - futures trend-pullback"
$form.Size=New-Object System.Drawing.Size(1180,760)
$form.BackColor=$BG; $form.ForeColor=$INK
$form.Font=New-Object System.Drawing.Font("Segoe UI",9)

# top control bar
$bar=New-Object System.Windows.Forms.Panel
$bar.Dock="Top"; $bar.Height=46; $bar.BackColor=[System.Drawing.Color]::FromArgb(18,18,20)
$form.Controls.Add($bar)

$symBox=New-Object System.Windows.Forms.ComboBox
$symBox.Items.AddRange(@("ES=F","NQ=F","YM=F","RTY=F","CL=F","GC=F","SPY","QQQ"))
$symBox.SelectedItem=$script:Symbol; $symBox.DropDownStyle="DropDownList"
$symBox.Location=New-Object System.Drawing.Point(12,10); $symBox.Width=90
$symBox.BackColor=[System.Drawing.Color]::FromArgb(25,26,29); $symBox.ForeColor=$INK; $symBox.FlatStyle="Flat"
$bar.Controls.Add($symBox)

$tfBox=New-Object System.Windows.Forms.ComboBox
$tfBox.Items.AddRange(@("Daily (weeks hold)","Hourly (days hold)"))
$tfBox.SelectedIndex= $(if($script:Interval -eq "1h"){1}else{0}); $tfBox.DropDownStyle="DropDownList"
$tfBox.Location=New-Object System.Drawing.Point(110,10); $tfBox.Width=160
$tfBox.BackColor=[System.Drawing.Color]::FromArgb(25,26,29); $tfBox.ForeColor=$INK; $tfBox.FlatStyle="Flat"
$bar.Controls.Add($tfBox)

$btXBtn=New-Object System.Windows.Forms.Button
$btXBtn.Text="Backtest this timeframe"; $btXBtn.Location=New-Object System.Drawing.Point(280,9); $btXBtn.Width=170; $btXBtn.Height=28
$btXBtn.FlatStyle="Flat"; $btXBtn.BackColor=[System.Drawing.Color]::FromArgb(25,26,29); $btXBtn.ForeColor=$INK
$bar.Controls.Add($btXBtn)

$refBtn=New-Object System.Windows.Forms.Button
$refBtn.Text="Refresh"; $refBtn.Location=New-Object System.Drawing.Point(458,9); $refBtn.Width=80; $refBtn.Height=28
$refBtn.FlatStyle="Flat"; $refBtn.BackColor=[System.Drawing.Color]::FromArgb(25,26,29); $refBtn.ForeColor=$INK
$bar.Controls.Add($refBtn)

$statusLbl=New-Object System.Windows.Forms.Label
$statusLbl.AutoSize=$true; $statusLbl.Location=New-Object System.Drawing.Point(556,15); $statusLbl.ForeColor=$MUT
$statusLbl.Text="loading..."; $bar.Controls.Add($statusLbl)

# right info panel
$info=New-Object System.Windows.Forms.TextBox
$info.Multiline=$true; $info.ReadOnly=$true; $info.Dock="Right"; $info.Width=320
$info.BackColor=[System.Drawing.Color]::FromArgb(16,16,18); $info.ForeColor=$INK; $info.BorderStyle="None"
$info.Font=New-Object System.Drawing.Font("Consolas",9.5); $info.ScrollBars="Vertical"
$form.Controls.Add($info)

# chart panel (custom-drawn)
$chart=New-Object System.Windows.Forms.Panel
$chart.Dock="Fill"; $chart.BackColor=$BG
$form.Controls.Add($chart)
$chart.BringToFront()

# enable double-buffering on the chart panel (reduce flicker) - non-essential, ignore if it fails
try { $bf=[System.Reflection.BindingFlags]'Instance,NonPublic'; [System.Windows.Forms.Control].GetProperty('DoubleBuffered',$bf).SetValue($chart,$true,$null) } catch {}

$chart.Add_Paint({
  param($s,$e)
  $g=$e.Graphics; $g.SmoothingMode="AntiAlias"
  $a=$script:Data; if($null -eq $a){ return }
  $W=$chart.ClientSize.Width; $H=$chart.ClientSize.Height
  $padL=10;$padR=64;$padT=12;$padB=22
  $closes=$a.closes; $n=$closes.Count
  $N=[math]::Min(160,$n); $start=$n-$N
  # y-range over visible window (highs/lows + MAs)
  $min=[double]::MaxValue;$max=[double]::MinValue
  for($k=$start;$k -lt $n;$k++){ $b=$a.bars[$k]; if($b.L -lt $min){$min=$b.L}; if($b.H -gt $max){$max=$b.H}
    if(-not [double]::IsNaN($a.s50[$k])){ if($a.s50[$k] -lt $min){$min=$a.s50[$k]}; if($a.s50[$k] -gt $max){$max=$a.s50[$k]} } }
  if($min -ge $max){ return }
  $rng=$max-$min; $plotW=$W-$padL-$padR; $plotH=$H-$padT-$padB
  $xAt={ param($idx) $padL + ($idx-$start)/[math]::Max(1,$N-1)*$plotW }
  $yAt={ param($v) $padT + (1-($v-$min)/$rng)*$plotH }
  $cw=[math]::Max(2.0,[math]::Min(9.0,$plotW/$N*0.6))
  # gridlines + price labels
  $gp=New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(28,28,32))
  $fMut=New-Object System.Drawing.SolidBrush $MUT
  $fnt=New-Object System.Drawing.Font("Consolas",8)
  for($gi=0;$gi -le 4;$gi++){ $v=$min+$rng*$gi/4; $y=& $yAt $v
    $g.DrawLine($gp,[single]$padL,[single]$y,[single]($W-$padR),[single]$y)
    $g.DrawString(("{0:N0}" -f $v),$fnt,$fMut,[single]($W-$padR+3),[single]($y-7)) }
  # MAs
  function DrawMA($arr,$col,$wd){ $pen=New-Object System.Drawing.Pen $col,$wd; $prev=$null
    for($k=$start;$k -lt $n;$k++){ if([double]::IsNaN($arr[$k])){continue}
      $pt=New-Object System.Drawing.PointF([single](& $xAt $k),[single](& $yAt $arr[$k]))
      if($null -ne $prev){ $g.DrawLine($pen,$prev,$pt) }; $prev=$pt } }
  DrawMA $a.s50 ([System.Drawing.Color]::FromArgb(34,197,94)) 2
  DrawMA $a.s10 $AMBER 1.5
  # candles
  for($k=$start;$k -lt $n;$k++){ $b=$a.bars[$k]; $up=$b.C -ge $b.O
    $col= if($up){$GREEN}else{$RED}; $pen=New-Object System.Drawing.Pen $col,1; $br=New-Object System.Drawing.SolidBrush $col
    $x=& $xAt $k; $yo=& $yAt $b.O; $yc=& $yAt $b.C; $yh=& $yAt $b.H; $yl=& $yAt $b.L
    $g.DrawLine($pen,[single]$x,[single]$yh,[single]$x,[single]$yl)
    $top=[math]::Min($yo,$yc); $bh=[math]::Max(1.0,[math]::Abs($yc-$yo))
    $g.FillRectangle($br,[single]($x-$cw/2),[single]$top,[single]$cw,[single]$bh) }
  # bull / bear markers on signals
  $mk=26
  for($k=$start;$k -lt $n;$k++){ $sg=$a.sig[$k]; if($sg -eq ""){continue}
    $b=$a.bars[$k]; $x=& $xAt $k
    if($sg -eq "buy" -and $null -ne $bullImg){ $y=(& $yAt $b.L)+6; $g.DrawImage($bullImg,[single]($x-$mk/2),[single]$y,[single]$mk,[single]$mk) }
    elseif($sg -eq "down" -and $null -ne $bearImg){ $y=(& $yAt $b.H)-$mk-6; $g.DrawImage($bearImg,[single]($x-$mk/2),[single]$y,[single]$mk,[single]$mk) }
  }
  # last price line
  $lp=& $yAt $closes[$n-1]
  $lpen=New-Object System.Drawing.Pen $INK,1; $lpen.DashStyle="Dash"
  $g.DrawLine($lpen,[single]$padL,[single]$lp,[single]($W-$padR),[single]$lp)
})

function Refresh-Data {
  $statusLbl.Text="fetching $($script:Symbol) $($script:Interval)..."
  $form.Refresh()
  try {
    $bars = Get-Series $script:Symbol $script:Interval
    $a = Analyze $bars $script:Interval
    $a | Add-Member -NotePropertyName bars -NotePropertyValue $bars
    $script:Data=$a
    $info.Text = (Signal-Info $a $script:Symbol $script:Interval $Account $RiskPct) + "`r`n" + ("-"*40) + "`r`n" + (Backtest-Text $a $script:Symbol $script:Interval) + "`r`n" + ("-"*40) + "`r`nBull = buy signal | Bear = downtrend/exit.`r`nEducational only - not financial advice.`r`nDoes NOT place orders."
    $statusLbl.Text = "$($script:Symbol) | $($TF[$script:Interval].label) | {0} bars | updated {1}" -f $bars.Count, (Get-Date -Format "HH:mm:ss")
    $chart.Invalidate()
  } catch {
    $statusLbl.Text = "data busy - retry"; $info.Text = "Couldn't load data:`r`n$($_.Exception.Message)`r`n`r`nYahoo may be rate-limiting. Click Refresh."
  }
}

$symBox.Add_SelectedIndexChanged({ $script:Symbol=$symBox.SelectedItem; Refresh-Data })
$tfBox.Add_SelectedIndexChanged({ $script:Interval= $(if($tfBox.SelectedIndex -eq 1){"1h"}else{"1d"}); Refresh-Data })
$btXBtn.Add_Click({ Refresh-Data })
$refBtn.Add_Click({ Refresh-Data })
$chart.Add_Resize({ $chart.Invalidate() })

# live refresh timer (reacts to live charts)
$timer=New-Object System.Windows.Forms.Timer
$timer.Interval = 60000   # 60s
$timer.Add_Tick({ Refresh-Data })
$form.Add_Shown({ Refresh-Data; $timer.Start() })
$form.Add_FormClosed({ $timer.Stop() })

[void]$form.ShowDialog()
