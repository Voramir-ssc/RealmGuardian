@echo off
echo ===================================================
echo   Starting RealmGuardian (Hardened Background Mode)
echo ===================================================

cd /d "%~dp0"
call service\start_services.bat

echo.
echo RealmGuardian is running in hardened background mode.
echo No CMD windows will stay open or be affected by other scripts.
echo Automatic recovery daemon is active.
