import sqlite3
import os

main_db_path = 'realmguardian.db'
backup_path = r'O:\Meine Ablage\001_SSCloud\001_Unterlagen\004_Heimnetzwerk\RealmGuardBacklog\realmguardian_2026-02-24_04-04-13.db'

print(f"Checking backup: {backup_path}")
if not os.path.exists(backup_path):
    print("Backup not found!")
    exit(1)

# Check what tables exist in the backup
backup_conn = sqlite3.connect(backup_path)
bc = backup_conn.cursor()
bc.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in bc.fetchall()]
print(f"Tables in backup: {tables}")
backup_conn.close()

if 'tracked_items' not in tables:
    print("WARNING: tracked_items table is NOT in this backup!")
    
conn = sqlite3.connect(main_db_path)
c = conn.cursor()

c.execute(f"ATTACH DATABASE '{backup_path}' AS backup_db")

try:
    if 'wow_token_history' in tables:
        c.execute("INSERT OR IGNORE INTO wow_token_history SELECT * FROM backup_db.wow_token_history")
        print("Restored wow_token_history")
    if 'tracked_items' in tables:
        c.execute("INSERT OR IGNORE INTO tracked_items SELECT * FROM backup_db.tracked_items")
        print("Restored tracked_items")
    if 'item_price_history' in tables:
        c.execute("INSERT OR IGNORE INTO item_price_history SELECT * FROM backup_db.item_price_history")
        print("Restored item_price_history")
    
    conn.commit()
    print("Success: Database migration completed.")
except Exception as e:
    print("Error during migration:", getattr(e, 'message', repr(e)))

conn.close()
