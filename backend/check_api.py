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
    # Fetch Voramir Die Aldor professions
    prof = client.get_character_professions(token, "die-aldor", "voramir")
    if prof:
        for p in prof.get('primaries', []):
            print(f"Profession: {p.get('profession', {}).get('name')}")
            for t in p.get('tiers', []):
                name = t.get('tier', {}).get('name')
                tid = t.get('tier', {}).get('id')
                print(f"  Tier: {name} (ID: {tid})")
    else:
        print("Could not fetch professions")
db.close()
