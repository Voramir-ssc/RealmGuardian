# Realm Wächter

Eine eigenständige Desktop-Applikation zur Verwaltung von World of Warcraft Charakteren, Überwachung von Item-Preisen und Realm-Status.

## Features

- **Die Kaserne (Charakter-Verwaltung)**: Verwalte deine Twinks (Name, Realm, Klasse, Volk, Status).
- **Das Schatzamt (Preis-Überwachung)**: Beobachte Preise für wichtige Items (z.B. Kräuter). Automatische Updates via Blizzard API.
- **Der Wächter (Dashboard)**: Übersicht über WoW Token Preis, Realm Status und Preis-Warnungen.

## Installation

1.  Stelle sicher, dass **Python** installiert ist.
2.  Installiere die benötigten Pakete:
    ```bash
    pip install -r requirements.txt
    ```

## Konfiguration

1.  Kopiere `config.example.json` zu `config.json`.
2.  Trage deine **Blizzard API Credentials** in `config.json` ein (Client ID und Secret erhältst du im [Battle.net Developer Portal](https://develop.battle.net/access/clients)).
3.  Passe `realm_name`, `region` und `locale` an.

**Hinweis:** Die Datei `config.json` ist im `.gitignore` und wird nicht hochgeladen, um deine Daten zu schützen.

Beispiel `config.json`:
```json
{
    "blizzard_client_id": "DEINE_CLIENT_ID",
    "blizzard_client_secret": "DEIN_CLIENT_SECRET",
    "realm_name": "Die Aldor",
    "region": "eu",
    "locale": "de_DE"
}
```

## Starten

Führe das Hauptskript aus:
```bash
python main.py
```

## Daten-Migration

Falls du Daten aus einer alten CSV-Tabelle importieren möchtest:
```bash
python import_data.py "pfad/zu/deiner/tabelle.csv"
```
Erwartete Spalten in der CSV: `Kraut`, `Erweiterung`, `letzter Verkauf`.
