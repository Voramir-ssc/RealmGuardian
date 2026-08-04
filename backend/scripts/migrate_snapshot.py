import sqlite3
import sys

def migrate():
    db_path = "realmguardian.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Checking if weekly_report_snapshots exists...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weekly_report_snapshots'")
        if not cursor.fetchone():
            print("Table does not exist. Nothing to migrate.")
            return

        print("Adding main_char_ilvl column...")
        try:
            cursor.execute("ALTER TABLE weekly_report_snapshots ADD COLUMN main_char_ilvl INTEGER DEFAULT 0")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column main_char_ilvl already exists.")
            else:
                raise e

        print("Adding main_char_professions column...")
        try:
            cursor.execute("ALTER TABLE weekly_report_snapshots ADD COLUMN main_char_professions VARCHAR")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column main_char_professions already exists.")
            else:
                raise e

        conn.commit()
        print("Migration complete!")
        
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate()
