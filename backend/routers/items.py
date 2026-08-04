import pydantic
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

import models
from dependencies import get_db, get_blizzard_client
from background_tasks import background_commodity_update

router = APIRouter(prefix="/api", tags=["Items & Crafting"])

class ItemRequest(pydantic.BaseModel):
    item_id: int

@router.get('/items/search')
def search_items(q: str):
    """
    Searches for items by German name using the Blizzard API.
    Returns a list of items with id, name, and icon.
    """
    if not q or len(q) < 3: return []
    blizzard_client = get_blizzard_client()
    search_results = blizzard_client.search_items_by_name(q)
    if not search_results or "results" not in search_results: return []

    items = []
    for entry in search_results["results"]:
        data = entry.get("data", {})
        item_id = data.get("id")
        
        name_dict = data.get("name", {})
        name = name_dict.get("de_DE") or name_dict.get("en_US") or "Unknown Item"
        
        if not item_id: continue

        media = blizzard_client.get_item_media(item_id)
        icon_url = None
        if media and 'assets' in media:
            for asset in media['assets']:
                if asset['key'] == 'icon':
                    icon_url = asset['value']
                    break

        items.append({"id": item_id, "name": name, "icon_url": icon_url})
    return items

@router.post('/items')
def add_tracked_item(item_req: ItemRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """ Adds a new World of Warcraft item to the watchlist. """
    exists = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == item_req.item_id).first()
    if exists: raise HTTPException(status_code=400, detail='Item already tracked')

    blizzard_client = get_blizzard_client()
    details = blizzard_client.get_item_details(item_req.item_id)
    if not details: raise HTTPException(status_code=404, detail='Item not found on Blizzard API')

    media = blizzard_client.get_item_media(item_req.item_id)
    icon_url = media['assets'][0]['value'] if media and 'assets' in media else None
    
    new_item = models.TrackedItem(
        item_id=details['id'],
        name=details['name'],
        icon_url=icon_url,
        quality=details.get('quality', {}).get('type', 'COMMON')
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    background_tasks.add_task(background_commodity_update)
    return new_item

@router.get('/items')
def get_tracked_items(db: Session = Depends(get_db)):
    """ Retrieves all currently tracked items and their latest logged price. """
    items = db.query(models.TrackedItem).all()
    result = []
    for item in items:
        latest = db.query(models.ItemPriceHistory).filter(models.ItemPriceHistory.item_id == item.id).order_by(models.ItemPriceHistory.timestamp.desc()).first()
        result.append({
            "id": item.id,
            "item_id": item.item_id,
            "name": item.name,
            "icon_url": item.icon_url,
            "quality": item.quality,
            "current_price": latest.buyout if latest else 0,
            "last_updated": latest.timestamp if latest else None
        })
    return result

@router.delete('/items/{item_id}')
def delete_tracked_item(item_id: int, db: Session = Depends(get_db)):
    """ Removes an item from the watchlist. """
    item = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == item_id).first()
    if not item: raise HTTPException(status_code=404, detail='Item not found')
    db.delete(item)
    db.commit()
    return {'message': 'Item deleted'}

@router.get("/items/{item_id}/history")
def get_item_history(item_id: int, range: str = "14d", db: Session = Depends(get_db)):
    """ Retrieves historical price data for a tracked item over a specified time range. """
    tracked = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == item_id).first()
    if not tracked: raise HTTPException(status_code=404, detail='Item not tracked')
         
    now = datetime.utcnow()
    if range == "24h": start_time, interval_seconds = now - timedelta(hours=24), 0
    elif range == "7d": start_time, interval_seconds = now - timedelta(days=7), 3600
    elif range == "14d": start_time, interval_seconds = now - timedelta(days=14), 7200
    elif range == "30d": start_time, interval_seconds = now - timedelta(days=30), 14400
    else: start_time, interval_seconds = now - timedelta(days=14), 7200

    start_timestamp = start_time.timestamp()
    query = db.query(models.ItemPriceHistory).filter(models.ItemPriceHistory.item_id == tracked.id).filter(models.ItemPriceHistory.timestamp >= start_time).order_by(models.ItemPriceHistory.timestamp.asc())
        
    results = query.all()
    if interval_seconds == 0 or not results:
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

# --- Recipes ---

class RecipeRequestBase(pydantic.BaseModel):
    crafted_item_id: int

@router.post('/recipes')
def add_recipe(req: RecipeRequestBase, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    exists = db.query(models.Recipe).filter(models.Recipe.crafted_item_id == req.crafted_item_id).first()
    if exists: raise HTTPException(status_code=400, detail="Recipe for this item is already tracked")

    blizzard_client = get_blizzard_client()
    item_data = blizzard_client.get_item_details(req.crafted_item_id)
    if not item_data: raise HTTPException(status_code=404, detail="Item not found on Blizzard API")

    media = blizzard_client.get_item_media(req.crafted_item_id)
    icon_url = media['assets'][0]['value'] if media and 'assets' in media else None
    
    new_recipe = models.Recipe(name=item_data.get('name', 'Unknown Item'), crafted_item_id=req.crafted_item_id, crafted_quantity=1, icon_url=icon_url)
    db.add(new_recipe)
    
    existing_tracked = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == req.crafted_item_id).first()
    if not existing_tracked:
        new_tracked = models.TrackedItem(item_id=item_data['id'], name=item_data['name'], icon_url=icon_url, quality=item_data.get('quality', {}).get('type', 'COMMON'))
        db.add(new_tracked)

    db.commit()
    db.refresh(new_recipe)
    background_tasks.add_task(background_commodity_update)
    return new_recipe

class ReagentRequest(pydantic.BaseModel):
    item_id: int
    quantity: int

@router.post('/recipes/{recipe_id}/reagents')
def add_reagent(recipe_id: int, req: ReagentRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe: raise HTTPException(status_code=404, detail="Recipe not found")
        
    exists = db.query(models.RecipeReagent).filter(models.RecipeReagent.recipe_id == recipe_id, models.RecipeReagent.item_id == req.item_id).first()
    if exists:
         exists.quantity = req.quantity
         db.commit()
         return exists

    blizzard_client = get_blizzard_client()
    item_data = blizzard_client.get_item_details(req.item_id)
    if not item_data: raise HTTPException(status_code=404, detail="Reagent item not found on Blizzard API")
        
    new_reagent = models.RecipeReagent(recipe_id=recipe_id, item_id=req.item_id, name=item_data.get('name', 'Unknown Reagent'), quantity=req.quantity)
    db.add(new_reagent)
    
    existing_tracked = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == req.item_id).first()
    if not existing_tracked:
        media = blizzard_client.get_item_media(req.item_id)
        icon_url = media['assets'][0]['value'] if media and 'assets' in media else None
        new_tracked = models.TrackedItem(item_id=item_data['id'], name=item_data['name'], icon_url=icon_url, quality=item_data.get('quality', {}).get('type', 'COMMON'))
        db.add(new_tracked)

    db.commit()
    background_tasks.add_task(background_commodity_update)
    return new_reagent

@router.delete('/recipes/{recipe_id}/reagents/{item_id}')
def delete_reagent(recipe_id: int, item_id: int, db: Session = Depends(get_db)):
    reagent = db.query(models.RecipeReagent).filter(models.RecipeReagent.recipe_id == recipe_id, models.RecipeReagent.item_id == item_id).first()
    if not reagent: raise HTTPException(status_code=404, detail="Reagent not found")
    db.delete(reagent)
    db.commit()
    return {"message": "Reagent deleted"}

@router.get('/recipes')
def get_recipes(db: Session = Depends(get_db)):
    recipes = db.query(models.Recipe).all()
    results = []
    for r in recipes:
        target_tracked = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == r.crafted_item_id).first()
        target_price = 0
        if target_tracked:
             latest = db.query(models.ItemPriceHistory).filter(models.ItemPriceHistory.item_id == target_tracked.id).order_by(models.ItemPriceHistory.timestamp.desc()).first()
             if latest: target_price = latest.buyout

        total_cost = 0
        reagents_data = []
        for reg in r.reagents:
            reg_price = 0
            reg_tracked = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == reg.item_id).first()
            if reg_tracked:
                 latest = db.query(models.ItemPriceHistory).filter(models.ItemPriceHistory.item_id == reg_tracked.id).order_by(models.ItemPriceHistory.timestamp.desc()).first()
                 if latest: reg_price = latest.buyout
            
            cost = reg_price * reg.quantity
            total_cost += cost
            reagents_data.append({
                "item_id": reg.item_id, "name": reg.name, "quantity": reg.quantity,
                "unit_price": reg_price, "total_price": cost
            })
            
        profit = (target_price * r.crafted_quantity) - total_cost
        results.append({
            "id": r.id, "name": r.name, "crafted_item_id": r.crafted_item_id, "crafted_quantity": r.crafted_quantity,
            "icon_url": r.icon_url, "target_price": target_price, "revenue": target_price * r.crafted_quantity,
            "total_cost": total_cost, "profit": profit, "reagents": reagents_data
        })
    return results

@router.delete('/recipes/{id}')
def delete_recipe(id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == id).first()
    if not recipe: raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(recipe)
    db.commit()
    return {"message": "Recipe deleted"}
