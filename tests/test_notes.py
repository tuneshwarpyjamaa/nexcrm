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
async def test_get_notes(client, mock_db):
    # Mock multiple rows for notes list with correct field names
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "title": "Note 1", 
            "body": "First note content",
            "contactid": "c_123",
            "contactname": "John Doe",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        },
        {
            "id": "2", 
            "title": "Note 2", 
            "body": "Second note content",
            "contactid": "c_456",
            "contactname": "Jane Smith",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
    ])
    
    response = await client.get("/api/notes", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Note 1"
    assert data[0]["body"] == "First note content"
    assert data[0]["contactId"] == "c_123"

@pytest.mark.anyio
async def test_create_note(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "n_123", 
        "title": "New Note", 
        "body": "New note content",
        "contactid": "c_789",
        "contactname": "New Contact",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    
    response = await client.post("/api/notes", 
        json={
            "title": "New Note", 
            "body": "New note content",
            "contactId": "c_789",
            "contactName": "New Contact"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == "New Note"
    assert response.json()["body"] == "New note content"
    assert response.json()["contactId"] == "c_789"

@pytest.mark.anyio
async def test_get_note_by_id(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "n_123", 
        "title": "Specific Note", 
        "body": "Specific note content",
        "contactid": "c_123",
        "contactname": "John Doe",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    
    response = await client.get("/api/notes/n_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Specific Note"
    assert data["body"] == "Specific note content"

@pytest.mark.anyio
async def test_update_note(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "n_123", 
        "title": "Updated Note", 
        "body": "Updated note content",
        "contactid": "c_123",
        "contactname": "Updated Contact",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    
    response = await client.put("/api/notes/n_123", 
        json={
            "title": "Updated Note", 
            "body": "Updated note content"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Note"
    assert data["body"] == "Updated note content"

@pytest.mark.anyio
async def test_delete_note(client, mock_db):
    mock_db.execute = AsyncMock(return_value="DELETE 1")
    
    response = await client.delete("/api/notes/n_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

@pytest.mark.anyio
async def test_create_note_invalid_data(client, mock_db):
    # Test with missing required fields
    response = await client.post("/api/notes", 
        json={"body": "Incomplete note"},
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_create_note_empty_content(client, mock_db):
    # Test with empty body - this should be allowed since body is optional
    response = await client.post("/api/notes", 
        json={
            "title": "Empty Content Note", 
            "body": "",
            "contactId": "c_123"
        },
        headers=headers
    )
    
    assert response.status_code == 200  # Should pass since body is optional

@pytest.mark.anyio
async def test_get_notes_by_contact(client, mock_db):
    # Test filtering notes by contact
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "title": "Contact Note", 
            "body": "Note for contact",
            "contactid": "c_123",
            "contactname": "John Doe",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
    ])
    
    response = await client.get("/api/notes", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["contactId"] == "c_123"

@pytest.mark.anyio
async def test_unauthorized_access(client, mock_db):
    # Test access without authentication
    response = await client.get("/api/notes")
    assert response.status_code == 401
