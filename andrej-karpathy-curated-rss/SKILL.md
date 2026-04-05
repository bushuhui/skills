---
name: andrej-karpathy-curated-rss
description: |
  抓取 Andrej Karpathy 精选 RSS 订阅包的最新内容，翻译摘要为中文，保存到 Obsidian 知识库。
  触发条件：
  - 用户要求抓取 Karpathy RSS
  - 定时 cron job 调用
  - 用户提到 "karpathy rss" 或 "karpathy 博客"
---

# Andrej Karpathy Curated RSS

抓取 Karpathy 精选 RSS pack（92 个顶级技术博客），提取过去 24 小时的新文章，翻译摘要为中文，保存到 Obsidian 知识库。

RSS 源：`https://youmind.com/rss/pack/andrej-karpathy-curated-rss`

## 工作流程

### 步骤 1：运行抓取脚本

```bash
python3 scripts/fetch_rss.py [hours]
```

- 默认抓取过去 24 小时的内容，可传参数调整（如 `48` 抓取 48 小时）
- 需要代理访问（脚本自动尝试 `HTTP_PROXY` 环境变量或 `http://127.0.0.1:7890`）
- 输出：JSON 数组到 stdout，每条包含 `title`、`link`、`author`、`published`、`summary`

### 步骤 2：翻译并保存到知识库

⚠️ 文件命名规则（避免 bisync 冲突）：
- 目标文件：`/home/bushuhui/data-all/note/bushuhui/Clippings/YYYYMM/YYYYMMDD-karpathy-rss.md`
- 每个来源用独立文件，不要写入 `YYYYMMDD.md` 主文件！
- 多个 cron job 写同一文件会导致 rclone bisync 产生 .conflict 文件

写入方式：
- 先用 `read` 检查文件是否存在
- 文件已存在 → 用 `edit` 追加到末尾（可能是手动触发了第二次）
- 文件不存在 → 用 `write` 创建新文件

文件格式：

```markdown
# Karpathy 精选 RSS - YYYY-MM-DD

> 来源: Andrej Karpathy Curated RSS (92 blogs)
> 抓取时间: YYYY-MM-DD HH:MM
> 文章数: N 篇

### [中文标题翻译]
- 原文: [英文标题](链接)
- 作者: xxx
- 时间: YYYY-MM-DD
- 摘要: [中文摘要，2-3 句话概括核心内容]

### [中文标题翻译]
...
```

翻译要求：
- 标题翻译成中文
- 摘要翻译成中文，保持简洁（2-3 句话）
- 专有名词保留英文（如 GPT、LLM、Rust、Linux 等）
- 如果原文摘要太短或无意义，根据标题和上下文写一句简短说明

### 步骤 3：同步

```bash
bash /home/bushuhui/scripts/backup_bushuhui_webdav.sh
```

## 注意事项

- 脚本路径相对于此 skill 目录：`scripts/fetch_rss.py`
- 需要网络代理访问 youmind.com
- 如果条目数为 0，说明过去 24 小时没有新内容，跳过保存
