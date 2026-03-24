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
async def test_complete_contact_workflow(client, mock_db):
    """Test complete workflow: create contact -> create deal -> create task -> create note"""
    
    # Step 1: Create a contact
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "c_123", 
        "name": "John Doe", 
        "email": "john@example.com", 
        "phone": "+1234567890",
        "company": "Acme Corp",
        "created_at": datetime.now()
    })
    
    contact_response = await client.post("/api/contacts", 
        json={
            "name": "John Doe", 
            "email": "john@example.com",
            "phone": "+1234567890",
            "company": "Acme Corp"
        },
        headers=headers
    )
    
    assert contact_response.status_code == 200
    contact_data = contact_response.json()
    contact_id = contact_data["id"]
    
    # Step 2: Create a deal for this contact
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "d_123", 
        "title": "Big Deal", 
        "value": 50000.0, 
        "status": "open",
        "contact_id": contact_id,
        "created_at": datetime.now()
    })
    
    deal_response = await client.post("/api/deals", 
        json={
            "title": "Big Deal", 
            "value": 50000.0, 
            "status": "open",
            "contact_id": contact_id
        },
        headers=headers
    )
    
    assert deal_response.status_code == 200
    deal_data = deal_response.json()
    deal_id = deal_data["id"]
    
    # Step 3: Create a task for this deal
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "t_123", 
        "title": "Follow up call", 
        "description": "Call client to discuss deal",
        "status": "pending",
        "priority": "high",
        "contact_id": contact_id,
        "deal_id": deal_id,
        "created_at": datetime.now()
    })
    
    task_response = await client.post("/api/tasks", 
        json={
            "title": "Follow up call", 
            "description": "Call client to discuss deal",
            "status": "pending",
            "priority": "high",
            "contact_id": contact_id,
            "deal_id": deal_id
        },
        headers=headers
    )
    
    assert task_response.status_code == 200
    task_data = task_response.json()
    task_id = task_data["id"]
    
    # Step 4: Create a note about the contact
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "n_123", 
        "title": "Initial Meeting Notes", 
        "content": "Had great initial meeting with John",
        "contact_id": contact_id,
        "created_at": datetime.now()
    })
    
    note_response = await client.post("/api/notes", 
        json={
            "title": "Initial Meeting Notes", 
            "content": "Had great initial meeting with John",
            "contact_id": contact_id
        },
        headers=headers
    )
    
    assert note_response.status_code == 200
    
    # Step 5: Log an activity
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "a_123", 
        "type": "meeting",
        "description": "Initial discovery meeting",
        "contact_id": contact_id,
        "deal_id": deal_id,
        "created_at": datetime.now()
    })
    
    activity_response = await client.post("/api/activities", 
        json={
            "type": "meeting",
            "description": "Initial discovery meeting",
            "contact_id": contact_id,
            "deal_id": deal_id
        },
        headers=headers
    )
    
    assert activity_response.status_code == 200

@pytest.mark.anyio
async def test_email_campaign_workflow(client, mock_db):
    """Test email campaign workflow: create contacts -> send emails -> track opens"""
    
    # Create multiple contacts
    contacts = [
        {"name": "Alice Smith", "email": "alice@example.com"},
        {"name": "Bob Johnson", "email": "bob@example.com"},
        {"name": "Carol White", "email": "carol@example.com"}
    ]
    
    contact_ids = []
    
    for contact in contacts:
        mock_db.fetchrow = AsyncMock(return_value={
            "id": f"c_{len(contact_ids) + 1}", 
            "name": contact["name"], 
            "email": contact["email"],
            "created_at": datetime.now()
        })
        
        response = await client.post("/api/contacts", json=contact, headers=headers)
        assert response.status_code == 200
        contact_ids.append(response.json()["id"])
    
    # Send emails to all contacts
    for i, contact_id in enumerate(contact_ids):
        mock_db.fetchrow = AsyncMock(return_value={
            "id": f"e_{i + 1}", 
            "to_email": contacts[i]["email"],
            "subject": "Special Offer",
            "body": "Check out our special offer!",
            "status": "sent",
            "contact_id": contact_id,
            "created_at": datetime.now()
        })
        
        response = await client.post("/api/emails/send", 
            json={
                "to_email": contacts[i]["email"],
                "subject": "Special Offer",
                "body": "Check out our special offer!",
                "contact_id": contact_id
            },
            headers=headers
        )
        
        assert response.status_code == 200
    
    # Track email opens
    mock_db.execute = AsyncMock(return_value=None)
    
    for i in range(len(contact_ids)):
        response = await client.get(f"/api/emails/track/e_{i + 1}/open")
        assert response.status_code == 200

@pytest.mark.anyio
async def test_sales_pipeline_workflow(client, mock_db):
    """Test complete sales pipeline: lead -> contact -> deal -> tasks -> won"""
    
    # Step 1: Create a lead (contact)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "c_lead_1", 
        "name": "Prospective Client", 
        "email": "lead@example.com",
        "created_at": datetime.now()
    })
    
    contact_response = await client.post("/api/contacts", 
        json={
            "name": "Prospective Client", 
            "email": "lead@example.com"
        },
        headers=headers
    )
    
    assert contact_response.status_code == 200
    contact_id = contact_response.json()["id"]
    
    # Step 2: Create initial deal
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "d_pipeline_1", 
        "title": "New Opportunity", 
        "value": 25000.0, 
        "status": "lead",
        "contact_id": contact_id,
        "created_at": datetime.now()
    })
    
    deal_response = await client.post("/api/deals", 
        json={
            "title": "New Opportunity", 
            "value": 25000.0, 
            "status": "lead",
            "contact_id": contact_id
        },
        headers=headers
    )
    
    assert deal_response.status_code == 200
    deal_id = deal_response.json()["id"]
    
    # Step 3: Create qualification tasks
    tasks = [
        {"title": "Initial call", "priority": "high"},
        {"title": "Send proposal", "priority": "medium"},
        {"title": "Follow up", "priority": "medium"}
    ]
    
    for i, task in enumerate(tasks):
        mock_db.fetchrow = AsyncMock(return_value={
            "id": f"t_{i + 1}", 
            "title": task["title"], 
            "status": "pending",
            "priority": task["priority"],
            "contact_id": contact_id,
            "deal_id": deal_id,
            "created_at": datetime.now()
        })
        
        response = await client.post("/api/tasks", 
            json={
                "title": task["title"],
                "priority": task["priority"],
                "contact_id": contact_id,
                "deal_id": deal_id
            },
            headers=headers
        )
        
        assert response.status_code == 200
    
    # Step 4: Update deal status through pipeline
    pipeline_stages = ["contacted", "qualified", "proposal", "negotiation", "won"]
    
    for stage in pipeline_stages:
        mock_db.fetchrow = AsyncMock(return_value={
            "id": deal_id,
            "title": "New Opportunity",
            "value": 25000.0,
            "status": stage,
            "contact_id": contact_id,
            "created_at": datetime.now()
        })
        
        response = await client.put(f"/api/deals/{deal_id}", 
            json={"status": stage},
            headers=headers
        )
        
        assert response.status_code == 200
    
    # Step 5: Log activities at each stage
    activities = [
        {"type": "call", "description": "Initial discovery call"},
        {"type": "email", "description": "Sent proposal document"},
        {"type": "meeting", "description": "Negotiation meeting"},
        {"type": "task", "description": "Final contract review"}
    ]
    
    for i, activity in enumerate(activities):
        mock_db.fetchrow = AsyncMock(return_value={
            "id": f"a_{i + 1}",
            "type": activity["type"],
            "description": activity["description"],
            "contact_id": contact_id,
            "deal_id": deal_id,
            "created_at": datetime.now()
        })
        
        response = await client.post("/api/activities", 
            json={
                "type": activity["type"],
                "description": activity["description"],
                "contact_id": contact_id,
                "deal_id": deal_id
            },
            headers=headers
        )
        
        assert response.status_code == 200

@pytest.mark.anyio
async def test_user_management_workflow(client, mock_db):
    """Test user management: register -> login -> update settings -> subscription"""
    
    # Step 1: Register new user
    mock_db.execute = AsyncMock(return_value=None)
    
    register_response = await client.post("/api/register", json={
        "name": "New User",
        "email": "newuser@example.com",
        "password": "securepassword123"
    })
    
    assert register_response.status_code == 200
    
    # Step 2: Login
    from auth.router import get_password_hash
    hashed = get_password_hash("securepassword123")
    
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "u_new_user",
        "email": "newuser@example.com",
        "password_hash": hashed
    })
    
    login_response = await client.post("/api/login", json={
        "email": "newuser@example.com",
        "password": "securepassword123"
    })
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: Update user settings
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "user_id": "u_new_user",
        "email_notifications": True,
        "push_notifications": False,
        "theme": "dark",
        "language": "en",
        "timezone": "UTC",
        "date_format": "YYYY-MM-DD",
        "time_format": "24h"
    })
    
    settings_response = await client.put("/api/settings", 
        json={
            "theme": "dark",
            "email_notifications": True,
            "push_notifications": False
        },
        headers=user_headers
    )
    
    assert settings_response.status_code == 200
    
    # Step 4: Upgrade subscription
    mock_db.execute = AsyncMock(return_value=None)
    
    subscription_response = await client.post("/api/subscriptions/subscribe", 
        json={
            "action": "upgrade",
            "plan_name": "premium"
        },
        headers=user_headers
    )
    
    assert subscription_response.status_code == 200

@pytest.mark.anyio
async def test_error_handling_workflow(client, mock_db):
    """Test error handling across different scenarios"""
    
    # Test unauthorized access
    response = await client.get("/api/contacts")
    assert response.status_code == 401
    
    # Test invalid token
    response = await client.get("/api/contacts", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    
    # Test valid token but database error
    mock_db.fetch = AsyncMock(side_effect=Exception("Database connection failed"))
    
    response = await client.get("/api/contacts", headers=headers)
    assert response.status_code == 500
    
    # Reset mock for successful case
    mock_db.fetch = AsyncMock(return_value=[])
    
    response = await client.get("/api/contacts", headers=headers)
    assert response.status_code == 200

@pytest.mark.anyio
async def test_data_consistency_workflow(client, mock_db):
    """Test data consistency across related entities"""
    
    # Create contact
    mock_db.execute = AsyncMock(return_value=None)
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "c_consistency_1", 
        "name": "Test Contact", 
        "email": "test@example.com",
        "created_at": datetime.now()
    })
    
    contact_response = await client.post("/api/contacts", 
        json={
            "name": "Test Contact", 
            "email": "test@example.com"
        },
        headers=headers
    )
    
    contact_id = contact_response.json()["id"]
    
    # Create deal linked to contact
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "d_consistency_1", 
        "title": "Test Deal", 
        "value": 10000.0, 
        "status": "open",
        "contact_id": contact_id,
        "created_at": datetime.now()
    })
    
    deal_response = await client.post("/api/deals", 
        json={
            "title": "Test Deal", 
            "value": 10000.0, 
            "status": "open",
            "contact_id": contact_id
        },
        headers=headers
    )
    
    deal_id = deal_response.json()["id"]
    
    # Verify contact appears in deal
    mock_db.fetchrow = AsyncMock(return_value={
        "id": deal_id,
        "title": "Test Deal",
        "value": 10000.0,
        "status": "open",
        "contact_id": contact_id,
        "created_at": datetime.now()
    })
    
    deal_get_response = await client.get(f"/api/deals/{deal_id}", headers=headers)
    assert deal_get_response.status_code == 200
    assert deal_get_response.json()["contact_id"] == contact_id
    
    # Create task linked to both contact and deal
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "t_consistency_1", 
        "title": "Test Task", 
        "status": "pending",
        "priority": "medium",
        "contact_id": contact_id,
        "deal_id": deal_id,
        "created_at": datetime.now()
    })
    
    task_response = await client.post("/api/tasks", 
        json={
            "title": "Test Task",
            "contact_id": contact_id,
            "deal_id": deal_id
        },
        headers=headers
    )
    
    task_id = task_response.json()["id"]
    
    # Verify task is linked correctly
    mock_db.fetchrow = AsyncMock(return_value={
        "id": task_id,
        "title": "Test Task",
        "contact_id": contact_id,
        "deal_id": deal_id,
        "created_at": datetime.now()
    })
    
    task_get_response = await client.get(f"/api/tasks/{task_id}", headers=headers)
    assert task_get_response.status_code == 200
    assert task_get_response.json()["contact_id"] == contact_id
    assert task_get_response.json()["deal_id"] == deal_id
