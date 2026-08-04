import sqlite3

db_file = 'realmguardian.db'
print(f"Connecting to {db_file}...")

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(characters)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'played_time' not in columns:
        print("Adding played_time column...")
        cursor.execute("ALTER TABLE characters ADD COLUMN played_time INTEGER DEFAULT 0")
        print("Done.")
    else:
        print("played_time column already exists.")

    conn.commit()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
