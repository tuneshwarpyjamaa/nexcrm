from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from db import get_db
from auth.dependencies import verify_token

router = APIRouter(prefix="/api")


def _row_to_activity(row) -> dict:
    return {
        "id": row["id"],
        "type": row["type"],
        "text": row["text"],
        "color": row["color"],
        "time": str(row["time"]) if row["time"] else None,
    }


@router.get("/activity")
async def get_activity(current_user: str = Depends(verify_token), db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM activity ORDER BY time DESC LIMIT 100")
    return [_row_to_activity(r) for r in rows]


@router.get("/activity/{activity_id}")
async def get_activity_by_id(activity_id: int, current_user: str = Depends(verify_token), db=Depends(get_db)):
    row = await db.fetchrow("SELECT * FROM activity WHERE id = $1", activity_id)
    if not row:
        raise HTTPException(status_code=404, detail="Activity not found")
    return _row_to_activity(row)


@router.post("/activity")
async def create_activity(activity: dict, current_user: str = Depends(verify_token), db=Depends(get_db)):
    type_ = activity.get("type")
    text = activity.get("text")
    color = activity.get("color", "blue")
    if not type_ or not text:
        raise HTTPException(status_code=400, detail="type and text are required")
    row = await db.fetchrow(
        "INSERT INTO activity (type, text, color, time) VALUES ($1, $2, $3, $4) RETURNING *",
        type_, text, color, datetime.now(),
    )
    return _row_to_activity(row)
