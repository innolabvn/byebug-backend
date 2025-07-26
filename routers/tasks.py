from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from urllib.parse import quote
from jinja2 import Template as JinjaTemplate

from models import Task, TaskUpdate
from database import get_database

router = APIRouter(tags=["tasks"])

@router.get("/tasks", response_model=List[Task])
async def get_all_tasks():
    """Return all tasks in the database."""
    db = get_database()
    # Retrieve every task document
    tasks = await db.byebug.tasks.find().to_list(None)
    return tasks

@router.post("/tasks", response_model=Task, status_code=201)
async def create_task(
    task: Task,
    template_id: Optional[str] = Query(None),
    base_url: str = Query("https://chat.openai.com/codex"),
):
    """Create a new task and optionally generate a Codex URL."""
    db = get_database()
    if await db.byebug.tasks.find_one({"id": task.id}):
        raise HTTPException(status_code=400, detail="Task already exists")

    task_data = task.dict()

    if template_id:
        template = await db.byebug.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        tpl = JinjaTemplate(template["content"])
        prompt = tpl.render(task=task_data)
        task_data["prompt"] = prompt
        task_data["codex_url"] = f"{base_url}?prompt={quote(prompt)}"

    await db.byebug.tasks.insert_one(task_data)
    return task_data

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


@router.post("/tasks/{task_id}/run-codex")
async def run_codex(task_id: str):
    """Mark task as in-progress and return its Codex URL."""
    db = get_database()
    task = await db.byebug.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    codex_url = task.get("codex_url")
    if not codex_url:
        raise HTTPException(status_code=400, detail="Task has no Codex URL")

    await db.byebug.tasks.update_one(
        {"id": task_id},
        {"$set": {"status": "progress"}},
    )
    return {"codex_url": codex_url, "prompt": task.get("prompt")}

