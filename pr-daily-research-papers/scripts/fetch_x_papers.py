#!/usr/bin/env python3
"""
Fetch paper-related tweets from key AI researchers on X/Twitter.
Uses Chrome MCP fetch script as fallback.
Output: JSON array to stdout.

NOTE: X/Twitter scraping is unreliable. This script is best-effort.
If it fails, the main workflow should continue without it.
"""

import sys
import json
import os
import subprocess
import re

# Key accounts to monitor
ACCOUNTS = [
    "_akhaliq",       # AK - daily paper digest king
    "OpenAI",
    "AnthropicAI",
    "GoogleDeepMind",
    "MetaAI",
    "DrJimFan",       # Jim Fan - NVIDIA embodied AI
    "labordes",       # SGLang
]

CHROME_MCP_SCRIPT = "/home/bushuhui/scripts/chrome-mcp-fetch.sh"


def fetch_account(account):
    """Try to fetch recent tweets from an account."""
    url = f"https://x.com/{account}"
    papers = []

    # Try Chrome MCP first
    if os.path.exists(CHROME_MCP_SCRIPT):
        try:
            result = subprocess.run(
                [CHROME_MCP_SCRIPT, url, "text"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout:
                text = result.stdout
                # Extract arxiv links
                arxiv_ids = re.findall(r"arxiv\.org/abs/(\d{4}\.\d{4,5})", text)
                for aid in set(arxiv_ids):
                    papers.append({
                        "arxiv_id": aid,
                        "title": "",
                        "link": f"https://arxiv.org/abs/{aid}",
                        "source": f"x/@{account}",
                        "summary": "",
                    })
        except Exception:
            pass

    return papers


def main():
    all_papers = []
    seen = set()

    for account in ACCOUNTS:
        print(f"# Checking @{account}...", file=sys.stderr)
        try:
            papers = fetch_account(account)
            for p in papers:
                if p["arxiv_id"] not in seen:
                    seen.add(p["arxiv_id"])
                    all_papers.append(p)
        except Exception as e:
            print(f"# Error with @{account}: {e}", file=sys.stderr)

    json.dump(all_papers, sys.stdout, ensure_ascii=False, indent=2)
    print(f"\n# Total: {len(all_papers)} papers from X/Twitter", file=sys.stderr)


if __name__ == "__main__":
    main()
