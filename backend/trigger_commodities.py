import asyncio
from main import update_commodity_prices
from database import SessionLocal

async def run():
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
