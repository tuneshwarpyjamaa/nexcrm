import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
import jwt
import os
from datetime import datetime, timedelta

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
async def test_register_invalid_email(client, mock_db):
    response = await client.post("/api/register", json={
        "name": "Test User",
        "email": "invalid-email",
        "password": "password123"
    })
    
    assert response.status_code == 422

@pytest.mark.anyio
async def test_register_weak_password(client, mock_db):
    response = await client.post("/api/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "123"
    })
    
    assert response.status_code == 422

@pytest.mark.anyio
async def test_register_missing_fields(client, mock_db):
    response = await client.post("/api/register", json={
        "name": "Test User"
        # Missing email and password
    })
    
    assert response.status_code == 422

@pytest.mark.anyio
async def test_register_empty_name(client, mock_db):
    response = await client.post("/api/register", json={
        "name": "",
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 422

@pytest.mark.anyio
async def test_register_duplicate_email(client, mock_db):
    # Mock database to return existing user
    mock_db.fetchrow = AsyncMock(return_value={"id": "existing_user"})
    
    response = await client.post("/api/register", json={
        "name": "Test User",
        "email": "existing@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 400

@pytest.mark.anyio
async def test_login(client, mock_db):
    # Mock the database fetchrow call for login
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

@pytest.mark.anyio
async def test_login_invalid_email(client, mock_db):
    response = await client.post("/api/login", json={
        "email": "invalid-email",
        "password": "password123"
    })
    
    assert response.status_code == 422

@pytest.mark.anyio
async def test_login_empty_password(client, mock_db):
    response = await client.post("/api/login", json={
        "email": "test@example.com",
        "password": ""
    })
    
    assert response.status_code == 422

@pytest.mark.anyio
async def test_login_missing_fields(client, mock_db):
    response = await client.post("/api/login", json={
        "email": "test@example.com"
        # Missing password
    })
    
    assert response.status_code == 422

@pytest.mark.anyio
async def test_login_user_not_found(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value=None)
    
    response = await client.post("/api/login", json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 401

@pytest.mark.anyio
async def test_login_wrong_password(client, mock_db):
    from auth.router import get_password_hash
    hashed = get_password_hash("correct_password")
    
    mock_db.fetchrow = AsyncMock(return_value={"password_hash": hashed})
    
    response = await client.post("/api/login", json={
        "email": "test@example.com",
        "password": "wrong_password"
    })
    
    assert response.status_code == 401

@pytest.mark.anyio
async def test_login_database_error(client, mock_db):
    mock_db.fetchrow = AsyncMock(side_effect=Exception("Database error"))
    
    response = await client.post("/api/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 500

@pytest.mark.anyio
async def test_token_validation_valid_token(client, mock_db):
    # Create a valid token
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
    
    response = await client.get("/api/protected-endpoint", headers={"Authorization": f"Bearer {token}"})
    # This test assumes there's a protected endpoint to validate against

@pytest.mark.anyio
async def test_token_validation_expired_token(client, mock_db):
    # Create an expired token
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    expired_token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() - timedelta(minutes=1)}, SECRET_KEY, algorithm="HS256")
    
    response = await client.get("/api/protected-endpoint", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401

@pytest.mark.anyio
async def test_token_validation_invalid_token(client, mock_db):
    response = await client.get("/api/protected-endpoint", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

@pytest.mark.anyio
async def test_token_validation_missing_token(client, mock_db):
    response = await client.get("/api/protected-endpoint")
    assert response.status_code == 401

@pytest.mark.anyio
async def test_token_validation_malformed_token(client, mock_db):
    response = await client.get("/api/protected-endpoint", headers={"Authorization": "Bearer malformed.token.here"})
    assert response.status_code == 401

@pytest.mark.anyio
async def test_password_hashing_consistency():
    from auth.router import get_password_hash
    password = "test_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Hashes should be different due to salt
    assert hash1 != hash2
    # But both should be properly formatted
    assert hash1.startswith("$2b$12$")
    assert hash2.startswith("$2b$12$")

@pytest.mark.anyio
async def test_password_verification():
    from auth.router import get_password_hash, verify_password
    password = "test_password"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

@pytest.mark.anyio
async def test_oauth_login_initiation(client, mock_db):
    response = await client.get("/api/auth/google")
    assert response.status_code == 200  # Returns auth_url instead of redirect
    assert "auth_url" in response.json()

@pytest.mark.anyio
async def test_oauth_callback_success(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value=None)  # User doesn't exist
    mock_db.execute = AsyncMock(return_value=None)
    
    response = await client.get("/api/auth/google/callback?code=valid_code&state=valid_state")
    assert response.status_code in [200, 302]

@pytest.mark.anyio
async def test_oauth_callback_error(client, mock_db):
    response = await client.get("/api/auth/google/callback?error=access_denied")
    assert response.status_code == 400

@pytest.mark.anyio
async def test_password_reset_request(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value={"email": "test@example.com"})
    mock_db.execute = AsyncMock(return_value=None)
    
    response = await client.post("/api/reset-password-request", data={
        "email": "test@example.com"
    })
    
    assert response.status_code == 200

@pytest.mark.anyio
async def test_password_reset_request_invalid_email(client, mock_db):
    response = await client.post("/api/reset-password-request", data={
        "email": "invalid-email"
    })
    
    assert response.status_code == 422

@pytest.mark.anyio
async def test_password_reset_nonexistent_user(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value=None)
    
    response = await client.post("/api/reset-password-request", data={
        "email": "nonexistent@example.com"
    })
    
    assert response.status_code == 404

@pytest.mark.anyio
async def test_password_reset_confirmation(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value={"email": "test@example.com"})
    mock_db.execute = AsyncMock(return_value=None)
    
    response = await client.post("/api/reset-password", json={
        "token": "valid_token",
        "new_password": "new_password123"
    })
    
    assert response.status_code == 200

@pytest.mark.anyio
async def test_password_reset_invalid_token(client, mock_db):
    response = await client.post("/api/reset-password", json={
        "token": "invalid_token",
        "new_password": "new_password123"
    })
    
    assert response.status_code == 400

@pytest.mark.anyio
async def test_password_reset_weak_password(client, mock_db):
    response = await client.post("/api/reset-password", json={
        "token": "valid_token",
        "new_password": "123"
    })
    
    assert response.status_code == 422

@pytest.mark.anyio
async def test_change_password(client, mock_db):
    from auth.router import get_password_hash
    current_hashed = get_password_hash("current_password")
    
    mock_db.fetchrow = AsyncMock(return_value={"password_hash": current_hashed})
    mock_db.execute = AsyncMock(return_value=None)
    
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
    
    response = await client.post("/api/change-password",
        data={
            "current_password": "current_password",
            "new_password": "new_password123"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200

@pytest.mark.anyio
async def test_change_password_wrong_current(client, mock_db):
    from auth.router import get_password_hash
    current_hashed = get_password_hash("current_password")
    
    mock_db.fetchrow = AsyncMock(return_value={"password_hash": current_hashed})
    
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
    
    response = await client.post("/api/change-password",
        data={
            "current_password": "wrong_password",
            "new_password": "new_password123"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 401

@pytest.mark.anyio
async def test_logout(client, mock_db):
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
    
    response = await client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
