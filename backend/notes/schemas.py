from pydantic import BaseModel
from typing import Optional, List

class NoteBase(BaseModel):
    title: str
    body: Optional[str] = None
    contactId: Optional[str] = None
    contactName: Optional[str] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    contactId: Optional[str] = None
    contactName: Optional[str] = None

class Note(NoteBase):
    id: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True
