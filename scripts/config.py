import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "output")
TRENDING_FILE = os.path.join(OUTPUT_DIR, "github_trending.json")
NEWS_FILE = os.path.join(OUTPUT_DIR, "news.json")

TRENDING_LIMIT = 25      # 趋势抓取条数
NEWS_PER_SOURCE = 15     # 每个新闻源条数

# 新闻源（增删只需改此列表，并在 fetch_news.py 的 REGISTRY 注册对应函数）
# 顺序即展示顺序：hackernews=科技, baidu/weibo=综合国内热点
# 注意：zhihu 接口需登录 cookie（401），已移出默认；如需启用见 fetch_news.fetch_zhihu 注释
NEWS_SOURCES = ["hackernews", "baidu", "weibo"]
