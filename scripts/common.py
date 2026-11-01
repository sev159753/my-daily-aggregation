import requests

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def http_get(url, timeout=15, headers=None, retries=2):
    h = dict(DEFAULT_HEADERS)
    if headers:
        h.update(headers)
    last = None
    for _ in range(retries + 1):
        try:
            r = requests.get(url, headers=h, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as e:  # noqa: BLE001 - 统一重试后抛出
            last = e
    raise last
