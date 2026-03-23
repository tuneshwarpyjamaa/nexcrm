from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import uuid
from typing import List
from tasks.schemas import Task, TaskCreate, TaskUpdate
from db import get_db
from auth.dependencies import verify_token
from simple_cache import get, set, clear_pattern

router = APIRouter(prefix="/api")


def _row_to_task(row) -> dict:
    # Task has no updatedAt column — only createdAt
    return {
        "id": row["id"],
        "title": row["title"],
        "contactId": row["contactId"],
        "dueDate": str(row["dueDate"]) if row["dueDate"] else None,
        "priority": row["priority"],
        "done": bool(row["done"]),
        "createdAt": str(row["createdAt"]) if row["createdAt"] else None,
    }


@router.get("/tasks", response_model=List[Task])
async def get_tasks(current_user: str = Depends(verify_token), db=Depends(get_db)):
    cache_key = f"tasks_{current_user}"
    cached = get(cache_key)
    if cached is not None:
        return cached
    rows = await db.fetch('SELECT * FROM tasks ORDER BY "createdAt" DESC')
    tasks = [_row_to_task(r) for r in rows]
    set(cache_key, tasks)
    return tasks


@router.post("/tasks", response_model=Task)
async def create_task(
    task: TaskCreate, current_user: str = Depends(verify_token), db=Depends(get_db)
):
    clear_pattern("tasks_")
    task_id = f"t_{uuid.uuid4().hex}"
    created_at = datetime.now()
    await db.execute(
        'INSERT INTO tasks (id, title, "contactId", "dueDate", priority, done, "createdAt") '
        "VALUES ($1, $2, $3, $4, $5, $6, $7)",
        task_id, task.title, task.contactId, task.dueDate,
        task.priority, task.done, created_at,
    )
    row = await db.fetchrow("SELECT * FROM tasks WHERE id = $1", task_id)
    return _row_to_task(row)


@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: str, updates: TaskUpdate,
    current_user: str = Depends(verify_token), db=Depends(get_db)
):
    existing = await db.fetchrow("SELECT id FROM tasks WHERE id = $1", task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    clear_pattern("tasks_")
    update_data = updates.dict(exclude_unset=True)
    # Task has NO updatedAt column — do not inject it

    set_clauses = [f'"{k}" = ${i + 1}' for i, k in enumerate(update_data.keys())]
    values = list(update_data.values()) + [task_id]
    await db.execute(
        f'UPDATE tasks SET {", ".join(set_clauses)} WHERE id = ${len(values)}',
        *values,
    )
    row = await db.fetchrow("SELECT * FROM tasks WHERE id = $1", task_id)
    return _row_to_task(row)


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str, current_user: str = Depends(verify_token), db=Depends(get_db)
):
    result = await db.execute("DELETE FROM tasks WHERE id = $1", task_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Task not found")
    clear_pattern("tasks_")
    return {"success": True}
