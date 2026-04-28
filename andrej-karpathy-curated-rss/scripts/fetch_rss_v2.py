#!/usr/bin/env python3
"""
Fetch Andrej Karpathy's curated RSS feeds and output JSON.
Sources:
  - Karpathy's personal blog: https://karpathy.github.io/feed.xml
  - OpenAI blog: https://openai.com/blog/rss.xml
  - Anthropic news: https://www.anthropic.com/news/rss.xml
  - Hugging Face blog: https://huggingface.co/blog/feed.xml
  - arXiv AI/ML (cs.CL, cs.LG, cs.AI): http://export.arxiv.org/api/rss?search_query=cat:cs.CL+OR+cat:cs.LG+OR+cat:cs.AI
Outputs JSON to stdout with articles from the past 24 hours.
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree

import urllib.request
import urllib.parse

# Disable proxy for direct connections
os.environ['no_proxy'] = '*'
os.environ['NO_PROXY'] = '*'

FEEDS = [
    {
        "name": "Karpathy Blog",
        "url": "https://karpathy.github.io/feed.xml",
        "link_prefix": "",
    },
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "link_prefix": "",
    },
    {
        "name": "Anthropic News",
        "url": "https://www.anthropic.com/news/rss.xml",
        "link_prefix": "",
    },
    {
        "name": "HuggingFace Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "link_prefix": "",
    },
]

ARXIV_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.CL+OR+cat:cs.LG+OR+cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=20"


def fetch_url(url, timeout=30):
    """Fetch URL content with error handling."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; KarpathyRSSBot/1.0)"
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[WARN] Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def parse_atom(xml_str, feed_name):
    """Parse Atom XML feed."""
    articles = []
    try:
        root = ElementTree.fromstring(xml_str)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            link_el = entry.find("atom:link[@rel='alternate']", ns)
            if link_el is None:
                link_el = entry.find("atom:link", ns)
            summary_el = entry.find("atom:summary", ns)
            if summary_el is None:
                summary_el = entry.find("atom:content", ns)
            published_el = entry.find("atom:published", ns)
            if published_el is None:
                published_el = entry.find("atom:updated", ns)
            author_el = entry.find("atom:author/atom:name", ns)

            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            link = link_el.get("href", "") if link_el is not None else ""
            summary = summary_el.text.strip() if summary_el is not None and summary_el.text else ""
            published = published_el.text.strip() if published_el is not None and published_el.text else ""
            author = author_el.text.strip() if author_el is not None and author_el.text else ""

            # Clean summary of HTML tags
            import re
            summary = re.sub(r'<[^>]+>', '', summary).strip()
            # Collapse whitespace
            summary = re.sub(r'\s+', ' ', summary).strip()

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
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            summary_el = entry.find("atom:summary", ns)
            published_el = entry.find("atom:published", ns)
            link_el = entry.find("atom:link[@type='text/html']", ns)
            if link_el is None:
                link_el = entry.find("atom:link[@rel='alternate']", ns)
            if link_el is None:
                link_el = entry.find("atom:link", ns)

            title = title_el.text.strip().replace("\n", " ").replace("  ", " ") if title_el is not None and title_el.text else ""
            summary = summary_el.text.strip().replace("\n", " ").replace("  ", " ") if summary_el is not None and summary_el.text else ""
            published = published_el.text.strip() if published_el is not None and published_el.text else ""
            link = link_el.get("href", "") if link_el is not None else ""

            import re
            summary = re.sub(r'<[^>]+>', '', summary).strip()
            summary = re.sub(r'\s+', ' ', summary).strip()

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

        # Try parsing various date formats
        for fmt in [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%d %H:%M:%S",
        ]:
            try:
                dt = datetime.strptime(pub, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                if dt >= cutoff:
                    filtered.append(art)
                break
            except ValueError:
                continue
        else:
            # Could not parse date, include it anyway
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

    # Fetch regular feeds
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
    recent = filter_recent(all_articles, hours=24)
    unique = deduplicate(recent)

    result = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_found": len(all_articles),
        "recent_count": len(unique),
        "articles": unique,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
