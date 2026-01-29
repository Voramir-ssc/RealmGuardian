@echo off
set "VENV_DIR=venv"

echo Prüfe virtuelle Umgebung...
if not exist "%VENV_DIR%" (
    echo Erstelle virtuelle Umgebung...
    python -m venv %VENV_DIR%
)

echo Aktiviere virtuelle Umgebung...
call %VENV_DIR%\Scripts\activate

echo Installiere/Pruefe Abhaengigkeiten...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Fehler beim Installieren der Abhaengigkeiten!
    pause
    exit /b
)

echo Starte Applikation...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Ein Fehler ist aufgetreten. Die App wurde beendet.
    pause
)
