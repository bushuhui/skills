#!/usr/bin/env python3
"""Brave Search API wrapper — web search & news search."""

import sys
import json
import os
import argparse
import time

import requests

API_KEY = os.environ.get("BRAVE_API_KEY", "")
BASE_URL = "https://api.search.brave.com/res/v1"
PROXY_URL = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or os.environ.get("ALL_PROXY")
PROXIES = {"https": PROXY_URL, "http": PROXY_URL} if PROXY_URL else None

HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "X-Subscription-Token": API_KEY,
}


def search_web(query: str, count: int = 10, offset: int = 0, freshness: str = None, country: str = None) -> list[dict]:
    """Brave Web Search API."""
    params = {"q": query, "count": min(count, 20)}
    if offset:
        params["offset"] = offset
    if freshness:
        params["freshness"] = freshness  # pd (past day), pw (past week), pm (past month), py (past year)
    if country:
        params["country"] = country
    try:
        r = requests.get(f"{BASE_URL}/web/search", headers=HEADERS, params=params, proxies=PROXIES, timeout=15)
        r.raise_for_status()
        data = r.json()
        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "href": item.get("url", ""),
                "body": item.get("description", ""),
                "age": item.get("age", ""),
            })
        return results
    except requests.exceptions.HTTPError as e:
        return [{"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}]
    except Exception as e:
        return [{"error": str(e)}]


def search_news(query: str, count: int = 10, freshness: str = None, country: str = None) -> list[dict]:
    """Brave News Search API."""
    params = {"q": query, "count": min(count, 20)}
    if freshness:
        params["freshness"] = freshness
    if country:
        params["country"] = country
    try:
        r = requests.get(f"{BASE_URL}/news/search", headers=HEADERS, params=params, proxies=PROXIES, timeout=15)
        r.raise_for_status()
        data = r.json()
        results = []
        for item in data.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "href": item.get("url", ""),
                "body": item.get("description", ""),
                "age": item.get("age", ""),
            })
        return results
    except requests.exceptions.HTTPError as e:
        return [{"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}]
    except Exception as e:
        return [{"error": str(e)}]


def main():
    parser = argparse.ArgumentParser(description="Brave Search API")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--count", type=int, default=10, help="Max results per query (max 20)")
    parser.add_argument("--news", action="store_true", help="Search news instead of web")
    parser.add_argument("--freshness", choices=["pd", "pw", "pm", "py"], help="Time filter: pd=day, pw=week, pm=month, py=year")
    parser.add_argument("--country", help="Country code (e.g. CN, US, JP)")
    parser.add_argument("--queries", nargs="+", help="Multiple queries (batch mode)")
    parser.add_argument("--offset", type=int, default=0, help="Result offset for pagination")
    args = parser.parse_args()

    if not API_KEY:
        print(json.dumps([{"error": "BRAVE_API_KEY not set"}]))
        sys.exit(1)

    queries = args.queries if args.queries else [args.query]
    search_fn = search_news if args.news else search_web
    all_results = {}

    for i, q in enumerate(queries):
        if i > 0:
            time.sleep(0.5)
        kwargs = {"query": q, "count": args.count}
        if args.freshness:
            kwargs["freshness"] = args.freshness
        if args.country:
            kwargs["country"] = args.country
        if not args.news and args.offset:
            kwargs["offset"] = args.offset
        all_results[q] = search_fn(**kwargs)

    if len(all_results) == 1:
        print(json.dumps(list(all_results.values())[0], ensure_ascii=False, indent=2))
    else:
        print(json.dumps(all_results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
