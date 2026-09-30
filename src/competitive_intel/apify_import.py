"""
Imports an Apify Website Content Crawler dataset into the raw store, for sites that render
with JavaScript and come back empty from fetch.py. Only URLs that pass the same selection
rules as fetch.py are kept, and an existing record is replaced only if the browser-rendered
version has more text.

Usage:  python3 src/competitive_intel/apify_import.py <datasetId>
"""
import glob
import hashlib
import json
import os
import re
import sys
from datetime import date
from urllib.parse import urlparse

import requests

from fetch import OUT_ROOT, classify, load_config, select_urls

API = "https://api.apify.com/v2/datasets/{}/items?format=json&clean=true&offset={}&limit=200" \
      "&fields=url,markdown,metadata"


def dataset_items(dataset_id: str):
    offset = 0
    while True:
        batch = requests.get(API.format(dataset_id, offset), timeout=120).json()
        if not batch:
            return
        yield from batch
        offset += len(batch)


def jsonld_questions(blocks) -> list:
    questions = []
    for block in blocks or []:
        for node in block.get("@graph", [block]) if isinstance(block, dict) else []:
            if isinstance(node, dict) and node.get("@type") == "FAQPage":
                entities = node.get("mainEntity", [])
                entities = entities if isinstance(entities, list) else [entities]
                questions += [q["name"] for q in entities if isinstance(q, dict) and q.get("name")]
    return questions


def main(dataset_id: str):
    defaults, sources = load_config()
    by_host = {s["domain"].replace("www.", ""): s for s in sources}
    wanted = {}  # normalized path per host -> allowed
    for host, source in by_host.items():
        wanted[host] = {urlparse(u).path.rstrip("/").lower() for u in select_urls(source, defaults)}

    crawl_date = date.today().isoformat()
    stats = {"imported": 0, "kept_existing": 0, "not_selected": 0}
    for item in dataset_items(dataset_id):
        parsed = urlparse(item["url"])
        host = parsed.netloc.replace("www.", "")
        source = by_host.get(host)
        path = parsed.path or "/"
        # Sites without a sitemap have no selection list; accept whatever the crawl found.
        if source is None or (len(wanted[host]) > 1 and path.rstrip("/").lower() not in wanted[host]):
            stats["not_selected"] += 1
            continue

        markdown = item.get("markdown") or ""
        # Patch the domain's latest crawl rather than opening a new, partial one.
        existing = sorted(glob.glob(os.path.join(OUT_ROOT, source["domain"], "*")))
        out_dir = existing[-1] if existing else os.path.join(OUT_ROOT, source["domain"], crawl_date)
        os.makedirs(out_dir, exist_ok=True)
        slug = (re.sub(r"[^a-zA-Z0-9]+", "_", path).strip("_") or "index")[:150]
        out_file = os.path.join(out_dir, f"{slug}.json")
        if os.path.exists(out_file) and json.load(open(out_file))["word_count"] >= len(markdown.split()):
            stats["kept_existing"] += 1
            continue

        metadata = item.get("metadata") or {}
        metadata_paths = defaults["metadata_only"] + source.get("metadata_only", [])
        content_type = classify(path, source.get("classify", []) + defaults["classify"],
                                defaults["course"] + source.get("course", []))
        metadata_only = content_type == "COURSE" or any(x in path.lower() for x in metadata_paths)
        headings = [{"level": len(m.group(1)), "text": m.group(2).strip()}
                    for m in re.finditer(r"^(#{1,3}) (.+)$", markdown, re.M)]
        record = {
            "source_domain": source["domain"],
            "tier": source.get("tier"),
            "url": item["url"],
            "crawl_date": os.path.basename(out_dir),
            "content_type": content_type,
            "capture_mode": "METADATA_ONLY" if metadata_only else "FULL",
            "content_sha256": hashlib.sha256(markdown.encode()).hexdigest(),
            "word_count": len(markdown.split()),
            "title": metadata.get("title") or "",
            "meta_description": metadata.get("description") or "",
            "headings": headings,
            "jsonld_questions": jsonld_questions(metadata.get("jsonLd")),
            "markdown": None if metadata_only else markdown,
            "fetched_via": "apify",
        }
        with open(out_file, "w") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        stats["imported"] += 1
    print(stats)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
