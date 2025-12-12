<div align="center">

# 🧠 Orion Assistant

![Orion bot preview](assets/bot_preview.png)

A local-first desktop AI assistant that can plan tasks, browse, search, email, translate, schedule, keep notes, and control your machine — powered by Ollama.

</div>

## What it can do (today)
- Route tasks through multiple agents: file open/search, browser launch + search, Google search (SerpAPI), email (IMAP/SMTP), calendar/reminders, translation, meeting notes/summarization, research, code generation, project scaffolding, Twilio call status/TwiML, and lightweight hardware/system controls.
- Keeps lightweight memory and notes (`orion_memory.json`, `notes/`) so it can reference recent work.
- Optional GUI frontends (e.g., `interactive_bot_gui.py`, `# orion_gui.py`) for a click-to-talk experience.
- Uses local LLMs via Ollama by default; can be pointed at other models through `.env`.

## Prerequisites
- Python 3.10+ (tested on 3.12)
- `virtualenv` installed (`python3 -m pip install --user virtualenv` if needed)
- Ollama running locally (see “Install Ollama” below)
- Optional: SerpAPI key (web search), email app password, Twilio creds for call status, Playwright browsers for headless automation

## Quick start
```bash
git clone https://github.com/yourusername/orion-assistant.git
cd orion-assistant

# Create and activate the virtualenv
python3 -m virtualenv .venv
source .venv/bin/activate

# Install Python deps
pip install -r requirements.txt

# Install Playwright browsers (needed for browser automation)
playwright install

# Copy env template and adjust if desired
cp .env.example .env

# Run (CLI)
python main.py
```

GUI entry points (after activation):
- `python interactive_bot_gui.py`
- `python "# orion_gui.py"` (if you prefer that UI variant)

## Install Ollama (detailed)
1. **Install the daemon**
   - Linux/macOS: `curl -fsSL https://ollama.com/install.sh | sh`
   - Windows: install from https://ollama.com/download or use WSL with the Linux install command.
2. **Start the service** (usually automatic): `ollama serve`
3. **Pull the models Orion expects**  
   ```bash
   ollama pull llama3          # chat + email
   ollama pull codellama:instruct  # router / fallback
   ```
4. **Verify**: `curl http://127.0.0.1:11434/api/tags` should list the pulled models.
5. **Customize models (optional)**: edit `.env` and set `ORION_MODEL_ROUTER`, `ORION_MODEL_CHAT`, `ORION_MODEL_EMAIL`, `ORION_MODEL_FALLBACK`.

## Configuration
- `.env` (optional): model overrides, Gemini keys, auto knowledge topic, hardware controls (see `.env.example`).
- `orion_credentials.json`: stored after first run; the app will prompt for `email`, `password` (app password), and optional `serpapi`.
- `contacts.json`, `notes/`, `tasks.json`, `orion_memory.json`: local data the assistant uses. These are ignored by git to keep secrets out of commits.

## Running & workflow
- Activate the venv: `source .venv/bin/activate`
- Run CLI: `python main.py` and type a command (e.g., “translate hello to Spanish”, “schedule meeting tomorrow 3pm”, “search latest AI papers”).
- Logs/output appear in the terminal; planner debug prints show which agent was chosen.
- For browser automation, ensure Playwright browsers are installed (`playwright install`) and that the script has access to a display (or use xvfb).

## GitHub-ready files
- `assets/bot_preview.png` is the face/preview image referenced above.
- `.gitignore` keeps secrets and local artifacts (env files, credentials, caches, venv) out of commits.

## Troubleshooting
- **Ollama not reachable**: ensure `ollama serve` is running; check `curl http://127.0.0.1:11434/api/generate` with a simple prompt.
- **Playwright missing browsers**: rerun `playwright install`.
- **PortAudio/PyAudio issues**: install system deps (`sudo apt-get install portaudio19-dev` on Debian/Ubuntu).
- **Credential prompts every run**: confirm `orion_credentials.json` is writable and not deleted between runs.
