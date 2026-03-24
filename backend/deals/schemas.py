from pydantic import BaseModel, ConfigDict, field_validator
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

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Title must be at least 2 characters long')
        if len(v.strip()) > 200:
            raise ValueError('Title must be less than 200 characters')
        return v.strip()

    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError('Deal value cannot be negative')
            if v > 999999999.99:
                raise ValueError('Deal value is too large')
        return v

    @field_validator('stage')
    @classmethod
    def validate_stage(cls, v):
        if v is not None:
            valid_stages = ['lead', 'qualified', 'proposal', 'negotiation', 'closed-won', 'closed-lost']
            if v.lower() not in valid_stages:
                raise ValueError(f'Stage must be one of: {", ".join(valid_stages)}')
        return v.lower() if v else v

    @field_validator('probability')
    @classmethod
    def validate_probability(cls, v):
        if v is not None:
            if not 0 <= v <= 100:
                raise ValueError('Probability must be between 0 and 100')
        return v

    @field_validator('closeDate')
    @classmethod
    def validate_close_date(cls, v):
        if v is not None:
            if v < date.today():
                raise ValueError('Close date cannot be in the past')
        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v) > 2000:
            raise ValueError('Notes must be less than 2000 characters')
        return v

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

    # Apply same validators as DealBase
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError('Title must be at least 2 characters long')
            if len(v.strip()) > 200:
                raise ValueError('Title must be less than 200 characters')
            return v.strip()
        return v

    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError('Deal value cannot be negative')
            if v > 999999999.99:
                raise ValueError('Deal value is too large')
        return v

    @field_validator('stage')
    @classmethod
    def validate_stage(cls, v):
        if v is not None:
            valid_stages = ['lead', 'qualified', 'proposal', 'negotiation', 'closed-won', 'closed-lost']
            if v.lower() not in valid_stages:
                raise ValueError(f'Stage must be one of: {", ".join(valid_stages)}')
        return v.lower() if v else v

    @field_validator('probability')
    @classmethod
    def validate_probability(cls, v):
        if v is not None:
            if not 0 <= v <= 100:
                raise ValueError('Probability must be between 0 and 100')
        return v

    @field_validator('closeDate')
    @classmethod
    def validate_close_date(cls, v):
        if v is not None:
            if v < date.today():
                raise ValueError('Close date cannot be in the past')
        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v) > 2000:
            raise ValueError('Notes must be less than 2000 characters')
        return v

class Deal(DealBase):
    id: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
