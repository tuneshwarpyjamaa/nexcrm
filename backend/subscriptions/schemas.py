from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubscriptionAction(BaseModel):
    action: str
    plan_name: str

class SubscriptionDetails(BaseModel):
    plan_name: str
    subscription_status: str
    subscription_end_date: Optional[datetime] = None
