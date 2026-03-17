from fastapi.testclient import TestClient
from main import app
from db import get_pool
import asyncio

client = TestClient(app)

def test_sub():
    email = "test_sub3@example.com"
    r = client.post("/api/register", json={"name": "Test", "email": email, "password": "pass"})
    
    r = client.post("/api/login", json={"email": email, "password": "pass"})
    token = r.json().get("access_token")
    
    headers = {"Authorization": f"Bearer {token}"}
    r2 = client.post("/api/subscriptions/subscribe", json={"action": "upgrade", "plan_name": "premium"}, headers=headers)
    print("Status code:", r2.status_code)
    print("Response:", r2.text)

if __name__ == "__main__":
    # need to establish pool first for lifespan
    with client:
        test_sub()
