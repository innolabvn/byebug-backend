import argparse
import json
import logging
import os
import time
from datetime import datetime
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_logger(log_path: str) -> logging.Logger:
    """Configure and return a logger that writes to the given path."""
    logger = logging.getLogger("codex_executor")
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(log_path)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    return logger


def log_json(json_path: str, message: str) -> None:
    """Append a JSON-formatted log entry to the given file."""
    entry = {"timestamp": datetime.utcnow().isoformat(), "message": message}
    with open(json_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def run_codex(prompt: str, repo_label: str, user_data_dir: str, profile: str, log_path: str, json_log_path: str) -> None:
    logger = setup_logger(log_path)
    log_json(json_log_path, "Starting Codex executor")
    logger.info("Starting Codex executor")

    options = Options()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f"--profile-directory={profile}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    try:
        encoded_prompt = quote(prompt)
        url = f"https://chat.openai.com/codex?prompt={encoded_prompt}"
        logger.info("Opening %s", url)
        log_json(json_log_path, f"Opening {url}")
        driver.get(url)

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        try:
            repo_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'repo-picker')]"))
            )
            repo_button.click()
            repo_item = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[text()='{repo_label}']"))
            )
            repo_item.click()
            logger.info("Selected repo %s", repo_label)
            log_json(json_log_path, f"Selected repo {repo_label}")
        except Exception as e:
            logger.warning("Could not select repo: %s", e)
            log_json(json_log_path, f"Repo selection failed: {e}")

        code_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Code')]"))
        )
        code_button.click()
        logger.info("Clicked Code button")
        log_json(json_log_path, "Clicked Code button")
        time.sleep(5)
    finally:
        driver.quit()
        logger.info("Browser closed")
        log_json(json_log_path, "Browser closed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Codex with Selenium")
    parser.add_argument("prompt", help="Prompt to send to Codex")
    parser.add_argument("repo_label", help="Repository label in Codex")
    parser.add_argument("user_data_dir", help="Chrome user data directory")
    parser.add_argument("--profile", default="Default", help="Chrome profile directory")
    parser.add_argument("--log", default="codex_executor.log", help="Path to text log file")
    parser.add_argument("--json-log", default="codex_executor.json", help="Path to JSON log file")
    args = parser.parse_args()

    run_codex(args.prompt, args.repo_label, args.user_data_dir, args.profile, args.log, args.json_log)


if __name__ == "__main__":
    main()
