# 🧠 Orion Assistant (Work in Progress)

**Orion** is a personal desktop AI assistant inspired by JARVIS from Iron Man — but built entirely in Python using local tools.  
I’m actively working on this project to create a real-time, voice-aware assistant that can understand natural commands and automate day-to-day tasks.

---

## 🔧 Status

🚧 **This project is under active development**  
I'm continuously adding features like voice control, task memory, translation, scheduling, and natural conversation.

---

## 🎯 What Orion Can (or Will) Do

- ✅ Open files from anywhere on your PC
- ✅ Search the web or specific websites
- ✅ Send and reply to emails professionally
- ✅ Translate text into other languages
- ✅ Create reminders and calendar events
- ✅ Understand voice input (click-to-talk)
- ✅ Plan commands using LLM (via Ollama)
- 🔜 Wake-word activation (e.g. “Orion”)
- 🔜 Voice output (TTS)

---

## 🛠️ Stack & Tools

- `Python 3.10+`
- `Tkinter` for GUI
- `Ollama` with LLMs like `llama3`, `codellama`
- `speech_recognition` for voice input
- `SerpAPI` for smart web search
- `smtplib` / `imaplib` for email
- `googletrans` for translation
- `ics` for calendar integration
- `json` for memory + credentials

---

## 📦 Install & Run

```bash
git clone https://github.com/yourusername/orion-assistant.git
cd orion-assistant

conda create -n orion python=3.10
conda activate orion

pip install -r requirements.txt
