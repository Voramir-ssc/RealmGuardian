#!/usr/bin/env bash
# RealmGuardian - Native Debian Dev/Start Script
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_DIR"

echo "========================================================"
echo "  Starting RealmGuardian natively on Debian"
echo "  Path: $REPO_DIR"
echo "========================================================"

# Check Python environment
if [ ! -d "backend/venv" ]; then
    echo "Python venv wird erstellt..."
    python3 -m venv backend/venv
    ./backend/venv/bin/pip install --upgrade pip
    ./backend/venv/bin/pip install -r backend/requirements.txt
fi

# Check Frontend Node environment
if [ ! -d "frontend/node_modules" ]; then
    echo "Node dependencies werden installiert..."
    cd frontend && npm install && cd ..
fi

echo "Starte Backend auf 0.0.0.0:8000 ..."
(cd backend && ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

echo "Starte Frontend Vite Dev Server auf 0.0.0.0:5173 ..."
(cd frontend && npm run dev -- --host 0.0.0.0) &
FRONTEND_PID=$!

echo "RealmGuardian laeuft! (Backend PID: $BACKEND_PID, Frontend PID: $FRONTEND_PID)"
echo "Druecke [STRG+C] zum Beenden beider Dienste."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait

