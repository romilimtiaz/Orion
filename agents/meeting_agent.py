import time
import requests
from utils.notes import append_note

MEETING_STATE = {
    "active": False,
    "topic": "",
    "log": [],
    "started_at": None,
}


def start_meeting(topic: str):
    MEETING_STATE["active"] = True
    MEETING_STATE["topic"] = topic or "meeting"
    MEETING_STATE["log"] = []
    MEETING_STATE["started_at"] = time.time()
    return f"🟢 Recording meeting on '{MEETING_STATE['topic']}'. Say 'stop meeting' when done."


def record_note(text: str):
    if not MEETING_STATE.get("active"):
        return "❌ No active meeting. Say 'start meeting about <topic>'."
    MEETING_STATE["log"].append(text)
    return f"📝 Captured: {text}"


def stop_and_summarize(model: str, ollama_url: str, context: str = ""):
    if not MEETING_STATE.get("active"):
        return "❌ No active meeting to stop."
    topic = MEETING_STATE.get("topic", "meeting")
    transcript = "\n".join(MEETING_STATE.get("log", []))
    MEETING_STATE["active"] = False
    MEETING_STATE["started_at"] = None

    if not transcript.strip():
        return "⚠️ Meeting ended, but no notes were captured."

    prompt = f"Summarize this meeting for work follow-up. Provide 3-7 bullets with action items if present.\nContext: {context}\nTopic: {topic}\nTranscript:\n{transcript}"
    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=90,
        )
        resp.raise_for_status()
        payload = resp.json()
        if "error" in payload:
            return f"❌ Summarization error: {payload['error']}"
        summary = payload.get("response", "").strip()
    except Exception as e:
        return f"❌ Summarization failed: {e}"

    if summary:
        append_note(topic, summary, source="meeting")
        return f"🛑 Meeting ended.\n📄 Summary:\n{summary}"
    return "⚠️ Meeting ended, but summary was empty."
