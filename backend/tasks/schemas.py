from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date

class TaskBase(BaseModel):
    title: str
    contactId: Optional[str] = None
    dueDate: Optional[date] = None
    priority: Optional[str] = "Normal"
    done: Optional[bool] = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    contactId: Optional[str] = None
    dueDate: Optional[date] = None
    priority: Optional[str] = None
    done: Optional[bool] = None

class Task(TaskBase):
    id: str
    createdAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
