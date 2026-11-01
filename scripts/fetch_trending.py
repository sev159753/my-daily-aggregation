#!/usr/bin/env python3
"""抓取 GitHub Trending（每日），输出 github_trending.json。"""
import json
import os
import re
import datetime
from bs4 import BeautifulSoup

from common import http_get
from config import OUTPUT_DIR, TRENDING_FILE, TRENDING_LIMIT

URL = "https://github.com/trending?since=daily"


def _clean_num(s):
    if not s:
        return None
    m = re.search(r"[\d,]+", s.replace(".", ""))
    return int(m.group().replace(",", "")) if m else None


def fetch():
    resp = http_get(URL, timeout=20)
    soup = BeautifulSoup(resp.text, "html.parser")
    out = []
    for art in soup.select("article.Box-row"):
        h2 = art.select_one("h2 a")
        if not h2:
            continue
        href = h2.get("href", "").strip()
        desc_el = art.select_one("p")
        desc = desc_el.get_text(" ", strip=True) if desc_el else ""
        lang_el = art.select_one('[itemprop="programmingLanguage"]')
        lang = lang_el.get_text(strip=True) if lang_el else None
        stars = None
        for a in art.select("a.Link--muted"):
            if "/stargazers" in a.get("href", ""):
                stars = _clean_num(a.get_text(" ", strip=True))
                break
        today = None
        span = art.select_one("span.d-inline-block.float-sm-right")
        if span:
            today = _clean_num(span.get_text(" ", strip=True))
        out.append({
            "repo": href.strip("/"),
            "url": "https://github.com" + href,
            "description": desc,
            "language": lang,
            "stars": stars,
            "today_stars": today,
        })
        if len(out) >= TRENDING_LIMIT:
            break
    return out


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    items = fetch()
    data = {
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "count": len(items),
        "items": items,
    }
    with open(TRENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"trending: wrote {len(items)} items -> {TRENDING_FILE}")


if __name__ == "__main__":
    main()
