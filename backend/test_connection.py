from config import config
from blizzard_api import BlizzardAPI
print("Teste Konfiguration...")
if not config.client_id or not config.client_secret:
    print("FEHLER: Client ID oder Secret fehlen in der Konfiguration.")
    sys.exit(1)

print("Konfiguration gefunden. Teste Blizzard API Verbindung...")
api = BlizzardAPI(config.client_id, config.client_secret, config.region)

try:
    token = api.get_token()
    if token:
        print("ERFOLG: Access Token erhalten.")
        
        print("Versuche WoW Token Preis abzurufen...")
        price_data = api.get_wow_token_price()
        if price_data:
            print(f"ERFOLG: WoW Token Preis abgerufen: {price_data.get('price', 0) / 10000}g")
        else:
            print("WARNUNG: Token konnte authentifiziert werden, aber Preisabfrage schlug fehl.")
    else:
        print("FEHLER: Kein Access Token erhalten.")
except Exception as e:
    print(f"FEHLER: Ausnahme bei API Verbindung: {e}")
    sys.exit(1)


