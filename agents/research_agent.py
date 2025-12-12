import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from utils.notes import append_note


def fetch_page(url, timeout=10):
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Orion/1.0"})
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"❌ Fetch failed for {url}: {e}")
        return ""


def extract_main_text(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    # remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    text = "\n".join(p for p in paragraphs if p)
    return text[:8000]  # keep concise


def summarize_sources(topic, urls, model, ollama_url="http://127.0.0.1:11434"):
    texts = []
    for url in urls[:3]:
        html = fetch_page(url)
        text = extract_main_text(html)
        if text:
            host = urlparse(url).netloc
            texts.append(f"[{host}] {text}")
    if not texts:
        return "❌ No content to summarize."
    prompt = f"Summarize the key points about '{topic}' from the sources below. Provide 3-5 concise bullets with source tags in brackets.\n\n" + "\n\n".join(texts)
    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=90,
        )
        resp.raise_for_status()
        payload = resp.json()
        if "error" in payload:
            return f"❌ LLM summarize error: {payload['error']}"
        return payload.get("response", "").strip() or "❌ Empty summary."
    except Exception as e:
        return f"❌ Summarization failed: {e}"


def research_topic(topic, serpapi_key, model, ollama_url="http://127.0.0.1:11434"):
    from agents.knowledge_agent import fetch_web_snippets  # reuse
    snippets = fetch_web_snippets(topic, serpapi_key)
    urls = []
    try:
        resp = requests.get(
            "https://serpapi.com/search.json",
            params={"engine": "google", "q": topic, "api_key": serpapi_key},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        for res in data.get("organic_results", [])[:3]:
            link = res.get("link")
            if link:
                urls.append(link)
    except Exception as e:
        print(f"❌ SerpAPI URL fetch failed: {e}")

    summary = summarize_sources(topic, urls, model, ollama_url)
    if summary and not summary.startswith("❌"):
        append_note(topic, summary, source="web research")
    return summary
