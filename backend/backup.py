import shutil
import os
from datetime import datetime

# Configuration
DB_FILE = "realmguardian.db"
BACKUP_DIR = r"O:\Meine Ablage\001_SSCloud\001_Unterlagen\004_Heimnetzwerk\RealmGuardBacklog"

def create_backup():
    """Creates a timestamped backup of the database, keeping only the 3 most recent backups."""
    if not os.path.exists(BACKUP_DIR):
        print(f"Backup directory not found: {BACKUP_DIR}")
        return False
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(BACKUP_DIR, f"realmguardian_{timestamp}.db")
    
    try:
        shutil.copy2(DB_FILE, backup_file)
        print(f"Backup created successfully: {backup_file}")
        
        # Keep only the last 3 backups
        backups = []
        for f in os.listdir(BACKUP_DIR):
            if f.startswith("realmguardian_") and f.endswith(".db"):
                backups.append(os.path.join(BACKUP_DIR, f))
        
        # Sort files by modification time (oldest first)
        backups.sort(key=os.path.getmtime)
        
        # Delete oldest files if we have more than 3
        while len(backups) > 3:
            oldest_backup = backups.pop(0)
            os.remove(oldest_backup)
            print(f"Deleted old backup: {oldest_backup}")
            
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False
    
if __name__ == "__main__":
    create_backup()
