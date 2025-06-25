# main.py

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
from utils.credentials import get_or_prompt_credentials


def is_general_question(command):
    system_prompt = """
You are a classifier. If the user is asking a question like "what can you do?", "who are you?", or "what is your purpose", respond with only: chat.
If it’s an action/task (email, open file, search, translate, reminder, calendar), respond with: task.
Only return one word: chat or task.
"""
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "codellama:instruct",
        "prompt": f"{system_prompt}\nUser: {command}",
        "stream": False
    })
    return response.json()["response"].strip().lower() == "chat"


def main_logic(user_command):
    creds = get_or_prompt_credentials()

    ORION_CONFIG = {
        "email": creds["email"],
        "password": creds["password"],
        "serpapi": creds.get("serpapi", "")
    }

    # 💬 General chat fallback
    if is_general_question(user_command):
        chat_prompt = f"You are Orion, a personal AI assistant. The user said: {user_command}\nReply helpfully."
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "codellama:instruct",
            "prompt": chat_prompt,
            "stream": False
        })
        reply = response.json()["response"]
        return f"🤖 {reply}"

    # 🧠 Intelligent planner routing
    output = "🧠 Thinking with Ollama...\n\n"
    plan = plan_command(user_command)

    # 🔍 Debug print
    print(f"📦 Planner output: {plan}")

    agent = plan.get("agent")
    info = plan.get("info", {})
    print(f"🧠 Detected agent: {agent}")

    # === FILE AGENT ===
    if agent == "file":
        filename = info.get("filename")
        if filename:
            file_path = global_find_file("C:\\", filename)
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
        result = handle_email_instruction(user_command, ORION_CONFIG["email"], ORION_CONFIG["password"])
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

    # === UNKNOWN AGENT ===
    else:
        output += f"🤷 I couldn't understand what to do with your command.\n[DEBUG] Agent: {agent}"

    return output


if __name__ == "__main__":
    print("Welcome to Orion 🦾")
    user_command = input("Enter your command: ")
    result = main_logic(user_command)
    print(result)
