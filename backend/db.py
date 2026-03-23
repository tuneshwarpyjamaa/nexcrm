import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

_pool = None

async def init_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)

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

async def get_db():
    pool = await get_pool()
    # To keep compatibility with existing `db = await get_db()` and `await close_db(db)` code,
    # we can acquire a connection from the pool.
    return await pool.acquire()

async def close_db(db):
    # Release the acquired connection back to the pool
    pool = await get_pool()
    await pool.release(db)
