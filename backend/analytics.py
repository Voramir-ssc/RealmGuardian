from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models
from sqlalchemy import func

def get_latest_price(db: Session, item_id: int) -> int:
    tracked = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == item_id).first()
    if not tracked:
        return 0
    latest = db.query(models.ItemPriceHistory).filter(models.ItemPriceHistory.item_id == tracked.id).order_by(models.ItemPriceHistory.timestamp.desc()).first()
    return latest.buyout if latest else 0

def calculate_liquidity_score(db: Session):
    now = datetime.utcnow()
    start_time = now - timedelta(hours=48)

    # Get all crafted items that have a recipe
    recipes = db.query(models.Recipe).all()
    
    results = []

    for recipe in recipes:
        tracked_crafted = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == recipe.crafted_item_id).first()
        if not tracked_crafted:
            continue
            
        # Get history for this item using the internal DB id
        history = db.query(models.ItemPriceHistory)\
            .filter(models.ItemPriceHistory.item_id == tracked_crafted.id)\
            .filter(models.ItemPriceHistory.timestamp >= start_time)\
            .order_by(models.ItemPriceHistory.timestamp.asc()).all()

        if len(history) < 2:
            continue

        total_sold = 0
        price_changes = 0
        
        prev_qty = history[0].quantity
        prev_price = history[0].buyout

        # Track sales and price changes
        for entry in history[1:]:
            curr_qty = entry.quantity
            curr_price = entry.buyout

            if curr_price == prev_price and curr_qty < prev_qty:
                total_sold += (prev_qty - curr_qty)
            elif curr_price != prev_price:
                price_changes += 1

            prev_qty = curr_qty
            prev_price = curr_price

        # We look at 48h of data, so divide by 2 for daily sell-through rate
        sell_through_rate = total_sold / 2.0

        if sell_through_rate < 1:
            continue

        # Calculate production cost
        crafting_cost = 0
        for reagent in recipe.reagents:
            reagent_price = get_latest_price(db, reagent.item_id)
            crafting_cost += reagent_price * reagent.quantity

        current_price = history[-1].buyout if history else 0
        profit = current_price - crafting_cost

        if profit <= 0:
            continue

        # Liquidity score = Sell-through rate * Profit margin / (Price changes + 1)
        profit_margin = profit / crafting_cost if crafting_cost > 0 else 0
        stability_index = 1.0 / (price_changes + 1)
        
        liquidity_score = sell_through_rate * profit_margin * stability_index

        results.append({
            "item_id": recipe.crafted_item_id,
            "name": recipe.name,
            "sell_through_rate_24h": sell_through_rate,
            "price_changes_48h": price_changes,
            "current_price": current_price,
            "crafting_cost": crafting_cost,
            "profit": profit,
            "liquidity_score": liquidity_score,
            "stability_index": stability_index
        })

    # Sort by liquidity score
    results.sort(key=lambda x: x["liquidity_score"], reverse=True)
    
    return results[:10]
