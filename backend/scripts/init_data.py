import asyncio
from main import update_token_price
from database import SessionLocal

async def run():
    print("Connecting to database...")
    db = SessionLocal()
    try:
        print("Triggering token price update...")
        await update_token_price(db)
        print("Update complete.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run())
