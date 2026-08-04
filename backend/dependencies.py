from typing import Generator
from sqlalchemy.orm import Session
from database import SessionLocal
from blizzard_api import BlizzardAPI
from config import config

blizzard_client_instance = None

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that yields a database session.
    Ensures the session is closed after the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_blizzard_client() -> BlizzardAPI:
    """
    Returns a singleton instance of the BlizzardAPI client.
    """
    global blizzard_client_instance
    if not blizzard_client_instance:
        blizzard_client_instance = BlizzardAPI(config.client_id, config.client_secret, config.region)
    return blizzard_client_instance
