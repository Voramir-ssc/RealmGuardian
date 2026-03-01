@echo off
echo Starting RealmGuardian...

cd %~dp0
set "PATH=C:\Program Files\Python311;C:\Program Files\Python311\Scripts;C:\Program Files\nodejs;%PATH%"

:: Environment configured via PATH above

:: Start Backend
start "RG Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Start Frontend
start "RG Frontend" cmd /k "cd frontend && npm run dev"

echo Services started.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
