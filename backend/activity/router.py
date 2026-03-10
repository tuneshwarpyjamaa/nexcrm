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

@router.get("/activity")
async def get_activity(current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM activity ORDER BY time DESC LIMIT 100")
        return [dict(row) for row in rows]

@router.post("/activity")
async def create_activity(activity: dict, current_user: str = Depends(verify_token)):
    type_ = activity.get("type")
    text = activity.get("text")
    if not type_ or not text:
        raise HTTPException(status_code=400, detail="Type and text are required")
    time = datetime.now()
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO activity (type, text, color, time) VALUES ($1, $2, $3, $4) RETURNING *",
            type_, text, activity.get("color", "blue"), time
        )
        return dict(row)
