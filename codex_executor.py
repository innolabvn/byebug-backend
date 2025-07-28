import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------------------------
# Step 1: Setup logger for .log output
# ----------------------------------------
def setup_logger(log_path: str) -> logging.Logger:
    logger = logging.getLogger("codex_executor")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # File handler with full info
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Stream handler to console (avoid emoji if console doesn't support)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    logger.addHandler(sh)

    logger.propagate = False
    return logger

# ----------------------------------------
# Step 2: Append to JSON log file
# ----------------------------------------
def log_json(json_path: str, message: str) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message,
    }
    with open(json_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# ----------------------------------------
# Step 3: Main automation logic for Codex
# ----------------------------------------
def run_codex(prompt: str, repo_label: str, user_data_dir: str, profile: str, log_path: str, json_log_path: str) -> None:
    logger = setup_logger(log_path)
    logger.info("Starting Codex executor")
    log_json(json_log_path, "\ud83d\ude80 Starting Codex executor")

    options = Options()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f"--profile-directory={profile}")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    try:
        encoded_prompt = quote(prompt)
        url = f"https://chat.openai.com/codex?prompt={encoded_prompt}"
        logger.info(f"Opening {url}")
        log_json(json_log_path, f"\ud83c\udf10 Opening {url}")
        driver.get(url)

        logger.info("Waiting for page load or login if required")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)

        # Step 1: Open repo dropdown
        logger.info("Clicking repository dropdown")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='View all code environments']"))
        )

        repo_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='View all code environments']"))
        )
        repo_button.click()
        log_json(json_log_path, "\ud83d\udcc2 Opened repository dropdown")

        # Step 2: Click repo item (get its parent button)
        logger.info(f"Selecting repo: {repo_label}")
        repo_item = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{repo_label}')]/ancestor::button"))
        )
        repo_item.click()
        logger.info(f"Selected repo: {repo_label}")
        log_json(json_log_path, f"\u2705 Selected repo {repo_label}")

        # Step 3: Click Code button
        logger.info("Looking for 'Code' button")
        code_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Code')]"))
        )
        code_button.click()
        logger.info("Clicked Code button")
        log_json(json_log_path, "\ud83d\udcc8 Clicked Code button")

        time.sleep(5)

    except Exception as e:
        logger.exception(f"Error occurred: {e}")
        log_json(json_log_path, f"\u274c Exception: {str(e)}")

    finally:
        driver.quit()
        logger.info("Browser closed")
        log_json(json_log_path, "\ud83d\udea9 Browser closed")

# ----------------------------------------
# Step 4: Parse args and generate log files
# ----------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Run Codex with Selenium")
    parser.add_argument("prompt", help="Prompt to send to Codex")
    parser.add_argument("repo_label", help="Repository label in Codex (e.g., innolabvn/byebug-backend)")
    parser.add_argument("user_data_dir", help="Chrome user data directory")
    parser.add_argument("--profile", default="Default", help="Chrome profile directory (default: Default)")
    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join("logs", f"codex_{timestamp}.log")
    json_log_path = os.path.join("logs", f"codex_{timestamp}.json")

    run_codex(args.prompt, args.repo_label, args.user_data_dir, args.profile, log_path, json_log_path)

if __name__ == "__main__":
    main()