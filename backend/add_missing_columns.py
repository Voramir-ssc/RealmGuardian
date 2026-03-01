import sqlite3

db_file = 'realmguardian.db'
print(f"Connecting to {db_file}...")

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(characters)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Existing columns: {columns}")
    
    if 'professions' not in columns:
        print("Adding professions column...")
        cursor.execute("ALTER TABLE characters ADD COLUMN professions TEXT")
        print("Added professions column.")
    else:
        print("professions column already exists.")
        
    if 'equipment' not in columns:
        print("Adding equipment column...")
        cursor.execute("ALTER TABLE characters ADD COLUMN equipment TEXT")
        print("Added equipment column.")
        
    if 'item_level' not in columns:
        print("Adding item_level column...")
        cursor.execute("ALTER TABLE characters ADD COLUMN item_level INTEGER DEFAULT 0")
        print("Added item_level column.")

    conn.commit()
    conn.close()
    print("Database update successful.")
except Exception as e:
    print(f"Error: {e}")
