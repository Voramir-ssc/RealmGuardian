@echo off
echo Starting RealmGuardian...

cd %~dp0

:: Start Backend
start "RG Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

:: Start Frontend
start "RG Frontend" cmd /k "cd frontend && npm run dev"

echo Services started.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
