@echo off
title STRATA Live
echo Starting STRATA Live...
REM start the local server + data proxy (own window, minimized)
start "STRATA Live server" /min powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve-app.ps1"
REM give it a second to bind
ping -n 3 127.0.0.1 >nul
set "URL=http://localhost:8799/"
set "EDGE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
set "CHROME86=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if exist "%EDGE%"    ( start "" "%EDGE%"    --app=%URL% & goto done )
if exist "%CHROME%"  ( start "" "%CHROME%"  --app=%URL% & goto done )
if exist "%CHROME86%"( start "" "%CHROME86%" --app=%URL% & goto done )
start "" %URL%
:done
exit
