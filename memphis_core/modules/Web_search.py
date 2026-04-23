"""
web_search.py — Busca na web via DuckDuckGo (gratuito, sem API key)
Usa a biblioteca duckduckgo-search para obter resultados reais.
Também faz scraping leve de páginas para extrair conteúdo relevante.
"""

import re
import urllib.request
import urllib.error
from html.parser import HTMLParser
from ddgs import DDGS

MAX_RESULT = 5
MAX_BODY_CHARS = 600

class _TextExtractor(HTMLParser):
    SKIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "form"}

    def __init__(self):
        super().__init__()
        self._skip = 0
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip += 1
    
    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip == 0:
            text = data.strip()
            if len(text) > 30:
                self.chunks.append(text)

def _fetch_page_text(url: str, max_char: int = MAX_BODY_CHARS) -> str:

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Memphis-IA/1.0)"},
        )

        with urllib.request.urlopen(request, timeout=5) as response:
            raw = response.read(32_000).decode("utf-8", errors="ignore")

        parse = _TextExtractor()
        parse.feed(raw)

        text = " ".join(parse.chunks)
        text = re.sub(r"\s{2,}", " ", text).strip()
        return text[:max_char]
    
    except Exception:
        return ""
    
def _search_ddg(query: str):
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=MAX_RESULT, region="br_pt"))
    
def search(query: str, fetch_content: bool = True) -> list[dict]:
    results = []

    try:
        hits = _search_ddg(query)

        if not hits:
            raise Exception("Sem resultados")
            
    except Exception as e:
        try:
            hits = _search_ddg(query + " especificações detalhes review")
        except Exception as e:
            return [{"error": str(e)}]
    
    for hit in hits:
        entry = {
            "title": hit.get("title", ""),
            "url": hit.get("href", ""),
            "snippet": hit.get("body", ""),
            "body": "",
        }

        if fetch_content and entry["url"]:
            entry["body"] = _fetch_page_text(entry["url"])
        
        results.append(entry)

    return results

def format_for_llm(results: list[dict]) -> str:
    if not results:
        return "Nenhum resultado encontrado."
    
    if "error" in results[0]:
        return f"Erro na busca: {results[0]['error']}"
    
    lines = ["=== Resultados da busca web ===\n"]

    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['title']}")
        lines.append(f"URL: {r['url']}")
        if r["snippet"]:
            lines.append(f"Resumo: {r['snippet']}")
        if r["body"]:
            lines.append(f"Conteúdo: {r['body']}")
        lines.append("")

    lines.append("=== Fim dos resultados ===")
    return "\n".join(lines)