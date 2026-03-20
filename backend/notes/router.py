from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import json
import jwt
import os
from typing import List
from notes.schemas import Note, NoteCreate, NoteUpdate
from simple_cache import get, set, clear_pattern
from db import get_db

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

@router.get("/notes", response_model=List[Note])
async def get_notes(current_user: str = Depends(verify_token)):
    db = await get_db()
    try:
        rows = await db.fetch('SELECT * FROM notes ORDER BY "createdAt" DESC')
        notes = []
        for row in rows:
            note = {
                'id': row['id'],
                'title': row['title'],
                'body': row['body'],
                'contactId': row['contactid'],
                'contactName': row['contactname'],
                'createdAt': str(row['createdAt']),
                'updatedAt': str(row['updatedAt'])
            }
            notes.append(note)
        # Cache the result
        cache_key_str = "notes"
        set(cache_key_str, notes)
        return notes
    finally:
        await db.close()

@router.post("/notes", response_model=Note)
async def create_note(note: NoteCreate, current_user: str = Depends(verify_token)):
    id = f"n_{int(datetime.now().timestamp() * 1000)}"
    createdAt = datetime.now()
    db = await get_db()
    await db.execute(
        'INSERT INTO notes (id, title, body, "contactid", "contactname", "createdAt") VALUES ($1, $2, $3, $4, $5, $6)',
        id, note.title, note.body, note.contactId, note.contactName, createdAt
    )
    row = await db.fetchrow("SELECT * FROM notes WHERE id = $1", id)
    note_data = {
        'id': row['id'],
        'title': row['title'],
        'body': row['body'],
        'contactId': row['contactid'],
        'contactName': row['contactname'],
        'createdAt': str(row['createdAt']),
        'updatedAt': str(row['updatedAt'])
    }
    await db.close()
    return note_data

@router.put("/notes/{id}", response_model=Note)
async def update_note(id: str, updates: NoteUpdate, current_user: str = Depends(verify_token)):
    update_data = updates.dict(exclude_unset=True)
    update_data["updatedAt"] = datetime.now()
    
    set_clauses = []
    values = []
    for i, (key, value) in enumerate(update_data.items()):
        set_clauses.append(f'"{key}" = ${i+1}')
        values.append(value)
    
    values.append(id)
    
    db = await get_db()
    await db.execute(f"UPDATE notes SET {', '.join(set_clauses)} WHERE id = ${len(values)}", *values)
    row = await db.fetchrow("SELECT * FROM notes WHERE id = $1", id)
    note_data = {
        'id': row['id'],
        'title': row['title'],
        'body': row['body'],
        'contactId': row['contactid'],
        'contactName': row['contactname'],
        'createdAt': str(row['createdAt']),
        'updatedAt': str(row['updatedAt'])
    }
    await db.close()
    return note_data

@router.delete("/notes/{id}")
async def delete_note(id: str, current_user: str = Depends(verify_token)):
    db = await get_db()
    await db.execute("DELETE FROM notes WHERE id = $1", id)
    await db.close()
    return {"success": True}
