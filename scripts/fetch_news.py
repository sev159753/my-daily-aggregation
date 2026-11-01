#!/usr/bin/env python3
"""聚合热点新闻：科技(HN) + 综合国内热点(百度/知乎/微博)。输出 news.json。

设计：每个源独立注册到 REGISTRY，单源失败不影响其他源（优雅降级）。
新增源 = 写一个 fetch_xxx 函数 + 在 config.NEWS_SOURCES 加一项。
"""
import json
import os
import datetime

from common import http_get
from config import OUTPUT_DIR, NEWS_FILE, NEWS_PER_SOURCE, NEWS_SOURCES

REGISTRY = {}


def source(name, category):
    def deco(fn):
        REGISTRY[name] = (category, fn)
        return fn
    return deco


@source("hackernews", "tech")
def fetch_hn(limit):
    ids = http_get(
        "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=20
    ).json()[:limit]
    items = []
    for id in ids:
        try:
            it = http_get(
                f"https://hacker-news.firebaseio.com/v0/item/{id}.json",
                timeout=8, retries=1,
            ).json()
        except Exception:  # noqa: BLE001
            continue
        if not it:
            continue
        items.append({
            "title": it.get("title"),
            "url": it.get("url") or f"https://news.ycombinator.com/item?id={id}",
            "score": it.get("score"),
            "by": it.get("by"),
        })
    return items


@source("baidu", "domestic")
def fetch_baidu(limit):
    resp = http_get(
        "https://top.baidu.com/api/board?platform=wise&tab=realtime", timeout=20
    ).json()
    items = []
    for card in resp.get("data", {}).get("cards", []):
        # 百度返回结构：card['content'] = [{'content': [真实条目...]}]
        inner = card.get("content", [])
        real = inner[0].get("content", []) if inner and isinstance(inner[0], dict) else inner
        for c in real:
            items.append({
                "title": c.get("word"),
                "url": c.get("url"),
                "hot": c.get("hotScore"),
            })
            if len(items) >= limit:
                return items
    return items


@source("zhihu", "domestic")
def fetch_zhihu(limit):
    url = f"https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit={limit}&desktop=true"
    resp = http_get(url, timeout=20).json()
    items = []
    for d in resp.get("data", [])[:limit]:
        t = d.get("target", {})
        items.append({
            "title": t.get("title"),
            "url": d.get("detailUrl") or f"https://www.zhihu.com/question/{t.get('id')}",
            "hot": d.get("detail_text"),
        })
    return items


@source("weibo", "domestic")
def fetch_weibo(limit):
    resp = http_get(
        "https://weibo.com/ajax/side/hotSearch",
        timeout=20, headers={"Referer": "https://weibo.com/"},
    ).json()
    items = []
    for r in resp.get("data", {}).get("realtime", [])[:limit]:
        word = r.get("word")
        items.append({
            "title": word,
            "url": f"https://s.weibo.com/weibo?q=%23{word}%23",
            "hot": r.get("num"),
        })
    return items


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sources_out = []
    for name in NEWS_SOURCES:
        if name not in REGISTRY:
            print(f"news: unknown source {name}, skip")
            continue
        category, fn = REGISTRY[name]
        try:
            items = [i for i in fn(NEWS_PER_SOURCE) if i.get("title")]
            sources_out.append({
                "name": name, "category": category,
                "count": len(items), "items": items,
            })
            print(f"news: {name} -> {len(items)} items")
        except Exception as e:  # noqa: BLE001
            print(f"news: {name} failed: {e}")
            sources_out.append({
                "name": name, "category": category,
                "count": 0, "items": [], "error": str(e),
            })
    data = {
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sources": sources_out,
    }
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"news: wrote -> {NEWS_FILE}")


if __name__ == "__main__":
    main()
