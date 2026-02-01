@echo off
echo Installing PyInstaller...
python -m pip install pyinstaller

echo Building EXE...
python -m PyInstaller --noconfirm --onefile --windowed --name "RealmGuardian" --icon=NONE --add-data "config.example.json;." main.py

echo.
echo Build complete! Check the 'dist' folder.
pause
