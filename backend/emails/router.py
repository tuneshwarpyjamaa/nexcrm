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

@router.get("/emails")
async def get_emails(current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM emails ORDER BY emails."sentAt" DESC')
        return [dict(row) for row in rows]

@router.post("/emails")
async def create_email(email: dict, current_user: str = Depends(verify_token)):
    to = email.get("to")
    if not to:
        raise HTTPException(status_code=400, detail="To is required")
    id = f"e_{int(datetime.now().timestamp() * 1000)}"
    sentAt = datetime.now()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO emails (id, to_email, subject, body, "sentAt") VALUES ($1, $2, $3, $4, $5)',
            id, to, email.get("subject"), email.get("body"), sentAt
        )
        row = await conn.fetchrow("SELECT * FROM emails WHERE id = $1", id)
        return dict(row)

@router.delete("/emails/{id}")
async def delete_email(id: str, current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM emails WHERE id = $1", id)
        return {"success": True}
