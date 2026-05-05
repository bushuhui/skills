#!/bin/bash
set -e

# ===== 论文自动审稿 - 环境变量配置 =====

# PDF 转 Markdown 服务（pi-llm-server）
export PI_LLM_URL="http://api.adv-ci.com:8090/v1"
export PI_LLM_API_KEY="sk-5f8b839908d14561590b70227c72ca86"

# 大语言模型审稿服务
export LLM_URL="http://api.adv-ci.com/v1"
export LLM_API_KEY="sk-lga9AVjRSOCC0GKZ7hfqgw"
export LLM_MODEL="openai_code"

cd /home/bushuhui/.agents/skills/paper-auto-review

echo "=== 环境变量已设置 ==="
echo "PI_LLM_URL=$PI_LLM_URL"
echo "LLM_URL=$LLM_URL"
echo "LLM_MODEL=$LLM_MODEL"
echo ""

exec python3 paper_auto_review.py --year 2026 "$@"
