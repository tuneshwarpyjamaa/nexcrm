from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import json
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

@router.get("/contacts")
async def get_contacts(current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM contacts ORDER BY createdAt DESC")
        return [dict(row) for row in rows]

@router.post("/contacts")
async def create_contact(contact: dict, current_user: str = Depends(verify_token)):
    name = contact.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    id = f"c_{int(datetime.now().timestamp() * 1000)}"
    createdAt = datetime.now()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO contacts (id, name, email, phone, company, title, status, tags, linkedin, notes, createdAt) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)",
            id, name, contact.get("email"), contact.get("phone"), contact.get("company"), contact.get("title"), contact.get("status"), json.dumps(contact.get("tags", [])), contact.get("linkedin"), contact.get("notes"), createdAt
        )
        row = await conn.fetchrow("SELECT * FROM contacts WHERE id = $1", id)
        return dict(row)

@router.put("/contacts/{id}")
async def update_contact(id: str, updates: dict, current_user: str = Depends(verify_token)):
    updates["updatedAt"] = datetime.now()
    fields = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates.keys()))
    values = list(updates.values())
    values.insert(0, id)
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE contacts SET {fields} WHERE id = $1", *values)
        row = await conn.fetchrow("SELECT * FROM contacts WHERE id = $1", id)
        return dict(row)

@router.delete("/contacts/{id}")
async def delete_contact(id: str, current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM contacts WHERE id = $1", id)
        return {"success": True}
