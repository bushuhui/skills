#!/usr/bin/env python3
"""
Fetch Andrej Karpathy's curated RSS feeds and output JSON.
Sources:
  - Karpathy's personal blog: https://karpathy.github.io/feed.xml
  - OpenAI blog: https://openai.com/blog/rss.xml
  - Anthropic news: https://www.anthropic.com/news/rss.xml
  - Hugging Face blog: https://huggingface.co/blog/feed.xml
  - arXiv AI/ML (cs.CL, cs.LG, cs.AI): http://export.arxiv.org/api/rss?search_query=cat:cs.CL+OR+cat:cs.LG+OR+cat:cs.AI
Outputs JSON to stdout with articles from the past N hours (default 24, via CLI arg).
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree

import urllib.request
from urllib.request import ProxyHandler, build_opener, Request, urlopen
from urllib.error import URLError

RSS_URL = "https://youmind.com/rss/pack/andrej-karpathy-curated-rss"

FEEDS = [
    {"name": "Karpathy Blog", "url": "https://karpathy.github.io/feed.xml"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
    {"name": "Anthropic News", "url": "https://www.anthropic.com/news/rss.xml"},
    {"name": "HuggingFace Blog", "url": "https://huggingface.co/blog/feed.xml"},
]

ARXIV_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.CL+OR+cat:cs.LG+OR+cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=20"

HOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 24

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}

DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%a, %d %b %Y %H:%M:%S %z",
    "%Y-%m-%d %H:%M:%S",
]


def get_proxy():
    """Get proxy URL from environment or default."""
    return os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or "http://127.0.0.1:7890"


def fetch_url(url, timeout=30):
    """Fetch URL content with proxy support and error handling."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; KarpathyRSSBot/1.0)"}
    proxy = get_proxy()
    try:
        opener = build_opener(ProxyHandler({"https": proxy, "http": proxy}))
        req = Request(url, headers=headers)
        return opener.open(req, timeout=timeout).read().decode("utf-8", errors="replace")
    except Exception:
        pass
    # Fallback: direct connection
    try:
        req = Request(url, headers=headers)
        return urlopen(req, timeout=timeout).read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[WARN] Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities, collapse whitespace."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_date(s: str) -> datetime:
    """Try multiple date formats; return None if all fail."""
    s = s.replace("Z", "+00:00")
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def find_text(entry, path, ns):
    """Safely find element text in XML."""
    el = entry.find(path, ns)
    return el.text.strip() if el is not None and el.text else ""


def parse_atom(xml_str, feed_name):
    """Parse Atom XML feed."""
    articles = []
    try:
        root = ElementTree.fromstring(xml_str)
        for entry in root.findall("atom:entry", ATOM_NS):
            title = find_text(entry, "atom:title", ATOM_NS)
            link_el = entry.find("atom:link[@rel='alternate']", ATOM_NS)
            if link_el is None:
                link_el = entry.find("atom:link", ATOM_NS)
            link = link_el.get("href", "") if link_el is not None else ""
            summary = find_text(entry, "atom:summary", ATOM_NS)
            if not summary:
                summary = find_text(entry, "atom:content", ATOM_NS)
            published = find_text(entry, "atom:published", ATOM_NS)
            if not published:
                published = find_text(entry, "atom:updated", ATOM_NS)
            author = find_text(entry, "atom:author/atom:name", ATOM_NS)

            summary = strip_html(summary)

            articles.append({
                "title": title,
                "link": link,
                "summary": summary[:500],
                "published": published,
                "author": author,
                "source": feed_name,
            })
    except Exception as e:
        print(f"[WARN] Failed to parse {feed_name}: {e}", file=sys.stderr)
    return articles


def parse_arxiv(xml_str):
    """Parse arXiv Atom feed."""
    articles = []
    try:
        root = ElementTree.fromstring(xml_str)
        for entry in root.findall("atom:entry", ARXIV_NS):
            title = find_text(entry, "atom:title", ARXIV_NS).replace("\n", " ").replace("  ", " ")
            summary = find_text(entry, "atom:summary", ARXIV_NS).replace("\n", " ").replace("  ", " ")
            published = find_text(entry, "atom:published", ARXIV_NS)
            link_el = entry.find("atom:link[@type='text/html']", ARXIV_NS)
            if link_el is None:
                link_el = entry.find("atom:link[@rel='alternate']", ARXIV_NS)
            if link_el is None:
                link_el = entry.find("atom:link", ARXIV_NS)
            link = link_el.get("href", "") if link_el is not None else ""

            summary = strip_html(summary)

            articles.append({
                "title": title,
                "link": link,
                "summary": summary[:500],
                "published": published,
                "author": "arXiv",
                "source": "arXiv (cs.CL/LG/AI)",
            })
    except Exception as e:
        print(f"[WARN] Failed to parse arXiv: {e}", file=sys.stderr)
    return articles


def filter_recent(articles, hours=24):
    """Filter articles published within the last N hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    filtered = []
    for art in articles:
        pub = art.get("published", "")
        if not pub:
            filtered.append(art)
            continue
        dt = parse_date(pub)
        if dt is None:
            filtered.append(art)
            continue
        if dt >= cutoff:
            filtered.append(art)
    return filtered


def deduplicate(articles):
    """Remove duplicates by title similarity."""
    seen = set()
    unique = []
    for art in articles:
        key = art["title"].lower().strip()[:80]
        if key not in seen:
            seen.add(key)
            unique.append(art)
    return unique


def main():
    all_articles = []

    # Fetch youmind RSS pack (single source, Atom format)
    print(f"[INFO] Fetching Karpack RSS ({RSS_URL})...", file=sys.stderr)
    content = fetch_url(RSS_URL)
    if content:
        articles = parse_atom(content, "Karpack")
        all_articles.extend(articles)
        print(f"[INFO]   Got {len(articles)} articles from Karpack", file=sys.stderr)

    # Fetch individual feeds
    for feed in FEEDS:
        print(f"[INFO] Fetching {feed['name']}...", file=sys.stderr)
        content = fetch_url(feed["url"])
        if content:
            articles = parse_atom(content, feed["name"])
            all_articles.extend(articles)
            print(f"[INFO]   Got {len(articles)} articles from {feed['name']}", file=sys.stderr)

    # Fetch arXiv
    print(f"[INFO] Fetching arXiv...", file=sys.stderr)
    content = fetch_url(ARXIV_URL)
    if content:
        articles = parse_arxiv(content)
        all_articles.extend(articles)
        print(f"[INFO]   Got {len(articles)} articles from arXiv", file=sys.stderr)

    # Filter and deduplicate
    recent = filter_recent(all_articles, hours=HOURS)
    unique = deduplicate(recent)

    result = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "hours_window": HOURS,
        "total_found": len(all_articles),
        "recent_count": len(unique),
        "articles": unique,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n# Total: {len(unique)} entries in last {HOURS}h", file=sys.stderr)


if __name__ == "__main__":
    main()
