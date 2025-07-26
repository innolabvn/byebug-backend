from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from urllib.parse import quote
from jinja2 import Template as JinjaTemplate

from database import get_database

router = APIRouter(prefix="/codex", tags=["codex"])

@router.get("/url/{task_id}")
async def generate_codex_url(
    task_id: str,
    template_id: str = Query(...),
    base_url: str = Query("https://chat.openai.com/codex"),
):
    """Create and store a Codex URL for a task using a template."""
    db = get_database()
    task = await db.byebug.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    template = await db.byebug.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    tpl = JinjaTemplate(template["content"])
    prompt = tpl.render(task=task)
    encoded_prompt = quote(prompt)
    codex_url = f"{base_url}?prompt={encoded_prompt}"

    await db.byebug.tasks.update_one(
        {"id": task_id},
        {"$set": {"codex_url": codex_url, "prompt": prompt}}
    )

    return {"codex_url": codex_url, "prompt": prompt}

