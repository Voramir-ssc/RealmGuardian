from database import init_db, get_session
from models.character import Character
from models.price_data import Item, Price, TokenPrice
from sqlalchemy import text

def inspect():
    engine = init_db()
    session = get_session(engine)
    
    print("--- Database Inspection ---")
    
    # Check Characters
    try:
        char_count = session.query(Character).count()
        print(f"Characters: {char_count}")
        if char_count > 0:
            first = session.query(Character).first()
            print(f"Sample: {first.name} ({first.realm})")
    except Exception as e:
        print(f"Error querying characters: {e}")

    # Check Token Prices
    try:
        token_count = session.query(TokenPrice).count()
        print(f"Token Prices: {token_count}")
    except Exception as e:
        print(f"Error querying tokens: {e}")

    # Check Items
    try:
        item_count = session.query(Item).count()
        print(f"Items: {item_count}")
    except Exception as e:
        print(f"Error querying items: {e}")
        
    session.close()

if __name__ == "__main__":
    inspect()
