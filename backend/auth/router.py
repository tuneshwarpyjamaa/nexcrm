from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from auth.schemas import UserLogin, UserCreate, Token, GoogleSignin
from db import get_db
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.integrations.base_client import OAuthError
from google.auth.transport import requests
from google.oauth2 import id_token
import asyncpg

router = APIRouter(prefix="/api")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    email = user.email
    password = user.password

    db = await get_db()
    row = await db.fetchrow("SELECT password_hash FROM users WHERE email = $1", email)
    if not row or not verify_password(password, row[0]):
        await db.close()
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    await db.close()
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(user: UserCreate):
    name = user.name
    email = user.email
    password = user.password
    
    hashed_password = get_password_hash(password)
    db = await get_db()
    try:
        await db.execute("INSERT INTO users (name, email, password_hash) VALUES ($1, $2, $3)", name, email, hashed_password)
        await db.commit()
        await db.close()
        return {"message": "User created successfully"}
    except asyncpg.IntegrityError:
        await db.close()
        raise HTTPException(status_code=400, detail="Email already exists")

@router.get("/auth/google/client_id")
async def get_google_client_id():
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    return {"client_id": GOOGLE_CLIENT_ID}

@router.post("/auth/google/signin")
async def google_signin(data: GoogleSignin):
    credential = data.credential
    try:
        idinfo = id_token.verify_oauth2_token(credential, requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo['email']
        name = idinfo['name']
        google_id = idinfo['sub']
        db = await get_db()
        row = await db.fetchrow("SELECT id FROM users WHERE google_id = $1", google_id)
        if row:
            user_id = row[0]
        else:
            # Check if email exists with local provider
            row = await db.fetchrow("SELECT id FROM users WHERE email = $1 AND provider = 'local'", email)
            if row:
                await db.close()
                raise HTTPException(status_code=400, detail="Email already exists with local account")
            # Create new user
            row = await db.fetchrow("INSERT INTO users (name, email, provider, google_id) VALUES ($1, $2, 'google', $3) RETURNING id", name, email, google_id)
            user_id = row[0]
        await db.close()
        access_token = create_access_token(data={"sub": email})
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token")
