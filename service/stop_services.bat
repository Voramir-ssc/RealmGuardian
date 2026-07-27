@echo off
echo ===================================================
echo   Stopping RealmGuardian Background Services
echo ===================================================

cd /d "%~dp0"

powershell -ExecutionPolicy Bypass -NoProfile -File "%CD%\stop_watchdog.ps1"

echo.
echo RealmGuardian Services successfully stopped.
