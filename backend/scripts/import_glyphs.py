import os
import time
import requests
from sqlalchemy.orm import Session

# Setup environment to run from backend directory
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from config import config
from blizzard_api import BlizzardAPI

def get_or_create_tracked_item(db: Session, item_id: int, item_name: str, icon_url: str = ""):
    tracked = db.query(models.TrackedItem).filter(models.TrackedItem.item_id == item_id).first()
    if not tracked:
        tracked = models.TrackedItem(item_id=item_id, name=item_name, icon_url=icon_url)
        db.add(tracked)
        db.commit()
        db.refresh(tracked)
    return tracked

def main():
    print("Initializing API...")
    api = BlizzardAPI(config.client_id, config.client_secret, config.region)
    token = api.get_token()
    db = SessionLocal()

    # 1. Get Inscription Skill Tiers
    print("Fetching Inscription Skill Tiers...")
    res = requests.get(f'https://{api.region}.api.blizzard.com/data/wow/profession/773?namespace=static-{api.region}&locale=de_DE', headers={'Authorization': f'Bearer {token}'})
    if res.status_code != 200:
        print("Failed to fetch profession 773")
        return
        
    tiers = res.json().get('skill_tiers', [])
    print(f"Found {len(tiers)} skill tiers.")

    glyph_recipes = []

    # 2. Iterate Tiers to find Glyphs
    for tier in tiers:
        tier_id = tier['id']
        tier_name = tier['name']
        print(f"Scanning {tier_name} ({tier_id})...")
        
        t_res = requests.get(f'https://{api.region}.api.blizzard.com/data/wow/profession/773/skill-tier/{tier_id}?namespace=static-{api.region}&locale=de_DE', headers={'Authorization': f'Bearer {token}'})
        if t_res.status_code != 200:
            print(f"Failed to fetch tier {tier_id}")
            continue
            
        categories = t_res.json().get('categories', [])
        for cat in categories:
            if "glyph" in cat['name'].lower() or "glyphe" in cat['name'].lower():
                recipes = cat.get('recipes', [])
                for r in recipes:
                    glyph_recipes.append({"id": r['id'], "name": r['name']})
                    
    print(f"Total Glyph recipes found: {len(glyph_recipes)}")
    
    # Exclude keywords for reagents
    exclude_reagents = ["pergament", "papier", "parchment", "paper"]

    added_count = 0
    
    # 3. Process each recipe
    for i, r_info in enumerate(glyph_recipes):
        recipe_id = r_info['id']
        
        # Check if recipe already in DB
        
        r_res = requests.get(f'https://{api.region}.api.blizzard.com/data/wow/recipe/{recipe_id}?namespace=static-{api.region}&locale=de_DE', headers={'Authorization': f'Bearer {token}'})
        if r_res.status_code != 200:
            print(f"  [{i+1}/{len(glyph_recipes)}] Failed to fetch recipe {recipe_id}")
            continue
            
        data = r_res.json()
        crafted_item = data.get('crafted_item', {})
        if not crafted_item:
            continue
            
        c_item_id = crafted_item['id']
        c_item_name = crafted_item['name']
        crafted_quantity = data.get('crafted_quantity', {}).get('value', 1)
        
        # Check if recipe already exists for this crafted item
        existing_recipe = db.query(models.Recipe).filter(models.Recipe.crafted_item_id == c_item_id).first()
        if existing_recipe:
            print(f"  [{i+1}/{len(glyph_recipes)}] Recipe for {c_item_name} already exists. Skipping.")
            continue
            
        print(f"  [{i+1}/{len(glyph_recipes)}] Processing {c_item_name}...")
        
        # Track the crafted item
        get_or_create_tracked_item(db, c_item_id, c_item_name)
        
        # Create Recipe
        new_recipe = models.Recipe(
            name=c_item_name,
            crafted_item_id=c_item_id,
            crafted_quantity=crafted_quantity,
            icon_url="" # Can leave empty or fetch later
        )
        db.add(new_recipe)
        db.commit()
        db.refresh(new_recipe)
        
        # Add reagents
        reagents = data.get('reagents', [])
        for reg in reagents:
            reg_item = reg.get('reagent', {})
            reg_id = reg_item.get('id')
            reg_name = reg_item.get('name', '')
            reg_qty = reg.get('quantity', 1)
            
            # Filter parchment/paper
            if any(exc in reg_name.lower() for exc in exclude_reagents):
                continue
                
            # Track the reagent
            get_or_create_tracked_item(db, reg_id, reg_name)
            
            # Add to recipe_reagents
            new_rr = models.RecipeReagent(
                recipe_id=new_recipe.id,
                item_id=reg_id,
                name=reg_name,
                quantity=reg_qty
            )
            db.add(new_rr)
            
        db.commit()
        added_count += 1
        
        # Small delay to not spam the API
        time.sleep(0.05)

    print(f"Done! Successfully imported {added_count} new Glyph recipes and tracked all required items.")
    db.close()

if __name__ == "__main__":
    main()
