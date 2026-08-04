"""
RealmGuardian Backend API
This module serves as the primary FastAPI application entry point.
It sets up the routers, database connections, and background tasks.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
import asyncio
from contextlib import asynccontextmanager

import models
from database import engine
from config import config
from auto_restore import check_and_restore

# Background Tasks
from background_tasks import scheduler

# Routers
from routers import auth, dashboard, items, tasks, reports

# Attempt auto-restore before SQLAlchemy tries to bind/create tables
check_and_restore()
models.Base.metadata.create_all(bind=engine)

_background_tasks = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Manager: Starts the background scheduler as soon as the API starts,
    and cleans up resources when the API stops.
    """
    task = asyncio.create_task(scheduler())
    _background_tasks.add(task)
    yield

app = FastAPI(title="RealmGuardian API", lifespan=lifespan)

# Enable CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for development/tailscale
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """ Health Check Endpoint: Returns the status of the backend server. """
    return {
        "status": "online", 
        "message": "RealmGuardian Backend is running",
        "configured": bool(config.client_id and config.client_secret)
    }

# Include all modularized routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(items.router)
app.include_router(tasks.router)
app.include_router(reports.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    with open('debug_sync_crash.txt', 'w') as err_f:
        err_f.write(traceback.format_exc())
    return JSONResponse(status_code=500, content={'message': 'Internal Server Error'})

if __name__ == "__main__":
    import uvicorn
    # Listen on all interfaces so remote devices can connect
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
