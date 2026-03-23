from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import json
import jwt
import os
from typing import List
from deals.schemas import Deal, DealCreate, DealUpdate
from simple_cache import get, set, clear_pattern
from db import get_db, close_db

router = APIRouter(prefix="/api")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.get("/deals", response_model=List[Deal])
async def get_deals(current_user: str = Depends(verify_token)):
    # Check cache first
    cache_key_str = f"deals_{current_user}"
    cached_data = get(cache_key_str)
    if cached_data is not None:
        return cached_data
    
    # If not cached, fetch from database
    db = await get_db()
    try:
        rows = await db.fetch('SELECT * FROM deals ORDER BY "createdAt" DESC')
        deals = []
        for row in rows:
            deal = {
                'id': row['id'],
                'title': row['title'],
                'contactId': row['contactid'],
                'company': row['company'],
                'value': row['value'],
                'stage': row['stage'],
                'probability': row['probability'],
                'closeDate': str(row['closedate']) if row['closedate'] else None,
                'notes': row['notes'],
                'createdAt': str(row['createdAt']),
                'updatedAt': str(row['updatedAt'])
            }
            deals.append(deal)
        # Cache the result
        set(cache_key_str, deals)
        return deals
    finally:
        await close_db(db)

@router.post("/deals", response_model=Deal)
async def create_deal(deal: DealCreate, current_user: str = Depends(verify_token)):
    # Clear cache on create
    clear_pattern("deals_")
    
    id = f"d_{int(datetime.now().timestamp() * 1000)}"
    createdAt = datetime.now()
    db = await get_db()
    try:
        await db.execute(
            'INSERT INTO deals (id, title, "contactId", company, value, stage, probability, "closeDate", notes, "createdAt") VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)',
            id, deal.title, deal.contactId, deal.company, deal.value, deal.stage, deal.probability, deal.closeDate, deal.notes, createdAt
        )
        row = await db.fetchrow("SELECT * FROM deals WHERE id = $1", id)
        deal_data = {
            'id': row['id'],
            'title': row['title'],
            'contactId': row['contactid'],
            'company': row['company'],
            'value': row['value'],
            'stage': row['stage'],
            'probability': row['probability'],
            'closeDate': str(row['closedate']) if row['closedate'] else None,
            'notes': row['notes'],
            'createdAt': str(row['createdAt']),
            'updatedAt': str(row['updatedAt'])
        }
        return deal_data
    finally:
        await close_db(db)

@router.put("/deals/{id}", response_model=Deal)
async def update_deal(id: str, updates: DealUpdate, current_user: str = Depends(verify_token)):
    # Clear cache on update
    clear_pattern("deals_")
    
    update_data = updates.dict(exclude_unset=True)
    update_data["updatedAt"] = datetime.now()
    
    set_clauses = []
    values = []
    for i, (key, value) in enumerate(update_data.items()):
        set_clauses.append(f'"{key}" = ${i+1}')
        values.append(value)
    
    values.append(id)
    
    db = await get_db()
    await db.execute(f"UPDATE deals SET {', '.join(set_clauses)} WHERE id = ${len(values)}", *values)
    row = await db.fetchrow("SELECT * FROM deals WHERE id = $1", id)
    deal_data = {
        'id': row['id'],
        'title': row['title'],
        'contactId': row['contactid'],
        'company': row['company'],
        'value': row['value'],
        'stage': row['stage'],
        'probability': row['probability'],
        'closeDate': str(row['closedate']) if row['closedate'] else None,
        'notes': row['notes'],
        'createdAt': str(row['createdAt']),
        'updatedAt': str(row['updatedAt'])
    }
    await close_db(db)
    return deal_data

@router.delete("/deals/{id}")
async def delete_deal(id: str, current_user: str = Depends(verify_token)):
    # Clear cache on delete
    clear_pattern("deals_")
    
    db = await get_db()
    try:
        await db.execute("DELETE FROM deals WHERE id = $1", id)
        return {"success": True}
    finally:
        await close_db(db)
