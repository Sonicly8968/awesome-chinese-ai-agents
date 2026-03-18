#!/usr/bin/env python3
"""
自动发微博脚本
从 weibo_posts.txt 轮流取文案，通过 Chrome AppleScript JS 发布
"""
import os, sys, json, logging, subprocess, re
from pathlib import Path
from datetime import datetime

REPO_DIR = Path(__file__).parent.parent
POSTS_FILE = Path(__file__).parent / "weibo_posts.txt"
STATE_FILE = Path(__file__).parent / ".weibo_state"
LOGS_DIR = REPO_DIR / "logs"

# ── 日志 ──────────────────────────────────────────────────────
LOGS_DIR.mkdir(exist_ok=True)
log_file = LOGS_DIR / f"weibo_{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler(log_file, encoding="utf-8")],
)
log = logging.getLogger(__name__)


def load_posts() -> list[str]:
    text = POSTS_FILE.read_text(encoding="utf-8")
    return [p.strip() for p in text.split("\n---\n") if p.strip()]


def get_next_index(total: int) -> int:
    if STATE_FILE.exists():
        try:
            return int(STATE_FILE.read_text().strip()) % total
        except:
            pass
    return 0


def save_index(idx: int):
    STATE_FILE.write_text(str(idx + 1))


def post_via_chrome(content: str) -> dict:
    """通过 Chrome AppleScript 执行发微博"""
    # 转义成 JS 字符串（json.dumps 自动处理 emoji/特殊字符）
    js_content = json.dumps(content)

    js_code = f"""(function() {{
    var content = {js_content};
    var xsrfMatch = document.cookie.match(/XSRF-TOKEN=([^;]+)/);
    if (!xsrfMatch) return JSON.stringify({{error: 'NO_XSRF', cookies: document.cookie.substring(0,100)}});
    var xsrf = xsrfMatch[1];
    var body = 'content=' + encodeURIComponent(content) + '&visible=0';
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/ajax/statuses/update', false);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-Xsrf-Token', xsrf);
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.withCredentials = true;
    xhr.send(body);
    return xhr.responseText.substring(0, 500);
}})()"""

    # 转义 JS 代码供 AppleScript 使用（把 " 换成 \" ）
    js_escaped = js_code.replace('\\', '\\\\').replace('"', '\\"')

    apple_script = f'''
tell application "Google Chrome"
    set wbTab to missing value
    repeat with w in windows
        repeat with t in tabs of w
            set u to URL of t
            if u contains "weibo.com" and u does not contain "passport" and u does not contain "login" then
                set wbTab to t
                exit repeat
            end if
        end repeat
        if wbTab is not missing value then exit repeat
    end repeat

    if wbTab is missing value then
        set wbTab to make new tab at end of tabs of window 1
        set URL of wbTab to "https://weibo.com/"
        delay 4
    end if

    set result to execute wbTab javascript "{js_escaped}"
    return result
end tell
'''
    result = subprocess.run(
        ["osascript", "-e", apple_script],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript 失败: {result.stderr[:200]}")

    resp_text = result.stdout.strip()
    try:
        return json.loads(resp_text)
    except:
        return {"raw": resp_text}


def main():
    posts = load_posts()
    if not posts:
        log.error("weibo_posts.txt 为空")
        sys.exit(1)

    total = len(posts)
    idx = get_next_index(total)
    content = posts[idx]

    log.info(f"📝 发布第 {idx+1}/{total} 条")
    log.info(f"预览: {content[:60]}...")

    try:
        resp = post_via_chrome(content)
    except Exception as e:
        log.error(f"❌ 调用失败: {e}")
        sys.exit(1)

    log.info(f"响应: {json.dumps(resp, ensure_ascii=False)[:200]}")

    # 判断成功（直接解析 or 从 raw 字段二次解析）
    mid = None
    if isinstance(resp, dict):
        mid = resp.get("data", {}).get("idstr")
        if not mid and "raw" in resp:
            try:
                inner = json.loads(resp["raw"])
                mid = inner.get("data", {}).get("idstr")
            except:
                import re
                m = re.search(r'"idstr"\s*:\s*"(\d+)"', resp.get("raw", ""))
                if m: mid = m.group(1)
    if mid:
        log.info(f"✅ 发布成功！微博 ID: {mid}")
        log.info(f"   链接: https://weibo.com/{mid}")
        save_index(idx)
    else:
        err = resp.get("error") or resp.get("raw") or resp
        log.error(f"❌ 发布失败: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
