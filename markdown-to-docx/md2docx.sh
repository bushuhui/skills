#!/bin/bash
# Markdown to DOCX 转换脚本
# 使用 pandoc 将 Markdown（含 LaTeX 公式）转换为 Word DOCX 格式

set -e

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法：./md2docx.sh <input.md> [output.docx]"
    echo ""
    echo "示例:"
    echo "  ./md2docx.sh paper.md"
    echo "  ./md2docx.sh paper.md output.docx"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-${1%.md}.docx}"

# 检查文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
    echo "错误：文件不存在：$INPUT_FILE"
    exit 1
fi

# 检查 pandoc 是否安装
if ! command -v pandoc &> /dev/null; then
    echo "错误：pandoc 未安装"
    echo "请先安装 pandoc:"
    echo "  Ubuntu/Debian: sudo apt install pandoc"
    echo "  macOS: brew install pandoc"
    echo "  或访问：https://pandoc.org/installing.html"
    exit 1
fi

echo "=== Markdown to DOCX 转换器 ==="
echo "输入文件：$INPUT_FILE"
echo "输出文件：$OUTPUT_FILE"
echo ""

# 执行转换
# --mathml: 使用 MathML（Word 原生支持）
# 默认支持 $...$ 和 $$...$$ LaTeX 公式
echo "正在转换..."
pandoc "$INPUT_FILE" -o "$OUTPUT_FILE" --mathml

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 转换成功：$OUTPUT_FILE"
    echo ""
    # 显示文件大小
    ls -lh "$OUTPUT_FILE" | awk '{print "  文件大小：" $5}'
else
    echo "✗ 转换失败"
    exit 1
fi
