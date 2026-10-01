from duckduckgo_search import DDGS
from typing import List, Dict

def perform_search(query: str, max_results: int = 3) -> List[Dict]:
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(r)
        return results
    except Exception as e:
        print(f"Web search error: {e}")
        return []
