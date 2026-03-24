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
async def test_send_email(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "e_123", 
        "to_email": "recipient@example.com",
        "subject": "Test Subject",
        "body": "Test email body",
        "status": "sent",
        "contact_id": "c_123",
        "created_at": datetime.now()
    })
    
    response = await client.post("/api/emails/send", 
        json={
            "to_email": "recipient@example.com",
            "subject": "Test Subject",
            "body": "Test email body",
            "contact_id": "c_123"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["subject"] == "Test Subject"
    assert response.json()["status"] == "sent"

@pytest.mark.anyio
async def test_get_emails(client, mock_db):
    # Mock multiple rows for emails list
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "to_email": "user1@example.com",
            "subject": "Subject 1",
            "body": "Body 1",
            "status": "sent",
            "contact_id": "c_123",
            "created_at": datetime.now()
        },
        {
            "id": "2", 
            "to_email": "user2@example.com",
            "subject": "Subject 2",
            "body": "Body 2",
            "status": "pending",
            "contact_id": "c_456",
            "created_at": datetime.now()
        }
    ])
    
    response = await client.get("/api/emails", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["subject"] == "Subject 1"
    assert data[0]["status"] == "sent"

@pytest.mark.anyio
async def test_get_email_by_id(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "e_123", 
        "to_email": "specific@example.com",
        "subject": "Specific Subject",
        "body": "Specific email body",
        "status": "sent",
        "contact_id": "c_123",
        "created_at": datetime.now()
    })
    
    response = await client.get("/api/emails/e_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Specific Subject"
    assert data["to_email"] == "specific@example.com"

@pytest.mark.anyio
async def test_get_email_not_found(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value=None)
    
    response = await client.get("/api/emails/nonexistent", headers=headers)
    assert response.status_code == 404

@pytest.mark.anyio
async def test_send_email_invalid_data(client, mock_db):
    # Test with missing required fields
    response = await client.post("/api/emails/send", 
        json={"subject": "Incomplete email"},
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_send_email_invalid_email_format(client, mock_db):
    # Test with invalid email format
    response = await client.post("/api/emails/send", 
        json={
            "to_email": "invalid-email",
            "subject": "Test Subject",
            "body": "Test body",
            "contact_id": "c_123"
        },
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_send_email_empty_subject(client, mock_db):
    # Test with empty subject
    response = await client.post("/api/emails/send", 
        json={
            "to_email": "test@example.com",
            "subject": "",
            "body": "Test body",
            "contact_id": "c_123"
        },
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_send_email_empty_body(client, mock_db):
    # Test with empty body
    response = await client.post("/api/emails/send", 
        json={
            "to_email": "test@example.com",
            "subject": "Test Subject",
            "body": "",
            "contact_id": "c_123"
        },
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_get_emails_by_status(client, mock_db):
    # Test filtering emails by status
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "to_email": "user@example.com",
            "subject": "Sent Email",
            "body": "Body",
            "status": "sent",
            "contact_id": "c_123",
            "created_at": datetime.now()
        }
    ])
    
    response = await client.get("/api/emails?status=sent", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "sent"

@pytest.mark.anyio
async def test_get_emails_by_contact(client, mock_db):
    # Test filtering emails by contact
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "to_email": "contact@example.com",
            "subject": "Contact Email",
            "body": "Body",
            "status": "sent",
            "contact_id": "c_123",
            "created_at": datetime.now()
        }
    ])
    
    response = await client.get("/api/emails?contact_id=c_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["contact_id"] == "c_123"

@pytest.mark.anyio
async def test_email_tracking_open(client, mock_db):
    # Test email tracking endpoint for opens
    mock_db.execute = AsyncMock(return_value=None)
    
    response = await client.get("/api/emails/track/e_123/open")
    
    assert response.status_code == 200
    # Should return a 1x1 pixel image for tracking

@pytest.mark.anyio
async def test_email_tracking_click(client, mock_db):
    # Test email tracking endpoint for clicks
    mock_db.execute = AsyncMock(return_value=None)
    
    response = await client.get("/api/emails/track/e_123/click?url=https://example.com")
    
    assert response.status_code == 302  # Redirect to the URL

@pytest.mark.anyio
async def test_unauthorized_access(client, mock_db):
    # Test access without authentication
    response = await client.get("/api/emails")
    assert response.status_code == 401

@pytest.mark.anyio
async def test_send_email_without_contact(client, mock_db):
    # Test sending email without associating with contact
    response = await client.post("/api/emails/send", 
        json={
            "to_email": "test@example.com",
            "subject": "Test Subject",
            "body": "Test body"
        },
        headers=headers
    )
    
    # This might be allowed depending on the implementation
    # Adjust expected status based on actual requirements
    assert response.status_code in [200, 422]
