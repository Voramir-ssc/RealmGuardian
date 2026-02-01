import requests
import datetime
import base64

class BlizzardAPIClient:
    def __init__(self, client_id, client_secret, region='eu', locale='de_DE'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.region = region
        self.locale = locale
        self.access_token = None
        self.token_expiry = datetime.datetime.now()

    def _get_token(self):
        if self.access_token and datetime.datetime.now() < self.token_expiry:
            return self.access_token

        url = f"https://{self.region}.battle.net/oauth/token"
        response = requests.post(url, data={'grant_type': 'client_credentials'}, auth=(self.client_id, self.client_secret), timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=data['expires_in'] - 60)
            return self.access_token
        else:
            raise Exception(f"Failed to retrieve access token: {response.status_code} - {response.text}")

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self._get_token()}',
            'Battlenet-Namespace': f'dynamic-{self.region}',
            'locale': self.locale
        }

    def get_wow_token_price(self):
        url = f"https://{self.region}.api.blizzard.com/data/wow/token/index"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()['price'] / 10000  # Convert to Gold
        return None

    def get_connected_realm_id(self, realm_slug):
        # Search for realm to get connected realm ID
        url = f"https://{self.region}.api.blizzard.com/data/wow/search/connected-realm"
        headers = self._get_headers()
        params = {
            'realms.slug': realm_slug,
            '_page': 1,
            'orderby': 'id',
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            results = response.json()['results']
            if results:
                return results[0]['data']['id']
        return None

    def get_realm_status(self, realm_slug):
        url = f"https://{self.region}.api.blizzard.com/data/wow/realm/{realm_slug}"
        headers = self._get_headers()
        params = {'namespace': f'dynamic-{self.region}'}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Simplified parsing based on actual response keys
            r_name = data.get('name', 'Unknown')
            # Status is often a generic 'type' in 'status' dict not found in all endpoints?
            # Based on debug output, we have 'type' at root.
            r_type = data.get('type', 'UNKNOWN')
            if isinstance(r_type, dict):
                 r_type = r_type.get('name', 'UNKNOWN')
                 
            # Check for 'status' field if it exists
            # data.get('status') might be a dict e.g. {'type': 'UP'}
            r_status = "UNKNOWN"
            status_field = data.get('status')
            if isinstance(status_field, dict):
                r_status = status_field.get('type', 'UNKNOWN')
            elif isinstance(status_field, str):
                r_status = status_field
            
            return f"{r_name} ({r_type} / {r_status})"
        return "Unknown"

    def get_auctions(self, connected_realm_id):
        # Regular auctions (non-commodity)
        url = f"https://{self.region}.api.blizzard.com/data/wow/connected-realm/{connected_realm_id}/auctions"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('auctions', [])
        return []

    def search_item(self, item_name):
        url = f"https://{self.region}.api.blizzard.com/data/wow/search/item"
        headers = self._get_headers()
        # Search ONLY in the configured locale to avoid implicit AND issues
        params = {
            'namespace': f'static-{self.region}',
            'locale': self.locale,
            f'name.{self.locale}': item_name,
            'orderby': 'id',
            '_page': 1
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            items = []
            for res in results:
                data = res.get('data', {})
                name = data.get('name', {}).get(self.locale, data.get('name', {}).get('en_US', 'Unknown'))
                item_id = data.get('id')
                items.append({'id': item_id, 'name': name})
            return items
        return []


    def get_commodity_auctions(self):
        # Commodity auctions (region-wide like Herbs)
        url = f"https://{self.region}.api.blizzard.com/data/wow/auctions/commodities"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('auctions', [])
        return []
        
    def get_item_price(self, item_id, auctions):
        # Helper to calculate average price from a list of auctions for a specific item
        # Filter auctions for item
        item_auctions = [a for a in auctions if a['item']['id'] == item_id]
        if not item_auctions:
            return 0
        
        # Calculate weighted average or min buyout? User asked for average.
        # Often min buyout is more relevant, but let's do simple average unit_price
        total_price = 0
        total_quantity = 0
        
        for auction in item_auctions:
            price = auction.get('unit_price', auction.get('buyout', 0))
            quantity = auction.get('quantity', 1)
            total_price += price * quantity
            total_quantity += quantity
            
        if total_quantity == 0:
            return 0
            
        return (total_price / total_quantity) / 10000 # Return in Gold
