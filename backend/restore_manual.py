import sqlite3
import os

db_path = 'realmguardian.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

data = [
    (242648976, '2026-02-06 12:00:00.000000'), 
    (247184326, '2026-02-07 12:00:00.000000'), 
    (250337716, '2026-02-08 12:00:00.000000'), 
    (255667579, '2026-02-09 12:00:00.000000'), 
    (260791118, '2026-02-10 12:00:00.000000'), 
    (263301967, '2026-02-11 12:00:00.000000'), 
    (269999683, '2026-02-12 12:00:00.000000'), 
    (272379147, '2026-02-13 12:00:00.000000'), 
    (279334414, '2026-02-14 12:00:00.000000'), 
    (286206496, '2026-02-15 12:00:00.000000'), 
    (290761368, '2026-02-16 12:00:00.000000'), 
    (295894876, '2026-02-17 12:00:00.000000'), 
    (302190257, '2026-02-18 12:00:00.000000'), 
    (306049938, '2026-02-19 12:00:00.000000'), 
    (310691279, '2026-02-20 10:47:05.791876'), 
    (2143303854, '2026-02-23 06:37:55.076207')
]
c.executemany('INSERT INTO account_gold_history (total_gold, timestamp) VALUES (?, ?)', data)
conn.commit()

backup_path = r'O:\Meine Ablage\001_SSCloud\001_Unterlagen\004_Heimnetzwerk\RealmGuardBacklog\realmguardian_2026-02-20_04-26-31.db'
if os.path.exists(backup_path):
    c.execute(f"ATTACH DATABASE '{backup_path}' AS backup_db")
    try:
        c.execute('INSERT INTO wow_token_history SELECT * FROM backup_db.wow_token_history')
        c.execute('INSERT INTO tracked_items SELECT * FROM backup_db.tracked_items')
        c.execute('INSERT INTO item_price_history SELECT * FROM backup_db.item_price_history')
        print('Tokens and Items Restored')
    except Exception as e:
        print('Error restoring from backup:', e)

conn.commit()
print('History restored in proper backend dir.')
