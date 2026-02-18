from dotenv import load_dotenv
import os
import json

load_dotenv()

CONFIG_FILE = "config.json"

class Config:
    def __init__(self):
        self.client_id = os.getenv("BLIZZARD_CLIENT_ID", "")
        self.client_secret = os.getenv("BLIZZARD_CLIENT_SECRET", "")
        self.region = os.getenv("BLIZZARD_REGION", "eu")
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.client_id = data.get("client_id", self.client_id)
                self.client_secret = data.get("client_secret", self.client_secret)
                self.region = data.get("region", self.region)

    def save(self):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "region": self.region
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

config = Config()
