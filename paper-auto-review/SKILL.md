# Paper Auto Review Skill

自动审稿工具：扫描论文目录，对未审稿的 PDF 调用 Kimi 自动生成审稿意见。

## 触发条件
- 用户要求审稿、自动审稿、paper review
- 用户提到论文审稿目录

## 配置
- 审稿脚本：`/home/bushuhui/scripts/teching_research/auto_review/kimi_pdf_auto_review.py`
- 审稿 Prompt：脚本同目录下 `review_prompt.md`
- 论文根目录：`/home/bushuhui/datacenter/papers/paper-review/`
- 输出文件：每篇论文目录下的 `review_kimi.md`

## 执行流程

### 1. 扫描待审稿论文
```bash
# 找出没有 review*.md 的论文目录
PAPER_ROOT="/home/bushuhui/datacenter/papers/paper-review"
YEAR="${1:-$(date +%Y)}"  # 默认当前年份

for d in "$PAPER_ROOT/$YEAR"/*/*; do
  if [ -d "$d" ]; then
    review_count=$(find "$d" -name "review*.md" -type f 2>/dev/null | wc -l)
    if [ "$review_count" -eq 0 ]; then
      pdf=$(find "$d" -name "*.pdf" -type f | head -1)
      if [ -n "$pdf" ]; then
        echo "$pdf"
      fi
    fi
  fi
done
```

### 2. 执行审稿
⚠️ 必须先切换到脚本目录（默认读取同目录的 review_prompt.md）：
```bash
cd /home/bushuhui/scripts/teching_research/auto_review
python3 kimi_pdf_auto_review.py --pdf "<PDF路径>" --timeout-ms 900000 --stable-seconds 20
```

### 3. 执行约束
- 每篇论文执行完后随机等待 20-60 秒：`sleep $((RANDOM % 41 + 20))`
- 单篇超时 15 分钟（900000ms）
- 如果某篇失败，记录错误继续下一篇
- 脚本需要 Kimi 登录态（`kimi_storage_state.json`），首次使用需 `--prepare-login` 手动登录

### 4. 推荐使用子 agent 执行
审稿耗时较长（每篇 5-15 分钟），建议 spawn 子 agent 避免占用 main session：
```
sessions_spawn:
  label: paper-review-batch
  model: aicodewith-claude/claude-sonnet-4-6
  runTimeoutSeconds: 7200
  task: (包含上述步骤的完整指令)
```

### 5. 完成后汇总
报告每篇论文的审稿状态（成功/失败）、耗时、输出文件路径。

## 可选参数
- `--headed`：有头浏览器模式（调试用）
- `--probe-layout`：仅验证页面布局，不发送消息
- `--prepare-login`：首次登录 Kimi 保存登录态
- `--prompt <file>`：自定义 prompt 文件
- `--attachment-timeout-ms`：附件上传超时（默认 8 分钟）

## 依赖
- Python 3 + playwright + browser_cookie3
- Chrome 浏览器（用于获取 Kimi cookie）
- Kimi 登录态文件
