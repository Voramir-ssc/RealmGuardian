@echo off
setlocal enabledelayedexpansion

echo =========================================================
echo   Installing RealmGuardian Autostart (Windows Scheduled Task)
echo =========================================================

cd /d "%~dp0"
set "VBS_PATH=%CD%\start_watchdog_hidden.vbs"

schtasks /Create /TN "RealmGuardianWatchdog" /TR "wscript.exe \"%VBS_PATH%\"" /SC ONLOGON /RL HIGHEST /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: RealmGuardian Autostart Task registered successfully!
    echo RealmGuardian will now automatically start in the background when Windows boots up.
) else (
    echo.
    echo ERROR: Failed to register Windows Task. Please run this script as Administrator.
)

pause
