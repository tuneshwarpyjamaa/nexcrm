from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import jwt
import os
import uuid
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


# --- Transparent 1x1 tracking pixel (GIF) ---
TRACKING_PIXEL = bytes([
    0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00,
    0x01, 0x00, 0x80, 0x00, 0x00, 0xff, 0xff, 0xff,
    0x00, 0x00, 0x00, 0x21, 0xf9, 0x04, 0x01, 0x00,
    0x00, 0x00, 0x00, 0x2c, 0x00, 0x00, 0x00, 0x00,
    0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x02, 0x44,
    0x01, 0x00, 0x3b
])


@router.get("/emails")
async def get_emails(current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            'SELECT * FROM emails ORDER BY emails."sentAt" DESC'
        )
        result = []
        for row in rows:
            d = dict(row)
            # Map to_email -> to for frontend compatibility
            d["to"] = d.pop("to_email", None)
            result.append(d)
        return result


@router.post("/emails")
async def create_email(email: dict, current_user: str = Depends(verify_token)):
    to = email.get("to")
    if not to:
        raise HTTPException(status_code=400, detail="To is required")

    id = f"e_{int(datetime.now().timestamp() * 1000)}"
    sentAt = datetime.now()
    tracking_id = str(uuid.uuid4())
    direction = email.get("direction", "sent")
    contact_id = email.get("contactId")
    email_type = email.get("type", "Follow-up")

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            '''INSERT INTO emails (
                id, to_email, subject, body, "sentAt",
                "trackingId", "openCount", "lastOpenedAt",
                "isRead", "readAt", direction, "contactId", type
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)''',
            id, to, email.get("subject"), email.get("body"), sentAt,
            tracking_id, 0, None,
            False, None, direction, contact_id, email_type
        )
        row = await conn.fetchrow("SELECT * FROM emails WHERE id = $1", id)
        d = dict(row)
        d["to"] = d.pop("to_email", None)
        return d


@router.patch("/emails/{id}")
async def update_email(id: str, data: dict, current_user: str = Depends(verify_token)):
    """Update email tracking fields (mark as read, etc.)"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT * FROM emails WHERE id = $1", id)
        if not existing:
            raise HTTPException(status_code=404, detail="Email not found")

        updates = []
        values = []
        param_idx = 1

        allowed_fields = {
            "isRead": '"isRead"',
            "readAt": '"readAt"',
            "direction": 'direction',
            "type": 'type',
        }

        for field, col in allowed_fields.items():
            if field in data:
                updates.append(f'{col} = ${param_idx}')
                val = data[field]
                # Convert ISO date strings to datetime
                if field in ("readAt",) and isinstance(val, str):
                    val = datetime.fromisoformat(val.replace("Z", "+00:00"))
                values.append(val)
                param_idx += 1

        if not updates:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        values.append(id)
        query = f'UPDATE emails SET {", ".join(updates)} WHERE id = ${param_idx}'
        await conn.execute(query, *values)

        row = await conn.fetchrow("SELECT * FROM emails WHERE id = $1", id)
        d = dict(row)
        d["to"] = d.pop("to_email", None)
        return d


@router.delete("/emails/{id}")
async def delete_email(id: str, current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM emails WHERE id = $1", id)
        return {"success": True}


@router.get("/emails/stats")
async def email_stats(current_user: str = Depends(verify_token)):
    """Get email tracking statistics."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM emails")
        sent = await conn.fetchval("SELECT COUNT(*) FROM emails WHERE direction = 'sent'")
        received = await conn.fetchval("SELECT COUNT(*) FROM emails WHERE direction = 'received'")
        opened = await conn.fetchval('SELECT COUNT(*) FROM emails WHERE "openCount" > 0')
        read_count = await conn.fetchval('SELECT COUNT(*) FROM emails WHERE "isRead" = true')
        unread = await conn.fetchval('SELECT COUNT(*) FROM emails WHERE "isRead" = false AND direction = \'received\'')
        total_opens = await conn.fetchval('SELECT COALESCE(SUM("openCount"), 0) FROM emails')

        return {
            "total": total,
            "sent": sent,
            "received": received,
            "opened": opened,
            "read": read_count,
            "unread": unread,
            "totalOpens": total_opens,
            "openRate": round((opened / sent * 100), 1) if sent > 0 else 0,
        }


# --- Tracking Pixel Endpoint (no auth required) ---
# This is loaded as an image in emails to track opens
tracking_router = APIRouter()


@tracking_router.get("/track/{tracking_id}.gif")
async def track_email_open(tracking_id: str):
    """Tracking pixel endpoint. Increments open count when loaded."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'SELECT id FROM emails WHERE "trackingId" = $1', tracking_id
        )
        if row:
            await conn.execute(
                '''UPDATE emails
                   SET "openCount" = "openCount" + 1,
                       "lastOpenedAt" = $1
                   WHERE "trackingId" = $2''',
                datetime.now(), tracking_id
            )

    return Response(
        content=TRACKING_PIXEL,
        media_type="image/gif",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )
