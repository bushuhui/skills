---
name: deep-research
description: |
  深度研究与搜索。当用户需要深入调研某个话题时触发：
  - "帮我调研一下 XXX"
  - "深度搜索 XXX"
  - "研究一下 XXX 的最新进展"
  - "帮我查一下 XXX 的资料"
  - 需要多轮搜索、多源整合的复杂信息需求
  不适用于：简单事实查询（直接回答）、已知 URL 抓取（用 web_fetch）
---

# Deep Research Skill

多轮迭代深度研究，整合多源信息生成调研报告。

## 工具

- **搜索脚本**: `scripts/search.py` — DuckDuckGo 搜索（无需 API key）
- **web_fetch** — 抓取网页正文
- **sessions_spawn** — 复杂调研可 spawn 子 agent 避免占用主 session context

## 搜索脚本用法

```bash
# 基础搜索（需设置代理：export HTTPS_PROXY=http://127.0.0.1:7890）
python3 scripts/search.py "query" -n 10

# 搜新闻
python3 scripts/search.py "AI agent" --news

# 批量搜索（多个关键词，推荐中英文各一组）
python3 scripts/search.py "placeholder" --queries "query1" "query2" "query3"
```

输出 JSON 数组，每条含 `title`, `href`, `body`。

## 调研流程

### 简单调研（单轮，直接在主 session）

适用于：明确话题、预计 3-5 个搜索即可覆盖。

1. 分析用户需求，拆解为 2-3 个搜索关键词（中英文各一组效果更好）
2. 运行 `search.py` 批量搜索
3. 从结果中挑选 3-5 个最相关的 URL
4. 用 `web_fetch` 逐个抓取正文
5. 整合信息，输出结构化报告

### 深度调研（多轮，spawn 子 agent）

适用于：开放性话题、需要多角度覆盖、预计信息量大。

spawn 子 agent，任务描述模板：

```
深度调研任务：[话题]

要求：
1. 用 search.py 脚本搜索（路径：~/.openclaw/workspace/skills/deep-research/scripts/search.py）
2. 至少搜索 3 轮，每轮根据上一轮发现调整关键词
3. 抓取 5-8 个高质量页面的正文
4. 输出结构化中文报告，包含：
   - 核心发现（3-5 条）
   - 详细分析（按主题分节）
   - 信息来源（附链接）
   - 知识空白（还有什么没覆盖到）
```

## 报告格式

```markdown
# [调研主题] 调研报告

> 调研时间: YYYY-MM-DD
> 搜索轮次: N 轮
> 覆盖来源: N 个

## 核心发现

1. ...
2. ...

## 详细分析

### [子话题 1]
...

### [子话题 2]
...

## 信息来源

1. [标题](URL) — 简述
2. ...

## 知识空白

- 还有哪些方面未覆盖
```

## 决策树

```
用户请求
├── 包含 URL → web_fetch 直接抓取
├── 简单事实问题 → 直接回答或单次搜索
├── 明确话题调研 → 简单调研流程（主 session）
└── 开放性/复杂调研 → spawn 子 agent 深度调研
```

## 注意事项

- 脚本自动从环境变量读取代理（HTTPS_PROXY/HTTP_PROXY），需要代理时设置 `HTTPS_PROXY=http://127.0.0.1:7890`
- 批量搜索自动间隔 1 秒避免频率限制
- 搜索结果的 `body` 可能为空，详细内容需要 `web_fetch` 抓取
- 中英文关键词各搜一组效果更好
- 调研报告默认中文，除非用户要求英文
