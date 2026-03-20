from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
import os
from typing import List
from subscriptions.schemas import SubscriptionAction, SubscriptionDetails
from db import get_db

router = APIRouter(prefix="/api/subscriptions")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.get("/me", response_model=SubscriptionDetails)
async def get_subscription(current_user_email: str = Depends(verify_token)):
    db = await get_db()
    cursor = await db.execute("SELECT plan_name, subscription_status, subscription_end_date FROM users WHERE email = $1", current_user_email)
    row = await cursor.fetchone()
    if not row:
        await db.close()
        raise HTTPException(status_code=404, detail="User not found")
    await db.close()
    return {"plan_name": row[0], "subscription_status": row[1], "subscription_end_date": row[2]}

@router.post("/subscribe")
async def create_subscription(action: SubscriptionAction, current_user_email: str = Depends(verify_token)):
    # This is a mock implementation of a payment flow.
    # In a real app, you would create a Razorpay subscription/order here and return the order_id.
    
    if action.action == "upgrade":
        db = await get_db()
        # Mock setting a 1 month subscription
        end_date = datetime.now() + timedelta(days=30)
        await db.execute(
            "UPDATE users SET plan_name = ?, subscription_status = 'active', subscription_end_date = ? WHERE email = ?",
            (action.plan_name, end_date, current_user_email)
        )
        await db.commit()
        await db.close()
        return {"success": True, "message": f"Successfully upgraded to {action.plan_name} plan", "end_date": end_date}
    elif action.action == "cancel":
        db = await get_db()
        await db.execute(
            "UPDATE users SET subscription_status = 'cancelled' WHERE email = ?",
            (current_user_email,)
        )
        await db.commit()
        await db.close()
        return {"success": True, "message": "Subscription cancelled"}
    
    raise HTTPException(status_code=400, detail="Invalid action")
