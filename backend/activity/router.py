from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import jwt
import os
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

@router.get("/activity")
async def get_activity(current_user: str = Depends(verify_token)):
    return []

@router.post("/activity")
async def create_activity(activity: dict, current_user: str = Depends(verify_token)):
    type_ = activity.get("type")
    text = activity.get("text")
    if not type_ or not text:
        raise HTTPException(status_code=400, detail="Type and text are required")
    return {"id": "a_123", "type": type_, "text": text}
