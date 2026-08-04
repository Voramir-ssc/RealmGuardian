import sys
sys.path.append('backend')
from database import SessionLocal
import models
from config import config

db = SessionLocal()
main_name = config.main_character.get("name", "Lenmera")
main_realm = config.main_character.get("realm", "Die Aldor")
main_char = db.query(models.Character).filter_by(name=main_name, realm=main_realm).order_by(models.Character.level.desc()).first()
if main_char:
    print("Found character:", main_char.id, main_char.name, main_char.level, main_char.item_level)
else:
    print("Not found")
