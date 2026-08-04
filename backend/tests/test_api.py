from fastapi.testclient import TestClient
import sys
import os

# Ensure backend root is in sys.path so it can find main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "RealmGuardian Backend is running" in data["message"]
