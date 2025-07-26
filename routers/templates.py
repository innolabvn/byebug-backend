from fastapi import APIRouter, HTTPException
from typing import List

from models import Template, TemplateUpdate
from database import get_database

router = APIRouter(tags=["templates"])

@router.get("/templates", response_model=List[Template])
async def list_templates():
    """Return all templates."""
    db = get_database()
    # Fetch all templates from MongoDB
    templates = await db.byebug.templates.find().to_list(None)
    return templates

@router.post("/templates", response_model=Template, status_code=201)
async def create_template(template: Template):
    """Create a new template."""
    db = get_database()
    # Ensure unique ID before insertion
    if await db.byebug.templates.find_one({"id": template.id}):
        raise HTTPException(status_code=400, detail="Template already exists")
    # Persist the template to the database
    await db.byebug.templates.insert_one(template.dict())
    return template

@router.get("/templates/{template_id}", response_model=Template)
async def get_template(template_id: str):
    """Get a template by ID."""
    db = get_database()
    # Find the template document
    tpl = await db.byebug.templates.find_one({"id": template_id})
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return tpl

@router.patch("/templates/{template_id}", response_model=Template)
async def update_template(template_id: str, update: TemplateUpdate):
    """Update an existing template."""
    db = get_database()
    update_data = {k: v for k, v in update.dict(exclude_unset=True).items()}
    # Apply partial update to the template
    result = await db.byebug.templates.update_one({"id": template_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    tpl = await db.byebug.templates.find_one({"id": template_id})
    return tpl

@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(template_id: str):
    """Remove a template."""
    db = get_database()
    # Delete the template document
    result = await db.byebug.templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return

