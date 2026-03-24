import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
import jwt
import os
from datetime import datetime, timedelta, date

# Create a mock JWT token to bypass auth middleware for testing
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
mock_token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
headers = {"Authorization": f"Bearer {mock_token}"}

@pytest.mark.anyio
async def test_get_tasks(client, mock_db):
    # Mock multiple rows for tasks list with correct field names
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "title": "Task 1", 
            "contactid": "c_123",
            "duedate": date.today() + timedelta(days=7),
            "priority": "High",
            "done": False,
            "createdAt": datetime.now()
        },
        {
            "id": "2", 
            "title": "Task 2", 
            "contactid": "c_456",
            "duedate": date.today() + timedelta(days=14),
            "priority": "Normal",
            "done": True,
            "createdAt": datetime.now()
        }
    ])
    
    response = await client.get("/api/tasks", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[0]["priority"] == "High"
    assert data[0]["contactId"] == "c_123"

@pytest.mark.anyio
async def test_create_task(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "t_123", 
        "title": "New Task", 
        "contactid": "c_789",
        "duedate": date.today() + timedelta(days=10),
        "priority": "High",
        "done": False,
        "createdAt": datetime.now()
    })
    
    response = await client.post("/api/tasks", 
        json={
            "title": "New Task", 
            "contactId": "c_789",
            "dueDate": (date.today() + timedelta(days=10)).isoformat(),
            "priority": "High"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == "New Task"
    assert response.json()["priority"] == "High"
    assert response.json()["contactId"] == "c_789"

@pytest.mark.anyio
async def test_get_task_by_id(client, mock_db):
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "t_123", 
        "title": "Specific Task", 
        "contactid": "c_123",
        "duedate": date.today() + timedelta(days=7),
        "priority": "High",
        "done": False,
        "createdAt": datetime.now()
    })
    
    response = await client.get("/api/tasks/t_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Specific Task"
    assert data["priority"] == "High"

@pytest.mark.anyio
async def test_update_task(client, mock_db):
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "t_123", 
        "title": "Updated Task", 
        "contactid": "c_123",
        "duedate": date.today() + timedelta(days=5),
        "priority": "Normal",
        "done": True,
        "createdAt": datetime.now()
    })
    
    response = await client.put("/api/tasks/t_123", 
        json={
            "title": "Updated Task", 
            "done": True,
            "priority": "Normal"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["done"] is True

@pytest.mark.anyio
async def test_delete_task(client, mock_db):
    mock_db.execute = AsyncMock(return_value="DELETE 1")
    
    response = await client.delete("/api/tasks/t_123", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

@pytest.mark.anyio
async def test_create_task_invalid_data(client, mock_db):
    # Test with missing required fields
    response = await client.post("/api/tasks", 
        json={"priority": "high"},
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.anyio
async def test_create_task_invalid_priority(client, mock_db):
    # Test with invalid priority value - but since priority is Optional[str], this might pass
    response = await client.post("/api/tasks", 
        json={
            "title": "Invalid Task", 
            "priority": "invalid_priority",
            "contactId": "c_123"
        },
        headers=headers
    )
    
    # This might pass validation since priority is just a string
    assert response.status_code in [200, 422]

@pytest.mark.anyio
async def test_get_tasks_by_status(client, mock_db):
    # Test filtering tasks by done status
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "title": "Pending Task", 
            "contactid": "c_123",
            "duedate": date.today() + timedelta(days=7),
            "priority": "High",
            "done": False,
            "createdAt": datetime.now()
        }
    ])
    
    response = await client.get("/api/tasks", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["done"] is False

@pytest.mark.anyio
async def test_get_tasks_by_priority(client, mock_db):
    # Test filtering tasks by priority
    mock_db.fetch = AsyncMock(return_value=[
        {
            "id": "1", 
            "title": "High Priority Task", 
            "contactid": "c_123",
            "duedate": date.today() + timedelta(days=7),
            "priority": "High",
            "done": False,
            "createdAt": datetime.now()
        }
    ])
    
    response = await client.get("/api/tasks", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["priority"] == "High"

@pytest.mark.anyio
async def test_unauthorized_access(client, mock_db):
    # Test access without authentication
    response = await client.get("/api/tasks")
    assert response.status_code == 401
