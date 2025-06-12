# Orion: Your Personal AI Assistant 🚀

Orion is an open-source, multi-agent AI assistant built in Python.

You can interact with Orion using natural language commands. It uses:

✅ Local LLM (via [Ollama](https://ollama.com))  
✅ File automation  
✅ Browser automation (via Playwright)  
✅ Modular agent architecture → easy to extend

---

## 🗺️ Current Capabilities

✅ Understand your command using LLM → converts to steps  
✅ Open local files anywhere on your PC  
✅ Open websites automatically  
✅ Perform search queries on Google and YouTube  
✅ Extensible architecture → you can add more agents easily

---

## 💻 How it works


Example flow:

👉 "Go to Google.com and search AI jobs" → Orion opens browser, types query  
👉 "Open RomilImtiaz ACCV.pdf" → Orion finds file and opens it

---

## 🏗️ Project Structure


---

## 🛠️ Installation

1️⃣ Clone this repo:

```bash
git clone project url
cd orion_project
2️⃣ Create conda environment:
conda create -n orion python=3.11
conda activate orion
3️⃣ Install requirements:
ollama pull llama3:8b
ollama serve
4️⃣ Install Ollama:

👉 https://ollama.com/download
👉 Pull model:
ollama pull llama3:8b
ollama serve
🚀 Usage
python main.py
🏗️ Roadmap (Planned)
✅ FileAgent → open files
✅ BrowserAgent → open websites + search
⬜️ BrowserAgent advanced → click buttons, type forms
⬜️ EmailAgent → read/send emails
⬜️ CalendarAgent → manage calendar
⬜️ VoiceAgent → speech input/output
⬜️ MemoryAgent → store preferences, task history
⬜️ GUI → build user-friendly interface

🤝 Contributing
Feel free to fork the project and submit PRs!
This is an open personal learning project — contributions welcome.

Credits
Ollama — local LLM runtime

Playwright — browser automation

Python ❤️

