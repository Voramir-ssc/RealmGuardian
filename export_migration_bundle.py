#!/usr/bin/env python3
"""
export_migration_bundle.py
Safely packages the active SQLite database (using SQLite online backup API to prevent file lock errors)
and the backend configuration into realmguardian_migration_bundle.zip for easy migration to Debian.
"""

import sqlite3
import zipfile
import os
import sys

def create_bundle():
    print("========================================================")
    print("  RealmGuardian - Migration Bundle Exporter")
    print("========================================================")
    
    repo_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(repo_root, "backend")
    db_file = os.path.join(backend_dir, "realmguardian.db")
    config_file = os.path.join(backend_dir, "config.json")
    bundle_zip = os.path.join(repo_root, "realmguardian_migration_bundle.zip")
    temp_db = os.path.join(repo_root, "temp_export_db.sqlite3")

    if not os.path.exists(db_file):
        print(f"[FEHLER] Datenbank nicht gefunden unter: {db_file}")
        sys.exit(1)

    print(f"Erstelle konsistente Online-Sicherung von {db_file}...")
    try:
        # SQLite Online-Backup verhindert File-Lock-Probleme, falls der Dienst noch laeuft
        src = sqlite3.connect(db_file)
        dst = sqlite3.connect(temp_db)
        with dst:
            src.backup(dst)
        src.close()
        dst.close()
    except Exception as e:
        print(f"[FEHLER] Fehler bei der Datenbanksicherung: {e}")
        if os.path.exists(temp_db):
            os.remove(temp_db)
        sys.exit(1)

    print("Komprimiere Daten nach realmguardian_migration_bundle.zip...")
    try:
        with zipfile.ZipFile(bundle_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(temp_db, arcname="realmguardian.db")
            if os.path.exists(config_file):
                zf.write(config_file, arcname="config.json")
                print(" -> config.json hinzugefuegt")
            else:
                print(" -> [WARNUNG] backend/config.json nicht gefunden")

        print("Sicherungs-Archiv erfolgreich erstellt!")
        size_mb = os.path.getsize(bundle_zip) / (1024 * 1024)
        print(f"Dateigroesse: {size_mb:.2f} MB")
        print(f"Ablageort:   {bundle_zip}")
        print("\nDiese Datei kann nun direkt auf das Debian-System kopiert werden.")
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)

if __name__ == "__main__":
    create_bundle()

