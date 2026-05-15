#!/bin/bash
# Markdown to DOCX 转换脚本
# 用法：
#   方式 A（直接转换，pandoc）：
#     ./md2docx.sh <input.md> [output.docx]
#
#   方式 B（模板转换，匹配样式）：
#     ./md2docx.sh --template <template.docx> <input.md> [output.docx]

set -e

usage() {
    echo "=== Markdown to DOCX 转换器 ==="
    echo ""
    echo "用法："
    echo "  方式 A（直接转换）："
    echo "    $0 <input.md> [output.docx]"
    echo "    $0 <input.md> [output.docx] --reference-doc|-r <template.docx>"
    echo ""
    echo "  方式 B（模板转换）："
    echo "    $0 --template <template.docx> <input.md> [output.docx]"
    echo ""
    echo "示例:"
    echo "  $0 paper.md"
    echo "  $0 paper.md output.docx"
    echo "  $0 paper.md -r /path/to/my-template.docx"
    echo "  $0 --template template.docx paper.md output.docx"
    exit 0
}

if [ $# -lt 1 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

# 解析参数
TEMPLATE=""
REFERENCE_DOC=""
while [[ "$1" == --* ]]; do
    case "$1" in
        --template|-t)
            TEMPLATE="$2"
            shift 2
            ;;
        --reference-doc|-r)
            REFERENCE_DOC="$2"
            shift 2
            ;;
        *)
            echo "未知选项：$1"
            usage
            ;;
    esac
done

INPUT_FILE="$1"
OUTPUT_FILE="${2:-${1%.md}.docx}"

if [ ! -f "$INPUT_FILE" ]; then
    echo "错误：文件不存在：$INPUT_FILE"
    exit 1
fi

if [ -n "$TEMPLATE" ] && [ ! -f "$TEMPLATE" ]; then
    echo "错误：模板文件不存在：$TEMPLATE"
    exit 1
fi

if [ -n "$REFERENCE_DOC" ] && [ ! -f "$REFERENCE_DOC" ]; then
    echo "错误：参考文档不存在：$REFERENCE_DOC"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# === 新增：Markdown 格式检查与修复 ===
if command -v python3 &> /dev/null && [ -f "$SCRIPT_DIR/md_fixer.py" ]; then
    echo "=== Markdown 格式检查 ==="
    python3 "$SCRIPT_DIR/md_fixer.py" "$INPUT_FILE"
    
    # 如果修复生成了 _format_fixed.md，使用修复后的文件
    FIXED_FILE="${INPUT_FILE%.md}_format_fixed.md"
    if [ -f "$FIXED_FILE" ]; then
        echo "使用修复后的文件进行转换：$FIXED_FILE"
        INPUT_FILE="$FIXED_FILE"
    fi
    echo ""
fi

if [ -n "$TEMPLATE" ]; then
    # 方式 B：模板转换
    echo "=== 方式 B：模板转换 ==="
    echo "输入文件：$INPUT_FILE"
    echo "参考模板：$TEMPLATE"
    echo "输出文件：$OUTPUT_FILE"
    echo ""

    if ! command -v python3 &> /dev/null; then
        echo "错误：python3 未安装"
        exit 1
    fi

    python3 "$SCRIPT_DIR/md2docx_template.py" "$INPUT_FILE" --template "$TEMPLATE" -o "$OUTPUT_FILE"

else
    # 方式 A：pandoc 直接转换
    echo "=== 方式 A：直接转换 ==="
    echo "输入文件：$INPUT_FILE"
    echo "输出文件：$OUTPUT_FILE"
    [ -n "$REFERENCE_DOC" ] && echo "参考文档：$REFERENCE_DOC" || echo "参考文档：内置模板"
    echo ""

    if ! command -v pandoc &> /dev/null; then
        echo "错误：pandoc 未安装"
        echo "请先安装 pandoc: sudo apt install pandoc"
        exit 1
    fi

    # 先运行 Python 脚本做公式修正
    if command -v python3 &> /dev/null && [ -f "$SCRIPT_DIR/md2docx_converter.py" ]; then
        REF_ARG=""
        [ -n "$REFERENCE_DOC" ] && REF_ARG="--reference-doc $REFERENCE_DOC"
        python3 "$SCRIPT_DIR/md2docx_converter.py" "$INPUT_FILE" "$OUTPUT_FILE" $REF_ARG
    else
        # 降级到纯 pandoc
        echo "正在转换..."
        REF_DOC="${REFERENCE_DOC:-$SCRIPT_DIR/template/pandoc-template.docx}"
        pandoc "$INPUT_FILE" -o "$OUTPUT_FILE" --mathml --reference-doc="$REF_DOC"
    fi
fi

if [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "✓ 转换成功：$OUTPUT_FILE"
    ls -lh "$OUTPUT_FILE" | awk '{print "  文件大小：" $5}'
else
    echo "✗ 转换失败"
    exit 1
fi
