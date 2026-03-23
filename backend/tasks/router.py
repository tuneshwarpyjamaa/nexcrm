from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import json
import jwt
import os
from typing import List
from tasks.schemas import Task, TaskCreate, TaskUpdate
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

@router.get("/tasks", response_model=List[Task])
async def get_tasks(current_user: str = Depends(verify_token)):
    # Check cache first
    cache_key_str = f"tasks_{current_user}"
    cached_data = get(cache_key_str)
    if cached_data is not None:
        return cached_data
    
    # If not cached, fetch from database
    db = await get_db()
    try:
        rows = await db.fetch('SELECT * FROM tasks ORDER BY "createdAt" DESC')
        tasks = []
        for row in rows:
            task = {
                'id': row['id'],
                'title': row['title'],
                'contactId': row['contactid'],
                'dueDate': str(row['duedate']) if row['duedate'] else None,
                'priority': row['priority'],
                'done': bool(row['done']),
                'createdAt': str(row['createdAt']),
                'updatedAt': str(row['updatedAt'])
            }
            tasks.append(task)
        # Cache the result
        set(cache_key_str, tasks)
        return tasks
    finally:
        await close_db(db)

@router.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate, current_user: str = Depends(verify_token)):
    # Clear cache on create
    clear_pattern("tasks_")
    
    id = f"t_{int(datetime.now().timestamp() * 1000)}"
    createdAt = datetime.now()
    db = await get_db()
    try:
        await db.execute(
            'INSERT INTO tasks (id, title, "contactId", "dueDate", priority, done, "createdAt") VALUES ($1, $2, $3, $4, $5, $6, $7)',
            id, task.title, task.contactId, task.dueDate, task.priority, task.done, createdAt
        )
        row = await db.fetchrow("SELECT * FROM tasks WHERE id = $1", id)
        task_data = {
            'id': row['id'],
            'title': row['title'],
            'contactId': row['contactid'],
            'dueDate': str(row['duedate']) if row['duedate'] else None,
            'priority': row['priority'],
            'done': bool(row['done']),
            'createdAt': str(row['createdAt']),
            'updatedAt': str(row['updatedAt'])
        }
        return task_data
    finally:
        await close_db(db)

@router.put("/tasks/{id}", response_model=Task)
async def update_task(id: str, updates: TaskUpdate, current_user: str = Depends(verify_token)):
    # Clear cache on update
    clear_pattern("tasks_")
    
    update_data = updates.dict(exclude_unset=True)
    update_data["updatedAt"] = datetime.now()
    
    set_clauses = []
    values = []
    for i, (key, value) in enumerate(update_data.items()):
        set_clauses.append(f'"{key}" = ${i+1}')
        values.append(value)
    
    values.append(id)
    
    db = await get_db()
    await db.execute(f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ${len(values)}", *values)
    row = await db.fetchrow("SELECT * FROM tasks WHERE id = $1", id)
    task_data = {
        'id': row['id'],
        'title': row['title'],
        'contactId': row['contactid'],
        'dueDate': row[3],
        'priority': row['priority'],
        'done': bool(row['done']),
        'createdAt': str(row['createdAt']),
        'updatedAt': str(row['updatedAt'])
    }
    await close_db(db)
    return task_data

@router.delete("/tasks/{id}")
async def delete_task(id: str, current_user: str = Depends(verify_token)):
    # Clear cache on delete
    clear_pattern("tasks_")
    
    db = await get_db()
    try:
        await db.execute("DELETE FROM tasks WHERE id = $1", id)
        return {"success": True}
    finally:
        await close_db(db)
