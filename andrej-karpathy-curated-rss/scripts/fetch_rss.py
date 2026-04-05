#!/usr/bin/env python3
"""
Fetch Andrej Karpathy's curated RSS pack and extract entries from the last 24 hours.
Output: JSON array of entries to stdout.
"""

import sys
import json
import re
import html
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError

RSS_URL = "https://youmind.com/rss/pack/andrej-karpathy-curated-rss"
NS = {"atom": "http://www.w3.org/2005/Atom"}
HOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 24


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def parse_date(s: str) -> datetime:
    """Parse ISO-8601 date string."""
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def fetch(url: str) -> bytes:
    """Fetch URL, trying proxy if direct fails."""
    headers = {"User-Agent": "Mozilla/5.0 (KarpathyRSS/1.0)"}
    # Try with proxy first (needed for youmind.com in China)
    import os
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or "http://127.0.0.1:7890"
    try:
        from urllib.request import ProxyHandler, build_opener
        opener = build_opener(ProxyHandler({"https": proxy, "http": proxy}))
        req = Request(url, headers=headers)
        return opener.open(req, timeout=30).read()
    except Exception:
        pass
    # Fallback: direct
    req = Request(url, headers=headers)
    return urlopen(req, timeout=30).read()


def main():
    data = fetch(RSS_URL)
    root = ET.fromstring(data)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS)

    entries = []
    for entry in root.findall("atom:entry", NS):
        pub = entry.findtext("atom:published", "", NS)
        upd = entry.findtext("atom:updated", "", NS)
        date_str = pub or upd
        if not date_str:
            continue
        dt = parse_date(date_str)
        if dt < cutoff:
            continue

        title = entry.findtext("atom:title", "", NS).strip()
        link_el = entry.find("atom:link", NS)
        link = link_el.get("href", "") if link_el is not None else ""
        author = ""
        author_el = entry.find("atom:author", NS)
        if author_el is not None:
            author = author_el.findtext("atom:name", "", NS).strip()

        # Get summary or content, strip HTML
        summary = entry.findtext("atom:summary", "", NS)
        content = entry.findtext("atom:content", "", NS)
        text = strip_html(summary or content or "")
        # Truncate to ~500 chars for summary
        if len(text) > 500:
            text = text[:497] + "..."

        entries.append({
            "title": title,
            "link": link,
            "author": author,
            "published": date_str,
            "summary": text,
        })

    json.dump(entries, sys.stdout, ensure_ascii=False, indent=2)
    print(f"\n# Total: {len(entries)} entries in last {HOURS}h", file=sys.stderr)


if __name__ == "__main__":
    main()
