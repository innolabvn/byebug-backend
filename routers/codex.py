from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from urllib.parse import quote
from jinja2 import Template as JinjaTemplate
import os
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from database import get_database

router = APIRouter(prefix="/codex", tags=["codex"])


def _create_driver() -> webdriver.Chrome:
    """Initialize a Chrome WebDriver using stored profile data."""
    options = Options()
    user_data_dir = os.environ.get("CHROME_USER_DATA_DIR")
    profile = os.environ.get("CHROME_PROFILE", "Default")
    if user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument(f"--profile-directory={profile}")

    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

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


@router.get("/repo")
async def list_codex_repos():
    """Retrieve the list of repositories from Codex."""
    repos = await asyncio.to_thread(_fetch_repositories)
    return {"repositories": repos}


@router.post("/ask")
async def ask_codex(prompt: Optional[str] = Query("abc")):
    """Send a prompt to Codex and return the discovered bugs."""
    bugs = await asyncio.to_thread(_ask_codex, prompt)
    return {"bugs": bugs}


def _fetch_repositories() -> List[str]:
    """Open Codex and return the available repository labels."""
    driver = _create_driver()
    repos: List[str] = []
    try:
        driver.get("https://chat.openai.com/codex")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        repo_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='View all code environments']"))
        )
        repo_button.click()

        repo_items = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@role='menu']//span"))
        )
        repos = [item.text for item in repo_items if item.text]
    finally:
        driver.quit()

    return repos


def _ask_codex(prompt: str) -> List[str]:
    """Send a prompt to Codex and return the bug list shown."""
    driver = _create_driver()
    bugs: List[str] = []
    try:
        encoded = quote(prompt)
        driver.get(f"https://chat.openai.com/codex?prompt={encoded}")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        input_box = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.TAG_NAME, "textarea"))
        )
        input_box.clear()
        input_box.send_keys(prompt)

        ask_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Ask')]"))
        )
        ask_button.click()

        bug_items = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.XPATH, "//li[contains(., 'bug') or contains(., 'Bug')]"))
        )
        bugs = [b.text for b in bug_items if b.text]
    finally:
        driver.quit()

    return bugs

