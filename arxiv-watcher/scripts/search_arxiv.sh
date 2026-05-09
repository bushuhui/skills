#!/usr/bin/env bash
# scripts/search_arxiv.sh — arXiv 数据源（RSS 优先 + API 备选）
#
# 用法:
#   模式 1 — RSS（获取某分类最新论文，推荐）:
#     ./search_arxiv.sh rss <categories> [max_results]
#     示例: ./search_arxiv.sh rss "cs.AI+cs.LG" 10
#
#   模式 2 — API 关键词搜索:
#     ./search_arxiv.sh search <query> [max_results]
#     示例: ./search_arxiv.sh search "LLM reasoning" 5
#
#   兼容旧用法（默认 search 模式）:
#     ./search_arxiv.sh <query> [max_results]
#
# RSS 数据源: https://rss.arxiv.org/
#   cs.AI(AI) cs.LG(ML) cs.CL(NLP) cs.CV(视觉) cs.NE(神经网络)
#   stat.ML(统计ML) eess.SP(信号处理) quant-ph(量子)
#
# API 数据源: https://export.arxiv.org/api/query

MODE=""
QUERY=""
MAX_RESULTS=10

# 解析参数
if [ "$1" = "rss" ]; then
  MODE="rss"
  QUERY="${2:-cs.AI+cs.LG+cs.CL}"
  MAX_RESULTS="${3:-20}"
elif [ "$1" = "search" ]; then
  MODE="search"
  QUERY="${2:-}"
  MAX_RESULTS="${3:-10}"
else
  # 兼容旧用法：直接传 query
  MODE="search"
  QUERY="$1"
  MAX_RESULTS="${2:-10}"
fi

if [ -z "$QUERY" ]; then
  echo "Usage: $0 [rss|search] <categories_or_query> [max_results]"
  echo "  RSS:  $0 rss cs.AI+cs.LG 10"
  echo "  API:  $0 search 'LLM reasoning' 5"
  exit 1
fi

if [ "$MODE" = "rss" ]; then
  # RSS 模式：获取当天新提交的论文
  curl -sL "https://rss.arxiv.org/rss/${QUERY}" | \
    awk -v max="$MAX_RESULTS" '
    BEGIN { count=0; in_item=0; }
    /<item>/ { in_item=1; item=""; }
    in_item { item = item $0 "\n"; }
    /<\/item>/ {
      in_item=0;
      count++;
      if (count <= max) printf "%s", item;
      else exit;
    }
    '
else
  # API 搜索模式：关键词搜索（支持排序）
  # URL 编码查询字符串
  ENCODED_QUERY=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$QUERY" 2>/dev/null || echo "$QUERY")
  curl -sL "https://export.arxiv.org/api/query?search_query=all:${ENCODED_QUERY}&start=0&max_results=${MAX_RESULTS}&sortBy=submittedDate&sortOrder=descending"
fi
