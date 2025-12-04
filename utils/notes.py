import os
import json
from pathlib import Path
from datetime import datetime

NOTES_DIR = Path("notes")
NOTES_DIR.mkdir(exist_ok=True)

def _topic_path(topic: str) -> Path:
    safe = "".join(c for c in topic if c.isalnum() or c in (" ", "_", "-")).strip()
    if not safe:
        safe = "untitled"
    return NOTES_DIR / f"{safe}.md"


def append_note(topic: str, content: str, source: str = ""):
    path = _topic_path(topic)
    ts = datetime.utcnow().isoformat()
    header = f"\n\n## {ts} UTC"
    if source:
        header += f" | source: {source}"
    text = f"{header}\n{content.strip()}\n"
    path.write_text(path.read_text() + text if path.exists() else f"# {topic}\n{text}")
    return f"📝 Note saved to {path}"


def read_notes(topic: str, limit: int = 5):
    path = _topic_path(topic)
    if not path.exists():
        return f"❌ No notes found for '{topic}'."
    lines = path.read_text().splitlines()
    # return last N sections
    sections = []
    current = []
    for line in lines:
        if line.startswith("## "):
            if current:
                sections.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current))
    snippet = "\n\n".join(sections[-limit:])
    return snippet or f"❌ Notes empty for '{topic}'."


def clear_notes(topic: str):
    path = _topic_path(topic)
    if path.exists():
        path.unlink()
        return f"🗑️ Cleared notes for '{topic}'."
    return f"❌ No notes found for '{topic}'."
