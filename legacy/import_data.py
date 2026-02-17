import csv
import datetime
from sqlalchemy.orm import Session
from database import init_db, get_session
from models.price_data import Item, Price

def import_csv(file_path):
    engine = init_db()
    session = get_session(engine)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Expected headers: Kraut, Erweiterung, letzter Verkauf
            # "letzter Verkauf" is assumed to be Price (Gold)
            
            count = 0
            for row in reader:
                name = row.get('Kraut') or row.get('Name')
                expansion = row.get('Erweiterung') or row.get('Expansion')
                price_str = row.get('letzter Verkauf') or row.get('Price')
                
                if not name:
                    continue
                    
                # 1. Ensure Item exists
                item = session.query(Item).filter_by(name=name).first()
                if not item:
                    # We need an ID. Since we don't have Blizzard IDs in CSV usually,
                    # we might need to fetch them or use a placeholder/hash.
                    # For now, we'll use a placeholder negative ID or hash if ID is mandatory.
                    # Ideally, we should lookup the ID via API, but for migration we might skip or use hash.
                    # Let's use a simple hash of the name for now because ID is Primary Key.
                    # Users should probably update IDs later via UI or API lookup.
                    item_id = abs(hash(name)) % 1000000 
                    item = Item(id=item_id, name=name, expansion=expansion)
                    session.add(item)
                    session.flush() # to get item.id available if needed

                # 2. Add Price
                if price_str:
                    try:
                        # Clean price string (e.g. "12,50 g" -> 12.50)
                        price_clean = price_str.replace('g', '').replace(' ', '').replace(',', '.')
                        price_val = float(price_clean)
                        
                        price_entry = Price(item_id=item.id, price=price_val, timestamp=datetime.datetime.now())
                        session.add(price_entry)
                        count += 1
                    except ValueError:
                        print(f"Skipping price for {name}: Invalid format {price_str}")
            
            session.commit()
            print(f"Import successful. Imported {count} price entries.")
            
    except Exception as e:
        print(f"Error importing CSV: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        import_csv(sys.argv[1])
    else:
        print("Usage: python import_data.py <path_to_csv>")
