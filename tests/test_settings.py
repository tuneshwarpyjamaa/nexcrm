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
async def test_get_user_settings(client, mock_db):
    # Mock user settings data
    mock_db.fetchrow = AsyncMock(return_value={
        "user_id": "u_123",
        "email_notifications": True,
        "push_notifications": False,
        "theme": "light",
        "language": "en",
        "timezone": "UTC",
        "date_format": "YYYY-MM-DD",
        "time_format": "24h"
    })
    
    response = await client.get("/api/settings", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email_notifications"] is True
    assert data["push_notifications"] is False
    assert data["theme"] == "light"

@pytest.mark.anyio
async def test_update_user_settings(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "user_id": "u_123",
        "email_notifications": False,
        "push_notifications": True,
        "theme": "dark",
        "language": "es",
        "timezone": "EST",
        "date_format": "DD/MM/YYYY",
        "time_format": "12h"
    })
    
    response = await client.put("/api/settings", 
        json={
            "email_notifications": False,
            "push_notifications": True,
            "theme": "dark",
            "language": "es",
            "timezone": "EST",
            "date_format": "DD/MM/YYYY",
            "time_format": "12h"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email_notifications"] is False
    assert data["theme"] == "dark"
    assert data["language"] == "es"

@pytest.mark.anyio
async def test_get_settings_not_found(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value=None)
    
    response = await client.get("/api/settings", headers=headers)
    assert response.status_code == 404

@pytest.mark.anyio
async def test_update_partial_settings(client, mock_db):
    # Test updating only some settings
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "user_id": "u_123",
        "email_notifications": True,  # Changed
        "push_notifications": False,  # Unchanged
        "theme": "light",             # Unchanged
        "language": "en",             # Unchanged
        "timezone": "UTC",            # Unchanged
        "date_format": "YYYY-MM-DD",  # Unchanged
        "time_format": "24h"          # Unchanged
    })
    
    response = await client.put("/api/settings", 
        json={"email_notifications": True},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email_notifications"] is True

@pytest.mark.anyio
async def test_update_settings_invalid_theme(client, mock_db):
    # Test with invalid theme value
    response = await client.put("/api/settings", 
        json={"theme": "invalid_theme"},
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_update_settings_invalid_language(client, mock_db):
    # Test with invalid language code
    response = await client.put("/api/settings", 
        json={"language": "invalid_lang"},
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_update_settings_invalid_timezone(client, mock_db):
    # Test with invalid timezone
    response = await client.put("/api/settings", 
        json={"timezone": "invalid_timezone"},
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_update_settings_invalid_date_format(client, mock_db):
    # Test with invalid date format
    response = await client.put("/api/settings", 
        json={"date_format": "invalid_format"},
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_update_settings_invalid_time_format(client, mock_db):
    # Test with invalid time format
    response = await client.put("/api/settings", 
        json={"time_format": "invalid_format"},
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_create_default_settings(client, mock_db):
    # Test creating default settings for new user
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "user_id": "u_123",
        "email_notifications": True,
        "push_notifications": True,
        "theme": "light",
        "language": "en",
        "timezone": "UTC",
        "date_format": "YYYY-MM-DD",
        "time_format": "24h"
    })
    
    response = await client.post("/api/settings", 
        json={},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "light"
    assert data["language"] == "en"

@pytest.mark.anyio
async def test_reset_settings_to_default(client, mock_db):
    # Test resetting settings to default values
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "user_id": "u_123",
        "email_notifications": True,
        "push_notifications": True,
        "theme": "light",
        "language": "en",
        "timezone": "UTC",
        "date_format": "YYYY-MM-DD",
        "time_format": "24h"
    })
    
    response = await client.post("/api/settings/reset", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "light"
    assert data["language"] == "en"

@pytest.mark.anyio
async def test_export_settings(client, mock_db):
    # Test exporting settings as JSON
    mock_db.fetchrow = AsyncMock(return_value={
        "user_id": "u_123",
        "email_notifications": True,
        "push_notifications": False,
        "theme": "dark",
        "language": "en",
        "timezone": "UTC",
        "date_format": "YYYY-MM-DD",
        "time_format": "24h"
    })
    
    response = await client.get("/api/settings/export", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "settings" in data
    assert data["settings"]["theme"] == "dark"

@pytest.mark.anyio
async def test_import_settings(client, mock_db):
    # Test importing settings from JSON
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "user_id": "u_123",
        "email_notifications": False,
        "push_notifications": True,
        "theme": "dark",
        "language": "es",
        "timezone": "EST",
        "date_format": "DD/MM/YYYY",
        "time_format": "12h"
    })
    
    settings_data = {
        "email_notifications": False,
        "push_notifications": True,
        "theme": "dark",
        "language": "es",
        "timezone": "EST",
        "date_format": "DD/MM/YYYY",
        "time_format": "12h"
    }
    
    response = await client.post("/api/settings/import", 
        json=settings_data,
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

@pytest.mark.anyio
async def test_unauthorized_access(client, mock_db):
    # Test access without authentication
    response = await client.get("/api/settings")
    assert response.status_code == 401
