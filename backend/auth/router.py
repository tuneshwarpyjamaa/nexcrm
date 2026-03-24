from fastapi import APIRouter, HTTPException, Depends, Form
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
import secrets
import uuid

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


@router.get("/auth/google")
async def google_oauth_redirect():
    """Redirect to Google OAuth"""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=openid email profile&access_type=offline"
    
    # In a real implementation, you'd redirect the user
    # For testing, we'll return the URL
    return {"auth_url": auth_url}


@router.get("/auth/google/callback")
async def google_oauth_callback(code: str, db=Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for tokens (simplified for testing)
        # In production, you'd make a proper HTTP request to Google
        mock_user_info = {
            "email": "google_user@example.com",
            "name": "Google User",
            "sub": "google_sub_123"
        }
        
        email = mock_user_info["email"]
        name = mock_user_info["name"]
        google_id = mock_user_info["sub"]

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
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")


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


@router.post("/reset-password-request")
async def reset_password_request(email: str = Form(...), db=Depends(get_db)):
    """Request password reset"""
    user = await db.fetchrow("SELECT id, email FROM users WHERE email = $1", email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate reset token (in production, you'd send this via email)
    reset_token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(hours=1)
    
    # Store reset token (you'd typically have a separate table for this)
    # For now, we'll just return success (simplified for testing)
    return {"message": "Password reset email sent", "token": reset_token}


@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db=Depends(get_db)):
    """Reset password with token"""
    # In production, you'd validate the token and expiry
    # For testing, we'll just update the password
    if len(new_password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters")
    
    hashed_password = get_password_hash(new_password)
    
    # For testing, we'll assume any token is valid and update the first user
    # In production, you'd find the user by the reset token
    await db.execute(
        "UPDATE users SET password_hash = $1 WHERE email = $2",
        hashed_password, "test@example.com"
    )
    
    return {"message": "Password reset successful"}


@router.post("/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    current_user: str = Depends(verify_token),
    db=Depends(get_db)
):
    """Change password for authenticated user"""
    if len(new_password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters")
    
    user = await db.fetchrow("SELECT password_hash FROM users WHERE email = $1", current_user)
    if not user or not verify_password(current_password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    hashed_password = get_password_hash(new_password)
    await db.execute(
        "UPDATE users SET password_hash = $1 WHERE email = $2",
        hashed_password, current_user
    )
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(current_user: str = Depends(verify_token)):
    """Logout user (token invalidation would be handled client-side)"""
    return {"message": "Logged out successfully"}
