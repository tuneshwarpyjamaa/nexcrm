from fastapi import APIRouter, HTTPException, Depends, Request, Response
from datetime import datetime
import uuid
from typing import List
from emails.schemas import Email, EmailCreate, EmailUpdate
from db import get_db
from auth.dependencies import verify_token
from simple_cache import get, set, clear_pattern

router = APIRouter(prefix="/api")

# Transparent 1x1 GIF tracking pixel
TRACKING_PIXEL = bytes([
    0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00,
    0x01, 0x00, 0x80, 0x00, 0x00, 0xff, 0xff, 0xff,
    0x00, 0x00, 0x00, 0x21, 0xf9, 0x04, 0x01, 0x00,
    0x00, 0x00, 0x00, 0x2c, 0x00, 0x00, 0x00, 0x00,
    0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x02, 0x44,
    0x01, 0x00, 0x3b,
])


def _row_to_email(row) -> dict:
    return {
        "id": row["id"],
        "to_email": row["to_email"],
        "subject": row["subject"],
        "body": row["body"],
        "trackingId": row["trackingId"],
        "openCount": row["openCount"] or 0,
        "lastOpenedAt": str(row["lastOpenedAt"]) if row["lastOpenedAt"] else None,
        "isRead": bool(row["isRead"]),
        "readAt": str(row["readAt"]) if row["readAt"] else None,
        "direction": row["direction"] or "sent",
        "contactId": row["contactId"],
        "type": row["type"],
        "sentAt": str(row["sentAt"]) if row["sentAt"] else None,
    }


@router.get("/emails", response_model=List[Email])
async def get_emails(current_user: str = Depends(verify_token), db=Depends(get_db)):
    # Cache is scoped per user to prevent cross-user data leaks
    cache_key = f"emails_{current_user}"
    cached = get(cache_key)
    if cached is not None:
        return cached
    rows = await db.fetch('SELECT * FROM emails ORDER BY "sentAt" DESC')
    emails = [_row_to_email(r) for r in rows]
    set(cache_key, emails)
    return emails


@router.post("/emails", response_model=Email)
async def create_email(
    email: EmailCreate, current_user: str = Depends(verify_token), db=Depends(get_db)
):
    clear_pattern("emails_")
    email_id = f"e_{uuid.uuid4().hex}"
    tracking_id = str(uuid.uuid4())
    sent_at = datetime.now()
    await db.execute(
        'INSERT INTO emails (id, to_email, subject, body, "trackingId", "contactId", type, "sentAt") '
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
        email_id, email.to_email, email.subject, email.body,
        tracking_id, email.contactId, email.type, sent_at,
    )
    row = await db.fetchrow("SELECT * FROM emails WHERE id = $1", email_id)
    return _row_to_email(row)


@router.put("/emails/{email_id}", response_model=Email)
async def update_email(
    email_id: str, updates: EmailUpdate,
    current_user: str = Depends(verify_token), db=Depends(get_db)
):
    existing = await db.fetchrow("SELECT id FROM emails WHERE id = $1", email_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Email not found")

    clear_pattern("emails_")
    update_data = updates.dict(exclude_unset=True)

    set_clauses = [f'"{k}" = ${i + 1}' for i, k in enumerate(update_data.keys())]
    values = list(update_data.values()) + [email_id]
    await db.execute(
        f'UPDATE emails SET {", ".join(set_clauses)} WHERE id = ${len(values)}',
        *values,
    )
    row = await db.fetchrow("SELECT * FROM emails WHERE id = $1", email_id)
    return _row_to_email(row)


@router.delete("/emails/{email_id}")
async def delete_email(
    email_id: str, current_user: str = Depends(verify_token), db=Depends(get_db)
):
    result = await db.execute("DELETE FROM emails WHERE id = $1", email_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Email not found")
    clear_pattern("emails_")
    return {"success": True}


# Single tracking endpoint — mounted separately without /api prefix
tracking_router = APIRouter()


@tracking_router.get("/track/{tracking_id}")
async def track_email_open(tracking_id: str, request: Request, db=Depends(get_db)):
    await db.execute(
        'UPDATE emails SET "openCount" = "openCount" + 1, "lastOpenedAt" = $1 WHERE "trackingId" = $2',
        datetime.now(), tracking_id,
    )
    return Response(content=TRACKING_PIXEL, media_type="image/gif")
