from fastapi import APIRouter, Depends
from db import get_db
from auth.dependencies import verify_token

router = APIRouter(prefix="/api")


@router.get("/settings")
async def get_settings(current_user: str = Depends(verify_token), db=Depends(get_db)):
    rows = await db.fetch("SELECT key, value FROM settings")
    return {row["key"]: row["value"] for row in rows}


@router.post("/settings")
async def update_settings(
    settings: dict, current_user: str = Depends(verify_token), db=Depends(get_db)
):
    for key, value in settings.items():
        await db.execute(
            "INSERT INTO settings (key, value) VALUES ($1, $2) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            str(key), str(value),
        )
    return {"success": True}
