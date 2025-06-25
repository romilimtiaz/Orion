# agents/llm_planner_agent.py

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "codellama:instruct"

def plan_command(command):
    prompt = f"""
You are Orion's planner module. Read the user's natural language command and return a JSON object with:
- "agent": one of [file, email, browser, search, calendar, reminder, translate, unknown]
- "info": contains only the extracted values needed for that agent

Respond ONLY in valid JSON format.
DO NOT include any explanation, markdown, or extra text.

Examples:

Command: Translate thank you to Arabic
→ {{"agent": "translate", "info": {{"text": "thank you", "language": "ar"}}}}

Command: Translate good night to French
→ {{"agent": "translate", "info": {{"text": "good night", "language": "fr"}}}}

Command: Schedule project presentation on 2025-06-30 15:00
→ {{"agent": "calendar", "info": {{"event": "project presentation", "datetime": "2025-06-30 15:00"}}}}

Command: Remind me to check oven at 2025-06-24 21:00
→ {{"agent": "reminder", "info": {{"task": "check oven", "datetime": "2025-06-24 21:00"}}}}

Command: \"\"\"{command}\"\"\"
"""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "stop": ["\n\n"]
        })

        result = response.json()["response"]
        print("\n🧪 Raw LLM response:\n", result)

        # 🧼 Clean out unwanted formatting like →, leading text, newlines
        clean = result.strip()
        if "{" in clean:
            clean = clean[clean.index("{"):]  # Start from first '{'
        
        try:
            parsed = json.loads(clean)
            return parsed
        except Exception as e:
            print("❌ JSON parse error:", e)
            return {"agent": "unknown", "info": {}}

    except Exception as e:
        print("❌ Planner error:", e)
        return {"agent": "unknown", "info": {}}
