import requests
import xml.etree.ElementTree as ET

ARXIV_API = "http://export.arxiv.org/api/query"

def search_papers(query: str, max_results: int = 5):
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    try:
        resp = requests.get(ARXIV_API, params=params, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ ArXiv request failed: {e}")
        return []

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as e:
        print(f"❌ ArXiv parse failed: {e}")
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    papers = []
    for entry in root.findall("atom:entry", ns)[:max_results]:
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
        link = ""
        for l in entry.findall("atom:link", ns):
            if l.attrib.get("type") == "text/html":
                link = l.attrib.get("href", "")
                break
        authors = [a.findtext("atom:name", default="", namespaces=ns) or "" for a in entry.findall("atom:author", ns)]
        papers.append({
            "title": title,
            "summary": summary,
            "link": link,
            "authors": [a for a in authors if a],
        })
    return papers
