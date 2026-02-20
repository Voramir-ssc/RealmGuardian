import sqlite3

try:
    conn = sqlite3.connect('realmguardian.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(characters)")
    columns = cursor.fetchall()
    
    print("Columns in 'characters' table:")
    for col in columns:
        print(col)
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
