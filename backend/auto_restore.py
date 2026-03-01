import sqlite3
import os
import shutil
import glob

DB_FILE = "realmguardian.db"
LOG_FILE = "backend.log"
BACKUP_DIR = r"O:\Meine Ablage\001_SSCloud\001_Unterlagen\004_Heimnetzwerk\RealmGuardBacklog"

def is_db_empty():
    if not os.path.exists(DB_FILE):
        return True
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # If no tables exist, it's empty
        if not tables:
            conn.close()
            return True
            
        # Check if characters table specifically has any rows
        if ('characters',) in tables:
            cursor.execute("SELECT COUNT(*) FROM characters")
            count = cursor.fetchone()[0]
            conn.close()
            return count == 0
            
        conn.close()
        return True
    except Exception:
        return True

def get_latest_backup(prefix, extension):
    if not os.path.exists(BACKUP_DIR):
        return None
        
    pattern = os.path.join(BACKUP_DIR, f"{prefix}*{extension}")
    files = glob.glob(pattern)
    if not files:
        return None
        
    # Get the latest based on modification time
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def check_and_restore():
    """Checks if the local database is missing/empty, and restores the latest DB and logs if so."""
    if is_db_empty():
        print("Database appears empty or missing. Attempting auto-restore from cloud backup...")
        
        latest_db_backup = get_latest_backup("realmguardian_", ".db")
        if latest_db_backup:
            try:
                shutil.copy2(latest_db_backup, DB_FILE)
                print(f"Successfully restored database from: {latest_db_backup}")
            except Exception as e:
                print(f"Failed to restore database: {e}")
        else:
            print("No database backup found in cloud storage.")
            
        latest_log_backup = get_latest_backup("backend_log_", ".log")
        if latest_log_backup:
             try:
                 shutil.copy2(latest_log_backup, LOG_FILE)
                 print(f"Successfully restored logs from: {latest_log_backup}")
             except Exception as e:
                 print(f"Failed to restore logs: {e}")
                 
if __name__ == "__main__":
    check_and_restore()
