# agents/search_agent.py

from serpapi import GoogleSearch

def search_google_and_get_snippets(query, api_key=None):
    print(f"🔍 Searching Google for: {query}")

    if not api_key:
        print("❌ SerpAPI key not provided.")
        return []

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key  # ✅ Dynamically passed from main.py
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        print(f"❌ SerpAPI error: {e}")
        return []

    snippets = []

    if "organic_results" in results:
        for result in results["organic_results"][:5]:  # Top 5
            snippet = result.get("snippet", "")
            if snippet:
                snippets.append(snippet)

    return snippets
