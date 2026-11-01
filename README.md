# 个人云端聚合服务（GitHub Trending + 每日热点）

每日自动抓取并生成两份静态 JSON，供个人 APP 拉取展示。纯公开数据、无密钥、零服务器费用。

- `github_trending.json` — GitHub 每日趋势项目
- `news.json` — 科技热点（Hacker News）+ 综合国内热点（百度/知乎/微博）

## 本地运行（验证/调试）

```bash
pip install -r requirements.txt
python scripts/fetch_trending.py
python scripts/fetch_news.py
# 产物在 output/ 目录
```

## 部署到 GitHub（一次性，约 3 分钟）

1. 在 GitHub 新建仓库（**推荐 public**，免 token；数据本身全公开）。
2. 进入本目录，初始化并推送：
   ```bash
   git init
   git add .
   git commit -m "init cloud aggregation"
   git branch -M main
   git remote add origin https://github.com/<你的用户名>/<仓库名>.git
   git push -u origin main
   ```
3. 开启 Pages：仓库 **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: gh-pages → Save**。
4. 开启 Actions：仓库 **Actions** 标签页，允许运行；可手动 **Run workflow** 一次验证。
5. 每日 UTC 0:00（北京时间 08:00）自动跑，结果发布到 `gh-pages` 分支。

## APP 端配置的两个 URL

```
https://<你的用户名>.github.io/<仓库名>/github_trending.json
https://<你的用户名>.github.io/<仓库名>/news.json
```

> 原生 APP（Flutter）发起 HTTP 请求不受浏览器 CORS 限制，直接拉取即可。

## 如何调整（最易扩展点）

| 想改什么 | 改哪里 |
|---|---|
| 增加/减少新闻源 | `scripts/config.py` 的 `NEWS_SOURCES` 列表 + 在 `fetch_news.py` 注册同名函数 |
| 抓取条数 | `config.py` 的 `TRENDING_LIMIT` / `NEWS_PER_SOURCE` |
| 执行频率 | `.github/workflows/daily.yml` 的 `cron`（如 `0 12 * * *` 改中午） |
| 趋势周期（周/月） | `fetch_trending.py` 的 `URL` 改 `?since=weekly` |
| 数据源挂了 | 单源失败自动跳过，不影响其他源与 APP |
