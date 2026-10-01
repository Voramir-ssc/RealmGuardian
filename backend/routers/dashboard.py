from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models
import analytics
from dependencies import get_db
from config import config

router = APIRouter(prefix="/api", tags=["Dashboard"])

@router.get('/user/gold-history')
def get_user_gold_history(db: Session = Depends(get_db)):
    """
    Retrieves the chronological history of the user's total account gold.
    Returns early snapshots for rendering historical charts.
    """
    history = db.query(models.AccountGoldHistory).order_by(models.AccountGoldHistory.timestamp.asc()).all()
    return {"history": history}

@router.get('/user/characters')
def get_user_characters(db: Session = Depends(get_db)):
    """
    Retrieves the list of locally synced characters for the dashboard and calculates
    the total combined gold across all characters.
    """
    chars = db.query(models.Character).all()
    
    main_name = config.main_character.get("name", "")
    main_realm = config.main_character.get("realm", "")
    
    def sort_key(c):
        is_main = (c.name.lower() == main_name.lower() and c.realm.lower() == main_realm.lower())
        # Sort main first (False < True, so not is_main puts main at top)
        # Then sort by level descending, then by item_level descending
        return (not is_main, -(c.level or 0), -(c.item_level or 0))
        
    chars.sort(key=sort_key)

    total_gold = sum(c.gold for c in chars)
    return {
        "total_gold": total_gold,
        "characters": chars
    }

@router.get("/token/latest")
def get_latest_token(db: Session = Depends(get_db)):
    """ Retrieves the latest recorded WoW token price. """
    latest = db.query(models.WowTokenHistory).order_by(models.WowTokenHistory.last_updated_timestamp.desc()).first()
    if not latest:
        return {"price": 0, "last_updated": 0, "formatted": "0g"}
    return {
        "price": latest.price,
        "last_updated": latest.last_updated_timestamp,
        "formatted": f"{latest.price / 10000:,.0f}g"
    }

@router.get("/token/history")
def get_token_history(range: str = "24h", db: Session = Depends(get_db)):
    """ Retrieves historical WoW Token prices downsampled for efficient charting. """
    now = datetime.utcnow()
    if range == "24h":
        start_time, interval_seconds = now - timedelta(hours=24), 0
    elif range == "7d":
        start_time, interval_seconds = now - timedelta(days=7), 3600
    elif range == "14d":
        start_time, interval_seconds = now - timedelta(days=14), 7200
    elif range == "30d":
        start_time, interval_seconds = now - timedelta(days=30), 14400
    else:
        start_time, interval_seconds = now - timedelta(hours=24), 0
    
    start_timestamp = start_time.timestamp()
    query = db.query(models.WowTokenHistory)\
        .filter(models.WowTokenHistory.last_updated_timestamp >= start_timestamp)\
        .order_by(models.WowTokenHistory.last_updated_timestamp.asc())

    results = query.all()
    if interval_seconds == 0 or not results:
        return results

    downsampled = []
    last_bucket = 0
    for entry in results:
        bucket = (entry.last_updated_timestamp // interval_seconds) * interval_seconds
        if bucket > last_bucket:
            downsampled.append(entry)
            last_bucket = bucket
    return downsampled

@router.get("/analysis/glyphs")
def get_glyph_analysis(db: Session = Depends(get_db)):
    """ Retrieves liquidity and profit score analysis for Glyphs. """
    return analytics.calculate_liquidity_score(db)
