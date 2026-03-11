from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Date, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)
    provider = Column(String, nullable=False, default='local')
    google_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    company = Column(String)
    title = Column(String)
    status = Column(String)
    tags = Column(Text)  # Stored as JSON string for now to match current logic
    linkedin = Column(String)
    notes = Column(Text)
    createdAt = Column(DateTime, default=datetime.datetime.now)
    updatedAt = Column(DateTime, onupdate=datetime.datetime.now)

class Deal(Base):
    __tablename__ = "deals"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    contactId = Column(String)
    company = Column(String)
    value = Column(Float)
    stage = Column(String)
    probability = Column(Integer)
    closeDate = Column(Date)
    notes = Column(Text)
    createdAt = Column(DateTime, default=datetime.datetime.now)
    updatedAt = Column(DateTime, onupdate=datetime.datetime.now)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    contactId = Column(String)
    dueDate = Column(Date)
    priority = Column(String)
    done = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.datetime.now)

class Note(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(Text)
    contactId = Column(String)
    contactName = Column(String)
    createdAt = Column(DateTime, default=datetime.datetime.now)
    updatedAt = Column(DateTime, onupdate=datetime.datetime.now)

class Email(Base):
    __tablename__ = "emails"
    id = Column(String, primary_key=True)
    to_email = Column(String)
    subject = Column(String)
    body = Column(Text)
    sentAt = Column(DateTime, default=datetime.datetime.now)
    trackingId = Column(String, nullable=True)
    openCount = Column(Integer, default=0)
    lastOpenedAt = Column(DateTime, nullable=True)
    isRead = Column(Boolean, default=False)
    readAt = Column(DateTime, nullable=True)
    direction = Column(String, default='sent')
    contactId = Column(String, nullable=True)
    type = Column(String, nullable=True)

class Activity(Base):
    __tablename__ = "activity"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    text = Column(Text)
    color = Column(String)
    time = Column(DateTime, default=datetime.datetime.now)

class Setting(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True)
    value = Column(Text)
