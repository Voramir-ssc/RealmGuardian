@echo off
echo Starting RealmGuardian...

cd %~dp0

:: Set Environment Paths (Python 3.12 & Node.js 24)
set "PYTHON_PATH=C:\Users\Stefan\AppData\Local\Programs\Python\Python312"
set "NODE_PATH=C:\Users\Stefan\AppData\Local\Microsoft\WinGet\Packages\OpenJS.NodeJS.LTS_Microsoft.Winget.Source_8wekyb3d8bbwe\node-v24.13.1-win-x64"

set "PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%NODE_PATH%;%PATH%"

:: Start Backend
start "RG Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

:: Start Frontend
start "RG Frontend" cmd /k "cd frontend && npm run dev"

echo Services started.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
