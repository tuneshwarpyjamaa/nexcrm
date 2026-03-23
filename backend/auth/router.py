from fastapi import APIRouter, HTTPException, Depends
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from auth.schemas import UserLogin, UserCreate, Token, GoogleSignin
from auth.dependencies import verify_token, SECRET_KEY, ALGORITHM
from db import get_db
import asyncpg
import jwt
from google.auth.transport import requests
from google.oauth2 import id_token

router = APIRouter(prefix="/api")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db=Depends(get_db)):
    row = await db.fetchrow("SELECT password_hash FROM users WHERE email = $1", user.email)
    if not row or not verify_password(user.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
async def register(user: UserCreate, db=Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    try:
        await db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES ($1, $2, $3)",
            user.name, user.email, hashed_password,
        )
        return {"message": "User created successfully"}
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Email already exists")


@router.get("/auth/google/client_id")
async def get_google_client_id():
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    return {"client_id": GOOGLE_CLIENT_ID}


@router.post("/auth/google/signin")
async def google_signin(data: GoogleSignin, db=Depends(get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(
            data.credential, requests.Request(), GOOGLE_CLIENT_ID
        )
        email = idinfo["email"]
        name = idinfo["name"]
        google_id = idinfo["sub"]

        row = await db.fetchrow("SELECT id FROM users WHERE google_id = $1", google_id)
        if not row:
            existing = await db.fetchrow(
                "SELECT id FROM users WHERE email = $1 AND provider = 'local'", email
            )
            if existing:
                raise HTTPException(
                    status_code=400, detail="Email already exists with local account"
                )
            await db.execute(
                "INSERT INTO users (name, email, provider, google_id) VALUES ($1, $2, 'google', $3)",
                name, email, google_id,
            )

        access_token = create_access_token(
            data={"sub": email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token")
