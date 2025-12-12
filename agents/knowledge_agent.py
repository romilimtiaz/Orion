import requests
from utils.memory import load_memory, save_memory

def fetch_web_snippets(query, serpapi_key):
    if not serpapi_key:
        print("❌ SerpAPI key missing; cannot update knowledge.")
        return []
    try:
        resp = requests.get(
            "https://serpapi.com/search.json",
            params={"engine": "google", "q": query, "api_key": serpapi_key},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        snippets = []
        for result in data.get("organic_results", [])[:5]:
            snippet = result.get("snippet")
            if snippet:
                snippets.append(snippet)
        return snippets
    except Exception as e:
        print(f"❌ Knowledge fetch failed: {e}")
        return []


def summarize_snippets(snippets, model, ollama_url):
    if not snippets:
        return ""
    prompt = "Summarize the following web snippets into a concise update (3 bullets max):\n\n"
    prompt += "\n".join(f"- {s}" for s in snippets)
    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        payload = resp.json()
        if "error" in payload:
            print(f"❌ LLM summarize error: {payload['error']}")
            return ""
        return payload.get("response", "").strip()
    except Exception as e:
        print(f"❌ LLM summarize failed: {e}")
        return ""


def update_knowledge(topic, serpapi_key, model, ollama_url="http://127.0.0.1:11434"):
    snippets = fetch_web_snippets(topic, serpapi_key)
    summary = summarize_snippets(snippets, model, ollama_url)
    if not summary:
        return "❌ Could not update knowledge."
    memory = load_memory()
    knowledge = memory.get("knowledge", {})
    knowledge[topic] = summary
    memory["knowledge"] = knowledge
    save_memory(memory)
    return f"📚 Knowledge updated for '{topic}':\n{summary}"
