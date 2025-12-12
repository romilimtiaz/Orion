# agents/search_agent.py

import requests

def search_google_and_get_snippets(query, api_key=None):
    print(f"🔍 Searching Google for: {query}")

    if not api_key:
        print("❌ SerpAPI key not provided.")
        return []

    try:
        response = requests.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google",
                "q": query,
                "api_key": api_key,
            },
            timeout=15,
        )
        response.raise_for_status()
        results = response.json()
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
