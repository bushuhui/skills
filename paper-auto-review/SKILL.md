---
name: paper-auto-review
description: 自动审稿工具：扫描论文目录，使用 pi-llm-server 转 Markdown，调用 Bailian LLM 生成审稿意见。Use when the user requests paper review, automatic review, or mentions paper review directory.
---

# Paper Auto Review Skill

自动审稿工具：扫描论文目录，对未审稿的论文自动生成审稿意见。

## 触发条件
- 用户要求审稿、自动审稿、paper review
- 用户提到论文审稿目录

## 配置
- 审稿脚本：`paper_auto_review.py`（本 skill 目录下）
- 英文审稿 Prompt：`review_prompt.md`（本 skill 目录下）
- 中文审稿 Prompt：`review_prompt_cn.md`（本 skill 目录下）
- 论文根目录：`/home/bushuhui/datacenter/papers/paper-review/`
- 输出文件：每篇论文目录下的 `review_draft.md`

## 语言检测
脚本自动检测论文语言：
- **中文论文**（中文字符占比 > 10%）：使用 `review_prompt_cn.md`，审稿意见为中文
- **英文论文**：使用 `review_prompt.md`，审稿意见为英文

## 执行流程

### 1. 扫描待审稿论文
```bash
# 找出没有 review*.md 的论文目录中的 PDF/DOCX/DOC 文件
cd /home/bushuhui/.agents/skills/paper-auto-review
python3 paper_auto_review.py --year 2026 --dry-run
```

### 2. 批量审稿
```bash
# 执行完整流程：扫描 → 转 Markdown → LLM 审稿 → 保存审稿意见
cd /home/bushuhui/.agents/skills/paper-auto-review
python3 paper_auto_review.py --year 2026
```

### 3. 自定义参数
```bash
# 指定论文根目录
python3 paper_auto_review.py --year 2026 --paper-root /path/to/papers

# 指定审稿 prompt
python3 paper_auto_review.py --year 2026 --review-prompt /path/to/prompt.md

# 指定目录搜索深度（默认 5）
python3 paper_auto_review.py --year 2026 --max-depth 5
```

### 4. 执行约束
- 每篇论文转 Markdown 后随机等待 5-15 秒，避免 API 限流
- 单篇 LLM 审稿超时 5 分钟（300 秒）
- 如果某篇失败，记录错误继续下一篇
- 已有 Markdown 文件的论文跳过转换步骤
- 已有 `review_draft.md` 的论文跳过审稿步骤
- 论文内容截断上限：200,000 字符（约 64K tokens，适配 qwen3.6-plus 的 128K 上下文窗口）

### 5. 推荐使用子 agent 执行
审稿耗时较长（每篇 3-10 分钟），建议 spawn 子 agent 避免占用 main session。

### 6. 完成后汇总
报告每篇论文的审稿状态（成功/失败/跳过）、输出文件路径。

## 常见坑

### 1. `patch` 工具对 `.py` 文件可能静默失败
修改脚本代码时，`patch` 操作可能报告 `success: true` 但文件内容实际未变。
**解决方案**：修改后用 `grep` 或 `read_file` 确认改动已生效。若 patch 不生效，改用 `write_file` 完整重写文件。

### 2. 后台进程 Python 输出缓冲
`python3 script.py` 在后台运行时，`print()` 输出会被缓冲，长时间看不到任何输出。
**解决方案**：使用 `PYTHONUNBUFFERED=1 python3 script.py` 启动。

### 3. 审稿文件名模式匹配
脚本通过 `source_path.glob("review*.md")` 判断是否已审稿。如果旧版脚本生成了 `{原名}_review_draft.md`（不以 review 开头），不会被检测到，导致同一论文重复审稿。
**解决方案**：脚本已修复，同时匹配 `review*.md` 和 `review_draft.md`。但手动清理残留的旧审稿文件仍建议。

### 4. 进程中断后文件可能未写入
审稿脚本生成审稿意见后写入磁盘，但如果进程被中断（SIGTERM），文件可能未完全写入或丢失。
**解决方案**：审稿前用 `--dry-run` 确认待审列表，审稿后检查输出文件是否真实存在。

### 5. 后台进程输出持续不可见（bash login shell 缓冲）
即使使用 `PYTHONUNBUFFERED=1` 或 `stdbuf`，通过 `terminal(background=true)` 启动的 bash login shell（`/usr/bin/bash -lic`）仍会缓冲子进程的 stdout，导致长时间看不到任何输出（`process.log` 返回 0 行）。
**解决方案**：
- 脚本内添加 `print` 覆盖：每行 print 后调用 `sys.stdout.flush()`（脚本顶部已内置 `_flush_print` 补丁）
- 或直接通过文件系统监控进度：`find ... -name "review_draft.md" -mmin -5`
- 不要依赖 `PYTHONUNBUFFERED=1` + `stdbuf`，对 bash login shell 无效

## 依赖
- Python 3 + requests
- pi-llm-server 服务（用于文档转 Markdown）
- Bailian LLM API（用于生成审稿意见）

## 环境变量
| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PI_LLM_URL` | `http://api.adv-ci.com:8090/v1` | pi-llm-server 地址 |
| `PI_LLM_API_KEY` | `sk-5f8b...` | pi-llm-server 认证 |
| `BAILIAN_URL` | `https://coding.dashscope.aliyuncs.com/v1` | Bailian API 地址 |
| `BAILIAN_API_KEY` | `sk-sp-67ea...` | Bailian 认证 |
| `BAILIAN_MODEL` | `qwen3.6-plus` | Bailian 模型 |
