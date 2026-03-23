from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from subscriptions.schemas import SubscriptionAction, SubscriptionDetails
from db import get_db
from auth.dependencies import verify_token

router = APIRouter(prefix="/api/subscriptions")


@router.get("/me", response_model=SubscriptionDetails)
async def get_subscription(current_user_email: str = Depends(verify_token), db=Depends(get_db)):
    row = await db.fetchrow(
        "SELECT plan_name, subscription_status, subscription_end_date FROM users WHERE email = $1",
        current_user_email,
    )
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "plan_name": row["plan_name"],
        "subscription_status": row["subscription_status"],
        "subscription_end_date": row["subscription_end_date"],
    }


@router.post("/subscribe")
async def create_subscription(
    action: SubscriptionAction,
    current_user_email: str = Depends(verify_token),
    db=Depends(get_db),
):
    if action.action == "upgrade":
        end_date = datetime.now() + timedelta(days=30)
        await db.execute(
            "UPDATE users SET plan_name = $1, subscription_status = 'active', subscription_end_date = $2 WHERE email = $3",
            action.plan_name, end_date, current_user_email,
        )
        return {
            "success": True,
            "message": f"Successfully upgraded to {action.plan_name} plan",
            "end_date": end_date,
        }
    elif action.action == "cancel":
        await db.execute(
            "UPDATE users SET subscription_status = 'cancelled' WHERE email = $1",
            current_user_email,
        )
        return {"success": True, "message": "Subscription cancelled"}

    raise HTTPException(status_code=400, detail="Invalid action")
