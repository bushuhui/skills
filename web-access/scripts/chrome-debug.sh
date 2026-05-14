#!/bin/bash
# Chrome remote debugging 守护脚本
# 使用 nohup 后台运行，立即返回

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 避免重复启动：检查 PID 文件
PID_FILE="${TMPDIR:-/tmp}/chrome-debug-${1:-9222}.pid"
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Chrome debug already running (PID=$OLD_PID)"
        exit 0
    fi
    rm -f "$PID_FILE"
fi

LOG_FILE="${TMPDIR:-/tmp}/chrome-debug-nohup.log"

echo "Starting Chrome debug daemon in background..."
nohup python3 "$SCRIPT_DIR/chrome-debug.py" "$@" > "$LOG_FILE" 2>&1 &

echo "Daemon started (PID=$!)"
echo "Nohup log: $LOG_FILE"
