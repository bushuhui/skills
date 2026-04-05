---
name: brave-search
description: |
  通过 Brave Search API 搜索网页和新闻。触发条件：
  - 用户要求搜索/查找资料
  - 需要获取最新信息（新闻、技术动态）
  - deep-research skill 的搜索后端替代
  - 用户提到 "brave 搜索" 或 "搜一下"
  不适用于：已知 URL 抓取（用 web_fetch）、简单事实问题（直接回答）
---

# Brave Search Skill

通过 Brave Search API 进行网页搜索和新闻搜索。

## 环境

- API Key 从环境变量 `BRAVE_API_KEY` 读取（已在 ~/scripts/shell_conf 配置）
- 支持代理：自动读取 `HTTPS_PROXY` / `HTTP_PROXY`

## 搜索脚本

```bash
# 基础搜索
python3 scripts/brave_search.py "query"

# 限制结果数
python3 scripts/brave_search.py "query" -n 5

# 搜新闻
python3 scripts/brave_search.py "AI agent" --news

# 时间过滤：pd=过去一天, pw=过去一周, pm=过去一月, py=过去一年
python3 scripts/brave_search.py "LLM benchmark" --freshness pw

# 指定国家
python3 scripts/brave_search.py "量化交易" --country CN

# 批量搜索（多关键词）
python3 scripts/brave_search.py "placeholder" --queries "query1" "query2" "query3"

# 翻页
python3 scripts/brave_search.py "query" --offset 10
```

输出 JSON 数组，每条含 `title`, `href`, `body`, `age`。

## 使用流程

1. 分析用户需求，拆解为搜索关键词（中英文各一组效果更好）
2. 运行 `brave_search.py` 搜索
3. 从结果中挑选最相关的 URL
4. 用 `web_fetch` 抓取正文获取详细内容
5. 整合信息回复用户

## 与 deep-research 配合

本 skill 可作为 deep-research 的搜索后端替代 DuckDuckGo：
- Brave API 质量更高、更稳定
- 支持时间过滤和国家过滤
- 有 `age` 字段标注结果时效性

## 注意事项

- 免费 API 限制：每月 2000 次请求，每秒 1 次
- 单次最多返回 20 条结果
- 批量搜索自动间隔 0.5 秒避免频率限制
