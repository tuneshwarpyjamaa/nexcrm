import pytest
from unittest.mock import AsyncMock
import jwt
import os
from datetime import datetime, timedelta

# Create a mock JWT token to bypass auth middleware for testing
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
mock_token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
headers = {"Authorization": f"Bearer {mock_token}"}

@pytest.mark.anyio
async def test_get_subscription(client, mock_db):
    # Mock row return from database for get endpoint
    mock_db.fetchrow = AsyncMock(return_value={
        "plan_name": "free",
        "subscription_status": "active",
        "subscription_end_date": None
    })
    
    response = await client.get("/api/subscriptions/me", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["plan_name"] == "free"
    assert response.json()["subscription_status"] == "active"

@pytest.mark.anyio
async def test_get_subscription_not_found(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value=None)
    
    response = await client.get("/api/subscriptions/me", headers=headers)
    assert response.status_code == 404

@pytest.mark.anyio
async def test_upgrade_subscription(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    
    response = await client.post("/api/subscriptions/subscribe", headers=headers, json={
        "action": "upgrade",
        "plan_name": "premium"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "premium" in data["message"]
    # Verify mock_db execute was called with UPGRADE statement
    mock_db.execute.assert_called_once()
    assert "UPDATE users SET plan_name = $1" in mock_db.execute.call_args[0][0]

@pytest.mark.anyio
async def test_cancel_subscription(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    
    response = await client.post("/api/subscriptions/subscribe", headers=headers, json={
        "action": "cancel",
        "plan_name": "premium" # Not strictly required for cancel but aligns with schema
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Subscription cancelled"
    mock_db.execute.assert_called_once()
    assert "UPDATE users SET subscription_status = 'cancelled'" in mock_db.execute.call_args[0][0]
