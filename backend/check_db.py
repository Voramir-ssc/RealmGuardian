from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Character, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./realmguardian.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()
chars = db.query(Character).all()
print(f"Total characters in DB: {len(chars)}")
for c in chars:
    print(f" - {c.name}: {c.gold}g, {c.played_time}s")
