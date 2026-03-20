import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

async def init_db():
    db = await asyncpg.connect(DATABASE_URL)
    
    # Drop existing tables
    await db.execute("DROP TABLE IF EXISTS contacts")
    await db.execute("DROP TABLE IF EXISTS deals")
    await db.execute("DROP TABLE IF EXISTS users")
    
    # Create users table
    await db.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            provider TEXT DEFAULT 'local',
            google_id TEXT,
            plan_name TEXT DEFAULT 'free',
            subscription_status TEXT DEFAULT 'active',
            subscription_end_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create contacts table
    await db.execute("""
        CREATE TABLE contacts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            company TEXT,
            title TEXT,
            status TEXT,
            tags TEXT,
            linkedin TEXT,
            notes TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create deals table
    await db.execute("""
        CREATE TABLE deals (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            contactId TEXT,
            company TEXT,
            value REAL DEFAULT 0.0,
            stage TEXT DEFAULT 'Lead',
            probability INTEGER DEFAULT 0,
            closeDate TEXT,
            notes TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create tasks table
    await db.execute("""
        CREATE TABLE tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            contactId TEXT,
            dueDate TEXT,
            priority TEXT DEFAULT 'Normal',
            done INTEGER DEFAULT 0,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create notes table
    await db.execute("""
        CREATE TABLE notes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            body TEXT,
            contactId TEXT,
            contactName TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create emails table
    await db.execute("""
        CREATE TABLE emails (
            id TEXT PRIMARY KEY,
            to_email TEXT NOT NULL,
            subject TEXT,
            body TEXT,
            trackingId TEXT,
            openCount INTEGER DEFAULT 0,
            lastOpenedAt TEXT,
            isRead INTEGER DEFAULT 0,
            readAt TEXT,
            direction TEXT DEFAULT 'sent',
            contactId TEXT,
            type TEXT,
            sentAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create activity table
    await db.execute("""
        CREATE TABLE activity (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL,
            text TEXT NOT NULL,
            color TEXT DEFAULT 'blue',
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create settings table
    await db.execute("""
        CREATE TABLE settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    await db.close()
    print("Database initialized successfully")

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
