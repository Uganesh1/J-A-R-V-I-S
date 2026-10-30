import requests
from bs4 import BeautifulSoup
from utils.network_checker import is_online

class WebSearch:
    def search(self, query: str):
        if not is_online():
            return "Internet is unavailable. Online search requires a connection."
        try:
            # DuckDuckGo HTML endpoint — no API key required, respects rate limits
            r = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "JARVIS/1.0 (local assistant)"},
                timeout=8
            )
            soup = BeautifulSoup(r.text, "html.parser")
            results = []
            for item in soup.select(".result")[:5]:
                title = item.select_one(".result__title")
                snippet = item.select_one(".result__snippet")
                if title:
                    results.append(f"- {title.get_text(strip=True)}: {snippet.get_text(strip=True) if snippet else ''}")
            return "\n".join(results) if results else "No results found."
        except Exception as e:
            return f"Search failed: {e}"