from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date

class DealBase(BaseModel):
    title: str
    contactId: Optional[str] = None
    company: Optional[str] = None
    value: Optional[float] = 0.0
    stage: Optional[str] = "Lead"
    probability: Optional[int] = 0
    closeDate: Optional[date] = None
    notes: Optional[str] = None

class DealCreate(DealBase):
    pass

class DealUpdate(BaseModel):
    title: Optional[str] = None
    contactId: Optional[str] = None
    company: Optional[str] = None
    value: Optional[float] = None
    stage: Optional[str] = None
    probability: Optional[int] = None
    closeDate: Optional[date] = None
    notes: Optional[str] = None

class Deal(DealBase):
    id: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
