from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import jwt
import os
from db import get_pool

router = APIRouter(prefix="/api")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.get("/notes")
async def get_notes(current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM notes ORDER BY createdAt DESC")
        return [dict(row) for row in rows]

@router.post("/notes")
async def create_note(note: dict, current_user: str = Depends(verify_token)):
    title = note.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")
    id = f"n_{int(datetime.now().timestamp() * 1000)}"
    createdAt = datetime.now()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO notes (id, title, body, contactId, contactName, createdAt) VALUES ($1, $2, $3, $4, $5, $6)",
            id, title, note.get("body"), note.get("contactId"), note.get("contactName"), createdAt
        )
        row = await conn.fetchrow("SELECT * FROM notes WHERE id = $1", id)
        return dict(row)

@router.put("/notes/{id}")
async def update_note(id: str, updates: dict, current_user: str = Depends(verify_token)):
    updates["updatedAt"] = datetime.now()
    fields = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates.keys()))
    values = list(updates.values())
    values.insert(0, id)
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE notes SET {fields} WHERE id = $1", *values)
        row = await conn.fetchrow("SELECT * FROM notes WHERE id = $1", id)
        return dict(row)

@router.delete("/notes/{id}")
async def delete_note(id: str, current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM notes WHERE id = $1", id)
        return {"success": True}
