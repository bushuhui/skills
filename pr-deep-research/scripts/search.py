#!/usr/bin/env python3
"""Deep search via DuckDuckGo HTML (no API key needed, proxy-friendly)."""

import sys
import json
import os
import re
import argparse
import time
from urllib.parse import unquote, urlparse, parse_qs

import requests
from html.parser import HTMLParser

PROXY_URL = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or os.environ.get("ALL_PROXY")
PROXIES = {"https": PROXY_URL, "http": PROXY_URL} if PROXY_URL else None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
}


def _extract_url(raw: str) -> str:
    """Extract real URL from DuckDuckGo redirect."""
    if "uddg=" in raw:
        m = re.search(r'uddg=([^&]+)', raw)
        if m:
            return unquote(m.group(1))
    return raw.lstrip("/")


def _strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r'<.*?>', '', text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#x27;", "'").replace("&nbsp;", " ")
    return text.strip()


def search_ddg(query: str, max_results: int = 10) -> list[dict]:
    """Search DuckDuckGo HTML version."""
    results = []
    try:
        r = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=HEADERS,
            proxies=PROXIES,
            timeout=15,
        )
        r.raise_for_status()
        html = r.text

        # Extract links, titles, snippets
        links = re.findall(r'class="result__a"\s+href="(.*?)"', html)
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
        snippets = re.findall(r'class="result__snippet">(.*?)</(?:span|td)', html, re.DOTALL)

        for i in range(min(max_results, len(links))):
            url = _extract_url(links[i])
            title = _strip_html(titles[i]) if i < len(titles) else ""
            snippet = _strip_html(snippets[i]) if i < len(snippets) else ""
            if url and not url.startswith("//duckduckgo"):
                results.append({"title": title, "href": url, "body": snippet})
    except Exception as e:
        return [{"error": str(e)}]
    return results


def search_ddg_news(query: str, max_results: int = 10) -> list[dict]:
    """Search DuckDuckGo News via HTML."""
    results = []
    try:
        r = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query, "iar": "news", "ia": "news"},
            headers=HEADERS,
            proxies=PROXIES,
            timeout=15,
        )
        r.raise_for_status()
        html = r.text

        links = re.findall(r'class="result__a"\s+href="(.*?)"', html)
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
        snippets = re.findall(r'class="result__snippet">(.*?)</(?:span|td)', html, re.DOTALL)

        for i in range(min(max_results, len(links))):
            url = _extract_url(links[i])
            title = _strip_html(titles[i]) if i < len(titles) else ""
            snippet = _strip_html(snippets[i]) if i < len(snippets) else ""
            if url and not url.startswith("//duckduckgo"):
                results.append({"title": title, "href": url, "body": snippet})
    except Exception as e:
        return [{"error": str(e)}]
    return results


def main():
    parser = argparse.ArgumentParser(description="Deep search via DuckDuckGo HTML")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--max-results", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--news", action="store_true", help="Search news")
    parser.add_argument("--queries", nargs="+", help="Multiple queries (batch mode)")
    args = parser.parse_args()

    all_results = {}
    queries = args.queries if args.queries else [args.query]
    search_fn = search_ddg_news if args.news else search_ddg

    for i, q in enumerate(queries):
        if i > 0:
            time.sleep(1)  # Rate limit between queries
        try:
            results = search_fn(q, max_results=args.max_results)
            all_results[q] = results
        except Exception as e:
            all_results[q] = [{"error": str(e)}]

    if len(all_results) == 1:
        print(json.dumps(list(all_results.values())[0], ensure_ascii=False, indent=2))
    else:
        print(json.dumps(all_results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
