import sys
import os
import csv
import openpyxl
from database import init_db, get_session
from models.character import Character

def import_characters(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    engine = init_db()
    session = get_session(engine)
    
    current_realm = "Unknown"
    count = 0
    
    if file_path.endswith('.xlsx'):
        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active # Assume first sheet
            # Convert to list of lists to match previous reader logic
            rows = []
            for row in sheet.iter_rows(values_only=True):
                rows.append([str(c) if c is not None else "" for c in row])
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return
    else:
        # CSV Fallback
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter=';')
                rows = list(reader)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return

    try:
        # Simple heuristic parser
        headers_found = False
        idx_name = idx_race = idx_class = idx_prof1 = idx_prof2 = idx_status = -1
        
        for row in rows:
            # Skip empty rows
            if not row or not any(row):
                continue
            
            # Check for Realm keywords (blocks)
            # If row has mostly empty cells but one text that looks like a Realm
            # Logic: If row is not the header and not data, maybe it's a Title/Realm
            clean_row = [c.strip() for c in row if c.strip()]
            
            if len(clean_row) == 1:
                # Potential Realm or Title
                candidate = clean_row[0]
                # Filter out common titles if known, else assume it's a realm
                if candidate not in ["Name", "Volk", "Divide and Conquer", "Die Aldor"] and len(candidate) > 2: 
                    current_realm = candidate
                    print(f"Detected Realm/Section: {current_realm}")
                elif candidate in ["Divide and Conquer", "Die Aldor"]:
                        current_realm = candidate
                        print(f"Detected Realm (Exact Match): {current_realm}")
                continue

            # Check for Header
            # Convert row to string logic for easier searching
            row_str = [str(c).strip() for c in row]
            
            if "Name" in row_str and ("Klasse" in row_str or "Class" in row_str):
                try:
                    idx_name = row_str.index("Name")
                    idx_race = row_str.index("Volk") if "Volk" in row_str else -1
                    idx_class = row_str.index("Klasse") if "Klasse" in row_str else -1
                    idx_prof1 = row_str.index("Beruf 1") if "Beruf 1" in row_str else -1
                    idx_prof2 = row_str.index("Beruf 2") if "Beruf 2" in row_str else -1
                    idx_status = row_str.index("Status") if "Status" in row_str else -1
                    headers_found = True
                    print(f"Headers found! Indices: Name={idx_name}, Class={idx_class}")
                    continue # Skip header row
                except ValueError:
                    print("Header parsing error")
                    pass
                
                if headers_found:
                    # Process Data Row
                    try:
                        name = row[idx_name].strip()
                        if not name: continue
                        
                        race = row[idx_race].strip() if idx_race != -1 else ""
                        char_class = row[idx_class].strip() if idx_class != -1 else ""
                        
                        # Debug Output
                        # print(f"Processing: {name} ({race} {char_class})")

                        prof1 = row[idx_prof1].strip() if idx_prof1 != -1 else ""
                        prof2 = row[idx_prof2].strip() if idx_prof2 != -1 else ""
                        status = row[idx_status].strip() if idx_status != -1 else "Active"
                        
                        # Cleanup status (e.g. checkbox symbols)
                        if status == "TRUE": status = "Aktiv"
                        if status == "FALSE": status = "Inaktiv"
                        
                        # Upsert or Add
                        existing = session.query(Character).filter_by(name=name, realm=current_realm).first()
                        if existing:
                            existing.race = race
                            existing.character_class = char_class
                            existing.profession_1 = prof1
                            existing.profession_2 = prof2
                            existing.status = status
                            print(f"Updated: {name} - {current_realm}")
                        else:
                            new_char = Character(
                                name=name,
                                realm=current_realm,
                                race=race,
                                character_class=char_class,
                                profession_1=prof1,
                                profession_2=prof2,
                                status=status
                            )
                            session.add(new_char)
                            print(f"Added: {name} - {current_realm}")
                            count += 1
                            
                    except IndexError:
                        continue

            session.commit()
            print(f"Import complete. Processed {count} new characters.")
            
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        import_characters(sys.argv[1])
    else:
        print("Usage: python import_characters.py <path_to_csv>")
