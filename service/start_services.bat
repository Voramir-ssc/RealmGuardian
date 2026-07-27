@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo   Starting RealmGuardian Background Service Daemon
echo ===================================================

cd /d "%~dp0"

:: Run VBScript to start PowerShell Watchdog completely hidden without CMD window
wscript //nologo start_watchdog_hidden.vbs

echo Services started successfully in the background.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Logs are saved in: service\logs\
