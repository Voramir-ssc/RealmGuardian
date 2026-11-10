@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

set "PY_EXE=backend\venv\Scripts\python.exe"
if not exist "!PY_EXE!" set "PY_EXE=python"

!PY_EXE! export_migration_bundle.py

echo.
pause
