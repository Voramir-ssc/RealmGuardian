import asyncio
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import sqlalchemy
import json

import models
from config import config
from dependencies import get_db, get_blizzard_client
from database import SessionLocal
import backup
from discord_report import send_weekly_report

async def update_token_price(db: Session):
    """
    Background Task: Fetches the latest WoW Token price from the Blizzard API.
    It checks if the timestamp is already in the database and inserts a new record if not.
    """
    blizzard_client = get_blizzard_client()
    if not config.client_id or not config.client_secret:
        print("Missing Blizzard API credentials.")
        return

    print("Fetching WoW Token Price...")
    try:
        data = blizzard_client.get_wow_token_price()
        if data:
            price_copper = data.get("price")
            last_updated_ms = data.get("last_updated_timestamp")
            last_updated = int(last_updated_ms / 1000)

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
    """
    blizzard_client = get_blizzard_client()
    try:
        print("Updating Commodity and Realm Prices...")
        tracked_items = db.query(models.TrackedItem).all()
        if not tracked_items:
            print("No tracked items. Skipping update.")
            return

        tracked_ids = {item.item_id for item in tracked_items}
        min_prices = {} 
        total_quantities = {}

        # Fetch Commodity snapshot
        c_snapshot = blizzard_client.get_commodity_price_snapshot()
        if c_snapshot and 'auctions' in c_snapshot:
            c_auctions = c_snapshot['auctions']
            print(f"Processing {len(c_auctions)} commodity auctions...")
            for auction in c_auctions:
                item_id = auction['item']['id']
                if item_id in tracked_ids:
                    price = auction.get('unit_price', auction.get('buyout', 0))
                    qty = auction.get('quantity', 1)
                    if item_id not in total_quantities: total_quantities[item_id] = 0
                    total_quantities[item_id] += qty
                    if price > 0:
                        if item_id not in min_prices or price < min_prices[item_id]:
                            min_prices[item_id] = price

        # Fetch Realm snapshot
        home_realm_id = getattr(config, 'home_realm_id', '1618')
        r_snapshot = blizzard_client.get_realm_auctions_snapshot(home_realm_id)
        if r_snapshot and 'auctions' in r_snapshot:
            r_auctions = r_snapshot['auctions']
            print(f"Processing {len(r_auctions)} realm auctions for realm {home_realm_id}...")
            for auction in r_auctions:
                item_id = auction['item']['id']
                if item_id in tracked_ids:
                    price = auction.get('unit_price', auction.get('buyout', 0))
                    qty = auction.get('quantity', 1)
                    if item_id not in total_quantities: total_quantities[item_id] = 0
                    total_quantities[item_id] += qty
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
                    quantity=total_quantities.get(item.item_id, 1),
                    timestamp=timestamp
                ))
                print(f"Updated {item.name}: {min_prices[item.item_id] / 10000}g (Qty: {total_quantities.get(item.item_id, 1)})")
        
        if new_entries:
            db.add_all(new_entries)
            db.commit()
    except Exception as e:
        print(f"Error updating commodities: {e}")

async def background_commodity_update():
    """Helper to run update in background with its own DB session"""
    db = next(get_db())
    try:
        await update_commodity_prices(db)
    finally:
        db.close()

def sync_user_characters(user_token: str):
    """
    Background Task: Syncs a user's World of Warcraft characters.
    """
    blizzard_client = get_blizzard_client()
    print("Starting background character sync...")
    new_db = SessionLocal()
    try:
        profile = blizzard_client.get_account_profile(user_token)
        if not profile:
            print("Failed to fetch profile.")
            return

        timestamp = datetime.utcnow()
        count = 0
        
        for account in profile.get('wow_accounts', []):
            for char in account.get('characters', []):
                try:
                    realm_id = char['realm']['id']
                    char_id = char['id']
                    
                    protected_details = blizzard_client.get_protected_character_profile(user_token, realm_id, char_id)
                    public_details = blizzard_client.get_character_profile(user_token, char['realm']['slug'], char['name'])

                    if not protected_details and not public_details:
                        db_ghost = new_db.query(models.Character).filter_by(blizzard_id=char['id']).first()
                        if db_ghost:
                            new_db.delete(db_ghost)
                            new_db.commit()
                        continue

                    gold = None
                    if protected_details and 'money' in protected_details: gold = protected_details['money']
                    elif public_details and 'money' in public_details: gold = public_details['money']
                    
                    stats = blizzard_client.get_character_statistics(user_token, char['realm']['slug'], char['name'])
                    item_level = public_details.get('equipped_item_level', 0) if public_details else 0

                    equipment_json = None
                    try:
                        raw_equip = blizzard_client.get_character_equipment(user_token, char['realm']['slug'], char['name'])
                        if raw_equip and 'equipped_items' in raw_equip:
                            parsed_items = []
                            for item in raw_equip['equipped_items']:
                                parsed_items.append({
                                    "id": item.get('item', {}).get('id'),
                                    "slot": item.get('slot', {}).get('type'),
                                    "name": item.get('name', 'Unknown'),
                                    "quality": item.get('quality', {}).get('type', 'COMMON'),
                                    "level": item.get('level', {}).get('value', 0)
                                })
                            equipment_json = json.dumps(parsed_items)
                    except Exception as eq_err: pass
                        
                    professions_json = None
                    try:
                        raw_professions = blizzard_client.get_character_professions(user_token, char['realm']['slug'], char['name'])
                        if raw_professions and 'primaries' in raw_professions:
                            parsed_professions = []
                            for prof in raw_professions['primaries']:
                                prof_data = {"name": prof.get('profession', {}).get('name', 'Unknown'), "tiers": []}
                                for tier in prof.get('tiers', []):
                                    prof_data["tiers"].append({
                                        "name": tier.get('tier', {}).get('name', 'Unknown Expansion'),
                                        "skill_points": tier.get('skill_points', 0),
                                        "max_skill_points": tier.get('max_skill_points', 0)
                                    })
                                parsed_professions.append(prof_data)
                            professions_json = json.dumps(parsed_professions)
                    except Exception as prof_err: pass

                    played_time = 0
                    delves_completed = 0
                    delves_max_tier = 0
                    if stats and 'categories' in stats:
                        for cat in stats['categories']:
                            for s in cat.get('statistics', []):
                                sid = s.get('id')
                                quant = int(s.get('quantity', 0))
                                if sid == 40734: delves_completed = quant
                                name_lower = s.get('name', '').lower()
                                if 'stufe' in name_lower or 'tier' in name_lower or 'level' in name_lower:
                                    if 'tiefe' in name_lower or 'delve' in name_lower:
                                        import re
                                        match = re.search(r'(?:stufe|tier|level)\s*(\d+)', name_lower)
                                        if match and quant > 0:
                                            tier = int(match.group(1))
                                            if tier > delves_max_tier: delves_max_tier = tier
                    
                    db_char = new_db.query(models.Character).filter_by(blizzard_id=char['id']).first()
                    
                    if not db_char:
                        db_char = models.Character(
                            blizzard_id=char['id'], name=char['name'], realm=char['realm']['name'],
                            level=char.get('level', 0), item_level=item_level, equipment=equipment_json,
                            professions=professions_json, gold=int(gold) if gold is not None else 0,
                            played_time=int(played_time), delves_completed=delves_completed,
                            delves_max_tier=delves_max_tier, last_updated=timestamp
                        )
                        if 'playable_class' in char: db_char.class_name = char['playable_class']['name']
                        else: db_char.class_name = char.get('character_class', {}).get('name', 'Unknown')
                        new_db.add(db_char)
                    else:
                        db_char.name = char['name']
                        db_char.realm = char['realm']['name']
                        db_char.level = char['level']
                        db_char.item_level = item_level
                        db_char.equipment = equipment_json
                        db_char.professions = professions_json
                        if gold is not None: db_char.gold = int(gold)
                        db_char.played_time = int(played_time)
                        db_char.delves_completed = delves_completed
                        db_char.delves_max_tier = delves_max_tier
                        db_char.last_updated = timestamp
                    
                    new_db.commit()
                    count += 1
                except Exception:
                    continue
        
        print(f"Background sync complete. Processed {count} characters.")

        total_account_gold = new_db.query(models.Character).with_entities(sqlalchemy.func.sum(models.Character.gold)).scalar() or 0
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        gold_snapshot = new_db.query(models.AccountGoldHistory).filter(models.AccountGoldHistory.timestamp >= today).first()
        if gold_snapshot:
            gold_snapshot.total_gold = total_account_gold
            gold_snapshot.timestamp = datetime.utcnow()
        else:
            gold_snapshot = models.AccountGoldHistory(total_gold=total_account_gold, timestamp=datetime.utcnow())
            new_db.add(gold_snapshot)
        new_db.commit()
        
    except Exception as e:
        print(f"Background sync failed: {e}")
    finally:
        new_db.close()

def check_and_reset_tasks(db: Session):
    now = datetime.utcnow()
    tasks = db.query(models.UserTask).filter(models.UserTask.is_completed == True).all()
    count = 0
    
    for task in tasks:
        if not task.last_completed_at: continue
        completed_date = task.last_completed_at
        should_reset = False
        
        if task.type == 'daily':
            current_reset = now.replace(hour=8, minute=0, second=0, microsecond=0)
            if now < current_reset: current_reset -= timedelta(days=1)
            if completed_date < current_reset: should_reset = True
        elif task.type == 'weekly':
            days_since_wednesday = (now.weekday() - 2) % 7
            current_reset = now.replace(hour=8, minute=0, second=0, microsecond=0) - timedelta(days=days_since_wednesday)
            if now.weekday() == 2 and now.hour < 8: current_reset -= timedelta(days=7)
            if completed_date < current_reset: should_reset = True
        elif task.type == 'monthly':
            current_reset = now.replace(day=1, hour=8, minute=0, second=0, microsecond=0)
            if now < current_reset:
                last_month = (now.month - 1) or 12
                year = now.year if last_month != 12 else now.year - 1
                current_reset = current_reset.replace(year=year, month=last_month)
            if completed_date < current_reset: should_reset = True
                
        if should_reset:
            task.is_completed = False
            task.last_completed_at = None
            count += 1
            
    if count > 0:
        db.commit()

async def scheduler():
    """
    Background Scheduler: Runs in an infinite loop while the server is alive.
    Triggers token and commodity price updates every 30 minutes, and performs a database backup at 4 AM server time.
    """
    while True:
        try:
            db = next(get_db())
            check_and_reset_tasks(db)
            
            local_now = datetime.now()
            if local_now.weekday() in [2, 5] and local_now.hour >= 20:
                last_snap = db.query(models.WeeklyReportSnapshot).order_by(models.WeeklyReportSnapshot.timestamp.desc()).first()
                if not last_snap or (datetime.utcnow() - last_snap.timestamp).total_seconds() > 43200:
                    print("Conditions met for Discord Report! Triggering background thread...")
                    import threading
                    threading.Thread(target=send_weekly_report).start()
            
            await update_token_price(db)
            await update_commodity_prices(db)

            token_entry = db.query(models.UserAccessToken).first()
            if token_entry:
                if time.time() < token_entry.expires_at:
                    import threading
                    threading.Thread(target=sync_user_characters, args=(token_entry.access_token,)).start()
                else:
                    db.delete(token_entry)
                    db.commit()

        except Exception as e:
            print(f"Scheduler Error: {e}")
        finally:
            if 'db' in locals():
                db.close()
        
        await asyncio.sleep(1800)

        now = datetime.now()
        if now.hour == 4 and now.minute < 30:
             try:
                 backup.create_backup()
             except Exception:
                 pass
