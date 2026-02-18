import requests
import time
from datetime import datetime

class BlizzardAPI:
    def __init__(self, client_id, client_secret, region="eu"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.region = region
        self.access_token = None
        self.token_expiry = 0

    def get_token(self):
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token

        url = f"https://{self.region}.battle.net/oauth/token"
        response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(self.client_id, self.client_secret))
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.token_expiry = time.time() + data["expires_in"] - 60 # Buffer
            return self.access_token
        else:
            raise Exception(f"Failed to get access token: {response.text}")

    def get_wow_token_price(self):
        token = self.get_token()
        url = f"https://{self.region}.api.blizzard.com/data/wow/token/index?namespace=dynamic-{self.region}"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching token price: {response.text}")
            return None

    def get_item_details(self, item_id):
        token = self.get_token()
        url = f"https://{self.region}.api.blizzard.com/data/wow/item/{item_id}?namespace=static-{self.region}&locale=en_US" # English for universal names
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_commodity_price_snapshot(self):
        token = self.get_token()
        # Fetch the auction house index to get the commodities URL
        # For connected realms, we usually query by a specific realm ID.
        # But commodities are region-wide (mostly). 
        # Actually, commodities are region-wide but accessed via a connected-realm ID.
        # Let's use a default connected realm for EU (e.g. 1305 for Aegwynn, or just any works for commodities).
        # Better: Use the Auctions API which separates commodities.
        
        # We need a connected realm ID. 
        # For simplicity, let's use a known big one or try to find one. 
        # EU-Silvermoon is 1325.
        connected_realm_id = 1325 
        
        url = f"https://{self.region}.api.blizzard.com/data/wow/connected-realm/{connected_realm_id}/auctions/commodities?namespace=dynamic-{self.region}"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
