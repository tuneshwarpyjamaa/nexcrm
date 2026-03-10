from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from db import get_pool, close_pool
from contacts.router import router as contacts_router
from deals.router import router as deals_router
from tasks.router import router as tasks_router
from notes.router import router as notes_router
from emails.router import router as emails_router
from activity.router import router as activity_router
from settings.router import router as settings_router
from auth.router import router as auth_router

@asynccontextmanager
async def lifespan(app):
    # Startup: initialize the connection pool
    await get_pool()
    yield
    # Shutdown: close the connection pool
    await close_pool()

app = FastAPI(lifespan=lifespan)
port = int(os.getenv("PORT", 3000))


# Database tables are now managed by Alembic migrations.
# To run migrations, use: alembic upgrade head

app.include_router(contacts_router)
app.include_router(deals_router)
app.include_router(tasks_router)
app.include_router(notes_router)
app.include_router(emails_router)
app.include_router(activity_router)
app.include_router(settings_router)
app.include_router(auth_router)


frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
