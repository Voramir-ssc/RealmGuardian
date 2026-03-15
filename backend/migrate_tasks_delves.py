import sqlite3
import os

db_file = 'realmguardian.db'

def run_migration():
    if not os.path.exists(db_file):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # Check Character table columns
        cursor.execute("PRAGMA table_info(characters)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'delves_completed' not in columns:
            cursor.execute("ALTER TABLE characters ADD COLUMN delves_completed INTEGER DEFAULT 0")
            print("Added delves_completed to characters")
            
        if 'delves_max_tier' not in columns:
            cursor.execute("ALTER TABLE characters ADD COLUMN delves_max_tier INTEGER DEFAULT 0")
            print("Added delves_max_tier to characters")
            
        # Create user_tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR NOT NULL,
                type VARCHAR NOT NULL,
                is_completed BOOLEAN DEFAULT 0,
                last_completed_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("Ensured user_tasks table exists")
        
        # Create indexes if they don't exist
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_tasks_id ON user_tasks (id)")

        conn.commit()
        print("Migration complete!")
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
