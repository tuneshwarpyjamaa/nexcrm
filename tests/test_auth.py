import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_register(client, mock_db):
    # Mock the database execute call
    mock_db.execute = AsyncMock(return_value=None)
    
    response = await client.post("/api/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}

@pytest.mark.anyio
async def test_login(client, mock_db):
    # Mock the database fetchrow call for login
    # Need to provide a hashed password
    from auth.router import get_password_hash
    hashed = get_password_hash("password123")
    
    mock_db.fetchrow = AsyncMock(return_value={"password_hash": hashed})
    
    response = await client.post("/api/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

from unittest.mock import AsyncMock
