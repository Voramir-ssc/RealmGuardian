# 🛡️ RealmGuardian – Debian Umzugs- & Deployment-Leitfaden
> **Zielsystem:** Debian / Proxmox LXC (`SSC-LXNode` – `10.10.10.224`)  
> **Domain:** `http://realmguardian.ssc.slan`  
> **Anweisung für Antigravity & Meister:** Diese Anleitung dient als verbindlicher Fahrplan für die Wiederinbetriebnahme nach dem Server-Umzug.

---

## 📋 1. Vorbereitungen auf dem alten System (Windows)

Da sensible API-Schlüssel (`config.json`) und die SQLite-Datenbank (`realmguardian.db`) aus Sicherheits- und Performancegründen im `.gitignore` liegen, müssen diese manuell bzw. gebündelt übertragen werden:

1. Führe im Projektordner unter Windows das Skript aus:
   ```cmd
   export_migration_bundle.bat
   ```
2. Dies erzeugt die Datei `realmguardian_migration_bundle.zip`. Sie enthält:
   - `backend/realmguardian.db` (Aktuelle WoW-Datenbank, Preishistorie, Chars & Berufe)
   - `backend/config.json` (Battle.net API Credentials & Discord Webhook)
3. Übertrage das Zip-Archiv via SCP / SFTP auf das Debian-System:
   ```bash
   scp realmguardian_migration_bundle.zip user@10.10.10.224:/opt/RealmGuardian/
   ```

---

## 🚀 2. Import & Start auf Debian (Zwei Wege)

Klone das Repository auf Debian:
```bash
git clone https://github.com/Voramir-ssc/RealmGuardian.git /opt/RealmGuardian
cd /opt/RealmGuardian
```

Importiere das Bundle mit dem automatischen Skript:
```bash
chmod +x import_migration_bundle.sh
./import_migration_bundle.sh
```
*(Alternativ: Kopiere `realmguardian.db` und `config.json` einfach direkt in das Verzeichnis `backend/`)*

---

### Weg A: Docker Compose Deployment (⭐ Empfohlen für SSC-LXNode)

Auf `SSC-LXNode` läuft die App als Multicontainer-Stack im externen Netzwerk `proxy-net`.

1. **Docker-Netzwerk sicherstellen:**
   ```bash
   docker network create proxy-net 2>/dev/null || true
   ```

2. **Container bauen und im Hintergrund starten:**
   ```bash
   docker compose up -d --build
   ```

3. **Status und Logs prüfen:**
   ```bash
   docker compose ps
   docker compose logs -f
   ```

   - Backend-Container: `realmguardian-backend` (Port intern 8000)
   - Frontend-Container: `realmguardian-frontend` (Port intern 80, Host-Port 5173)

---

### Weg B: Nativer Start / Entwicklungs-Modus auf Debian

Falls Docker nicht genutzt werden soll:

1. **Voraussetzungen installieren:**
   ```bash
   sudo apt update
   sudo apt install -y python3-venv python3-pip nodejs npm unzip
   ```

2. **Automatischer Dev-Start:**
   ```bash
   chmod +x service/debian/start_dev.sh
   ./service/debian/start_dev.sh
   ```
   *Richtet selbstständig `backend/venv` und `frontend/node_modules` ein und startet Backend auf `0.0.0.0:8000` sowie Frontend auf `0.0.0.0:5173`.*

---

## 🌐 3. Infrastruktur-Integration (SSC-LXNode)

### A. Nginx Proxy Manager (NPM) Host
- **Domain Names:** `realmguardian.ssc.slan`
- **Scheme:** `http`
- **Forward Hostname / IP:**
  - *Bei Docker (im `proxy-net`):* `realmguardian-frontend`
  - *Bei nativem Start / Dev-PC:* `10.10.10.224` (oder `10.10.10.220`)
- **Forward Port:** `80` *(bei Docker)* bzw. `5173` *(bei nativem Vite)*
- **Websockets Support:** `Ja` (Aktivieren)
- **Block Common Exploits:** `Ja`

### B. Homarr Kachel-Definition
- **App Name:** `RealmGuardian` (Helgris Schmiede)
- **Kategorie:** `Gaming & Tools`
- **Interne URL:** `http://realmguardian.ssc.slan`
- **Icon:** `world-of-warcraft` oder `tabler:shield-lock` / `tabler:hammer`

### C. Uptime Kuma Healthcheck
- **Monitor Typ:** `HTTP(s)`
- **Name:** `RealmGuardian API`
- **Target URL:** `http://10.10.10.224:8000/` *(Direkte Entkopplung vom Proxy)*
- **Erwarteter Status-Code:** `200`
- **Zusätzlicher Web-Check:** `http://realmguardian.ssc.slan` (Status `200`)

---

## 🤖 4. Anweisung für Antigravity auf dem neuen System

Wenn Meister dieses Projekt auf dem neuen Debian-System öffnet und sagt:
> *"Antigravity, nimm RealmGuardian in Betrieb!"*

Soll Antigravity folgendes ausführen:
1. Prüfen, ob `backend/realmguardian.db` und `backend/config.json` vorhanden sind. Wenn nicht, Meister bitten, `realmguardian_migration_bundle.zip` abzulegen oder `config.json` aus `config.example.json` zu erstellen.
2. Prüfen, ob Docker (`docker compose`) vorhanden ist:
   - Wenn ja: `docker compose up -d --build` ausführen und Healthcheck `http://localhost:8000/` prüfen.
   - Wenn nein: `python3-venv` & `npm` prüfen und `service/debian/start_dev.sh` starten.
3. Die NPM-, Homarr- und Uptime-Kuma-Parameter ausgeben und bestätigen, dass Helgris Schmiede wieder einsatzbereit ist!
