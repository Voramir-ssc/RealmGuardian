from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
import pydantic
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, get_db
from config import config
from blizzard_api import BlizzardAPI
import asyncio
import time
from datetime import datetime, timedelta
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
            # Blizzard returns milliseconds, we store seconds
            last_updated_ms = data.get("last_updated_timestamp")
            last_updated = int(last_updated_ms / 1000)

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

@app.get("/api/token/history")
def get_token_history(range: str = "24h", db: Session = Depends(get_db)):
    now = datetime.utcnow()
    
    # Refined Time Ranges & Downsampling
    # 24h: 20min intervals (raw)
    # 7d: 1 hour intervals
    # 14d: 2 hour intervals
    # 30d: 4 hour intervals
    
    if range == "24h":
        start_time = now - timedelta(hours=24)
        interval_seconds = 0
    elif range == "7d":
        start_time = now - timedelta(days=7)
        interval_seconds = 3600
    elif range == "14d":
        start_time = now - timedelta(days=14)
        interval_seconds = 7200
    elif range == "30d":
        start_time = now - timedelta(days=30)
        interval_seconds = 14400
    else:
        # Default
        start_time = now - timedelta(hours=24)
        interval_seconds = 0
    
    start_timestamp = start_time.timestamp()

    # Query
    query = db.query(models.WowTokenHistory)\
        .filter(models.WowTokenHistory.last_updated_timestamp >= start_timestamp)\
        .order_by(models.WowTokenHistory.last_updated_timestamp.asc())

    results = query.all()

    if interval_seconds == 0 or not results:
        return results

    # Downsampling
    downsampled = []
    last_bucket = 0
    for entry in results:
        bucket = (entry.last_updated_timestamp // interval_seconds) * interval_seconds
        if bucket > last_bucket:
            downsampled.append(entry)
            last_bucket = bucket
            
    return downsampled


# --- Auth & Character Endpoints ---

from fastapi.responses import RedirectResponse

from fastapi import FastAPI, Depends, HTTPException, Request

@app.get('/api/auth/login')
def login(request: Request):
    # Hardcoded base URL for local development to ensure consistency
    base_url = "http://localhost:8000"
    redirect_uri = f"{base_url}/api/auth/callback"
    url = blizzard_client.get_authorization_url(redirect_uri)
    return RedirectResponse(url)

@app.get('/api/auth/callback')
def auth_callback(code: str, state: str, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    base_url = "http://localhost:8000"
    redirect_uri = f"{base_url}/api/auth/callback"
    user_token = blizzard_client.exchange_code_for_token(code, redirect_uri)
    
    if not user_token:
        raise HTTPException(status_code=400, detail="Failed to retrieve user token")

    # Start background sync
    background_tasks.add_task(sync_user_characters, user_token, db)
    
    # Redirect immediately
    return RedirectResponse("http://localhost:5173?connected=true")

def sync_user_characters(user_token: str, db: Session):
    print("Starting background character sync...")
    try:
        # Fetch Profile
        profile = blizzard_client.get_account_profile(user_token)
        
        if not profile or 'wow_accounts' not in profile:
            print("No WoW accounts found in background sync.")
            return

        # DEBUG: Dump account profile
        import json
        with open("debug_account.json", "w") as f:
            json.dump(profile, f, indent=4)

        timestamp = datetime.utcnow()
        count = 0
        
        for account in profile['wow_accounts']:
            for char in account.get('characters', []):
                try:
                    realm_id = char['realm']['id']
                    char_id = char['id']
                    
                    # Fetch Protected Profile (for Gold)
                    protected_details = blizzard_client.get_protected_character_profile(user_token, realm_id, char_id)
                    
                    # Fetch Public Profile (Fallback)
                    public_details = blizzard_client.get_character_profile(user_token, char['realm']['slug'], char['name'])

                    # Determine Gold
                    gold = 0
                    if protected_details and 'money' in protected_details:
                        gold = protected_details['money']
                    elif public_details and 'money' in public_details:
                        gold = public_details['money']
                    
                    # Fetch Achievements Statistics for Playtime
                    stats = blizzard_client.get_character_statistics(user_token, char['realm']['slug'], char['name'])
                    
                    # DEBUG: Dump details
                    with open(f"debug_char_{char['name']}.json", "w") as f:
                        json.dump({"protected": protected_details, "public": public_details, "stats": stats}, f, indent=4)

                    played_time = 0
                    # Parse Playtime (Recursive search for "Total time played")
                    if stats and 'categories' in stats:
                        def find_played_time(categories):
                            for cat in categories:
                                if 'statistics' in cat:
                                    for stat in cat['statistics']:
                                        if stat.get('name') == 'Total time played':
                                            # format is likely milliseconds in 'quantity'
                                            return stat.get('quantity', 0) / 1000
                                if 'sub_categories' in cat:
                                    res = find_played_time(cat['sub_categories'])
                                    if res: return res
                            return 0
                        
                        played_time = find_played_time(stats['categories'])
                    
                    # Update DB
                    db_char = db.query(models.Character).filter_by(id=char['id']).first()
                    if not db_char:
                        db_char = models.Character(
                            id=char['id'],
                            name=char['name'],
                            realm=char['realm']['name'],
                            region="eu",
                            level=char['level'],
                            gold=int(gold),
                            played_time=int(played_time),
                            last_updated=timestamp
                        )
                        if 'playable_class' in char:
                            db_char.character_class = char['playable_class']['name']
                            
                        db.add(db_char)
                    else:
                        db_char.name = char['name']
                        db_char.realm = char['realm']['name']
                        db_char.level = char['level']
                        db_char.gold = int(gold)
                        db_char.played_time = int(played_time)
                        db_char.last_updated = timestamp
                    
                    db.commit() # Commit each char to show progress? Or batch? Commit each is safer for now.
                    count += 1
                    print(f"Synced {char['name']}: {gold/10000}g, {played_time/3600}h")

                except Exception as e:
                    print(f"Failed to sync char {char.get('name')}: {e}")
                    continue
        
        print(f"Background sync complete. Processed {count} characters.")
        
    except Exception as e:
        print(f"Background sync failed: {e}")
        import traceback
        traceback.print_exc()

@app.get('/api/user/characters')
def get_user_characters(db: Session = Depends(get_db)):
    chars = db.query(models.Character).order_by(models.Character.level.desc()).all()
    total_gold = sum(c.gold for c in chars)
    return {
        "total_gold": total_gold,
        "characters": chars
    }


@app.get("/api/items/{item_id}/history")
def get_item_history(item_id: int, range: str = "14d", db: Session = Depends(get_db)):
    # Find internal ID first
    tracked = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == item_id).first()
    if not tracked:
         raise HTTPException(status_code=404, detail='Item not tracked')
         
    now = datetime.utcnow()
    
    if range == "24h":
        start_time = now - timedelta(hours=24)
        interval_seconds = 0
    elif range == "7d":
        start_time = now - timedelta(days=7)
        interval_seconds = 3600
    elif range == "14d":
        start_time = now - timedelta(days=14)
        interval_seconds = 7200
    elif range == "30d":
        start_time = now - timedelta(days=30)
        interval_seconds = 14400
    else:
        start_time = now - timedelta(days=14)
        interval_seconds = 7200 # Default to 14d for items

    start_timestamp = start_time.timestamp()
    
    query = db.query(models.ItemPriceHistory)\
        .filter(models.ItemPriceHistory.item_id == tracked.id)\
        .filter(models.ItemPriceHistory.timestamp >= start_time)\
        .order_by(models.ItemPriceHistory.timestamp.asc())
        
    results = query.all()
    
    if interval_seconds == 0 or not results:
        # Transform for frontend (needs timestamp field similar to token)
        return [{"price": r.buyout, "last_updated_timestamp": r.timestamp.timestamp()} for r in results]

    downsampled = []
    last_bucket = 0
    for entry in results:
        ts = entry.timestamp.timestamp()
        bucket = (ts // interval_seconds) * interval_seconds
        if bucket > last_bucket:
            downsampled.append({"price": entry.buyout, "last_updated_timestamp": ts})
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

from fastapi import BackgroundTasks

async def background_commodity_update():
    # Helper to run update in background with its own DB session
    db = next(get_db()) # Assuming get_db provides a SessionLocal equivalent
    try:
        await update_commodity_prices(db)
    finally:
        db.close()

@app.post('/api/items')
def add_tracked_item(item_req: ItemRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Check if already exists
    exists = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == item_req.item_id).first()
    if exists:
        raise HTTPException(status_code=400, detail='Item already tracked')

    # Fetch details from Blizzard
    details = blizzard_client.get_item_details(item_req.item_id)
    if not details:
        raise HTTPException(status_code=404, detail='Item not found on Blizzard API')

    # Fetch media
    media = blizzard_client.get_item_media(item_req.item_id)
    icon_url = None
    if media and 'assets' in media:
        icon_url = media['assets'][0]['value']
    
    # Create Item
    new_item = models.TrackedItem(
        item_id=details['id'],
        name=details['name'],
        icon_url=icon_url,
        quality=details['quality']['type']
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    # Trigger immediate price update
    background_tasks.add_task(background_commodity_update)
    
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
