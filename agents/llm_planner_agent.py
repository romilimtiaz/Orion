# agents/llm_planner_agent.py

import requests
import json
import os
from utils.gemini_client import generate as gemini_generate, get_gemini_api_key

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "codellama:instruct"

def _validate_plan(obj: dict) -> bool:
    if not isinstance(obj, dict):
        return False
    agent = obj.get("agent")
    info = obj.get("info")
    if agent not in ["file", "email", "browser", "search", "calendar", "reminder", "translate", "knowledge", "hardware", "system", "task_add", "task_list", "notes_add", "notes_read", "notes_clear", "meeting", "papers", "code", "scaffold", "call", "updater", "unknown"]:
        return False
    if not isinstance(info, dict):
        return False
    return True


def _keyword_fallback(command: str):
    lc = command.lower()
    if "paper" in lc or "arxiv" in lc or "research" in lc:
        return {"agent": "papers", "info": {"topic": command}}
    if "note" in lc and "read" in lc:
        return {"agent": "notes_read", "info": {"topic": command}}
    if "note" in lc and ("add" in lc or "save" in lc):
        return {"agent": "notes_add", "info": {"topic": "general", "content": command}}
    if "note" in lc and ("clear" in lc or "delete" in lc):
        return {"agent": "notes_clear", "info": {"topic": "general"}}
    if "meeting" in lc:
        if "start" in lc:
            return {"agent": "meeting", "info": {"action": "start", "topic": command}}
        if "stop" in lc or "end" in lc or "summarize" in lc:
            return {"agent": "meeting", "info": {"action": "stop"}}
        if "add" in lc:
            return {"agent": "meeting", "info": {"action": "add", "content": command}}
    if "code" in lc or "python" in lc or "function" in lc:
        return {"agent": "code", "info": {"prompt": command}}
    if "scaffold" in lc or "project" in lc:
        return {"agent": "scaffold", "info": {"project": command, "template": "opencv_face_tracker"}}
    if "call status" in lc or "call" in lc:
        return {"agent": "call", "info": {"action": "set", "message": command}}
    if "lock" in lc or "volume" in lc or "brightness" in lc:
        if "lock" in lc:
            return {"agent": "system", "info": {"action": "lock"}}
        if "volume" in lc:
            direction = "up" if "up" in lc or "raise" in lc else "down" if "down" in lc or "lower" in lc else "mute" if "mute" in lc else "up"
            return {"agent": "system", "info": {"action": "volume", "direction": direction}}
        if "brightness" in lc:
            direction = "up" if "up" in lc or "brighter" in lc else "down"
            return {"agent": "system", "info": {"action": "brightness", "direction": direction}}
    if "update" in lc:
        topic = command if "feature" in lc else "AI assistant new features"
        return {"agent": "updater", "info": {"topic": topic}}
    if "translate" in lc:
        return {"agent": "translate", "info": {"text": command, "language": "en"}}
    return {"agent": "unknown", "info": {}}


def plan_command(command, model: str | None = None, history: list | None = None, retries: int = 1):
    history_text = ""
    if history:
        history_lines = []
        for h in history[-5:]:
            history_lines.append(f"- User: {h.get('command','')} | Agent: {h.get('agent','')} | Result: {h.get('result','')}")
        history_text = "\nRecent interactions:\n" + "\n".join(history_lines) + "\n"

    prompt = f"""
You are Orion's planner module. Read the user's natural language command and return a JSON object with:
- "agent": one of [file, email, browser, search, calendar, reminder, translate, knowledge, hardware, system, task_add, task_list, notes_add, notes_read, notes_clear, meeting, papers, code, scaffold, call, updater, unknown]
- "info": contains only the extracted values needed for that agent

Respond ONLY in valid JSON format.
DO NOT include any explanation, markdown, or extra text.
{history_text}

Examples:

Command: Translate thank you to Arabic
→ {{"agent": "translate", "info": {{"text": "thank you", "language": "ar"}}}}

Command: Translate good night to French
→ {{"agent": "translate", "info": {{"text": "good night", "language": "fr"}}}}

Command: Schedule project presentation on 2025-06-30 15:00
→ {{"agent": "calendar", "info": {{"event": "project presentation", "datetime": "2025-06-30 15:00"}}}}

Command: Remind me to check oven at 2025-06-24 21:00
→ {{"agent": "reminder", "info": {{"task": "check oven", "datetime": "2025-06-24 21:00"}}}}

Command: Update yourself on AI news
→ {{"agent": "knowledge", "info": {{"topic": "AI news"}}}}

Command: Lock my screen
→ {{"agent": "hardware", "info": {{"action": "lock_screen"}}}}

Command: Queue a research task on quantum computing
→ {{"agent": "task_add", "info": {{"type": "research", "topic": "quantum computing"}}}}

Command: Show my tasks
→ {{"agent": "task_list", "info": {{}}}}

Command: Add note about LLM safety
→ {{"agent": "notes_add", "info": {{"topic": "LLM safety", "content": "Model eval ideas..."}}}}

Command: Read notes on LLM safety
→ {{"agent": "notes_read", "info": {{"topic": "LLM safety"}}}}

Command: Clear notes on LLM safety
→ {{"agent": "notes_clear", "info": {{"topic": "LLM safety"}}}}

Command: Start meeting about quarterly review
→ {{"agent": "meeting", "info": {{"action": "start", "topic": "quarterly review"}}}}

Command: Stop meeting and summarize
→ {{"agent": "meeting", "info": {{"action": "stop"}}}}

Command: Add this to the meeting: we need to ship on time
→ {{"agent": "meeting", "info": {{"action": "add", "content": "we need to ship on time"}}}}

Command: Find recent papers on diffusion models
→ {{"agent": "papers", "info": {{"topic": "diffusion models"}}}}

Command: Write a Python function for quicksort
→ {{"agent": "code", "info": {{"prompt": "Write a Python function for quicksort"}}}}

Command: Scaffold an OpenCV face tracker project
→ {{"agent": "scaffold", "info": {{"project": "OpenCV face tracker", "template": "opencv_face_tracker"}}}}

Command: Set call status to I'm busy, please call later
→ {{"agent": "call", "info": {{"action": "set", "message": "I'm busy, please call later"}}}}

Command: Lock my screen
→ {{"agent": "system", "info": {{"action": "lock"}}}}

Command: Volume up
→ {{"agent": "system", "info": {{"action": "volume", "direction": "up"}}}}

Command: Dim the screen
→ {{"agent": "system", "info": {{"action": "brightness", "direction": "down"}}}}

Command: Auto-update Orion with new feature ideas
→ {{"agent": "updater", "info": {{"topic": "AI assistant new features"}}}}

Command: \"\"\"{command}\"\"\"
"""

    attempts = retries + 1
    last_error = None

    for attempt in range(attempts):
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": model or DEFAULT_MODEL,
                "prompt": prompt,
                "stream": False,
                "stop": ["\n\n"]
            }, timeout=60)
            response.raise_for_status()
            payload = response.json()
            if "error" in payload:
                last_error = payload["error"]
                print(f"❌ Planner error from Ollama: {payload['error']}")
                continue
            result = payload.get("response", "")
            if not result:
                last_error = "empty_response"
                print("❌ Planner error: empty response from Ollama (check model pull and endpoint).")
                continue

            print("\n🧪 Raw LLM response:\n", result)

            # 🧼 Clean out unwanted formatting like →, leading text, newlines
            clean = result.strip()
            if "{" in clean:
                clean = clean[clean.index("{"):]  # Start from first '{'

            try:
                parsed = json.loads(clean)
                if _validate_plan(parsed):
                    if parsed.get("agent") == "unknown":
                        fb = _keyword_fallback(command)
                        if fb.get("agent") != "unknown":
                            return fb
                    return parsed
                last_error = "schema_validation_failed"
                print("❌ Planner error: response failed schema validation.")
            except Exception as e:
                last_error = f"json_parse_error: {e}"
                print("❌ JSON parse error:", e)

        except Exception as e:
            last_error = str(e)
            print("❌ Planner error:", e)

    # Fallback keyword routing if LLM failed completely
    fb = _keyword_fallback(command)
    if fb.get("agent") != "unknown":
        return fb
    return {"agent": "unknown", "info": {}, "error": last_error}
