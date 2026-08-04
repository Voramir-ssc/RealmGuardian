import sqlite3
conn = sqlite3.connect('realmguardian.db')
c = conn.cursor()
c.execute("SELECT id, level, item_level FROM characters WHERE name='Lenmera' AND realm='Die Aldor' ORDER BY level DESC LIMIT 1")
print(c.fetchall())
conn.close()
