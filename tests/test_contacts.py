import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
import json
from datetime import datetime

@pytest.mark.anyio
async def test_get_contacts(client, mock_db):
    # Mock multiple rows with all required fields
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "name": "John Doe", 
            "email": "john@example.com",
            "phone": "+1234567890",
            "company": "Acme Corp",
            "title": "CEO",
            "status": "lead",
            "tags": '["vip", "client"]',
            "linkedin": "https://www.linkedin.com/in/johndoe",
            "notes": "Important client",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        },
        {
            "id": "2", 
            "name": "Jane Doe", 
            "email": "jane@example.com",
            "phone": "+0987654321",
            "company": "Tech Inc",
            "title": "CTO",
            "status": "prospect",
            "tags": '["prospect"]',
            "linkedin": "https://www.linkedin.com/in/janedoe",
            "notes": "Potential client",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
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
    assert data[0]["phone"] == "+1234567890"

@pytest.mark.anyio
async def test_create_contact(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "c_123", 
        "name": "New Contact", 
        "email": "new@example.com",
        "phone": "+1122334455",
        "company": "New Corp",
        "title": "Manager",
        "status": "lead",
        "tags": '["new"]',
        "linkedin": "https://www.linkedin.com/in/newcontact",
        "notes": "New contact notes",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    
    import os
    import jwt
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm="HS256")
    
    response = await client.post("/api/contacts", 
        json={
            "name": "New Contact", 
            "email": "new@example.com",
            "phone": "+1122334455",
            "company": "New Corp",
            "title": "Manager",
            "status": "lead",
            "tags": ["new"],
            "linkedin": "https://www.linkedin.com/in/newcontact",
            "notes": "New contact notes"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "New Contact"
    assert response.json()["phone"] == "+1122334455"

@pytest.mark.anyio
async def test_get_contact_by_id(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "c_123", 
        "name": "Specific Contact", 
        "email": "specific@example.com",
        "phone": "+1234567890",
        "company": "Specific Corp",
        "title": "Director",
        "status": "lead",
        "tags": '["important"]',
        "linkedin": "https://www.linkedin.com/in/specific",
        "notes": "Specific notes",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    
    import os
    import jwt
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm="HS256")
    
    response = await client.get("/api/contacts/c_123", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Specific Contact"
    assert data["email"] == "specific@example.com"

@pytest.mark.anyio
async def test_get_contact_not_found(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value=None)
    
    import os
    import jwt
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm="HS256")
    
    response = await client.get("/api/contacts/nonexistent", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

@pytest.mark.anyio
async def test_update_contact(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "c_123", 
        "name": "Updated Contact", 
        "email": "updated@example.com",
        "phone": "+9876543210",
        "company": "Updated Corp",
        "title": "Senior Manager",
        "status": "active",
        "tags": '["updated", "vip"]',
        "linkedin": "https://linkedin.com/in/updated",
        "notes": "Updated notes",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    
    import os
    import jwt
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm="HS256")
    
    response = await client.put("/api/contacts/c_123", 
        json={
            "name": "Updated Contact", 
            "phone": "+9876543210",
            "status": "active"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Contact"
    assert data["phone"] == "+9876543210"

@pytest.mark.anyio
async def test_delete_contact(client, mock_db):
    mock_db.execute = AsyncMock(return_value="DELETE 1")
    
    import os
    import jwt
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm="HS256")
    
    response = await client.delete("/api/contacts/c_123", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

@pytest.mark.anyio
async def test_create_contact_invalid_data(client, mock_db):
    # Test with missing required fields
    import os
    import jwt
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm="HS256")
    
    response = await client.post("/api/contacts", 
        json={"email": "incomplete@example.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_create_contact_invalid_email(client, mock_db):
    # Test with invalid email format
    import os
    import jwt
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm="HS256")
    
    response = await client.post("/api/contacts", 
        json={
            "name": "Test Contact",
            "email": "invalid-email-format"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_unauthorized_access(client, mock_db):
    # Test access without authentication
    response = await client.get("/api/contacts")
    assert response.status_code == 401
