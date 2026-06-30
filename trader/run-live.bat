@echo off
REM Double-click to open the STRATA Live charting app (bull/bear signals on a live chart).
powershell -ExecutionPolicy Bypass -File "%~dp0strata-live.ps1" %*
if errorlevel 1 ( echo. & echo The app exited with an error above. & pause )
