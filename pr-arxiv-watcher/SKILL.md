---
name: pr-arxiv-watcher
description: Search and summarize papers from ArXiv via RSS (latest by category) or API (keyword search). Use when the user asks for the latest research, specific topics on ArXiv, or a daily summary of AI papers.
---

# ArXiv Watcher

This skill interacts with ArXiv using two data sources:

1. **RSS 数据源**（默认推荐）— 获取某分类当天最新提交的论文
2. **API 搜索** — 按关键词/作者搜索论文

## 数据源

### RSS（默认）

- 地址：`https://rss.arxiv.org/rss/<categories>`
- 优势：轻量、无频率限制、返回当天新论文
- 限制：不支持关键词搜索，只能按分类获取

**常用分类**：
| 分类 | 说明 |
|------|------|
| `cs.AI` | 人工智能 |
| `cs.LG` | 机器学习 |
| `cs.CL` | 自然语言处理 |
| `cs.CV` | 计算机视觉 |
| `cs.NE` | 神经网络 |
| `stat.ML` | 统计机器学习 |
| `eess.SP` | 信号处理 |
| `quant-ph` | 量子物理 |

**组合分类**：用 `+` 连接，如 `cs.AI+cs.LG+cs.CL`

### API 搜索

- 地址：`https://export.arxiv.org/api/query`
- 支持关键词、作者、标题搜索
- 支持按提交日期排序

## Workflow

1. 根据用户需求选择模式：
   - **"最新/今天/new/today/每日"** → RSS 模式：`./search_arxiv.sh rss <categories> <count>`
   - **"搜索/找关于/keyword/search"** → API 模式：`./search_arxiv.sh search "<query>" <count>`
2. 解析返回的 XML（`<entry>` 或 `<item>`，含 `<title>`, `<summary>`, `<link>`）
3. 向用户展示结果（标题、作者、摘要、链接）
4. **MANDATORY**: 将讨论过的论文记录到 `memory/RESEARCH_LOG.md`：
   ```markdown
   ### [YYYY-MM-DD] TITLE_OF_PAPER
   - **Authors**: Author List
   - **Link**: ArXiv Link
   - **Summary**: Brief summary of the paper and its relevance.
   ```

## Examples

- "今天 arXiv 有什么新论文" → `./search_arxiv.sh rss "cs.AI+cs.LG+cs.CL" 10`
- "搜索 LLM reasoning 相关的论文" → `./search_arxiv.sh search "LLM reasoning" 5`
- "看看今天 cs.CV 有什么新东西" → `./search_arxiv.sh rss "cs.CV" 15`
- "找一下 Yann LeCun 最近的论文" → `./search_arxiv.sh search "au:Yann_LeCun" 5`

## Resources

- `scripts/search_arxiv.sh`: RSS + API 双模式脚本
