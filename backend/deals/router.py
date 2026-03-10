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

@router.get("/deals")
async def get_deals(current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM deals ORDER BY createdAt DESC")
        return [dict(row) for row in rows]

@router.post("/deals")
async def create_deal(deal: dict, current_user: str = Depends(verify_token)):
    title = deal.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")
    id = f"d_{int(datetime.now().timestamp() * 1000)}"
    createdAt = datetime.now()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO deals (id, title, contactId, company, value, stage, probability, closeDate, notes, createdAt) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
            id, title, deal.get("contactId"), deal.get("company"), deal.get("value"), deal.get("stage"), deal.get("probability"), deal.get("closeDate"), deal.get("notes"), createdAt
        )
        row = await conn.fetchrow("SELECT * FROM deals WHERE id = $1", id)
        return dict(row)

@router.put("/deals/{id}")
async def update_deal(id: str, updates: dict, current_user: str = Depends(verify_token)):
    updates["updatedAt"] = datetime.now()
    fields = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates.keys()))
    values = list(updates.values())
    values.insert(0, id)
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE deals SET {fields} WHERE id = $1", *values)
        row = await conn.fetchrow("SELECT * FROM deals WHERE id = $1", id)
        return dict(row)

@router.delete("/deals/{id}")
async def delete_deal(id: str, current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM deals WHERE id = $1", id)
        return {"success": True}
