import shutil
import os
import datetime
from config import config
from dotenv import load_dotenv

# Load environment variables explicitly if not already loaded
load_dotenv()

DB_FILE = "realmguardian.db"
BACKUP_PATH = os.getenv("BACKUP_PATH")

def perform_backup():
    if not BACKUP_PATH:
        print("Backup skipped: BACKUP_PATH not set in .env")
        return

    if not os.path.exists(DB_FILE):
        print(f"Backup failed: Database file '{DB_FILE}' not found.")
        return

    # Ensure backup directory exists
    if not os.path.exists(BACKUP_PATH):
        try:
            os.makedirs(BACKUP_PATH)
            print(f"Created backup directory: {BACKUP_PATH}")
        except Exception as e:
            print(f"Backup failed: Could not create backup directory. {e}")
            return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"realmguardian_{timestamp}.db"
    backup_file = os.path.join(BACKUP_PATH, backup_filename)

    try:
        shutil.copy2(DB_FILE, backup_file)
        print(f"Backup successful: {backup_file}")
        
        # Optional: Cleanup old backups (keep last 30 days)
        cleanup_old_backups()
        
    except Exception as e:
        print(f"Backup failed: {e}")

def cleanup_old_backups(days_to_keep=30):
    try:
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(days=days_to_keep)
        
        for filename in os.listdir(BACKUP_PATH):
            if filename.startswith("realmguardian_") and filename.endswith(".db"):
                file_path = os.path.join(BACKUP_PATH, filename)
                file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mod_time < cutoff:
                    os.remove(file_path)
                    print(f"Deleted old backup: {filename}")
    except Exception as e:
        print(f"Cleanup warning: {e}")

if __name__ == "__main__":
    perform_backup()
