# main.py

import os
import requests
import json
from agents.llm_planner_agent import plan_command
from agents.file_agent import open_file, global_find_file
from agents.browser_agent import open_website, open_website_and_search
from agents.search_agent import search_google_and_get_snippets
from agents.email_agent import handle_email_instruction
from agents.calendar_agent import schedule_event
from agents.reminder_agent import schedule_reminder, calculate_delay
from agents.translate_agent import translate_text
from agents.knowledge_agent import update_knowledge
from agents.hardware_agent import execute_hardware_action
from agents.system_agent import lock_screen, volume, brightness
from agents.research_agent import research_topic
from agents.meeting_agent import start_meeting, record_note, stop_and_summarize
from agents.paper_agent import search_papers
from agents.scaffold_agent import scaffold_project
from agents.call_agent import set_status as set_call_status, get_status as get_call_status, build_twiml as build_call_twiml
from agents.updater_agent import propose_updates
from utils.credentials import get_or_prompt_credentials
from utils.memory import log_interaction, get_recent_history
from utils.config import load_dotenv, get_model_overrides
from utils.notes import append_note, read_notes, clear_notes
from utils.tasks import add_task, list_tasks, start_worker

OLLAMA_URL = "http://127.0.0.1:11434"
load_dotenv()
MODEL_CONFIG = get_model_overrides({
    "router": "codellama:instruct",
    "chat": "llama3",
    "email": "llama3",
    "fallback": "codellama:instruct",
})


def model_for(key: str) -> str:
    return MODEL_CONFIG.get(key) or MODEL_CONFIG["fallback"]


def is_general_question(command):
    system_prompt = """
You are a classifier. If the user is asking a question like "what can you do?", "who are you?", or "what is your purpose", respond with only: chat.
If it’s an action/task (email, open file, search, translate, reminder, calendar), respond with: task.
Only return one word: chat or task.
"""
    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": model_for("router"),
            "prompt": f"{system_prompt}\nUser: {command}",
            "stream": False
        }, timeout=30)
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            print(f"⚠️ Ollama classify error: {payload['error']}")
            return False
        reply = payload.get("response", "")
        if not reply:
            print("⚠️ Ollama classify missing response; check model and endpoint.")
            return False
        return reply.strip().lower() == "chat"
    except Exception as e:
        print(f"⚠️ Ollama classify failed, defaulting to task: {e}")
        return False


def main_logic(user_command):
    creds = get_or_prompt_credentials()

    ORION_CONFIG = {
        "email": creds["email"],
        "password": creds["password"],
        "serpapi": creds.get("serpapi", "")
    }

    # Optional auto knowledge update on startup (triggered by env)
    auto_topic = os.environ.get("ORION_AUTO_UPDATE_TOPIC")
    if auto_topic:
        summary = update_knowledge(auto_topic, ORION_CONFIG["serpapi"], model_for("chat"))
        print(summary)

    # Start simple task worker (runs pending once per invocation)
    def task_handler(task):
        ttype = task.get("type")
        payload = task.get("payload", {})
        if ttype == "knowledge":
            topic = payload.get("topic", "general")
            return update_knowledge(topic, ORION_CONFIG["serpapi"], model_for("chat"))
        if ttype == "research":
            topic = payload.get("topic", "general")
            return research_topic(topic, ORION_CONFIG["serpapi"], model_for("chat"))
        return f"❌ Unknown task type: {ttype}"

    start_worker(task_handler)

    # 💬 General chat fallback
    if is_general_question(user_command):
        chat_prompt = f"You are Orion, a personal AI assistant. The user said: {user_command}\nReply helpfully."
        try:
            response = requests.post(f"{OLLAMA_URL}/api/generate", json={
                "model": model_for("chat"),
                "prompt": chat_prompt,
                "stream": False
            }, timeout=60)
            response.raise_for_status()
            payload = response.json()
            if "error" in payload:
                return f"⚠️ Ollama chat error: {payload['error']}"
            reply = payload.get("response", "")
            return f"🤖 {reply}" if reply else "⚠️ Ollama returned no reply."
        except Exception as e:
            return f"⚠️ Ollama chat failed: {e}"

    # 🧠 Intelligent planner routing
    output = "🧠 Thinking with Ollama...\n\n"
    history = get_recent_history()
    plan = plan_command(user_command, model=model_for("router"), history=history)

    # 🔍 Debug print
    print(f"📦 Planner output: {plan}")

    agent = plan.get("agent")
    info = plan.get("info", {})
    print(f"🧠 Detected agent: {agent}")

    # === FILE AGENT ===
    if agent == "file":
        filename = info.get("filename")
        if filename:
            from pathlib import Path
            file_path = global_find_file(Path.home(), filename)
            open_file(file_path)
            output += f"📂 Opened file: {file_path}"
        else:
            output += "❌ No filename found."

    # === BROWSER AGENT ===
    elif agent == "browser":
        url = info.get("url")
        search = info.get("search")
        if url and search:
            open_website_and_search(url, search)
            output += f"🌐 Opened {url} and searched for {search}"
        elif url:
            open_website(url)
            output += f"🌐 Opened {url}"
        else:
            output += "❌ No URL found."

    # === SEARCH AGENT ===
    elif agent == "search":
        query = info.get("query")
        if query:
            snippets = search_google_and_get_snippets(query, ORION_CONFIG["serpapi"])
            output += "🔎 Top info found:\n\n"
            for i, s in enumerate(snippets, 1):
                output += f"{i}. {s}\n"
        else:
            output += "❌ No query provided."

    # === EMAIL AGENT ===
    elif agent == "email":
        result = handle_email_instruction(
            user_command,
            ORION_CONFIG["email"],
            ORION_CONFIG["password"],
            planner_model=model_for("router"),
            email_model=model_for("email"),
        )
        output += result or "📧 Email processed."

    # === CALENDAR AGENT ===
    elif agent == "calendar":
        event = info.get("event")
        datetime_str = info.get("datetime")
        if event and datetime_str:
            result = schedule_event(event, datetime_str)
            output += result
        else:
            output += "❌ Missing event name or datetime."

    # === REMINDER AGENT ===
    elif agent == "reminder":
        task = info.get("task")
        datetime_str = info.get("datetime")
        delay = calculate_delay(datetime_str)
        if delay > 0:
            result = schedule_reminder(task, delay)
            output += result
        else:
            output += "❌ Invalid or past reminder time."

    # === TRANSLATE AGENT ===
    elif agent == "translate":
        text = info.get("text")
        lang = info.get("language")
        if text and lang:
            result = translate_text(text, lang)
            output += result
        else:
            output += "❌ Missing translation text or language."

    # === KNOWLEDGE UPDATE AGENT ===
    elif agent == "knowledge":
        topic = info.get("topic") or user_command
        result = update_knowledge(topic, ORION_CONFIG["serpapi"], model_for("chat"))
        output += result

    # === HARDWARE AGENT ===
    elif agent == "hardware":
        action = info.get("action")
        if action:
            result = execute_hardware_action(action)
            output += result
        else:
            output += "❌ No hardware action specified."

    # === SYSTEM AGENT ===
    elif agent == "system":
        action = info.get("action")
        if action == "lock":
            output += lock_screen()
        elif action == "volume":
            direction = info.get("direction", "up")
            output += volume(direction)
        elif action == "brightness":
            direction = info.get("direction", "up")
            output += brightness(direction)
        else:
            output += "❌ Unknown system action."

    # === MEETING AGENT ===
    elif agent == "meeting":
        action = info.get("action", "").lower()
        if action == "start":
            topic = info.get("topic") or "meeting"
            output += start_meeting(topic)
        elif action == "add":
            content = info.get("content") or user_command
            output += record_note(content)
        elif action == "stop":
            output += stop_and_summarize(model_for("chat"), OLLAMA_URL, context="work meeting")
        else:
            output += "❌ Meeting action must be start/add/stop."

    # === PAPERS AGENT ===
    elif agent == "papers":
        topic = info.get("topic") or user_command
        papers = search_papers(topic)
        if not papers:
            output += "❌ No papers found or fetch failed."
        else:
            output += f"📚 Top papers for '{topic}':\n\n"
            for i, p in enumerate(papers, 1):
                authors = ", ".join(p.get("authors", []))
                output += f"{i}. {p.get('title','')}\n   Authors: {authors}\n   Link: {p.get('link','')}\n"

    # === CODE AGENT ===
    elif agent == "code":
        prompt = info.get("prompt") or user_command
        system_prompt = (
            "You are Orion's coding copilot. Produce concise, well-formatted code with minimal explanation. "
            "If code is long, focus on the core function. Include short comments only if they clarify intent."
        )
        try:
            resp = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model_for("chat"),
                    "prompt": f"{system_prompt}\n\nRequest: {prompt}\n\nAnswer:",
                    "stream": False,
                },
                timeout=90,
            )
            resp.raise_for_status()
            payload = resp.json()
            if "error" in payload:
                output += f"⚠️ Code generation error: {payload['error']}"
            else:
                code = payload.get("response", "").strip()
                output += code or "⚠️ Code generation returned empty."
        except Exception as e:
            output += f"⚠️ Code generation failed: {e}"

    # === SCAFFOLD AGENT ===
    elif agent == "scaffold":
        project = info.get("project") or "Project"
        template = info.get("template") or "opencv_face_tracker"
        desc = info.get("description") or user_command
        result = scaffold_project(project, desc, template)
        output += result

    # === CALL AGENT ===
    elif agent == "call":
        action = info.get("action", "set")
        if action == "set":
            message = info.get("message") or user_command
            status = set_call_status(message)
            output += f"📞 Call status set: {status['message']}"
        elif action == "get":
            status = get_call_status()
            output += f"📞 Current call status: {status['message']}"
        elif action == "twiml":
            caller = info.get("caller")
            output += build_call_twiml(caller)
        else:
            output += "❌ Unknown call action."

    # === TASK MANAGEMENT ===
    elif agent == "task_list":
        tasks = list_tasks()
        output += "🗒️ Tasks:\n" + json.dumps(tasks, indent=2)

    elif agent == "task_add":
        topic = info.get("topic") or "general"
        ttype = info.get("type") or "research"
        task = add_task(ttype, {"topic": topic})
        output += f"🆕 Task queued: {task['id']} ({ttype}) on '{topic}'"

    # === NOTES MANAGEMENT ===
    elif agent == "notes_read":
        topic = info.get("topic") or "general"
        output += read_notes(topic)
    elif agent == "notes_clear":
        topic = info.get("topic") or "general"
        output += clear_notes(topic)
    elif agent == "notes_add":
        topic = info.get("topic") or "general"
        content = info.get("content") or user_command
        output += append_note(topic, content, source="user")

    # === UPDATER AGENT ===
    elif agent == "updater":
        topic = info.get("topic") or "AI assistant new features"
        result = propose_updates(topic, ORION_CONFIG["serpapi"], model_for("chat"), OLLAMA_URL)
        output += result

    # === UNKNOWN AGENT ===
    else:
        output += f"🤷 I couldn't understand what to do with your command.\n[DEBUG] Agent: {agent}"

    # 🧠 Auto-updater: log recent interaction for lightweight learning
    snippet = output[:200]
    log_interaction(user_command, agent or "unknown", snippet)

    return output


if __name__ == "__main__":
    print("Welcome to Orion 🦾")
    user_command = input("Enter your command: ")
    result = main_logic(user_command)
    print(result)
