import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
import jwt
import os
from datetime import datetime, timedelta

# Create a mock JWT token to bypass auth middleware for testing
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
mock_token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
headers = {"Authorization": f"Bearer {mock_token}"}

@pytest.mark.anyio
async def test_get_deals(client, mock_db):
    # Mock multiple rows for deals list with correct field names
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "title": "Deal 1", 
            "value": 10000.0, 
            "stage": "lead",
            "contactid": "c_123",
            "company": "Acme Corp",
            "probability": 25,
            "closedate": (datetime.now() + timedelta(days=30)).date(),
            "notes": "Initial contact made",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        },
        {
            "id": "2", 
            "title": "Deal 2", 
            "value": 25000.0, 
            "stage": "qualified",
            "contactid": "c_456",
            "company": "Tech Inc",
            "probability": 75,
            "closedate": (datetime.now() + timedelta(days=60)).date(),
            "notes": "Proposal sent",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
    ])
    
    response = await client.get("/api/deals", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Deal 1"
    assert data[0]["value"] == 10000.0
    assert data[0]["contactId"] == "c_123"

@pytest.mark.anyio
async def test_create_deal(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "d_123", 
        "title": "New Deal", 
        "value": 15000.0, 
        "stage": "lead",
        "contactid": "c_789",
        "company": "New Company",
        "probability": 50,
        "closedate": (datetime.now() + timedelta(days=45)).date(),
        "notes": "New deal created",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    
    response = await client.post("/api/deals", 
        json={
            "title": "New Deal", 
            "value": 15000.0, 
            "stage": "lead",
            "contactId": "c_789",
            "company": "New Company",
            "probability": 50,
            "closeDate": (datetime.now() + timedelta(days=45)).date().isoformat(),
            "notes": "New deal created"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == "New Deal"
    assert response.json()["value"] == 15000.0
    assert response.json()["contactId"] == "c_789"

@pytest.mark.anyio
async def test_get_deal_by_id(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "d_123", 
        "title": "Specific Deal", 
        "value": 20000.0, 
        "stage": "proposal",
        "contactid": "c_123",
        "company": "Specific Corp",
        "probability": 80,
        "closedate": (datetime.now() + timedelta(days=30)).date(),
        "notes": "Specific deal notes",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    
    response = await client.get("/api/deals/d_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Specific Deal"
    assert data["stage"] == "proposal"

@pytest.mark.anyio
async def test_get_deal_not_found(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value=None)
    
    response = await client.get("/api/deals/nonexistent", headers=headers)
    assert response.status_code == 404

@pytest.mark.anyio
async def test_update_deal(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "d_123", 
        "title": "Updated Deal", 
        "value": 30000.0, 
        "stage": "negotiation",
        "contactid": "c_123",
        "company": "Updated Corp",
        "probability": 90,
        "closedate": datetime.now() + timedelta(days=15),
        "notes": "Updated deal notes",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    
    response = await client.put("/api/deals/d_123", 
        json={
            "title": "Updated Deal", 
            "value": 30000.0, 
            "stage": "negotiation",
            "probability": 90
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Deal"
    assert data["stage"] == "negotiation"

@pytest.mark.anyio
async def test_delete_deal(client, mock_db):
    mock_db.execute = AsyncMock(return_value="DELETE 1")
    
    response = await client.delete("/api/deals/d_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

@pytest.mark.anyio
async def test_create_deal_invalid_data(client, mock_db):
    # Test with missing required fields
    response = await client.post("/api/deals", 
        json={"value": 10000.0},
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_create_deal_invalid_value(client, mock_db):
    # Test with negative deal value
    response = await client.post("/api/deals", 
        json={
            "title": "Invalid Deal", 
            "value": -5000.0, 
            "stage": "lead",
            "contactId": "c_123"
        },
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_unauthorized_access(client, mock_db):
    # Test access without authentication
    response = await client.get("/api/deals")
    assert response.status_code == 401

@pytest.mark.anyio
async def test_invalid_token(client, mock_db):
    # Test with invalid token
    response = await client.get("/api/deals", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
