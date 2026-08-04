import sys
import traceback
from database import engine, SessionLocal
import models
from blizzard_api import BlizzardAPI
from config import config

models.Base.metadata.create_all(bind=engine)
blizzard_client = BlizzardAPI(config.client_id, config.client_secret, config.region)

db = SessionLocal()
try:
    print("Starting update...")
    tracked_items = db.query(models.TrackedItem).all()
    for item in tracked_items:
        details = blizzard_client.get_item_details(item.item_id)
        if details and 'name' in details:
            name_val = details['name']
            if isinstance(name_val, dict):
                new_name = name_val.get('de_DE', name_val.get('en_US', item.name))
            else:
                new_name = name_val
            
            if new_name != item.name:
                print(f"TrackedItem {item.item_id}: {item.name} -> {new_name}")
                item.name = new_name
                
                # Update Recipe names that match this item
                recipes = db.query(models.Recipe).filter(models.Recipe.crafted_item_id == item.item_id).all()
                for r in recipes:
                    if r.name != new_name:
                        print(f" Recipe {r.id}: {r.name} -> {new_name}")
                        r.name = new_name
                        
                # Update RecipeReagent names that match this item
                reagents = db.query(models.RecipeReagent).filter(models.RecipeReagent.item_id == item.item_id).all()
                for reg in reagents:
                    if reg.name != new_name:
                        print(f" Reagent {reg.id}: {reg.name} -> {new_name}")
                        reg.name = new_name
                        
    # Now check Recipes that might not be in TrackedItems
    for r in db.query(models.Recipe).all():
        details = blizzard_client.get_item_details(r.crafted_item_id)
        if details and 'name' in details:
            name_val = details['name']
            new_name = name_val.get('de_DE', name_val.get('en_US', r.name)) if isinstance(name_val, dict) else name_val
            if new_name != r.name:
                print(f"Recipe {r.id} (not tracked): {r.name} -> {new_name}")
                r.name = new_name

    # Now check RecipeReagents that might not be in TrackedItems
    for reg in db.query(models.RecipeReagent).all():
        details = blizzard_client.get_item_details(reg.item_id)
        if details and 'name' in details:
            name_val = details['name']
            new_name = name_val.get('de_DE', name_val.get('en_US', reg.name)) if isinstance(name_val, dict) else name_val
            if new_name != reg.name:
                print(f"Reagent {reg.id} (not tracked): {reg.name} -> {new_name}")
                reg.name = new_name

    db.commit()
    print("Update complete")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
finally:
    db.close()
