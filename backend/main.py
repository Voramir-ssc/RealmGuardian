"""
RealmGuardian Backend API
This module serves as the primary FastAPI application entry point.
It handles Blizzard API integrations, user authentication, and data synchronization
for World of Warcraft tokens, characters, and commodity prices.

[2026-02-20T10:35:00] STATUS: WORKING
- Battle.net OAuth Login and Return-Redirect redirect successfully
- Background Character Sync correctly fetches 40 chars and filters 404 ghosts
- Token and Item tracking fetch accurately
DO NOT BREAK THIS BASE FUNCTIONALITY.
"""

from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
import pydantic
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, get_db, SessionLocal
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
    """
    Background Task: Fetches the latest WoW Token price from the Blizzard API.
    It checks if the timestamp is already in the database and inserts a new record if not.
    """
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
    """
    Background Task: Updates prices for all user-tracked commodities.
    It takes an auction house snapshot from the Blizzard API, extracts the lowest prices
    for tracked items, and saves them to the price history table.
    """
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
    """
    FastAPI Lifespan Manager: Starts the background scheduler as soon as the API starts,
    and cleans up resources when the API stops.
    """
    # Startup: Start background task loop
    asyncio.create_task(scheduler())
    yield
    # Shutdown logic if needed

async def scheduler():
    """
    Background Scheduler: Runs in an infinite loop while the server is alive.
    Triggers token and commodity price updates every 30 minutes, and performs a database backup at 4 AM server time.
    """
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
    """ Health Check Endpoint: Returns the status of the backend server. """
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
def login(request: Request, tab: str = "settings"):
    """
    Initiates the Battle.net OAuth2 login flow.
    Passes the user's active frontend tab in the `state` parameter so they are returned
    to the correct page after authentication.
    """
    global blizzard_client
    if not blizzard_client:
        blizzard_client = BlizzardAPI(config.client_id, config.client_secret, config.region)

    # Hardcoded base URL for local development to ensure consistency
    base_url = "http://localhost:8000"
    redirect_uri = f"{base_url}/api/auth/callback"
    url = blizzard_client.get_authorization_url(redirect_uri, state=tab)
    return RedirectResponse(url)

@app.get('/api/auth/callback')
def auth_callback(code: str, state: str, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    OAuth2 Callback Callback Endpoint: Handles the response from Battle.net.
    Exchanges the authorization code for an access token, triggers a background character sync,
    and redirects the user back to the React frontend with its active tab restored.
    """
    global blizzard_client
    if not blizzard_client:
        blizzard_client = BlizzardAPI(config.client_id, config.client_secret, config.region)

    base_url = "http://localhost:8000"
    redirect_uri = f"{base_url}/api/auth/callback"
    user_token = blizzard_client.exchange_code_for_token(code, redirect_uri)
    
    if not user_token:
        raise HTTPException(status_code=400, detail="Failed to retrieve user token")

    # Start background sync
    background_tasks.add_task(sync_user_characters, user_token)
    
    # Redirect immediately
    return RedirectResponse(f"http://localhost:5173?connected=true&tab={state}")

def sync_user_characters(user_token: str):
    """
    Background Task: Syncs a user's World of Warcraft characters.
    Fetches the profile summary, then iterates through all characters to fetch their
    public/protected profiles (for gold) and achievement statistics (for playtime),
    updating the local database.
    """
    print("Starting background character sync...")
    new_db = SessionLocal()
    try:
        # Debug: Log start
        with open("debug_sync_start.txt", "w") as f:
            f.write(f"Sync started at {time.time()}\nToken: {user_token[:10]}...")

        # Fetch Profile
        profile = blizzard_client.get_account_profile(user_token)
        if not profile:
            print("Failed to fetch profile.")
            with open("debug_sync_error.txt", "w") as f:
                f.write("Failed to fetch profile (None returned)")
            return

        # Fetch Characters
        chars = profile.get('wow_accounts', [])
        all_characters = []
        for account in chars:
            all_characters.extend(account.get('characters', []))

        print(f"Found {len(all_characters)} characters.")
        
        with open("debug_sync_chars.txt", "w") as f:
            f.write(f"Found {len(all_characters)} characters.\n")
            import json
            f.write(json.dumps(all_characters, indent=2))
            
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        print(f"Sync Error: {e}")
        with open("debug_sync_crash.txt", "w") as f:
            f.write(str(e) + "\n" + err)
        # DEBUG: Dump account profile
        import json
        with open("debug_account.json", "w") as f:
            json.dump(profile, f, indent=4)
        return # Exit if main profile fetch failed

    try:
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

                    # Filter Ghost Characters (Deleted/Transferred) that return 404
                    if not protected_details and not public_details:
                        print(f"Skipping ghost character {char['name']}")
                        continue

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
                    # Note: Blizzard has completely removed 'Total time played' from the external Web API.
                    # This information is now only available via the in-game Lua API (/played).
                    
                    # Update DB
                    # Lookup by Blizzard ID (unique), NOT database ID
                    db_char = new_db.query(models.Character).filter_by(blizzard_id=char['id']).first()
                    
                    if not db_char:
                        db_char = models.Character(
                            blizzard_id=char['id'],
                            name=char['name'],
                            realm=char['realm']['name'],
                            level=char.get('level', 0),
                            gold=int(gold),
                            played_time=int(played_time),
                            last_updated=timestamp
                        )
                        if 'playable_class' in char:
                            db_char.class_name = char['playable_class']['name']
                        else:
                            db_char.class_name = char.get('character_class', {}).get('name', 'Unknown')
                            
                        new_db.add(db_char)
                    else:
                        db_char.name = char['name']
                        db_char.realm = char['realm']['name']
                        db_char.level = char['level']
                        db_char.gold = int(gold)
                        db_char.played_time = int(played_time)
                        db_char.last_updated = timestamp
                    
                    new_db.commit()
                    count += 1
                    print(f"Synced {char['name']}: {gold/10000}g, {played_time/3600}h")

                except Exception as e:
                    print(f"Failed to sync char {char.get('name')}: {e}")
                    with open(f"debug_sync_commit_error_{char.get('name')}.txt", "w") as f:
                         f.write(str(e))
                    continue
        
        print(f"Background sync complete. Processed {count} characters.")
        
    except Exception as e:
        print(f"Background sync failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        new_db.close()

@app.get('/api/user/characters')
def get_user_characters(db: Session = Depends(get_db)):
    """
    Retrieves the list of locally synced characters for the dashboard and calculates
    the total combined gold across all characters.
    """
    chars = db.query(models.Character).order_by(models.Character.level.desc()).all()
    total_gold = sum(c.gold for c in chars)
    return {
        "total_gold": total_gold,
        "characters": chars
    }


@app.get("/api/items/{item_id}/history")
def get_item_history(item_id: int, range: str = "14d", db: Session = Depends(get_db)):
    """
    Retrieves historical price data for a tracked item over a specified time range,
    downsampling data points to ensure efficient frontend rendering.
    """
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
    """ Trigger a manual SQLite database backup. """
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
    """
    Adds a new World of Warcraft item to the watchlist.
    Fetches the item's static details and icon from the Blizzard API before saving.
    """
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
    """ Retrieves all currently tracked items and their latest logged price for the Watchlist. """
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
    """ Removes an item from the watchlist. """
    item = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    
    db.delete(item)
    db.commit()
    return {'message': 'Item deleted'}

if __name__ == "__main__":
    import uvicorn
    # Listen on all interfaces so remote devices can connect
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
