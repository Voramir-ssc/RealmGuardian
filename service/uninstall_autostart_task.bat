@echo off
echo =========================================================
echo   Removing RealmGuardian Autostart (Windows Scheduled Task)
echo =========================================================

schtasks /Delete /TN "RealmGuardianWatchdog" /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: RealmGuardian Autostart Task removed.
) else (
    echo.
    echo Task was not found or failed to delete.
)

pause
