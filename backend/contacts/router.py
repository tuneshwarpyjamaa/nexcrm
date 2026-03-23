from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import json
import jwt
import os
from typing import List
from contacts.schemas import Contact, ContactCreate, ContactUpdate
from db import get_db, close_db
from simple_cache import get, set, clear_pattern

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
    # Check cache first
    cache_key_str = f"contacts_{current_user}"
    cached_data = get(cache_key_str)
    if cached_data is not None:
        return cached_data
    
    # If not cached, fetch from database
    db = await get_db()
    try:
        rows = await db.fetch('SELECT * FROM contacts ORDER BY "createdAt" DESC')
        contacts = []
        for row in rows:
            contact = {
                'id': row['id'],
                'name': row['name'],
                'email': row['email'],
                'phone': row['phone'],
                'company': row['company'],
                'title': row['title'],
                'status': row['status'],
                'tags': json.loads(row['tags']) if row['tags'] else [],
                'linkedin': row['linkedin'],
                'notes': row['notes'],
                'createdAt': str(row['createdAt']),
                'updatedAt': str(row['updatedAt'])
            }
            contacts.append(format_contact(contact))
        # Cache the result
        set(cache_key_str, contacts)
        return contacts
    finally:
        await close_db(db)

@router.post("/contacts", response_model=Contact)
async def create_contact(contact: ContactCreate, current_user: str = Depends(verify_token)):
    # Clear cache on create
    clear_pattern("contacts_")
    
    id = f"c_{int(datetime.now().timestamp() * 1000)}"
    createdAt = datetime.now()
    db = await get_db()
    try:
        await db.execute(
            'INSERT INTO contacts (id, name, email, phone, company, title, status, tags, linkedin, notes, "createdAt") VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)',
            id, contact.name, contact.email, contact.phone, contact.company, contact.title, contact.status, json.dumps(contact.tags), contact.linkedin, contact.notes, createdAt
        )
        row = await db.fetchrow("SELECT * FROM contacts WHERE id = $1", id)
        contact_data = {
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'phone': row['phone'],
            'company': row['company'],
            'title': row['title'],
            'status': row['status'],
            'tags': json.loads(row['tags']) if row['tags'] else [],
            'linkedin': row['linkedin'],
            'notes': row['notes'],
            'createdAt': str(row['createdAt']),
            'updatedAt': str(row['updatedAt'])
        }
        return format_contact(contact_data)
    finally:
        await close_db(db)

@router.put("/contacts/{id}", response_model=Contact)
async def update_contact(id: str, updates: ContactUpdate, current_user: str = Depends(verify_token)):
    # Clear cache on update
    clear_pattern("contacts_")
    
    update_data = updates.dict(exclude_unset=True)
    update_data["updatedAt"] = datetime.now()
    
    if "tags" in update_data and update_data["tags"] is not None:
        update_data["tags"] = json.dumps(update_data["tags"])
        
    set_clauses = []
    values = []
    for i, (key, value) in enumerate(update_data.items()):
        set_clauses.append(f'"{key}" = ${i+1}')
        values.append(value)
    
    values.append(id)
    
    db = await get_db()
    try:
        await db.execute(f"UPDATE contacts SET {', '.join(set_clauses)} WHERE id = ${len(values)}", *values)
        row = await db.fetchrow("SELECT * FROM contacts WHERE id = $1", id)
        contact_data = {
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'phone': row['phone'],
            'company': row['company'],
            'title': row['title'],
            'status': row['status'],
            'tags': json.loads(row['tags']) if row['tags'] else [],
            'linkedin': row['linkedin'],
            'notes': row['notes'],
            'createdAt': str(row['createdAt']),
            'updatedAt': str(row['updatedAt'])
        }
        return format_contact(contact_data)
    finally:
        await close_db(db)

@router.delete("/contacts/{id}")
async def delete_contact(id: str, current_user: str = Depends(verify_token)):
    # Clear cache on delete
    clear_pattern("contacts_")
    
    db = await get_db()
    try:
        await db.execute("DELETE FROM contacts WHERE id = $1", id)
        return {"success": True}
    finally:
        await close_db(db)
