#!/usr/bin/env bash
set -e

echo "========================================================"
echo "  RealmGuardian - Migration Bundle Importer (Debian)"
echo "========================================================"
echo ""

ARCHIVE="realmguardian_migration_bundle.zip"

if [ ! -f "$ARCHIVE" ]; then
    echo "[FEHLER] $ARCHIVE nicht gefunden!"
    echo "Bitte lege die Datei '$ARCHIVE' in das Hauptverzeichnis von RealmGuardian."
    exit 1
fi

if ! command -v unzip &> /dev/null; then
    echo "Entpack-Werkzeug 'unzip' wird benoetigt. Installiere..."
    sudo apt-get update && sudo apt-get install -y unzip
fi

echo "Entpacke $ARCHIVE nach backend/ ..."
unzip -o "$ARCHIVE"

# Falls das Archiv den Pfad backend/ enthielt oder direkt
if [ -f "realmguardian.db" ]; then
    mv -f realmguardian.db backend/
fi
if [ -f "config.json" ]; then
    mv -f config.json backend/
fi

chmod 644 backend/realmguardian.db 2>/dev/null || true
if [ -f "backend/config.json" ]; then
    chmod 600 backend/config.json
fi

echo ""
echo "[ERFOLG] Datenbank und Konfiguration wurden erfolgreich importiert!"
echo "Dateien in backend/:"
ls -lh backend/realmguardian.db backend/config.json 2>/dev/null || true
echo ""

