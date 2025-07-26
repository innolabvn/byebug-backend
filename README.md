# Byebug Backend

This FastAPI service powers task tracking, Codex integration, and analytics for the Byebug project.

## Running

```bash
docker compose up --build
```

The API will be available at `http://localhost:5000`. Interactive documentation is provided by Swagger UI at [`/docs`](http://localhost:5000/docs).

## API Overview

### Tasks
- `GET /api/tasks` – list tasks
- `POST /api/tasks` – create a task; optional `template_id` query parameter will generate a Codex prompt and URL
- `GET /api/tasks/{task_id}` – retrieve a task
- `PATCH /api/tasks/{task_id}` – update a task
- `DELETE /api/tasks/{task_id}` – delete a task
- `POST /api/tasks/{task_id}/run-codex` – mark a task as in progress and return the Codex URL

### Codex
- `GET /api/codex/url/{task_id}` – build and store a Codex URL for the task using a template (`template_id` query parameter)

### Templates
- `GET /api/templates` – list templates
- `POST /api/templates` – create a template
- `GET /api/templates/{template_id}` – retrieve a template
- `PATCH /api/templates/{template_id}` – update a template
- `DELETE /api/templates/{template_id}` – delete a template

### Analytics
- `GET /api/analytics/test-runs`
- `GET /api/analytics/bugs`
- `GET /api/analytics/coverage`
- `GET /api/analytics/summary`

## Codex Executor

A helper script `codex_executor.py` automates launching Codex with Selenium. It opens the Codex UI with a given prompt, selects the configured repository, clicks the **Code** button and writes logs to both a text file and a JSON file.

### Usage

```bash
python codex_executor.py "<prompt>" <repo_label> <chrome_user_data_dir> [--profile Default] [--log path/to/logfile.log] [--json-log path/to/log.json]
```

Both log files are appended to each time the script runs so you can inspect the execution history later.
