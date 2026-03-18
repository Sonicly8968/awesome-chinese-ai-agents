#!/bin/bash
# 雪球资源自动收集 wrapper
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$REPO_DIR/logs"
LOG_FILE="$LOG_DIR/collect_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ===== 开始自动收集 =====" >> "$LOG_FILE"

python3 "$REPO_DIR/scripts/collect_resources.py" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 退出码: $EXIT_CODE" >> "$LOG_FILE"
