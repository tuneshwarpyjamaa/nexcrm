import pytest
import os
import sys
import asyncio

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from httpx import AsyncClient
from main import app
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def client():
    # Use ASGITransport to avoid deprecation warnings
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture(autouse=True)
async def mock_db(monkeypatch):
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    
    # Configure the mock pool to return the mock connection in an async context manager
    # async with pool.acquire() as conn:
    context_manager = MagicMock()
    context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
    context_manager.__aexit__ = AsyncMock(return_value=None)
    
    mock_pool.acquire.return_value = context_manager
    
    # Patch get_pool in all modules that might use it
    import db
    import auth.router
    import contacts.router
    import deals.router
    import tasks.router
    import notes.router
    import emails.router
    import activity.router
    import settings.router
    import subscriptions.router
    
    mock_get_pool = AsyncMock(return_value=mock_pool)
    
    monkeypatch.setattr(db, "get_pool", mock_get_pool)

    for module in [auth.router, contacts.router, deals.router, tasks.router,
                   notes.router, emails.router, activity.router, settings.router,
                   subscriptions.router]:
        if hasattr(module, "get_pool"):
            monkeypatch.setattr(module, "get_pool", mock_get_pool)

    # Also patch get_db if needed
    mock_get_db = AsyncMock(return_value=mock_conn)
    monkeypatch.setattr(db, "get_db", mock_get_db)

    for module in [auth.router, contacts.router, deals.router, tasks.router,
                   notes.router, emails.router, activity.router, settings.router,
                   subscriptions.router]:
        if hasattr(module, "get_db"):
            monkeypatch.setattr(module, "get_db", mock_get_db)
    
    return mock_conn
