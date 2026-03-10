from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import json
import jwt
import os
from typing import List
from contacts.schemas import Contact, ContactCreate, ContactUpdate
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

def format_contact(row):
    contact = dict(row)
    if contact.get("tags"):
        try:
            contact["tags"] = json.loads(contact["tags"])
        except (json.JSONDecodeError, TypeError):
            contact["tags"] = []
    else:
        contact["tags"] = []
    return contact

@router.get("/contacts", response_model=List[Contact])
async def get_contacts(current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM contacts ORDER BY contacts."createdAt" DESC')
        return [format_contact(row) for row in rows]

@router.post("/contacts", response_model=Contact)
async def create_contact(contact: ContactCreate, current_user: str = Depends(verify_token)):
    id = f"c_{int(datetime.now().timestamp() * 1000)}"
    createdAt = datetime.now()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO contacts (id, name, email, phone, company, title, status, tags, linkedin, notes, "createdAt") VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)',
            id, contact.name, contact.email, contact.phone, contact.company, contact.title, contact.status, json.dumps(contact.tags), contact.linkedin, contact.notes, createdAt
        )
        row = await conn.fetchrow("SELECT * FROM contacts WHERE id = $1", id)
        return format_contact(row)

@router.put("/contacts/{id}", response_model=Contact)
async def update_contact(id: str, updates: ContactUpdate, current_user: str = Depends(verify_token)):
    update_data = updates.dict(exclude_unset=True)
    update_data["updatedAt"] = datetime.now()
    
    if "tags" in update_data and update_data["tags"] is not None:
        update_data["tags"] = json.dumps(update_data["tags"])
        
    fields = ", ".join(f'"{k}" = ${i+2}' for i, k in enumerate(update_data.keys()))
    values = list(update_data.values())
    values.insert(0, id)
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE contacts SET {fields} WHERE id = $1", *values)
        row = await conn.fetchrow("SELECT * FROM contacts WHERE id = $1", id)
        return format_contact(row)

@router.delete("/contacts/{id}")
async def delete_contact(id: str, current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM contacts WHERE id = $1", id)
        return {"success": True}
