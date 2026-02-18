from fastapi import FastAPI, Depends, HTTPException
import pydantic
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
import backup

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

async def update_commodity_prices(db: Session):
    try:
        print("Updating Commodity Prices...")
        tracked_items = db.query(models.TrackedItem).all()
        if not tracked_items:
            print("No tracked items. Skipping commodity update.")
            return

        # Fetch snapshot
        snapshot = blizzard_client.get_commodity_price_snapshot()
        if not snapshot or 'auctions' not in snapshot:
            return

        tracked_ids = {item.item_id for item in tracked_items}
        min_prices = {} 

        print(f"Processing {len(snapshot['auctions'])} auctions for {len(tracked_ids)} tracked items...")
        
        for auction in snapshot['auctions']:
            item_id = auction['item']['id']
            if item_id in tracked_ids:
                price = auction.get('unit_price', auction.get('buyout', 0))
                if price > 0:
                    if item_id not in min_prices or price < min_prices[item_id]:
                        min_prices[item_id] = price
        
        new_entries = []
        timestamp = datetime.utcnow()
        
        for item in tracked_items:
            if item.item_id in min_prices:
                new_entries.append(models.ItemPriceHistory(
                    item_id=item.id,
                    buyout=min_prices[item.item_id],
                    timestamp=timestamp
                ))
                print(f"Updated {item.name}: {min_prices[item.item_id] / 10000}g")
        
        if new_entries:
            db.add_all(new_entries)
            db.commit()
    except Exception as e:
        print(f"Error updating commodities: {e}")

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
            await update_commodity_prices(db)
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
                 # copying a small DB is fast enough.
                 backup.create_backup()
             except Exception as e:
                 print(f"Backup Error: {e}")

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
    allow_origins=["*"], # Allow all for development/tailscale
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


@app.post('/api/backup')
def trigger_backup():
    success = backup.create_backup()
    if success:
        return {'status': 'success', 'message': 'Backup created'}
    else:
        raise HTTPException(status_code=500, detail='Backup failed')


# --- Item Tracking Endpoints ---

class ItemRequest(pydantic.BaseModel):
    item_id: int

@app.post('/api/items')
def add_tracked_item(item_req: ItemRequest, db: Session = Depends(get_db)):
    # Check if already exists
    exists = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == item_req.item_id).first()
    if exists:
        raise HTTPException(status_code=400, detail='Item already tracked')

    # Fetch details from Blizzard
    details = blizzard_client.get_item_details(item_req.item_id)
    if not details:
        raise HTTPException(status_code=404, detail='Item not found on Blizzard API')

    # Create Item
    new_item = models.TrackedItem(
        item_id=details['id'],
        name=details['name'],
        icon_url=details['media']['assets'][0]['value'] if 'media' in details else None,
        quality=details['quality']['type']
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get('/api/items')
def get_tracked_items(db: Session = Depends(get_db)):
    items = db.query(models.TrackedItem).all()
    result = []
    for item in items:
        # Get latest price
        latest = db.query(models.ItemPriceHistory)\
            .filter(models.ItemPriceHistory.item_id == item.id)\
            .order_by(models.ItemPriceHistory.timestamp.desc())\
            .first()
        
        item_data = {
            "id": item.id,
            "item_id": item.item_id,
            "name": item.name,
            "icon_url": item.icon_url,
            "quality": item.quality,
            "current_price": latest.buyout if latest else 0,
            "last_updated": latest.timestamp if latest else None
        }
        result.append(item_data)
    return result

@app.delete('/api/items/{item_id}')
def delete_tracked_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    
    db.delete(item)
    db.commit()
    return {'message': 'Item deleted'}
