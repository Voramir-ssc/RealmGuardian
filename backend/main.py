from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, get_db
from config import config
from blizzard_api import BlizzardAPI
import asyncio
import time
from datetime import datetime
from contextlib import asynccontextmanager

models.Base.metadata.create_all(bind=engine)

# Global API Client
blizzard_client = None

async def update_token_price(db: Session):
    global blizzard_client
    if not config.client_id or not config.client_secret:
        print("Missing Blizzard API credentials.")
        return

    if not blizzard_client:
        blizzard_client = BlizzardAPI(config.client_id, config.client_secret, config.region)

    print("Fetching WoW Token Price...")
    try:
        data = blizzard_client.get_wow_token_price()
        if data:
            price_copper = data.get("price")
            last_updated = data.get("last_updated_timestamp")

            # Check if this timestamp already exists to avoid duplicates
            existing = db.query(models.WowTokenHistory).filter_by(last_updated_timestamp=last_updated).first()
            if not existing:
                new_entry = models.WowTokenHistory(
                    price=price_copper,
                    last_updated_timestamp=last_updated,
                    region=config.region
                )
                db.add(new_entry)
                db.commit()
                print(f"Updated Token Price: {price_copper / 10000}g")
            else:
                print("Token price already up to date.")
    except Exception as e:
        print(f"Error updating token price: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background task loop
    asyncio.create_task(scheduler())
    yield
    # Shutdown logic if needed

async def scheduler():
    while True:
        try:
            # Create a new session for the background task
            db = next(get_db())
            await update_token_price(db)
        except Exception as e:
            print(f"Scheduler Error: {e}")
        finally:
            if 'db' in locals():
                db.close()
        
        # Wait for 30 minutes
        await asyncio.sleep(1800)

        # Run Backup every ~24 hours (48 * 30min)
        # For simplicity, we can check the hour or just use a counter.
        # However, a simpler approach is to run it on startup or specific time.
        # Let's keep it simple: run backup if hour is 4 AM (server time)
        now = datetime.now()
        if now.hour == 4 and now.minute < 30:
             try:
                 print("Starting daily backup...")
                 # Run synchronously to avoid complex async file IO issues, 
                 # as database copy is fast for SQLite
                 from backup import perform_backup
                 perform_backup()
             except Exception as e:
                 print(f"Backup Error: {e}")

app = FastAPI(title="RealmGuardian API", lifespan=lifespan)

# Enable CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online", 
        "message": "RealmGuardian Backend is running",
        "configured": bool(config.client_id and config.client_secret)
    }

@app.get("/api/token/latest")
def get_latest_token(db: Session = Depends(get_db)):
    latest = db.query(models.WowTokenHistory).order_by(models.WowTokenHistory.last_updated_timestamp.desc()).first()
    if not latest:
        return {"price": 0, "last_updated": 0, "formatted": "0g"}
    return {
        "price": latest.price,
        "last_updated": latest.last_updated_timestamp,
        "formatted": f"{latest.price / 10000:,.0f}g"
    }

from datetime import datetime, timedelta

@app.get("/api/token/history")
def get_token_history(range: str = "24h", db: Session = Depends(get_db)):
    now = datetime.utcnow()
    
    if range == "24h":
        start_time = now - timedelta(hours=24)
        interval_seconds = 0 # No aggregation
    elif range == "7d":
        start_time = now - timedelta(days=7)
        interval_seconds = 3600 # 1 hour
    elif range == "1m":
        start_time = now - timedelta(days=30)
        interval_seconds = 14400 # 4 hours
    elif range == "3m":
        start_time = now - timedelta(days=90)
        interval_seconds = 43200 # 12 hours
    elif range == "1y":
        start_time = now - timedelta(days=365)
        interval_seconds = 86400 # 24 hours
    else:
        # Default to 24h
        start_time = now - timedelta(hours=24)
        interval_seconds = 0

    # Convert to timestamp for basic filtering
    start_timestamp = start_time.timestamp()

    # Query all data in range
    query = db.query(models.WowTokenHistory)\
        .filter(models.WowTokenHistory.last_updated_timestamp >= start_timestamp)\
        .order_by(models.WowTokenHistory.last_updated_timestamp.asc())
        
    results = query.all()

    if interval_seconds == 0 or not results:
        return results

    # Basic Downsampling in Python (Group by interval)
    downsampled = []
    last_bucket = 0
    
    for entry in results:
        # Calculate bucket (start of interval)
        bucket = (entry.last_updated_timestamp // interval_seconds) * interval_seconds
        
        if bucket > last_bucket:
            downsampled.append(entry)
            last_bucket = bucket
            
    return downsampled

