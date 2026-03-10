import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

pool = None

async def create_pool():
    return await asyncpg.create_pool(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        min_size=2,
        max_size=10,
        command_timeout=30,
        statement_cache_size=100,
    )

async def get_pool():
    global pool
    if pool is None:
        pool = await create_pool()
    return pool

async def close_pool():
    global pool
    if pool is not None:
        await pool.close()
        pool = None
