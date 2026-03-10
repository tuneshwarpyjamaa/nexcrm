from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from db import get_pool
from contacts.router import router as contacts_router
from deals.router import router as deals_router
from tasks.router import router as tasks_router
from notes.router import router as notes_router
from emails.router import router as emails_router
from activity.router import router as activity_router
from settings.router import router as settings_router
from auth.router import router as auth_router

app = FastAPI()
port = int(os.getenv("PORT", 3000))

async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
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
                createdAt TIMESTAMP,
                updatedAt TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS deals (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                contactId TEXT,
                company TEXT,
                value REAL,
                stage TEXT,
                probability INTEGER,
                closeDate DATE,
                notes TEXT,
                createdAt TIMESTAMP,
                updatedAt TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                contactId TEXT,
                dueDate DATE,
                priority TEXT,
                done BOOLEAN DEFAULT FALSE,
                createdAt TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                body TEXT,
                contactId TEXT,
                contactName TEXT,
                createdAt TIMESTAMP,
                updatedAt TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                to_email TEXT,
                subject TEXT,
                body TEXT,
                sentAt TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS activity (
                id SERIAL PRIMARY KEY,
                type TEXT,
                text TEXT,
                color TEXT,
                time TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

@app.on_event("startup")
async def startup_event():
    await get_pool()
    await init_db()

app.include_router(contacts_router)
app.include_router(deals_router)
app.include_router(tasks_router)
app.include_router(notes_router)
app.include_router(emails_router)
app.include_router(activity_router)
app.include_router(settings_router)
app.include_router(auth_router)

app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")
