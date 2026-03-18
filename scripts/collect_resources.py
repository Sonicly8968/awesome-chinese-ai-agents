#!/usr/bin/env python3
"""
自动收集中文 AI Agent 相关项目，更新 collected_resources.md 并 push 到 GitHub
用法：
  python3 scripts/collect_resources.py           # 正常运行
  python3 scripts/collect_resources.py --dry-run # 只打印不写入
"""

import os
import re
import sys
import json
import time
import logging
import argparse
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── 路径配置 ────────────────────────────────────────────────
REPO_DIR = Path(__file__).parent.parent
COLLECTED_MD = REPO_DIR / "collected_resources.md"
README_MD = REPO_DIR / "README.md"
LOGS_DIR = REPO_DIR / "logs"

# ── 搜索关键词 ───────────────────────────────────────────────
GITHUB_QUERIES = [
    "Chinese AI agent",
    "中文 AI agent",
    "中文 LLM agent",
    "AI 助手 Python",
    "Chinese LLM tool",
    "智能体 开源",
    "国产 LLM agent",
]

# 过滤掉的 GitHub 系统账号（非真实用户/项目）
GITHUB_SYSTEM_OWNERS = {
    "sponsors", "apps", "marketplace", "trending", "explore",
    "features", "about", "contact", "security", "pricing",
    "topics", "collections", "enterprise", "team",
}

# 过滤用的关键词（项目名/描述中至少含其一，才算相关）
RELEVANCE_KEYWORDS = [
    "agent", "llm", "gpt", "ai", "chat", "智能", "助手", "机器人",
    "langchain", "rag", "embedding", "中文", "chinese", "qwen", "deepseek",
    "workflow", "automation", "copilot", "bot",
]


# ── 日志配置 ─────────────────────────────────────────────────
def setup_logger(dry_run: bool) -> logging.Logger:
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / f"collect_{datetime.now().strftime('%Y-%m-%d')}.log"
    handlers = [logging.StreamHandler(sys.stdout)]
    if not dry_run:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    return logging.getLogger(__name__)


# ── GitHub Token ─────────────────────────────────────────────
def get_github_token() -> str | None:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        return token
    try:
        r = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return None


# ── HTTP 工具 ────────────────────────────────────────────────
def http_get(url: str, headers: dict = None, timeout: int = 15) -> dict | None:
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "awesome-chinese-ai-agents-bot/1.0")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def http_get_text(url: str, headers: dict = None, timeout: int = 15) -> str | None:
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


# ── 已有项目去重 ──────────────────────────────────────────────
def get_existing_urls() -> set[str]:
    """从 collected_resources.md 和 README.md 提取所有 GitHub URL"""
    urls = set()
    pattern = re.compile(r'https://github\.com/([\w.-]+/[\w.-]+)')
    for md_file in [COLLECTED_MD, README_MD]:
        if md_file.exists():
            text = md_file.read_text(encoding="utf-8")
            for m in pattern.finditer(text):
                # 标准化：去掉末尾 .git / 路径
                repo = m.group(1).strip("/").lower()
                # 只保留 owner/repo 形式（不含子路径）
                parts = repo.split("/")
                if len(parts) >= 2:
                    urls.add(f"https://github.com/{parts[0]}/{parts[1]}")
    return urls


# ── 相关性过滤 ────────────────────────────────────────────────
def is_relevant(name: str, description: str) -> bool:
    # 过滤系统账号（如 sponsors/explore, apps/dependabot）
    owner = name.split("/")[0].lower() if "/" in name else ""
    if owner in GITHUB_SYSTEM_OWNERS:
        return False
    text = f"{name} {description}".lower()
    return any(kw in text for kw in RELEVANCE_KEYWORDS)


# ── 数据源 1：GitHub API 搜索 ─────────────────────────────────
def fetch_github_api(token: str | None) -> list[dict]:
    results = []
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    # 7天内更新的项目
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

    seen = set()
    for query in GITHUB_QUERIES:
        q = urllib.parse.quote(f"{query} pushed:>{since}")
        url = f"https://api.github.com/search/repositories?q={q}&sort=updated&per_page=20"
        data = http_get(url, headers)
        if not data or "items" not in data:
            continue
        time.sleep(1)  # 避免触发频率限制

        for item in data["items"]:
            repo_url = item["html_url"].lower().rstrip("/")
            if repo_url in seen:
                continue
            seen.add(repo_url)
            if not is_relevant(item.get("name", ""), item.get("description") or ""):
                continue
            results.append({
                "name": item["full_name"],
                "url": item["html_url"],
                "description": item.get("description") or "暂无描述",
                "stars": item.get("stargazers_count", 0),
                "source": "GitHub API 搜索",
            })

    return results


# ── 数据源 2：GitHub Trending（HTML 爬取） ────────────────────
def fetch_github_trending() -> list[dict]:
    results = []
    urls_to_scrape = [
        "https://github.com/trending/python?since=daily",
        "https://github.com/trending?since=daily",
    ]
    for url in urls_to_scrape:
        html = http_get_text(url)
        if not html:
            continue
        # 解析 trending 列表中的仓库
        repos = re.findall(r'href="(/[\w.-]+/[\w.-]+)"[^>]*>', html)
        descriptions = re.findall(r'<p\s+class="col-9[^"]*"[^>]*>\s*(.*?)\s*</p>', html, re.DOTALL)
        stars_list = re.findall(r'aria-label="(\d[\d,]*) stars this repository"', html)

        seen = set()
        for i, repo_path in enumerate(repos[:30]):
            parts = repo_path.strip("/").split("/")
            if len(parts) != 2:
                continue
            repo_url = f"https://github.com{repo_path}"
            if repo_url in seen:
                continue
            seen.add(repo_url)
            name = "/".join(parts)
            desc = descriptions[i].strip() if i < len(descriptions) else ""
            desc = re.sub(r'<[^>]+>', '', desc).strip()
            stars_raw = stars_list[i].replace(",", "") if i < len(stars_list) else "0"
            try:
                stars = int(stars_raw)
            except ValueError:
                stars = 0
            if not is_relevant(name, desc):
                continue
            results.append({
                "name": name,
                "url": repo_url,
                "description": desc or "暂无描述",
                "stars": stars,
                "source": "GitHub Trending",
            })
        time.sleep(1)

    return results


# ── 数据源 3：Hacker News ─────────────────────────────────────
def fetch_hacker_news() -> list[dict]:
    results = []
    queries = ["Chinese AI agent", "LLM agent China", "AI assistant Chinese"]
    seen = set()

    for query in queries:
        q = urllib.parse.quote(query)
        url = f"https://hn.algolia.com/api/v1/search?query={q}&tags=story&numericFilters=created_at_i>{int(time.time()) - 86400}"
        data = http_get(url)
        if not data or "hits" not in data:
            continue

        for hit in data["hits"]:
            link = hit.get("url", "")
            title = hit.get("title", "")
            if not link or "github.com" not in link:
                continue
            # 只处理 GitHub 链接
            m = re.search(r'github\.com/([\w.-]+/[\w.-]+)', link)
            if not m:
                continue
            repo_url = f"https://github.com/{m.group(1)}"
            if repo_url in seen:
                continue
            seen.add(repo_url)
            if not is_relevant(title, ""):
                continue
            results.append({
                "name": m.group(1),
                "url": repo_url,
                "description": title,
                "stars": 0,
                "source": "Hacker News",
            })
        time.sleep(0.5)

    return results


# ── 格式化新增内容 ─────────────────────────────────────────────
def format_new_section(new_items: list[dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"\n## 自动收集 - {now}\n"]

    # 按来源分组
    by_source: dict[str, list[dict]] = {}
    for item in new_items:
        by_source.setdefault(item["source"], []).append(item)

    for source, items in by_source.items():
        lines.append(f"\n### {source}\n")
        for i, item in enumerate(items, 1):
            stars_str = f" ({item['stars']:,} stars)" if item["stars"] > 0 else ""
            lines.append(f"{i}. **{item['name']}**{stars_str} - 来源: {source}")
            lines.append(f"   - {item['url']}")
            lines.append(f"   - {item['description']}")
            lines.append("")

    return "\n".join(lines)


# ── Git 提交 & Push ───────────────────────────────────────────
def git_commit_push(count: int, log: logging.Logger) -> bool:
    try:
        subprocess.run(["git", "add", "collected_resources.md", "logs/"], cwd=REPO_DIR, check=True)
        msg = f"auto: 自动收集 {count} 个新项目 [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"
        subprocess.run(["git", "commit", "-m", msg], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        log.info(f"✅ 已提交并推送到 GitHub（{count} 个新项目）")
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"❌ Git 操作失败: {e}")
        return False


# ── 主流程 ────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="只打印，不写入文件")
    args = parser.parse_args()

    log = setup_logger(args.dry_run)
    mode = "[DRY RUN] " if args.dry_run else ""
    log.info(f"{mode}开始收集... 渠道: GitHub API, GitHub Trending, HN")

    token = get_github_token()
    if token:
        log.info("🔑 GitHub Token: 已获取")
    else:
        log.info("⚠️  GitHub Token: 未找到，API 限速较低（60次/小时）")

    # 获取已有 URL
    existing_urls = get_existing_urls()
    log.info(f"📋 已有项目 URL 数: {len(existing_urls)}")

    # 并发收集
    all_raw: list[dict] = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {
            pool.submit(fetch_github_api, token): "GitHub API",
            pool.submit(fetch_github_trending): "GitHub Trending",
            pool.submit(fetch_hacker_news): "Hacker News",
        }
        for future in as_completed(futures):
            source = futures[future]
            try:
                items = future.result()
                log.info(f"  {source}: 获取到 {len(items)} 个候选项目")
                all_raw.extend(items)
            except Exception as e:
                log.warning(f"  {source}: 失败 ({e})")

    # 去重（跨来源去重 + 排除已有）
    new_items = []
    seen_urls = set()
    for item in all_raw:
        url_lower = item["url"].lower().rstrip("/")
        if url_lower in existing_urls:
            continue
        if url_lower in seen_urls:
            continue
        seen_urls.add(url_lower)
        new_items.append(item)

    # 按 stars 排序
    new_items.sort(key=lambda x: x["stars"], reverse=True)

    log.info(f"✨ 去重后新项目: {len(new_items)} 个")

    if not new_items:
        log.info("📭 没有新项目，退出")
        return

    # 打印详情
    for item in new_items:
        log.info(f"  + {item['name']} ({item['stars']} ⭐) [{item['source']}]")
        log.info(f"    {item['url']}")
        log.info(f"    {item['description'][:80]}")

    if args.dry_run:
        log.info(f"\n[DRY RUN] 以上 {len(new_items)} 个项目将被追加到 collected_resources.md")
        return

    # 追加到 collected_resources.md
    section = format_new_section(new_items)
    with open(COLLECTED_MD, "a", encoding="utf-8") as f:
        f.write(section)
    log.info(f"📝 已追加到 {COLLECTED_MD.name}")

    # Git 提交推送
    git_commit_push(len(new_items), log)


if __name__ == "__main__":
    main()
