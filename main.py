from fastapi import FastAPI

from routers import tasks, templates, analytics
from routers import codex

tags_metadata = [
    {"name": "tasks", "description": "Manage tasks"},
    {"name": "templates", "description": "Template management"},
    {"name": "analytics", "description": "Analytics endpoints"},
    {"name": "codex", "description": "Codex integration"},
]

app = FastAPI(
    title="Byebug Backend API",
    docs_url="/docs",
    openapi_url="/openapi.json",
    openapi_tags=tags_metadata,
)

# Register routers for each service
app.include_router(tasks.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(codex.router, prefix="/api")

@app.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"message": "pong"}
