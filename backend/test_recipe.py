import requests
from config import config
from blizzard_api import BlizzardAPI
import json

def test_recipe_search():
    print("Testing Recipe Search...")
    b = BlizzardAPI(config.client_id, config.client_secret, config.region)
    token = b.get_token()
    print(f"Token: {token[:10]}...")
    
    # Let's search items instead, as the recipe search might require specific parameters or be deprecated
    url = f"https://{b.region}.api.blizzard.com/data/wow/search/item?name.de_DE=Friedensblume&namespace=static-{b.region}&orderby=id&_page=1"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"GET {url}")
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
       data = response.json()
       print(json.dumps(data, indent=2)[:500])
    else:
       print(response.text)

if __name__ == '__main__':
    test_recipe_search()
