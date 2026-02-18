import asyncio
import main
from main import update_commodity_prices
from database import SessionLocal
from config import config
from blizzard_api import BlizzardAPI

async def run():
    print("Initializing API Client...")
    main.blizzard_client = BlizzardAPI(config.client_id, config.client_secret, config.region)
    
    print("Connecting to database...")
    db = SessionLocal()
    try:
        print("Triggering Commodity Price Update...")
        await update_commodity_prices(db)
        print("Update complete.")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run())
