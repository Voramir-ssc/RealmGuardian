import asyncio
from datetime import datetime, timedelta
import random
from database import SessionLocal
from models import WowTokenHistory

# Base price for EU token (approximate current value)
BASE_PRICE_GOLD = 425000 
BASE_PRICE_COPPER = BASE_PRICE_GOLD * 10000

def generate_history():
    db = SessionLocal()
    try:
        print("Checking existing data...")
        count = db.query(WowTokenHistory).count()
        if count > 5:
            print(f"Database already has {count} entries. Skipping backfill to preserve specific data.")
            # However, user wants "real looking" data. Only backfill if very empty.
            if count > 20: 
                return

        print("Generating dummy history for the last 24 hours...")
        
        # Generate data for the last 24h (every 30 mins)
        now = datetime.now()
        entries = []
        
        # Create a curve
        for i in range(48):
            time_offset = now - timedelta(minutes=30 * (48 - i))
            # Random fluctuation +/- 2%
            fluctuation = random.uniform(0.98, 1.02)
            # Add a trend (sine wave-ish or just random walk)
            price = int(BASE_PRICE_COPPER * fluctuation)
            
            timestamp = time_offset.timestamp()
            
            # Check if exists
            exists = db.query(WowTokenHistory).filter_by(last_updated_timestamp=timestamp).first()
            if not exists:
                entries.append(WowTokenHistory(
                    price=price,
                    last_updated_timestamp=timestamp,
                    region="eu"
                ))
        
        if entries:
            db.add_all(entries)
            db.commit()
            print(f"Added {len(entries)} historical entries.")
        else:
            print("No new entries needed.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_history()
