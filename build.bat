@echo off
set "VENV_DIR=venv"

echo Checking for virtual environment...
if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
) else (
    echo WARNING: Virtual environment not found. Building with system Python.
    echo This might fail if customtkinter is not installed globally.
)

echo Installing/Updating PyInstaller...
python -m pip install pyinstaller

echo Installing dependencies (just in case)...
python -m pip install -r requirements.txt

echo Building EXE...
REM --collect-all customtkinter is important to gather theme files and the module itself if hidden
python -m PyInstaller --noconfirm --onefile --windowed --name "RealmGuardian" --icon=NONE --collect-all customtkinter --add-data "config.example.json;." main.py

echo.
echo Build complete! Check the 'dist' folder.
pause
