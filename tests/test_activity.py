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
async def test_get_activities(client, mock_db):
    # Mock multiple rows for activities list
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "type": "call",
            "description": "Called client about proposal",
            "contact_id": "c_123",
            "deal_id": "d_123",
            "user_id": "u_123",
            "created_at": datetime.now()
        },
        {
            "id": "2", 
            "type": "email",
            "description": "Sent follow-up email",
            "contact_id": "c_456",
            "deal_id": None,
            "user_id": "u_123",
            "created_at": datetime.now()
        }
    ])
    
    response = await client.get("/api/activities", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["type"] == "call"
    assert data[0]["description"] == "Called client about proposal"

@pytest.mark.anyio
async def test_create_activity(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "a_123", 
        "type": "meeting",
        "description": "Meeting with client",
        "contact_id": "c_789",
        "deal_id": "d_456",
        "user_id": "u_123",
        "created_at": datetime.now()
    })
    
    response = await client.post("/api/activities", 
        json={
            "type": "meeting",
            "description": "Meeting with client",
            "contact_id": "c_789",
            "deal_id": "d_456"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["type"] == "meeting"
    assert response.json()["description"] == "Meeting with client"

@pytest.mark.anyio
async def test_get_activity_by_id(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "a_123", 
        "type": "task",
        "description": "Completed task",
        "contact_id": "c_123",
        "deal_id": "d_123",
        "user_id": "u_123",
        "created_at": datetime.now()
    })
    
    response = await client.get("/api/activities/a_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "task"
    assert data["description"] == "Completed task"

@pytest.mark.anyio
async def test_get_activity_not_found(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value=None)
    
    response = await client.get("/api/activities/nonexistent", headers=headers)
    assert response.status_code == 404

@pytest.mark.anyio
async def test_update_activity(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "a_123", 
        "type": "call",
        "description": "Updated call description",
        "contact_id": "c_123",
        "deal_id": "d_123",
        "user_id": "u_123",
        "created_at": datetime.now()
    })
    
    response = await client.put("/api/activities/a_123", 
        json={
            "description": "Updated call description"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated call description"

@pytest.mark.anyio
async def test_delete_activity(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    
    response = await client.delete("/api/activities/a_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

@pytest.mark.anyio
async def test_create_activity_invalid_data(client, mock_db):
    # Test with missing required fields
    response = await client.post("/api/activities", 
        json={"type": "call"},
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_create_activity_invalid_type(client, mock_db):
    # Test with invalid activity type
    response = await client.post("/api/activities", 
        json={
            "type": "invalid_type",
            "description": "Invalid activity",
            "contact_id": "c_123"
        },
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_create_activity_empty_description(client, mock_db):
    # Test with empty description
    response = await client.post("/api/activities", 
        json={
            "type": "call",
            "description": "",
            "contact_id": "c_123"
        },
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_get_activities_by_type(client, mock_db):
    # Test filtering activities by type
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "type": "call",
            "description": "Call activity",
            "contact_id": "c_123",
            "deal_id": None,
            "user_id": "u_123",
            "created_at": datetime.now()
        }
    ])
    
    response = await client.get("/api/activities?type=call", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "call"

@pytest.mark.anyio
async def test_get_activities_by_contact(client, mock_db):
    # Test filtering activities by contact
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "type": "email",
            "description": "Email activity",
            "contact_id": "c_123",
            "deal_id": None,
            "user_id": "u_123",
            "created_at": datetime.now()
        }
    ])
    
    response = await client.get("/api/activities?contact_id=c_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["contact_id"] == "c_123"

@pytest.mark.anyio
async def test_get_activities_by_deal(client, mock_db):
    # Test filtering activities by deal
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "type": "meeting",
            "description": "Meeting activity",
            "contact_id": "c_123",
            "deal_id": "d_123",
            "user_id": "u_123",
            "created_at": datetime.now()
        }
    ])
    
    response = await client.get("/api/activities?deal_id=d_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["deal_id"] == "d_123"

@pytest.mark.anyio
async def test_create_activity_without_contact_or_deal(client, mock_db):
    # Test creating activity without associating with contact or deal
    response = await client.post("/api/activities", 
        json={
            "type": "task",
            "description": "General activity"
        },
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error - should have at least one

@pytest.mark.anyio
async def test_unauthorized_access(client, mock_db):
    # Test access without authentication
    response = await client.get("/api/activities")
    assert response.status_code == 401
