@echo off
REM Double-click to run the STRATA Trader. Passes through any extra flags.
REM   run.bat                 -> full ES backtest + live setup
REM   run.bat -All            -> scan every market's live setup
REM   run.bat -Symbol NQ=F    -> backtest Nasdaq
powershell -ExecutionPolicy Bypass -File "%~dp0strata-trader.ps1" %*
echo.
pause
