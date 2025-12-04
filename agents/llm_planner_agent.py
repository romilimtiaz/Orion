# agents/llm_planner_agent.py

import requests
import json

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "codellama:instruct"

def _validate_plan(obj: dict) -> bool:
    if not isinstance(obj, dict):
        return False
    agent = obj.get("agent")
    info = obj.get("info")
    if agent not in ["file", "email", "browser", "search", "calendar", "reminder", "translate", "knowledge", "hardware", "task_add", "task_list", "notes_add", "notes_read", "notes_clear", "meeting", "papers", "unknown"]:
        return False
    if not isinstance(info, dict):
        return False
    return True


def plan_command(command, model: str | None = None, history: list | None = None, retries: int = 1):
    history_text = ""
    if history:
        history_lines = []
        for h in history[-5:]:
            history_lines.append(f"- User: {h.get('command','')} | Agent: {h.get('agent','')} | Result: {h.get('result','')}")
        history_text = "\nRecent interactions:\n" + "\n".join(history_lines) + "\n"

    prompt = f"""
You are Orion's planner module. Read the user's natural language command and return a JSON object with:
- "agent": one of [file, email, browser, search, calendar, reminder, translate, knowledge, hardware, task_add, task_list, notes_add, notes_read, notes_clear, meeting, papers, unknown]
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
                    return parsed
                last_error = "schema_validation_failed"
                print("❌ Planner error: response failed schema validation.")
            except Exception as e:
                last_error = f"json_parse_error: {e}"
                print("❌ JSON parse error:", e)

        except Exception as e:
            last_error = str(e)
            print("❌ Planner error:", e)

    return {"agent": "unknown", "info": {}, "error": last_error}
