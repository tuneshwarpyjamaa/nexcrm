from pydantic import BaseModel
from typing import Optional

class EmailBase(BaseModel):
    to_email: str
    subject: Optional[str] = None
    body: Optional[str] = None
    contactId: Optional[str] = None
    type: Optional[str] = None

class EmailCreate(EmailBase):
    pass

class EmailUpdate(BaseModel):
    to_email: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    openCount: Optional[int] = None
    lastOpenedAt: Optional[str] = None
    isRead: Optional[int] = None
    readAt: Optional[str] = None
    direction: Optional[str] = None
    contactId: Optional[str] = None
    type: Optional[str] = None

class Email(EmailBase):
    id: str
    trackingId: Optional[str] = None
    openCount: int
    lastOpenedAt: Optional[str] = None
    isRead: int
    readAt: Optional[str] = None
    direction: str
    sentAt: str

    class Config:
        from_attributes = True
