import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from datetime import datetime
import os
import jwt

@pytest.fixture
def auth_headers():
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.anyio
async def test_get_deals(client, mock_db, auth_headers):
    mock_db.fetch = AsyncMock(return_value=[
        {"id": "d1", "title": "Big Deal", "value": 5000, "createdAt": datetime.now()}
    ])
    
    response = await client.get("/api/deals", headers=auth_headers)
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Big Deal"

@pytest.mark.anyio
async def test_get_tasks(client, mock_db, auth_headers):
    mock_db.fetch = AsyncMock(return_value=[
        {"id": "t1", "title": "First Task", "done": False, "createdAt": datetime.now()}
    ])
    
    response = await client.get("/api/tasks", headers=auth_headers)
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "First Task"
