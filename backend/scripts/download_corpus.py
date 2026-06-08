"""
从 chinese-poetry GitHub 仓库下载语料 JSON。

用法：
    python scripts/download_corpus.py

需要网络访问 GitHub（配置代理或使用镜像）：
    set HTTP_PROXY=http://127.0.0.1:7890
    set HTTPS_PROXY=http://127.0.0.1:7890
"""

import json
import os
import time
from pathlib import Path

import httpx

DATA_DIR = Path(__file__).parent.parent / "data"

# chinese-poetry 原始 JSON 文件的 raw 地址
# 唐诗全集（分卷）+ 宋词精选
CORPUS_FILES = {
    "tangshi": [
        ("https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master/唐诗三百首/唐诗三百首.json", "tangshi_300.json"),
    ],
    "songci": [
        ("https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master/宋词/宋词三百首.json", "songci_300.json"),
    ],
}

GITHUB_RAW = "https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master"
GHPROXY = "https://ghproxy.cn/https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master"

# 优先走 ghproxy（国内可达），再试原始 GitHub raw（需代理）
CDN_FILES = [
    (f"{GHPROXY}/唐诗三百首/唐诗三百首.json", f"{GITHUB_RAW}/唐诗三百首/唐诗三百首.json", "tangshi_300.json"),
    (f"{GHPROXY}/宋词/宋词三百首.json", f"{GITHUB_RAW}/宋词/宋词三百首.json", "songci_300.json"),
]


def download(url: str, dest: Path, client: httpx.Client) -> bool:
    try:
        r = client.get(url, timeout=30, follow_redirects=True)
        r.raise_for_status()
        dest.write_bytes(r.content)
        print(f"  OK  {dest.name}  ({len(r.content) // 1024} KB)")
        return True
    except Exception as e:
        print(f"  FAIL  {url}: {e}")
        return False


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    proxies = {"https://": proxy, "http://": proxy} if proxy else None
    client = httpx.Client(proxies=proxies)

    print("下载语料到", DATA_DIR)
    for proxy_url, fallback_url, filename in CDN_FILES:
        dest = DATA_DIR / filename
        if dest.exists():
            print(f"  SKIP  {filename} 已存在")
            continue
        print(f"下载 {filename} ...")
        for url in (proxy_url, fallback_url):
            if download(url, dest, client):
                break
        time.sleep(0.3)

    client.close()

    # 简单验证
    total = 0
    for f in DATA_DIR.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        count = len(data) if isinstance(data, list) else 0
        print(f"{f.name}: {count} 首")
        total += count
    print(f"\n合计 {total} 首，语料准备完成。")
    print("下一步运行: python scripts/build_index.py")


if __name__ == "__main__":
    main()
