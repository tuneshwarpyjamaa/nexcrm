from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
import re

class ContactBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = []
    linkedin: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v.strip()) > 100:
            raise ValueError('Name must be less than 100 characters')
        return v.strip()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            # Basic phone validation - allows international formats
            phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
            if not re.match(phone_pattern, v.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')):
                raise ValueError('Invalid phone number format')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['lead', 'prospect', 'customer', 'inactive', 'archived']
            if v.lower() not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v.lower() if v else v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Cannot have more than 10 tags')
            for tag in v:
                if len(tag) > 20:
                    raise ValueError('Each tag must be less than 20 characters')
        return v or []

    @field_validator('linkedin')
    @classmethod
    def validate_linkedin(cls, v):
        if v is not None:
            if not v.startswith('https://www.linkedin.com/'):
                raise ValueError('LinkedIn URL must start with https://www.linkedin.com/')
        return v

class ContactCreate(ContactBase):
    @field_validator('email')
    @classmethod
    def validate_email_required(cls, v, info):
        # For creation, email is recommended but not required
        return v

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    linkedin: Optional[str] = None
    notes: Optional[str] = None

    # Apply same validators as ContactBase
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError('Name must be at least 2 characters long')
            if len(v.strip()) > 100:
                raise ValueError('Name must be less than 100 characters')
            return v.strip()
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
            if not re.match(phone_pattern, v.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')):
                raise ValueError('Invalid phone number format')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['lead', 'prospect', 'customer', 'inactive', 'archived']
            if v.lower() not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v.lower() if v else v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Cannot have more than 10 tags')
            for tag in v:
                if len(tag) > 20:
                    raise ValueError('Each tag must be less than 20 characters')
        return v

    @field_validator('linkedin')
    @classmethod
    def validate_linkedin(cls, v):
        if v is not None:
            if not v.startswith('https://www.linkedin.com/'):
                raise ValueError('LinkedIn URL must start with https://www.linkedin.com/')
        return v

class Contact(ContactBase):
    id: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
