from fastapi import APIRouter, HTTPException
from typing import List

from models import Task, TaskUpdate
from database import get_database

router = APIRouter()

@router.get("/tags", response_model=List[Task])
async def get_all_tasks():
    """Return all tasks in the database."""
    db = get_database()
    # Retrieve every task document
    tasks = await db.byebug.tasks.find().to_list(None)
    return tasks

@router.post("/tasks", response_model=Task, status_code=201)
async def create_task(task: Task):
    """Create a new task."""
    db = get_database()
    # Prevent duplicates based on provided ID
    if await db.byebug.tasks.find_one({"id": task.id}):
        raise HTTPException(status_code=400, detail="Task already exists")
    # Insert the new task
    await db.byebug.tasks.insert_one(task.dict())
    return task

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get a task by its ID."""
    db = get_database()
    # Look up the task in MongoDB
    task = await db.byebug.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, update: TaskUpdate):
    """Update a task by ID."""
    db = get_database()
    update_data = {k: v for k, v in update.dict(exclude_unset=True).items()}
    # Apply updates to the task document
    result = await db.byebug.tasks.update_one({"id": task_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    task = await db.byebug.tasks.find_one({"id": task_id})
    return task

@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: str):
    """Delete a task by ID."""
    db = get_database()
    # Remove the task from the collection
    result = await db.byebug.tasks.delete_one({"id": task_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return

