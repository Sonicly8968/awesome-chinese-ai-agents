#!/bin/bash
# 自动发微博脚本
# 从 weibo_posts.txt 轮流取文案，通过 Chrome AppleScript 发布

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
POSTS_FILE="$REPO_DIR/scripts/weibo_posts.txt"
STATE_FILE="$REPO_DIR/scripts/.weibo_state"
LOG_DIR="$REPO_DIR/logs"
LOG_FILE="$LOG_DIR/weibo_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

# 读取上次发布的索引
LAST_IDX=0
[ -f "$STATE_FILE" ] && LAST_IDX=$(cat "$STATE_FILE")

# 读取文案列表（每条用 --- 分隔）
TOTAL=$(grep -c "^---$" "$POSTS_FILE" 2>/dev/null || echo 0)
TOTAL=$((TOTAL + 1))

# 计算本次索引（循环轮播）
NEXT_IDX=$(( LAST_IDX % TOTAL ))

# 提取第 N 条文案（0-indexed）
CONTENT=$(awk -v idx="$NEXT_IDX" 'BEGIN{i=0} /^---$/{i++; next} i==idx{print}' "$POSTS_FILE")

if [ -z "$CONTENT" ]; then
    log "❌ 文案为空（index=$NEXT_IDX），跳过"
    exit 1
fi

log "📝 准备发布第 $((NEXT_IDX+1))/$TOTAL 条文案"
log "内容预览: $(echo "$CONTENT" | head -1 | cut -c1-50)..."

# 把内容写入临时文件，避免 AppleScript 字符串注入问题
TMP_CONTENT=$(mktemp /tmp/weibo_content_XXXX.txt)
echo "$CONTENT" > "$TMP_CONTENT"

# 把内容做成 JSON 字符串（Python 处理转义）
JSON_CONTENT=$(python3 -c "
import sys, json
txt = open('$TMP_CONTENT').read().strip()
print(json.dumps(txt))
")

rm -f "$TMP_CONTENT"

# 通过 Chrome AppleScript 执行发布
RESULT=$(osascript - <<ENDSCRIPT
set jsonContent to "$JSON_CONTENT"

tell application "Google Chrome"
    set wbTab to missing value
    repeat with w in windows
        repeat with t in tabs of w
            set tabUrl to URL of t
            if tabUrl contains "weibo.com" and tabUrl does not contain "passport" and tabUrl does not contain "login" then
                set wbTab to t
                exit repeat
            end if
        end repeat
        if wbTab is not missing value then exit repeat
    end repeat

    if wbTab is missing value then
        set newTab to make new tab at end of tabs of window 1
        set URL of newTab to "https://weibo.com/"
        delay 4
        set wbTab to newTab
    end if

    set jsCode to "
        (function() {
            var content = " & jsonContent & ";
            var xsrfMatch = document.cookie.match(/XSRF-TOKEN=([^;]+)/);
            if (!xsrfMatch) return 'NO_XSRF';
            var xsrf = xsrfMatch[1];
            var body = 'content=' + encodeURIComponent(content) + '&visible=0';
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/ajax/statuses/update', false);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.setRequestHeader('X-Xsrf-Token', xsrf);
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.withCredentials = true;
            xhr.send(body);
            return xhr.responseText.substring(0, 300);
        })()
    "
    set result to execute wbTab javascript jsCode
    return result
end tell
ENDSCRIPT
)

log "API 响应: $RESULT"

# 判断是否成功（检查返回 JSON 里有 id 字段）
if echo "$RESULT" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    mid = d.get('data', {}).get('idstr', '')
    if mid:
        print('SUCCESS:' + mid)
        sys.exit(0)
except:
    pass
sys.exit(1)
" 2>/dev/null; then
    MID=$(echo "$RESULT" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d['data']['idstr'])")
    log "✅ 发布成功！微博 ID: $MID | https://weibo.com/$MID"
    # 更新索引
    echo $((NEXT_IDX + 1)) > "$STATE_FILE"
else
    log "❌ 发布失败，响应: $RESULT"
    exit 1
fi
