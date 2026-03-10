from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import jwt
import os
from typing import List
from tasks.schemas import Task, TaskCreate, TaskUpdate
from db import get_pool

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

@router.get("/tasks", response_model=List[Task])
async def get_tasks(current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM tasks ORDER BY tasks."createdAt" DESC')
        return [dict(row) for row in rows]

@router.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate, current_user: str = Depends(verify_token)):
    id = f"t_{int(datetime.now().timestamp() * 1000)}"
    createdAt = datetime.now()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO tasks (id, title, "contactId", "dueDate", priority, done, "createdAt") VALUES ($1, $2, $3, $4, $5, $6, $7)',
            id, task.title, task.contactId, task.dueDate, task.priority, task.done, createdAt
        )
        row = await conn.fetchrow("SELECT * FROM tasks WHERE id = $1", id)
        return dict(row)

@router.put("/tasks/{id}", response_model=Task)
async def update_task(id: str, updates: TaskUpdate, current_user: str = Depends(verify_token)):
    update_data = updates.dict(exclude_unset=True)
    
    fields = ", ".join(f'"{k}" = ${i+2}' for i, k in enumerate(update_data.keys()))
    values = list(update_data.values())
    values.insert(0, id)
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE tasks SET {fields} WHERE id = $1", *values)
        row = await conn.fetchrow("SELECT * FROM tasks WHERE id = $1", id)
        return dict(row)

@router.delete("/tasks/{id}")
async def delete_task(id: str, current_user: str = Depends(verify_token)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM tasks WHERE id = $1", id)
        return {"success": True}
