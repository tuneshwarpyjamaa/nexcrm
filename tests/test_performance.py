import pytest
import asyncio
import time
import statistics
from httpx import AsyncClient
from unittest.mock import AsyncMock
import jwt
import os
from datetime import datetime, timedelta

class PerformanceMetrics:
    def __init__(self):
        self.response_times = []
        self.success_count = 0
        self.error_count = 0
        self.total_requests = 0
    
    def record_response(self, response_time: float, success: bool):
        self.response_times.append(response_time)
        self.total_requests += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def get_stats(self):
        if not self.response_times:
            return {}
        
        return {
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": (self.success_count / self.total_requests) * 100,
            "avg_response_time": statistics.mean(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "median_response_time": statistics.median(self.response_times),
            "p95_response_time": self._percentile(self.response_times, 95),
            "p99_response_time": self._percentile(self.response_times, 99)
        }
    
    def _percentile(self, data, percentile):
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

@pytest.mark.asyncio
async def test_concurrent_api_requests(client, mock_db):
    """Test performance under concurrent load"""
    metrics = PerformanceMetrics()
    
    # Mock database responses
    mock_db.fetch = AsyncMock(return_value=[
        {"id": "1", "name": "Contact 1", "email": "contact1@example.com"},
        {"id": "2", "name": "Contact 2", "email": "contact2@example.com"}
    ])
    
    # Create auth token
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    async def make_request():
        start_time = time.time()
        try:
            response = await client.get("/api/contacts", headers=headers)
            success = response.status_code == 200
        except Exception:
            success = False
        end_time = time.time()
        
        response_time = end_time - start_time
        metrics.record_response(response_time, success)
    
    # Run 50 concurrent requests
    tasks = [make_request() for _ in range(50)]
    await asyncio.gather(*tasks)
    
    stats = metrics.get_stats()
    
    # Performance assertions
    assert stats["success_rate"] >= 95  # At least 95% success rate
    assert stats["avg_response_time"] < 1.0  # Average response time under 1 second
    assert stats["p95_response_time"] < 2.0  # 95th percentile under 2 seconds

@pytest.mark.asyncio
async def test_database_query_performance(client, mock_db):
    """Test database query performance under load"""
    metrics = PerformanceMetrics()
    
    # Mock slower database responses to simulate real conditions
    async def slow_fetch(*args, **kwargs):
        await asyncio.sleep(0.1)  # Simulate 100ms database query
        return [
            {"id": f"{i}", "name": f"Deal {i}", "value": i * 1000}
            for i in range(100)
        ]
    
    mock_db.fetch = AsyncMock(side_effect=slow_fetch)
    
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    async def make_request():
        start_time = time.time()
        try:
            response = await client.get("/api/deals", headers=headers)
            success = response.status_code == 200
        except Exception:
            success = False
        end_time = time.time()
        
        response_time = end_time - start_time
        metrics.record_response(response_time, success)
    
    # Run 20 concurrent requests with database queries
    tasks = [make_request() for _ in range(20)]
    await asyncio.gather(*tasks)
    
    stats = metrics.get_stats()
    
    # Database query performance assertions
    assert stats["success_rate"] >= 90
    assert stats["avg_response_time"] < 0.5  # Should handle 100ms queries efficiently

@pytest.mark.asyncio
async def test_write_operation_performance(client, mock_db):
    """Test write operation performance"""
    metrics = PerformanceMetrics()
    
    # Mock database write operations
    async def slow_execute(*args, **kwargs):
        await asyncio.sleep(0.05)  # Simulate 50ms write operation
        return None
    
    async def slow_fetchrow(*args, **kwargs):
        await asyncio.sleep(0.05)  # Simulate 50ms read operation
        return {"id": "new_id", "name": "New Contact", "email": "new@example.com"}
    
    mock_db.execute = AsyncMock(side_effect=slow_execute)
    mock_db.fetchrow = AsyncMock(side_effect=slow_fetchrow)
    
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    async def create_contact():
        start_time = time.time()
        try:
            response = await client.post("/api/contacts", 
                json={
                    "name": f"Test Contact {time.time()}",
                    "email": f"test{time.time()}@example.com"
                },
                headers=headers
            )
            success = response.status_code == 200
        except Exception:
            success = False
        end_time = time.time()
        
        response_time = end_time - start_time
        metrics.record_response(response_time, success)
    
    # Run 30 concurrent write operations
    tasks = [create_contact() for _ in range(30)]
    await asyncio.gather(*tasks)
    
    stats = metrics.get_stats()
    
    # Write operation performance assertions
    assert stats["success_rate"] >= 90
    assert stats["avg_response_time"] < 0.3  # Should handle writes efficiently

@pytest.mark.asyncio
async def test_memory_usage_simulation(client, mock_db):
    """Test performance with large data sets"""
    metrics = PerformanceMetrics()
    
    # Mock large dataset responses
    def generate_large_dataset(size):
        return [
            {
                "id": f"{i}",
                "name": f"Contact {i}",
                "email": f"contact{i}@example.com",
                "phone": f"+1{random.randint(2000000000, 9999999999)}",
                "company": f"Company {i}",
                "created_at": datetime.now().isoformat()
            }
            for i in range(size)
        ]
    
    import random
    large_dataset = generate_large_dataset(1000)
    mock_db.fetch = AsyncMock(return_value=large_dataset)
    
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    async def make_request():
        start_time = time.time()
        try:
            response = await client.get("/api/contacts", headers=headers)
            success = response.status_code == 200
            # Verify response size
            if success:
                assert len(response.json()) == 1000
        except Exception:
            success = False
        end_time = time.time()
        
        response_time = end_time - start_time
        metrics.record_response(response_time, success)
    
    # Run 10 requests with large datasets
    tasks = [make_request() for _ in range(10)]
    await asyncio.gather(*tasks)
    
    stats = metrics.get_stats()
    
    # Large dataset performance assertions
    assert stats["success_rate"] >= 80  # May have some failures with large data
    assert stats["avg_response_time"] < 2.0  # Should handle large datasets reasonably

@pytest.mark.asyncio
async def test_authentication_performance(client, mock_db):
    """Test authentication endpoint performance"""
    metrics = PerformanceMetrics()
    
    # Mock authentication
    from auth.router import get_password_hash
    hashed = get_password_hash("password123")
    mock_db.fetchrow = AsyncMock(return_value={"password_hash": hashed})
    
    async def login():
        start_time = time.time()
        try:
            response = await client.post("/api/login", json={
                "email": "test@example.com",
                "password": "password123"
            })
            success = response.status_code == 200
            if success:
                assert "access_token" in response.json()
        except Exception:
            success = False
        end_time = time.time()
        
        response_time = end_time - start_time
        metrics.record_response(response_time, success)
    
    # Run 100 concurrent login attempts
    tasks = [login() for _ in range(100)]
    await asyncio.gather(*tasks)
    
    stats = metrics.get_stats()
    
    # Authentication performance assertions
    assert stats["success_rate"] >= 95
    assert stats["avg_response_time"] < 0.5  # Auth should be fast

@pytest.mark.asyncio
async def test_concurrent_user_simulation(client, mock_db):
    """Simulate multiple users performing different operations"""
    metrics = PerformanceMetrics()
    
    # Mock various database operations
    mock_db.fetch = AsyncMock(return_value=[
        {"id": "1", "name": "Contact 1", "email": "contact1@example.com"}
    ])
    mock_db.fetchrow = AsyncMock(return_value={
        "id": "new_id", "name": "New Entity", "created_at": datetime.now()
    })
    mock_db.execute = AsyncMock(return_value=None)
    
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    
    async def user_operations(user_id: int):
        headers = {"Authorization": f"Bearer {jwt.encode({'sub': f'user{user_id}@example.com', 'exp': datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm='HS256')}"}
        
        operations = [
            # Get contacts
            lambda: client.get("/api/contacts", headers=headers),
            # Get deals
            lambda: client.get("/api/deals", headers=headers),
            # Get tasks
            lambda: client.get("/api/tasks", headers=headers),
            # Create contact
            lambda: client.post("/api/contacts", 
                json={"name": f"User {user_id} Contact", "email": f"user{user_id}@example.com"},
                headers=headers
            ),
            # Create task
            lambda: client.post("/api/tasks", 
                json={"title": f"User {user_id} Task", "priority": "medium"},
                headers=headers
            )
        ]
        
        for operation in operations:
            start_time = time.time()
            try:
                response = await operation()
                success = response.status_code in [200, 201]
            except Exception:
                success = False
            end_time = time.time()
            
            response_time = end_time - start_time
            metrics.record_response(response_time, success)
    
    # Simulate 20 users with 5 operations each
    tasks = [user_operations(i) for i in range(20)]
    await asyncio.gather(*tasks)
    
    stats = metrics.get_stats()
    
    # Multi-user performance assertions
    assert stats["success_rate"] >= 85
    assert stats["avg_response_time"] < 1.0

@pytest.mark.asyncio
async def test_rate_limiting_simulation(client, mock_db):
    """Test performance under potential rate limiting"""
    metrics = PerformanceMetrics()
    
    mock_db.fetch = AsyncMock(return_value=[])
    
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    token = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    async def rapid_requests():
        # Make 10 requests in quick succession
        for _ in range(10):
            start_time = time.time()
            try:
                response = await client.get("/api/contacts", headers=headers)
                success = response.status_code in [200, 429]  # 429 = rate limited
            except Exception:
                success = False
            end_time = time.time()
            
            response_time = end_time - start_time
            metrics.record_response(response_time, success)
            await asyncio.sleep(0.01)  # Small delay between requests
    
    # Run 5 users making rapid requests
    tasks = [rapid_requests() for _ in range(5)]
    await asyncio.gather(*tasks)
    
    stats = metrics.get_stats()
    
    # Rate limiting performance assertions
    # Some requests might be rate limited (429), but overall should be reasonable
    assert stats["success_rate"] >= 70  # Allow for some rate limiting

if __name__ == "__main__":
    # Run performance tests individually
    pytest.main([__file__, "-v", "-s"])
