import asyncpg
import os
from typing import AsyncGenerator
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

_pool = None


async def init_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=5,
            max_size=10,
            command_timeout=60,
            ssl="require"
        )


async def close_pool():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def get_pool():
    global _pool
    if _pool is None:
        await init_pool()
    return _pool


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """FastAPI dependency that yields a DB connection and guarantees release."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn
