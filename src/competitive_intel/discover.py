"""
Sitemap discovery for every source in sources.yaml. Writes the URL list per domain to
staging/competitive_intel/sitemaps/<domain>.txt and prints a size summary.

Usage:  python3 src/competitive_intel/discover.py
"""
import gzip
import os
import re
from concurrent.futures import ThreadPoolExecutor

import requests
import yaml

USER_AGENT = "Mozilla/5.0 (compatible; research-crawler/1.0)"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "staging/competitive_intel/sitemaps"
MAX_SITEMAPS = 60


def get(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=25)
    resp.raise_for_status()
    body = resp.content
    if body[:2] == b"\x1f\x8b":
        body = gzip.decompress(body)
    return body.decode("utf-8", "replace")


def discover(domain: str) -> dict:
    roots = []
    try:
        roots = re.findall(r"(?im)^sitemap:\s*(\S+)", get(f"https://{domain}/robots.txt"))
    except requests.RequestException:
        pass
    roots = roots or [f"https://{domain}/sitemap.xml", f"https://{domain}/sitemap_index.xml"]

    pages, queue, seen = set(), list(roots), set()
    while queue and len(seen) < MAX_SITEMAPS:
        sitemap = queue.pop(0)
        if sitemap in seen:
            continue
        seen.add(sitemap)
        try:
            xml = get(sitemap)
        except requests.RequestException:
            continue
        locs = re.findall(r"<loc>\s*(?:<!\[CDATA\[)?\s*([^<\]\s]+)", xml)
        if "<sitemapindex" in xml:
            queue += locs
        else:
            pages.update(locs)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{domain}.txt"), "w") as f:
        f.write("\n".join(sorted(pages)))
    return {"domain": domain, "sitemaps": len(seen), "urls": len(pages)}


if __name__ == "__main__":
    with open(os.path.join(HERE, "sources.yaml")) as f:
        domains = [s["domain"] for s in yaml.safe_load(f)["sources"]]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for row in sorted(pool.map(discover, domains), key=lambda r: -r["urls"]):
            print(f"{row['urls']:>6} urls  {row['sitemaps']:>3} sitemaps  {row['domain']}")
