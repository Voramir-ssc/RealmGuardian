import sqlite3
import json
import os
import glob

db_file = 'realmguardian.db'
print(f"Connecting to {db_file}...")

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Get all characters
    cursor.execute("SELECT id, name, gold FROM characters")
    characters = cursor.fetchall()
    
    restored_count = 0
    for char_id, name, current_gold in characters:
        if current_gold == 0:
            # Check debug files
            debug_file = f"debug_char_{name}.json"
            if os.path.exists(debug_file):
                with open(debug_file, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        protected_money = data.get("protected", {}).get("money") if data.get("protected") else None
                        public_money = data.get("public", {}).get("money") if data.get("public") else None
                        
                        gold_val = protected_money if protected_money is not None else public_money
                        
                        if gold_val is not None and gold_val > 0:
                            cursor.execute("UPDATE characters SET gold = ? WHERE id = ?", (gold_val, char_id))
                            print(f"Restored {name}'s gold to {gold_val/10000}g")
                            restored_count += 1
                    except Exception as e:
                        print(f"Could not read {debug_file}: {e}")
            else:
                # Also try matching by looking inside the files just in case it has weird characters
                pass
                
    conn.commit()
    conn.close()
    print(f"Database update successful. Restored {restored_count} characters.")
except Exception as e:
    print(f"Error: {e}")
