from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import json
import uuid
from typing import List
from contacts.schemas import Contact, ContactCreate, ContactUpdate
from db import get_db
from auth.dependencies import verify_token
from simple_cache import get, set, clear_pattern

router = APIRouter(prefix="/api")


def _row_to_contact(row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "company": row["company"],
        "title": row["title"],
        "status": row["status"],
        "tags": json.loads(row["tags"]) if row["tags"] else [],
        "linkedin": row["linkedin"],
        "notes": row["notes"],
        "createdAt": str(row["createdAt"]) if row["createdAt"] else None,
        "updatedAt": str(row["updatedAt"]) if row["updatedAt"] else None,
    }


@router.get("/contacts", response_model=List[Contact])
async def get_contacts(current_user: str = Depends(verify_token), db=Depends(get_db)):
    cache_key = f"contacts_{current_user}"
    cached = get(cache_key)
    if cached is not None:
        return cached
    rows = await db.fetch('SELECT * FROM contacts ORDER BY "createdAt" DESC')
    contacts = [_row_to_contact(r) for r in rows]
    set(cache_key, contacts)
    return contacts


@router.get("/contacts/{contact_id}", response_model=Contact)
async def get_contact_by_id(contact_id: str, current_user: str = Depends(verify_token), db=Depends(get_db)):
    row = await db.fetchrow("SELECT * FROM contacts WHERE id = $1", contact_id)
    if not row:
        raise HTTPException(status_code=404, detail="Contact not found")
    return _row_to_contact(row)


@router.post("/contacts", response_model=Contact)
async def create_contact(
    contact: ContactCreate, current_user: str = Depends(verify_token), db=Depends(get_db)
):
    clear_pattern("contacts_")
    contact_id = f"c_{uuid.uuid4().hex}"
    created_at = datetime.now()
    await db.execute(
        'INSERT INTO contacts (id, name, email, phone, company, title, status, tags, linkedin, notes, "createdAt") '
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)",
        contact_id, contact.name, contact.email, contact.phone, contact.company,
        contact.title, contact.status, json.dumps(contact.tags or []),
        contact.linkedin, contact.notes, created_at,
    )
    row = await db.fetchrow("SELECT * FROM contacts WHERE id = $1", contact_id)
    return _row_to_contact(row)


@router.put("/contacts/{contact_id}", response_model=Contact)
async def update_contact(
    contact_id: str, updates: ContactUpdate,
    current_user: str = Depends(verify_token), db=Depends(get_db)
):
    existing = await db.fetchrow("SELECT id FROM contacts WHERE id = $1", contact_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Contact not found")

    clear_pattern("contacts_")
    update_data = updates.dict(exclude_unset=True)
    update_data["updatedAt"] = datetime.now()
    if "tags" in update_data and update_data["tags"] is not None:
        update_data["tags"] = json.dumps(update_data["tags"])

    set_clauses = [f'"{k}" = ${i + 1}' for i, k in enumerate(update_data.keys())]
    values = list(update_data.values()) + [contact_id]
    await db.execute(
        f'UPDATE contacts SET {", ".join(set_clauses)} WHERE id = ${len(values)}',
        *values,
    )
    row = await db.fetchrow("SELECT * FROM contacts WHERE id = $1", contact_id)
    return _row_to_contact(row)


@router.delete("/contacts/{contact_id}")
async def delete_contact(
    contact_id: str, current_user: str = Depends(verify_token), db=Depends(get_db)
):
    result = await db.execute("DELETE FROM contacts WHERE id = $1", contact_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Contact not found")
    clear_pattern("contacts_")
    return {"success": True}
