# 🧠 Orion Assistant

**Orion** is a desktop-based intelligent voice and text assistant, inspired by Iron Man's JARVIS. It can understand natural language commands, automate everyday tasks like sending emails, opening files, performing web searches, scheduling reminders, translating text, and more — all powered by local LLMs (like Ollama).

---

## 🚀 Features

- 🎤 **Voice command support** via microphone (click-to-speak)
- 💬 **Natural language input** using powerful LLM planning
- 📂 Open files by name from any folder
- 📧 Compose and send professional emails using AI
- 🌐 Perform smart Google searches
- 🌍 Translate phrases into multiple languages
- 📅 Schedule calendar events and reminders
- 🧠 Memory module (remembers contacts, tasks)
- 🖥️ Jarvis-style GUI built with `tkinter`
- 🧩 Modular agent design: add your own skills easily!

---


## 🛠️ Tech Stack

- `Python 3.10+`
- `Tkinter` for desktop UI
- `speech_recognition` for voice input
- `Ollama` with `llama3` / `codellama` for command planning
- `SerpAPI` for Google search results
- `smtplib` + `imaplib` for email read/write
- `googletrans` for translation
- `ics` for calendar integration

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/orion-assistant.git
cd orion-assistant

# Create and activate virtual environment
conda create -n orion python=3.10
conda activate orion

# Install dependencies
pip install -r requirements.txt
