#!/usr/bin/env python3
"""
Fetch today's papers from HuggingFace Daily Papers page.
Output: JSON array to stdout.
"""

import sys
import json
import re
import os
from urllib.request import urlopen, Request, ProxyHandler, build_opener
from datetime import datetime, timezone

HF_URL = "https://huggingface.co/papers"


def fetch(url):
    headers = {"User-Agent": "Mozilla/5.0 (DailyResearchPapers/1.0)"}
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or "http://127.0.0.1:7890"
    # Try proxy first
    try:
        opener = build_opener(ProxyHandler({"https": proxy, "http": proxy}))
        req = Request(url, headers=headers)
        return opener.open(req, timeout=30).read().decode("utf-8")
    except Exception:
        pass
    # Fallback direct
    req = Request(url, headers=headers)
    return urlopen(req, timeout=30).read().decode("utf-8")


def parse_hf_papers(html_text):
    """Extract paper info from HuggingFace papers page HTML."""
    papers = []

    # Match paper entries: look for arxiv links and titles
    # HF papers page has patterns like: href="/papers/XXXX.XXXXX"
    paper_blocks = re.findall(
        r'href="/papers/(\d{4}\.\d{4,5})"[^>]*>([^<]+)</a>',
        html_text
    )

    seen = set()
    for arxiv_id, title in paper_blocks:
        title = title.strip()
        if not title or arxiv_id in seen:
            continue
        if len(title) < 10:  # skip noise
            continue
        seen.add(arxiv_id)
        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "link": f"https://arxiv.org/abs/{arxiv_id}",
            "hf_link": f"https://huggingface.co/papers/{arxiv_id}",
            "published": datetime.now(timezone.utc).isoformat(),
            "summary": "",
            "source": "huggingface",
        })

    return papers


def main():
    try:
        html_text = fetch(HF_URL)
        papers = parse_hf_papers(html_text)
        json.dump(papers, sys.stdout, ensure_ascii=False, indent=2)
        print(f"\n# Total: {len(papers)} papers from HuggingFace", file=sys.stderr)
    except Exception as e:
        print(f"# Error: {e}", file=sys.stderr)
        json.dump([], sys.stdout)


if __name__ == "__main__":
    main()
