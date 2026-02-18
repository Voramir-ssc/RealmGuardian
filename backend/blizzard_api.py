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
        url = f"https://{self.region}.api.blizzard.com/data/wow/item/{item_id}?namespace=static-{self.region}&locale=en_US"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_item_media(self, item_id):
        token = self.get_token()
        url = f"https://{self.region}.api.blizzard.com/data/wow/media/item/{item_id}?namespace=static-{self.region}"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_commodity_price_snapshot(self):
        token = self.get_token()
        url = f"https://{self.region}.api.blizzard.com/data/wow/auctions/commodities?namespace=dynamic-{self.region}&locale=en_US"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    # --- OAuth2 & Profile Methods ---

    def get_authorization_url(self, redirect_uri):
        return f"https://oauth.battle.net/authorize?client_id={self.client_id}&scope=wow.profile&state=random_state&redirect_uri={redirect_uri}&response_type=code"

    def exchange_code_for_token(self, code, redirect_uri):
        url = "https://oauth.battle.net/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
        return None

    def get_account_profile(self, user_token):
        url = f"https://{self.region}.api.blizzard.com/profile/user/wow?namespace=profile-{self.region}&locale=en_US"
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_character_profile(self, user_token, realm_slug, char_name):
        # We need lowercase name and slug for API
        url = f"https://{self.region}.api.blizzard.com/profile/wow/character/{realm_slug}/{char_name.lower()}?namespace=profile-{self.region}&locale=en_US"
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
