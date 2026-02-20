import sqlite3
import os
import sys

# Paths
DB_NEW = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'realmguardian.db')
DB_BACKUP = r"O:\Meine Ablage\001_SSCloud\001_Unterlagen\004_Heimnetzwerk\RealmGuardBacklog\realmguardian_2026-02-20_04-26-31.db"

def restore_history():
    print(f"Connecting to backup db: {DB_BACKUP}")
    print(f"Connecting to active db: {DB_NEW}")
    
    conn_new = sqlite3.connect(DB_NEW)
    conn_backup = sqlite3.connect(DB_BACKUP)
    
    c_new = conn_new.cursor()
    c_backup = conn_backup.cursor()
    
    tables_to_restore = [
        'wow_token_history',
        'tracked_items',
        'item_price_history',
        'account_gold_history'
    ]
    
    for table in tables_to_restore:
        print(f"Restoring {table}...")
        
        try:
            # 1. Fetch all rows from backup
            c_backup.execute(f"SELECT * FROM {table}")
            rows = c_backup.fetchall()
            
            if not rows:
                print(f"  -> No data found in backup for {table}.")
                continue
                
            # 2. Get column names
            c_backup.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in c_backup.fetchall()]
            col_names = ", ".join(columns)
            placeholders = ", ".join(["?" for _ in columns])
            
            # 3. Clear new table
            c_new.execute(f"DELETE FROM {table}")
            
            # 4. Insert rows into new table
            insert_query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
            c_new.executemany(insert_query, rows)
            
            print(f"  -> Restored {len(rows)} rows to {table}.")
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                print(f"  -> Table {table} does not exist in backup, skipping.")
            else:
                raise e
        
    conn_new.commit()
    conn_backup.close()
    conn_new.close()
    
    # Run the backfill script since the gold history wasn't in the backup
    print("Running backfill for gold history...")
    from backend import backfill_gold
    backfill_gold.backfill_gold_history()
    
    print("Restore complete.")

if __name__ == "__main__":
    # Add root folder to sys path to allow importing backend module
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    restore_history()
