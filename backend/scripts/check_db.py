from database import SessionLocal
import models
db = SessionLocal()
print(f"Tracked: {db.query(models.TrackedItem).count()}")
for i in db.query(models.TrackedItem).all(): print(f" - {i.item_id}: {i.name}")
print(f"Recipes: {db.query(models.Recipe).count()}")
for r in db.query(models.Recipe).all(): print(f" - {r.id}: {r.name}")
print(f"Reagents: {db.query(models.RecipeReagent).count()}")
for rg in db.query(models.RecipeReagent).all(): print(f" - {rg.item_id}: {rg.name}")
db.close()
