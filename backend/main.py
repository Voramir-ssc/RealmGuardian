from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, get_db
from config import config
from blizzard_api import BlizzardAPI
import asyncio
import time
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

@app.get("/api/token/history")
def get_token_history(limit: int = 100, db: Session = Depends(get_db)):
    history = db.query(models.WowTokenHistory).order_by(models.WowTokenHistory.last_updated_timestamp.desc()).limit(limit).all()
    return history

