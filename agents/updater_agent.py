import requests
from agents.knowledge_agent import fetch_web_snippets
from utils.notes import append_note
from utils.tasks import add_task


def _call_llm(model: str, prompt: str, ollama_url: str):
    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=90,
        )
        resp.raise_for_status()
        payload = resp.json()
        if "error" in payload:
            return "", payload["error"]
        return payload.get("response", "").strip(), None
    except Exception as e:
        return "", str(e)


def propose_updates(topic: str, serpapi_key: str, model: str, ollama_url: str, add_tasks_flag: bool = True):
    if not serpapi_key:
        return "❌ SerpAPI key missing; cannot auto-update."

    snippets = fetch_web_snippets(topic, serpapi_key)
    if not snippets:
        return "❌ No snippets fetched; cannot propose updates."

    prompt = (
        "You are an AI product assistant for Orion. Based on these web snippets, propose 3 concrete feature ideas "
        "for Orion with a short action step each. Keep it concise, one line per idea.\n\n"
        + "\n".join(f"- {s}" for s in snippets)
    )
    ideas_text, err = _call_llm(model, prompt, ollama_url)
    if err:
        return f"❌ LLM error: {err}"
    if not ideas_text:
        return "❌ LLM returned no ideas."

    # Save to notes
    append_note("orion_ideas", ideas_text, source="auto-updater")

    # Optionally add tasks
    if add_tasks_flag:
        lines = [ln.strip("-• ").strip() for ln in ideas_text.splitlines() if ln.strip()]
        for ln in lines:
            add_task("research", {"topic": ln})

    return f"🚀 Auto-updater ideas logged:\n{ideas_text}"
