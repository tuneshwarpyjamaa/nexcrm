from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import uuid
from typing import List
from notes.schemas import Note, NoteCreate, NoteUpdate
from db import get_db
from auth.dependencies import verify_token
from simple_cache import get, set, clear_pattern

router = APIRouter(prefix="/api")


_DB_COL = {
    "contactId": "contactid",
    "contactName": "contactname",
    "updatedAt": '"updatedAt"',
}


def _db_col(name: str) -> str:
    return _DB_COL.get(name, name)


def _row_to_note(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "body": row["body"],
        "contactId": row["contactid"],
        "contactName": row["contactname"],
        "createdAt": str(row["createdAt"]) if row["createdAt"] else None,
        "updatedAt": str(row["updatedAt"]) if row["updatedAt"] else None,
    }


@router.get("/notes", response_model=List[Note])
async def get_notes(current_user: str = Depends(verify_token), db=Depends(get_db)):
    # Cache is scoped per user to prevent cross-user data leaks
    cache_key = f"notes_{current_user}"
    cached = get(cache_key)
    if cached is not None:
        return cached
    rows = await db.fetch('SELECT * FROM notes ORDER BY "createdAt" DESC')
    notes = [_row_to_note(r) for r in rows]
    set(cache_key, notes)
    return notes


@router.post("/notes", response_model=Note)
async def create_note(
    note: NoteCreate, current_user: str = Depends(verify_token), db=Depends(get_db)
):
    clear_pattern("notes_")
    note_id = f"n_{uuid.uuid4().hex}"
    created_at = datetime.now()
    await db.execute(
        'INSERT INTO notes (id, title, body, contactid, contactname, "createdAt") '
        "VALUES ($1, $2, $3, $4, $5, $6)",
        note_id, note.title, note.body, note.contactId, note.contactName, created_at,
    )
    row = await db.fetchrow("SELECT * FROM notes WHERE id = $1", note_id)
    return _row_to_note(row)


@router.put("/notes/{note_id}", response_model=Note)
async def update_note(
    note_id: str, updates: NoteUpdate,
    current_user: str = Depends(verify_token), db=Depends(get_db)
):
    existing = await db.fetchrow("SELECT id FROM notes WHERE id = $1", note_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")

    clear_pattern("notes_")
    update_data = updates.dict(exclude_unset=True)
    update_data["updatedAt"] = datetime.now()

    set_clauses = [f'{_db_col(k)} = ${i + 1}' for i, k in enumerate(update_data.keys())]
    values = list(update_data.values()) + [note_id]
    await db.execute(
        f'UPDATE notes SET {", ".join(set_clauses)} WHERE id = ${len(values)}',
        *values,
    )
    row = await db.fetchrow("SELECT * FROM notes WHERE id = $1", note_id)
    return _row_to_note(row)


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: str, current_user: str = Depends(verify_token), db=Depends(get_db)
):
    result = await db.execute("DELETE FROM notes WHERE id = $1", note_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Note not found")
    clear_pattern("notes_")
    return {"success": True}
