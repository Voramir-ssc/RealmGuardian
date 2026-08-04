import sqlite3

def add_column():
    con = sqlite3.connect('realmguardian.db')
    cur = con.cursor()
    
    # Check if column already exists
    cur.execute("PRAGMA table_info(characters);")
    columns = [row[1] for row in cur.fetchall()]
    
    if 'reputations' not in columns:
        print("Adding 'reputations' column to 'characters' table...")
        cur.execute("ALTER TABLE characters ADD COLUMN reputations TEXT;")
        con.commit()
        print("Column added successfully.")
    else:
        print("'reputations' column already exists.")
        
    con.close()

if __name__ == "__main__":
    add_column()
