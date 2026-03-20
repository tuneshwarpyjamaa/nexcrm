import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

async def get_db():
    return await asyncpg.connect(DATABASE_URL)

async def close_db(db):
    await db.close()
