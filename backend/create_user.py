"""
Quick user creation script
"""

import asyncio
import asyncpg
import os
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    db = await asyncpg.connect(DATABASE_URL)
    
    email = "amish@gmail.com"
    name = "Amish"
    password = "password123"
    
    hashed_password = pwd_context.hash(password)
    
    await db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES ($1, $2, $3)",
        name, email, hashed_password
    )
    await db.close()
    
    print(f"User created: {email}")
    print("Password: password123")

if __name__ == "__main__":
    asyncio.run(create_user())
