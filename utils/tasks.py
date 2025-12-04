import json
import threading
from pathlib import Path
from datetime import datetime

TASKS_FILE = Path("tasks.json")
_lock = threading.Lock()

def _load():
    if not TASKS_FILE.exists():
        return []
    return json.loads(TASKS_FILE.read_text())

def _save(tasks):
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))

def add_task(task_type: str, payload: dict):
    with _lock:
        tasks = _load()
        task = {
            "id": f"task-{len(tasks)+1}",
            "type": task_type,
            "payload": payload,
            "status": "pending",
            "created": datetime.utcnow().isoformat(),
        }
        tasks.append(task)
        _save(tasks)
    return task

def list_tasks():
    return _load()

def update_task_status(task_id: str, status: str, result: str = ""):
    with _lock:
        tasks = _load()
        for t in tasks:
            if t["id"] == task_id:
                t["status"] = status
                if result:
                    t["result"] = result
                break
        _save(tasks)


def start_worker(handler):
    # Minimal worker stub; runs once on startup to finish pending tasks.
    tasks = _load()
    for t in tasks:
        if t.get("status") == "pending":
            update_task_status(t["id"], "running")
            try:
                result = handler(t)
                update_task_status(t["id"], "done", result or "")
            except Exception as e:
                update_task_status(t["id"], "failed", str(e))
