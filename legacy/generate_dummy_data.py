import datetime
import random
from database import init_db, get_session
from models.character import Character
from models.price_data import Item, Price, TokenPrice

def generate_data():
    engine = init_db()
    session = get_session(engine)
    
    print("Generating Dummy Data...")

    # 1. Clear existing generic data (optional, but good for clean state)
    # session.query(Character).delete() 
    # session.query(TokenPrice).delete()
    # session.commit()

    # 2. Characters
    realms = ["Die Aldor", "Blackhand", "Antonidas", "Eredar"]
    classes = ["Krieger", "Magier", "Priester", "Jäger", "Schurke", "Hexenmeister", "Paladin", "Druide", "Schamane"]
    races = ["Mensch", "Orc", "Nachtelf", "Untoter", "Zwerg", "Tauren", "Gnom", "Troll", "Draenei", "Blutelf"]
    
    chars = []
    for i in range(15):
        c_class = random.choice(classes)
        name = f"Hero{i+1}"
        realm = random.choice(realms)
        
        char = Character(
            name=name,
            realm=realm,
            race=random.choice(races),
            character_class=c_class,
            profession_1="Kräuterkunde" if random.random() > 0.5 else "Bergbau",
            profession_2="Alchemie" if random.random() > 0.5 else "Schmiedekunst",
            status="Aktiv" if random.random() > 0.2 else "Inaktiv"
        )
        session.merge(char) # Merge prevents duplicates if running multiple times
        print(f"Added Character: {name} - {realm}")

    # 3. Token Prices (Last 30 Days)
    base_price = 350000
    now = datetime.datetime.now()
    
    for i in range(30):
        # Create a price for each day in the past 30 days
        day = now - datetime.timedelta(days=30-i)
        
        # Fluctuation +/- 5%
        fluctuation = random.uniform(0.95, 1.05)
        price_val = base_price * fluctuation
        
        # Slowly increasing trend
        base_price += random.randint(-1000, 2000)
        
        tp = TokenPrice(
            price=int(price_val),
            timestamp=day
        )
        session.add(tp)
    
    print(f"Added 30 days of token history.")

    # 4. Items and Prices (for alerts)
    sample_items = [
        {"name": "Teufelsstoff", "id": 1001, "threshold": 50},
        {"name": "Arkankristall", "id": 1002, "threshold": 200},
        {"name": "Schwarzer Lotus", "id": 1003, "threshold": 1500},
    ]

    for item_data in sample_items:
        item = session.query(Item).filter_by(id=item_data["id"]).first()
        if not item:
            item = Item(
                id=item_data["id"],
                name=item_data["name"],
                min_price_threshold=item_data["threshold"]
            )
            session.add(item)
        
        # Add a low price to trigger alert
        low_price = Price(
            item_id=item_data["id"],
            price=item_data["threshold"] - 10, # Below threshold
            timestamp=now
        )
        session.add(low_price)
        print(f"Added Item & Alert Price for: {item_data['name']}")

    session.commit()
    print("Done! Database populated.")
    session.close()

if __name__ == "__main__":
    generate_data()
