from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import uuid
from typing import List
from deals.schemas import Deal, DealCreate, DealUpdate
from db import get_db
from auth.dependencies import verify_token
from simple_cache import get, set, clear_pattern

router = APIRouter(prefix="/api")


_DB_COL = {
    "contactId": "contactid",
    "closeDate": "closedate",
    "updatedAt": '"updatedAt"',
}


def _db_col(name: str) -> str:
    return _DB_COL.get(name, name)


def _row_to_deal(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "contactId": row["contactid"],
        "company": row["company"],
        "value": row["value"],
        "stage": row["stage"],
        "probability": row["probability"],
        "closeDate": str(row["closedate"]) if row["closedate"] else None,
        "notes": row["notes"],
        "createdAt": str(row["createdAt"]) if row["createdAt"] else None,
        "updatedAt": str(row["updatedAt"]) if row["updatedAt"] else None,
    }


@router.get("/deals", response_model=List[Deal])
async def get_deals(current_user: str = Depends(verify_token), db=Depends(get_db)):
    cache_key = f"deals_{current_user}"
    cached = get(cache_key)
    if cached is not None:
        return cached
    rows = await db.fetch('SELECT * FROM deals ORDER BY "createdAt" DESC')
    deals = [_row_to_deal(r) for r in rows]
    set(cache_key, deals)
    return deals


@router.post("/deals", response_model=Deal)
async def create_deal(
    deal: DealCreate, current_user: str = Depends(verify_token), db=Depends(get_db)
):
    clear_pattern("deals_")
    deal_id = f"d_{uuid.uuid4().hex}"
    created_at = datetime.now()
    await db.execute(
        'INSERT INTO deals (id, title, contactid, company, value, stage, probability, closedate, notes, "createdAt") '
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
        deal_id, deal.title, deal.contactId, deal.company, deal.value,
        deal.stage, deal.probability, deal.closeDate, deal.notes, created_at,
    )
    row = await db.fetchrow("SELECT * FROM deals WHERE id = $1", deal_id)
    return _row_to_deal(row)


@router.put("/deals/{deal_id}", response_model=Deal)
async def update_deal(
    deal_id: str, updates: DealUpdate,
    current_user: str = Depends(verify_token), db=Depends(get_db)
):
    existing = await db.fetchrow("SELECT id FROM deals WHERE id = $1", deal_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Deal not found")

    clear_pattern("deals_")
    update_data = updates.dict(exclude_unset=True)
    update_data["updatedAt"] = datetime.now()

    set_clauses = [f'{_db_col(k)} = ${i + 1}' for i, k in enumerate(update_data.keys())]
    values = list(update_data.values()) + [deal_id]
    await db.execute(
        f'UPDATE deals SET {", ".join(set_clauses)} WHERE id = ${len(values)}',
        *values,
    )
    row = await db.fetchrow("SELECT * FROM deals WHERE id = $1", deal_id)
    return _row_to_deal(row)


@router.delete("/deals/{deal_id}")
async def delete_deal(
    deal_id: str, current_user: str = Depends(verify_token), db=Depends(get_db)
):
    result = await db.execute("DELETE FROM deals WHERE id = $1", deal_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Deal not found")
    clear_pattern("deals_")
    return {"success": True}
