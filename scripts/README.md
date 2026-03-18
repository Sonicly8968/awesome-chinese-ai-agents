# scripts/ 说明

## collect_resources.py

自动从多个渠道收集中文 AI Agent 相关项目，追加到 `collected_resources.md` 并推送到 GitHub。

### 渠道

| 渠道 | 说明 |
|------|------|
| GitHub API 搜索 | 搜索最近7天更新的相关项目 |
| GitHub Trending | 爬取 Daily Trending |
| Hacker News | 搜索最近24小时的相关内容 |

### 用法

```bash
# 正常运行（写入文件 + git push）
python3 scripts/collect_resources.py

# 只预览不写入
python3 scripts/collect_resources.py --dry-run
```

### 环境变量

| 变量 | 说明 |
|------|------|
| `GITHUB_TOKEN` | GitHub API Token（可选，提高速率限制） |

如果没有设置，会自动从 `gh auth token` 获取。

### 自动执行

通过 cron 每天 08:00 / 13:00 / 19:00 自动运行：

```
0 8,13,19 * * * /path/to/run_collect.sh
```

日志存储在 `logs/collect_YYYY-MM-DD.log`（不推送到 GitHub）。
