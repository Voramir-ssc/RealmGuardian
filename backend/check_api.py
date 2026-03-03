from blizzard_api import BlizzardAPI
from config import config
client = BlizzardAPI(config.client_id, config.client_secret, config.region)
res = client.get_item_details(2447)
print("Result:")
print(res)
