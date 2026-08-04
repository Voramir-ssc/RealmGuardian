import datetime
import random
import sqlalchemy
from database import SessionLocal, engine, Base
import models

def backfill_gold_history():
    """Generates fake historical gold data for the last 14 days based on current gold."""
    db = SessionLocal()
    try:
        # Get current gold sum
        current_gold = db.query(models.Character).with_entities(sqlalchemy.func.sum(models.Character.gold)).scalar() or 0
        if current_gold == 0:
            print("No characters found with gold. Cannot backfill.")
            return

        print(f"Current real total gold: {current_gold / 10000}g")

        today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        base_gold = current_gold

        # Generate fake data for the last 14 days
        for i in range(1, 15):
            past_date = today - datetime.timedelta(days=i)
            
            # Fluctuate the gold backwards (we were poorer in the past)
            # Random drop between 0.5% and 2.5% per day backwards
            fluctuation = random.uniform(0.975, 0.995) 
            base_gold = int(base_gold * fluctuation)
            
            # Check if entry exists to avoid duplicate backfills
            existing = db.query(models.AccountGoldHistory).filter(
                models.AccountGoldHistory.timestamp >= past_date,
                models.AccountGoldHistory.timestamp < past_date + datetime.timedelta(days=1)
            ).first()

            if not existing:
                snapshot = models.AccountGoldHistory(
                    total_gold=base_gold,
                    timestamp=past_date + datetime.timedelta(hours=12) # Simulate sync around noon
                )
                db.add(snapshot)
                print(f"Added historical data for {past_date.strftime('%Y-%m-%d')}: {base_gold / 10000}g")
            else:
                print(f"Data for {past_date.strftime('%Y-%m-%d')} already exists.")

        # Ensure today is correct (in case sync hasn't run yet)
        today_existing = db.query(models.AccountGoldHistory).filter(models.AccountGoldHistory.timestamp >= today).first()
        if not today_existing:
            today_snapshot = models.AccountGoldHistory(
                total_gold=current_gold,
                timestamp=datetime.datetime.utcnow()
            )
            db.add(today_snapshot)

        db.commit()
        print("Backfill complete!")

    except Exception as e:
        print(f"Error during backfill: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    backfill_gold_history()
