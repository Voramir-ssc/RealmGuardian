import shutil
import os
from datetime import datetime

# Configuration
DB_FILE = os.getenv("DB_FILE", "realmguardian.db")
LOG_FILE = os.getenv("LOG_FILE", "backend.log")
BACKUP_DIR = os.getenv("BACKUP_PATH", r"O:\Meine Ablage\001_SSCloud\001_Unterlagen\004_Heimnetzwerk\RealmGuardBacklog")
MAX_BACKUPS = int(os.getenv("MAX_BACKUPS", "7"))

def create_backup():
    """Creates a timestamped backup of the database, keeping the most recent backups."""
    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            print(f"Created backup directory: {BACKUP_DIR}")
        except Exception as e:
            print(f"Backup directory could not be created: {e}")
            return False
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_db_file = os.path.join(BACKUP_DIR, f"realmguardian_{timestamp}.db")
    backup_log_file = os.path.join(BACKUP_DIR, f"backend_log_{timestamp}.log")

    try:
        shutil.copy2(DB_FILE, backup_db_file)
        if os.path.exists(LOG_FILE):
             shutil.copy2(LOG_FILE, backup_log_file)
        print(f"Backup created successfully: {backup_db_file}")
        
        # Keep only the last MAX_BACKUPS backups for both DB and Logs
        for prefix in ["realmguardian_", "backend_log_"]:
            backups = []
            for f in os.listdir(BACKUP_DIR):
                if f.startswith(prefix):
                    backups.append(os.path.join(BACKUP_DIR, f))
            
            backups.sort(key=os.path.getmtime)
            
            while len(backups) > MAX_BACKUPS:
                oldest_backup = backups.pop(0)
                os.remove(oldest_backup)
                print(f"Deleted old backup: {oldest_backup}")
            
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False
    
if __name__ == "__main__":
    create_backup()
