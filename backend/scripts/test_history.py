import requests
import sys

BASE_URL = "http://localhost:8000"

def test_history_ranges():
    ranges = ["24h", "7d", "1m", "1y"]
    
    print(f"Testing history endpoint at {BASE_URL}...")
    
    for r in ranges:
        try:
            url = f"{BASE_URL}/api/token/history?range={r}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[PASS] Range '{r}': {len(data)} items returned.")
            else:
                print(f"[FAIL] Range '{r}': Status {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"[ERROR] Range '{r}': {e}")

if __name__ == "__main__":
    test_history_ranges()
