import shutil
import os
from datetime import datetime

# Configuration
DB_FILE = "realmguardian.db"
BACKUP_DIR = r"O:\Meine Ablage\001_SSCloud\001_Unterlagen\004_Heimnetzwerk\RealmGuardBacklog"

def create_backup():
    """Creates a timestamped backup of the database."""
    if not os.path.exists(BACKUP_DIR):
        print(f"Backup directory not found: {BACKUP_DIR}")
        return False
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(BACKUP_DIR, f"realmguardian_{timestamp}.db")
    
    try:
        shutil.copy2(DB_FILE, backup_file)
        print(f"Backup created successfully: {backup_file}")
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False
    
if __name__ == "__main__":
    create_backup()
