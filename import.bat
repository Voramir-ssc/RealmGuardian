@echo off
set "VENV_DIR=venv"

if not exist "%VENV_DIR%" (
    echo Fehler: Virtuelle Umgebung nicht gefunden. Bitte zuerst run.bat starten!
    pause
    exit /b
)

if "%~1"=="" (
    echo Bitte ziehe eine CSV oder Excel Datei auf dieses Skript!
    pause
    exit /b
)

echo Importiere: %~1
call %VENV_DIR%\Scripts\activate
python import_characters.py "%~1"

echo.
echo Fertig.
pause
