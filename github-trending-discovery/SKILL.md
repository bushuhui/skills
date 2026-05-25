---
name: github-trending-discovery
description: "Automated discovery of trending GitHub repositories — search, filter, classify, and save to knowledge base. Triggers on: GitHub trending, hot repos, find popular repos, github 热点, github 热门仓库."
---

# GitHub Trending Repository Discovery

Automate discovery of trending/high-star GitHub repos, filter noise, classify by domain, and save to knowledge base.

## Trigger Conditions

- User asks about GitHub trending / hot repos / "github 上有什么新项目"
- User shares a GitHub repo screenshot and wants to explore similar
- User requests periodic GitHub monitoring
- Periodic cron job execution

## Core Workflow

### 1. Search via GitHub API

**Primary method**: GitHub Search API for recently-created high-star repos:

```bash
curl -s "https://api.github.com/search/repositories?q=created:>2026-05-01&sort=stars&order=desc&per_page=40"
```

**⚠️ CRITICAL PITFALL**: GitHub Search API returns truncated JSON for large responses (response body gets cut mid-stream, causing JSON parse errors). Two fallback strategies:

**Fallback A**: Use Python regex extraction on raw response:
```python
import re, urllib.request
raw = response.read().decode()
names = re.findall(r'"full_name"\s*:\s*"([^"]+)"', raw)
stars = re.findall(r'"stargazers_count"\s*:\s*(\d+)', raw)
langs = re.findall(r'"language"\s*:\s*"([^"]+)"', raw)
descs = re.findall(r'"description"\s*:\s*"((?:[^"\\]|\\.)*)"', raw)
```

**Fallback B**: Use `per_page=25` or less to stay under truncation threshold, or fetch individual repo info via `/repos/{owner}/{name}` API.

### 2. Get Real Descriptions

GitHub Search API `description` field is **not the real repo description** — it's a context snippet from search matches. Must call individual repo API for accurate descriptions:

```python
url = f'https://api.github.com/repos/{owner}/{name}'
```

Add `time.sleep(0.2)` between calls to avoid rate limiting.

### 3. SEO Spam Detection

**Most important filter.** GitHub trending search returns massive amounts of SEO spam repos (download aggregators, mod menus, emulator scams). **2026-05-25 session reality check: 10/19 repos were spam with old rules.** Detection rules (expanded):

| Signal | Pattern | Examples that slipped through |
|--------|---------|-------------------------------|
| Download keywords | `download\s+free`, `latest\s+version` | AutoCAD crack, Forza download |
| Platform stuffing | `windows.*mac.*android.*ios.*pc` | Tomodachi Life spam |
| Keyword comma pile | Description has >4 commas | Polymarket bot (repetitive) |
| App scam pattern | `Steam.*download.*free.*github` | — |
| Empty/missing description | `description` is null or empty | — |
| **"2026" in description** | `2026` appears in description text | CS2-Cheat-2026, Network-Optimizer-2026, Casino-Bonus-2026 |
| **Emoji stuffing** | ≥3 emoji characters in description | 🚀🔧⚡🏝️🎮 in spam repos |
| **Crack / bypass / unlock** | `crack|bypass|unlock|hack|cheat|spoof` | CS2 cheat, Hardware spoof, FL Studio unlock |
| **Casino / gambling** | `casino|bonus|gambling|betting|polymarket.*bot` | casino-bonus, polymarket-trading-bot (x2) |
| **Repetitive text** | Same phrase repeated ≥3 times in description | "Polymarket Trading Bot Polymarket Trading Bot Polymarket..." |
| **Booster / optimizer** | `booster|optimizer|boost.*fps|fix.*ping` | Discord booster, Ping Slayer |
| **Token management** | `token.*manager|auto.*boost` | guild-advancement-automator |
| **18+ / uncensored** | `uncensored|18\+|nsfw|adult` | uncensored-ai-image-video-generator |
| **Game mod / guide** | `mod.*pack|release.*date|multiplayer.*guide` | Subnautica 2 guide, Tomodachi Life |

**Scoring**: Each matched signal = 1 point. If score ≥ 2 → **skip**. If score = 1 → flag for manual review.

**Additional heuristic**: If `stargazers_count` > 400 but `forks_count` = 0 or very low (<5), likely artificial star inflation → skip.

### 4. Classification

Classify filtered repos into categories:

**🤖 AI / ML**: `ai`, `agent`, `llm`, `model`, `chatbot`, `ml`, `diffusion`, `rag`, `nlp`, `computer vision`, `training`, `inference`, `text generation`

**🛠️ Dev Tools**: `cli`, `terminal`, `editor`, `framework`, `library`, `docker`, `kubernetes`, `api`, `compiler`, `database`, `web`, `frontend`, `backend`

**📦 Other**: Everything else

### 5. Output Format

**Always list ALL filtered repos in complete tables first**, then optionally highlight 2-3 noteworthy projects at the end. Never show only a subset — users expect the full list.

Markdown table with columns: #, Project (link), Stars (+ Forks), Description, Language. Group by category. Max 10 per category.

### 6. Save to Knowledge Base

```
/home/a409/knowledge_base/note/pi-lab/Clippings/YYYYMM/GitHub-Trending/trending-YYYYMMDD.md
```

Update daily index file `Clippings/YYYYMM/YYYYMMDD.md`.

## Script

The reusable script is at `scripts/github_trending.py` within this skill directory. Execute with:

```bash
python3 /home/bushuhui/.hermes/skills/github-trending-discovery/scripts/github_trending.py
```

The script:
- Searches repos created in last 4 days (via GitHub Search API)
- Fetches detailed info for each repo (via `/repos/{owner}/{name}` API)
- Filters SEO spam with a **scoring system** (score ≥ 2 → skip)
  - Checks: "2026" year spam, emoji stuffing, crack/bypass terms, platform stuffing, comma piles, repetitive text, specific spam patterns (casino/bonus/booster/uncensored), star/fork ratio anomaly
- Classifies into AI/Dev/Other
- Saves Markdown to knowledge base
- Updates daily index

## Cron Job

A cron job named "GitHub热点仓库速报" runs every 3 days, executing the script and delivering results to the conversation.

## Repo Cloning Strategy

When downloading repos from search results:

```bash
# 1. Try clone with timeout + no-prompt
cd /home/a409/knowledge_base/codebase
GIT_TERMINAL_PROMPT=0 timeout 60 git clone https://github.com/{owner}/{repo}.git 2>&1

# 2. If "destination path already exists", just cd in and git pull
cd {repo} && git pull 2>&1

# 3. If clone fails with auth error, repo may be private or deleted
```

## Pitfalls

| Issue | Fix |
|-------|-----|
| `could not read Username for 'https://github.com'` | Use `GIT_TERMINAL_PROMPT=0 timeout 60` prefix to fail fast instead of hanging |
| "destination path already exists" | Repo already downloaded; just `cd` in and `git pull` |
| Clone silently succeeds but repo is empty | Check `ls` output; some repos are just SEO pages with no real files |
| GitHub returns 404 on `/repos/{owner}/{name}` | Repo was deleted or renamed — skip silently |

