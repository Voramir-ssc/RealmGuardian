import json
import requests
from modules.api_client import BlizzardAPIClient

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("config.json not found!")
        return None

def test_api():
    config = load_config()
    if not config:
        return

    client = BlizzardAPIClient(
        config['blizzard_client_id'],
        config['blizzard_client_secret'],
        config.get('region', 'eu'),
        config.get('locale', 'de_DE')
    )

    # 2. Test Realm Status RAW
    realm_name = config.get('realm_name', 'Die Aldor')
    realm_slug = realm_name.lower().replace(' ', '-')
    print(f"\n2. Testing Realm Status for '{realm_slug}'...")
    
    url = f"https://{client.region}.api.blizzard.com/data/wow/realm/{realm_slug}"
    headers = client._get_headers()
    params = {'namespace': f'dynamic-{client.region}'}
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response JSON keys:", response.json().keys())
            print("Type field:", response.json().get('type'))
            print("Status field:", response.json().get('status'))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"FAILED: {e}")

    # 3. Test Item Search RAW
    search_term = "Friedensblume" # Static test
    print(f"\n3. Testing Item Search for '{search_term}'...")
    url = f"https://{client.region}.api.blizzard.com/data/wow/search/item"
    params = {
        'namespace': f'static-{client.region}',
        'locale': client.locale,
        'name.de_DE': search_term, 
        'orderby': 'id',
        '_page': 1
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Results Count: {len(response.json().get('results', []))}")
            if response.json().get('results'):
                print("First Result:", response.json().get('results')[0])
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"FAILED: {e}")

    # 4. Test WoW Token
    print(f"\n4. Testing WoW Token...")
    try:
        price = client.get_wow_token_price()
        print(f"Token Price: {price} Gold")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_api()
