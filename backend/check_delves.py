import sqlite3
import json
import config
from blizzard_api import BlizzardAPI

db = sqlite3.connect('realmguardian.db')
cursor = db.cursor()
cursor.execute("SELECT access_token FROM user_access_tokens LIMIT 1")
row = cursor.fetchone()
if not row:
    print("No token found")
else:
    token = row[0]
    client = BlizzardAPI(config.config.client_id, config.config.client_secret, config.config.region)
    # Check stats for delves
    stats = client.get_character_statistics(token, "die-aldor", "voramir")
    if stats:
        with open("voramir_stats.json", "w") as f:
            json.dump(stats, f, indent=4)
        print("Stats dumped to voramir_stats.json")
db.close()
