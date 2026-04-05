#!/usr/bin/env python3
"""
Fetch recent papers from arXiv API for specified categories.
Output: JSON array of papers to stdout.
"""

import sys
import json
import re
import html
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen, Request
import time

HOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 24

CATEGORIES = [
    "cs.CL",    # NLP/LLM
    "cs.AI",    # AI
    "cs.LG",    # Machine Learning
    "cs.MA",    # Multi-Agent
    "cs.RO",    # Robotics
    "cs.CV",    # Computer Vision
    "stat.ML",  # ML Stats
    "q-fin.TR", # Trading
    "q-fin.CP", # Computational Finance
    "eess.SY",  # Systems/Control (UAV)
]

KEYWORDS = [
    "large language model", "LLM", "GPT", "transformer", "language model",
    "instruction tuning", "alignment", "RLHF", "reasoning", "chain-of-thought",
    "in-context learning", "fine-tuning", "pretraining", "mixture of experts",
    "MoE", "scaling law",
    "reinforcement learning", "GRPO", "PPO", "DPO", "reward model",
    "policy optimization", "actor-critic", "Q-learning",
    "agent", "tool use", "function calling", "planning", "multi-agent",
    "autonomous agent", "agentic", "code generation",
    "UAV", "drone", "unmanned aerial", "quadrotor", "aerial robot",
    "path planning", "swarm", "formation control",
    "quantitative trading", "algorithmic trading", "financial",
    "stock predict", "portfolio", "time series forecast",
    "robot", "manipulation", "grasping", "locomotion", "embodied",
    "VLA", "vision-language-action", "sim-to-real", "humanoid",
    "dexterous", "navigation", "SLAM",
]

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def normalize(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", text))).strip()


def extract_id(url):
    m = re.search(r"(\d{4}\.\d{4,5})", url)
    return m.group(1) if m else url


def is_relevant(title, summary, cats):
    text = (title + " " + summary).lower()
    niche = {"cs.RO", "cs.MA", "q-fin.TR", "q-fin.CP", "eess.SY"}
    if any(c in niche for c in cats):
        return True
    for kw in KEYWORDS:
        if kw.lower() in text:
            return True
    return False


def fetch_category(cat, max_results=100):
    url = f"https://export.arxiv.org/api/query?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    req = Request(url, headers={"User-Agent": "DailyResearchPapers/1.0"})
    try:
        data = urlopen(req, timeout=60).read()
    except Exception as e:
        print(f"# Error fetching {cat}: {e}", file=sys.stderr)
        return []

    root = ET.fromstring(data)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS)
    papers = []

    for entry in root.findall("atom:entry", NS):
        pub = entry.findtext("atom:published", "", NS)
        if not pub:
            continue
        try:
            dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt < cutoff:
            continue

        title = normalize(entry.findtext("atom:title", "", NS))
        summary = normalize(entry.findtext("atom:summary", "", NS))

        link = ""
        for lk in entry.findall("atom:link", NS):
            if lk.get("type") == "text/html":
                link = lk.get("href", "")
                break
        if not link:
            link = entry.findtext("atom:id", "", NS)

        arxiv_id = extract_id(link)
        authors = [a.findtext("atom:name", "", NS).strip()
                    for a in entry.findall("atom:author", NS)]

        cats = []
        pc = entry.find("arxiv:primary_category", NS)
        if pc is not None:
            cats.append(pc.get("term", ""))
        for c in entry.findall("atom:category", NS):
            t = c.get("term", "")
            if t and t not in cats:
                cats.append(t)

        if not is_relevant(title, summary, cats):
            continue

        if len(summary) > 600:
            summary = summary[:597] + "..."

        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "link": link,
            "authors": authors[:5],
            "published": pub,
            "summary": summary,
            "categories": cats[:5],
            "source": "arxiv",
        })

    return papers


def main():
    all_papers = {}
    for cat in CATEGORIES:
        print(f"# Fetching {cat}...", file=sys.stderr)
        papers = fetch_category(cat)
        for p in papers:
            aid = p["arxiv_id"]
            if aid not in all_papers:
                all_papers[aid] = p
            else:
                # merge categories
                for c in p["categories"]:
                    if c not in all_papers[aid]["categories"]:
                        all_papers[aid]["categories"].append(c)
        time.sleep(3)  # arXiv rate limit: 3s between requests

    result = sorted(all_papers.values(), key=lambda x: x["published"], reverse=True)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print(f"\n# Total: {len(result)} papers in last {HOURS}h", file=sys.stderr)


if __name__ == "__main__":
    main()
