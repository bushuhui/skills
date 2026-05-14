---
name: info-daily-hot-topics
description: 每日自动抓取热点新闻话题，从 NewsNow、今日热榜、SoPilot 三个源聚合热点资讯，按日期归档到知识库。Use when 用户需要获取每日热点、今日热门话题、新闻聚合，或提到 hot topics、daily news、今日热点。
---

# Daily Hot Topics

## Quick start

```bash
python3 fetch_hot_topics.py
```

## 工作流

1. 连接本地 Chrome (CDP, 端口 9222)
2. 依次抓取三个源:
   - **NewsNow** — 全球热点新闻
   - **今日热榜** — 中文互联网热门话题
   - **SoPilot** — 科技/AI 领域热点
3. 按日期归档到 `Clippings/YYYYMM/YYYYMMDD_热点资讯.md`

## 输出规范

- **路径**: `Clippings/YYYYMM/YYYYMMDD_热点资讯.md`
- **格式**: Markdown，每个源一个区块，含标题列表和链接
- **命名**: 按执行日期，格式 `YYYYMMDD_热点资讯.md`

## 定时执行

- **Cron ID**: `daily-hot-topics`
- **时间**: 每天 07:20 (Asia/Shanghai)
- **触发**: 远程 trigger 自动执行

## 前置条件

- Chrome 浏览器运行在 `--remote-debugging-port=9222`
- 复用浏览器真实 IP 和登录态，绕过 Cloudflare

## 容错

- 单个源失败不影响其他源，失败源在文件中标注错误信息
