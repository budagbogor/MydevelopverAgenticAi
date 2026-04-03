from duckduckgo_search import DDGS
import json

class WebSearch:
    def __init__(self):
        self.ddgs = DDGS()

    def search_query(self, query, max_results=5):
        """Mencari informasi di web dan mengembalikan snippet teks."""
        try:
            print(f"🔍 Searching: {query}...")
            results = self.ddgs.text(query, max_results=max_results)
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "title": r.get('title'),
                    "link": r.get('href'),
                    "snippet": r.get('body')
                })
            return formatted_results
        except Exception as e:
            print(f"❌ Search Error: {e}")
            return []

    def get_formatted_string(self, query, max_results=3):
        """Mengembalikan hasil pencarian dalam bentuk string untuk LLM."""
        results = self.search_query(query, max_results)
        if not results:
            return "Tidak ditemukan hasil pencarian."
        
        output = f"HASIL PENCARIAN UNTUK: '{query}'\n"
        for i, r in enumerate(results, 1):
            output += f"{i}. {r['title']}\n   Link: {r['link']}\n   Snippet: {r['snippet']}\n\n"
        return output

if __name__ == "__main__":
    s = WebSearch()
    print(s.get_formatted_string("React latest version 2026"))
