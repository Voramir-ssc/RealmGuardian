import sqlite3
import config
import main
from blizzard_api import BlizzardAPI

main.blizzard_client = BlizzardAPI(config.config.client_id, config.config.client_secret, config.config.region)

db = sqlite3.connect('realmguardian.db')
cursor = db.cursor()
cursor.execute("SELECT access_token FROM user_access_tokens LIMIT 1")
row = cursor.fetchone()
if not row:
    print("No token found")
else:
    token = row[0]
    print("Triggering sync...")
    main.sync_user_characters(token)
    print("Sync finished.")
db.close()
