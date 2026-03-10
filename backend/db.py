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
    )

async def get_pool():
    global pool
    if pool is None:
        pool = await create_pool()
    return pool
