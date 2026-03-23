from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import json
import jwt
import os
import uuid
from typing import List
from emails.schemas import Email, EmailCreate, EmailUpdate
from simple_cache import get, set, clear_pattern
from db import get_db, close_db

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


# --- Transparent 1x1 tracking pixel (GIF) ---
TRACKING_PIXEL = bytes([
    0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00,
    0x01, 0x00, 0x80, 0x00, 0x00, 0xff, 0xff, 0xff,
    0x00, 0x00, 0x00, 0x21, 0xf9, 0x04, 0x01, 0x00,
    0x00, 0x00, 0x00, 0x2c, 0x00, 0x00, 0x00, 0x00,
    0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x02, 0x44,
    0x01, 0x00, 0x3b
])


@router.get("/emails", response_model=List[Email])
async def get_emails(current_user: str = Depends(verify_token)):
    cache_key_str = "emails"
    cached_data = get(cache_key_str)
    if cached_data is not None:
        return cached_data

    db = await get_db()
    rows = await db.fetch('SELECT * FROM emails ORDER BY "sentAt" DESC')
    emails = []
    for row in rows:
        email = {
            'id': row['id'],
            'to_email': row['to_email'],
            'subject': row['subject'],
            'body': row['body'],
            'trackingId': row['trackingid'],
            'openCount': row['opencount'],
            'lastOpenedAt': str(row['lastopenedat']) if row['lastopenedat'] else None,
            'isRead': bool(row['isread']),
            'readAt': str(row['readat']) if row['readat'] else None,
            'direction': row['direction'],
            'contactId': row['contactid'],
            'type': row['type'],
            'sentAt': str(row['sentAt'])
        }
        emails.append(email)
    await close_db(db)
    # Cache the result
    set(cache_key_str, emails)
    return emails

@router.post("/emails", response_model=Email)
async def create_email(email: EmailCreate, current_user: str = Depends(verify_token)):
    clear_pattern("emails")
    id = f"e_{int(datetime.now().timestamp() * 1000)}"
    trackingId = str(uuid.uuid4())
    sentAt = datetime.now()
    db = await get_db()
    await db.execute(
        'INSERT INTO emails (id, "to_email", subject, body, "trackingId", "contactId", type, "sentAt") VALUES ($1, $2, $3, $4, $5, $6, $7, $8)',
        id, email.to_email, email.subject, email.body, trackingId, email.contactId, email.type, sentAt
    )
    row = await db.fetchrow("SELECT * FROM emails WHERE id = $1", id)
    email_data = {
        'id': row['id'],
        'to_email': row['to_email'],
        'subject': row['subject'],
        'body': row['body'],
        'trackingId': row['trackingid'],
        'openCount': row['opencount'],
        'lastOpenedAt': str(row['lastopenedat']) if row['lastopenedat'] else None,
        'isRead': bool(row['isread']),
        'readAt': str(row['readat']) if row['readat'] else None,
        'direction': row['direction'],
        'contactId': row['contactid'],
        'type': row['type'],
        'sentAt': str(row['sentAt']),
    }
    await close_db(db)
    return email_data

@router.put("/emails/{id}", response_model=Email)
async def update_email(id: str, updates: EmailUpdate, current_user: str = Depends(verify_token)):
    clear_pattern("emails")
    update_data = updates.dict(exclude_unset=True)
    
    set_clauses = []
    values = []
    for i, (key, value) in enumerate(update_data.items()):
        set_clauses.append(f'"{key}" = ${i+1}')
        values.append(value)
    
    values.append(id)
    
    db = await get_db()
    await db.execute(f"UPDATE emails SET {', '.join(set_clauses)} WHERE id = ${len(values)}", *values)
    row = await db.fetchrow("SELECT * FROM emails WHERE id = $1", id)
    email_data = {
        'id': row['id'],
        'to_email': row['to_email'],
        'subject': row['subject'],
        'body': row['body'],
        'trackingId': row['trackingid'],
        'openCount': row['opencount'],
        'lastOpenedAt': str(row['lastopenedat']) if row['lastopenedat'] else None,
        'isRead': bool(row['isread']),
        'readAt': str(row['readat']) if row['readat'] else None,
        'direction': row['direction'],
        'contactId': row['contactid'],
        'type': row['type'],
        'sentAt': str(row['sentAt']),
    }
    await close_db(db)
    return email_data

@router.delete("/emails/{id}")
async def delete_email(id: str, current_user: str = Depends(verify_token)):
    clear_pattern("emails")
    db = await get_db()
    await db.execute("DELETE FROM emails WHERE id = $1", id)
    await close_db(db)
    return {"success": True}

# Email tracking endpoint
@router.get("/track/{tracking_id}")
async def track_email_open(tracking_id: str, request: Request):
    db = await get_db()
    try:
        # Update email open count and last opened time
        await db.execute(
            'UPDATE emails SET "openCount" = "openCount" + 1, "lastOpenedAt" = $1 WHERE "trackingId" = $2',
            datetime.now(), tracking_id
        )
    finally:
        await close_db(db)
    
    # Return transparent 1x1 GIF
    return Response(content=TRACKING_PIXEL, media_type="image/gif")

# Separate router for tracking
tracking_router = APIRouter()

@tracking_router.get("/track/{tracking_id}")
async def track_email_open(tracking_id: str, request: Request):
    db = await get_db()
    try:
        # Update email open count and last opened time
        await db.execute(
            'UPDATE emails SET "openCount" = "openCount" + 1, "lastOpenedAt" = $1 WHERE "trackingId" = $2',
            datetime.now(), tracking_id
        )
    finally:
        await close_db(db)
    
    # Return transparent 1x1 GIF
    return Response(content=TRACKING_PIXEL, media_type="image/gif")
