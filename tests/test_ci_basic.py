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
async def test_basic_imports():
    """Test that basic imports work"""
    try:
        import sys
        sys.path.append('./backend')
        from backend.main import app
        assert app is not None
        print("✅ Basic imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        raise

@pytest.mark.anyio
async def test_app_creation():
    """Test FastAPI app creation"""
    import sys
    sys.path.append('./backend')
    from backend.main import app
    
    assert app.title == "FastAPI"  # Default FastAPI title
    print("✅ App creation successful")

@pytest.mark.anyio
async def test_auth_register_basic(client, mock_db):
    """Test basic auth registration"""
    mock_db.execute = AsyncMock(return_value=None)
    
    response = await client.post("/api/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}
    print("✅ Auth registration working")

@pytest.mark.anyio
async def test_subscription_basic(client, mock_db):
    """Test basic subscription endpoint"""
    mock_db.fetchrow = AsyncMock(return_value={
        "plan_name": "Basic",
        "subscription_status": "active",
        "subscription_end_date": "2024-12-31"
    })
    
    response = await client.get("/api/subscriptions/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "plan_name" in data
    assert data["plan_name"] == "Basic"
    print("✅ Subscription endpoint working")

@pytest.mark.anyio
async def test_login_basic(client, mock_db):
    """Test basic login functionality"""
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
    print("✅ Login working")
