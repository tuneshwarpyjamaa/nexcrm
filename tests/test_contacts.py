import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
import json
from datetime import datetime

@pytest.mark.anyio
async def test_get_contacts(client, mock_db):
    # Mock multiple rows
    mock_db.fetch = AsyncMock(return_value=[
        {"id": "1", "name": "John Doe", "email": "john@example.com", "createdAt": datetime.now()},
        {"id": "2", "name": "Jane Doe", "email": "jane@example.com", "createdAt": datetime.now()}
    ])
    
    # We need a token for this request
    # For simplicity, we'll mock verify_token or provide a fake token and mock its decoding
    import os
    import jwt
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm="HS256")
    
    response = await client.get("/api/contacts", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "John Doe"

@pytest.mark.anyio
async def test_create_contact(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "c_123", "name": "New Contact", "email": "new@example.com", "createdAt": datetime.now()
    })
    
    import os
    import jwt
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm="HS256")
    
    response = await client.post("/api/contacts", 
        json={"name": "New Contact", "email": "new@example.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "New Contact"
