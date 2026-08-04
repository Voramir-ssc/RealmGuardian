import os
import sys

# Das Backend-Verzeichnis als Arbeitsverzeichnis für Imports setzen
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)

from database import engine
import models

print("Dropping all tables...")
models.Base.metadata.drop_all(bind=engine)
print("Creating all tables from models...")
models.Base.metadata.create_all(bind=engine)
print("Done! Database schema is now matching the SQLAlchemy models.")
