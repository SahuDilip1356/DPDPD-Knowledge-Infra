#!/usr/bin/env python3
"""Classify curated DPDPA reading-list crawls into unpublished Opinion records.

Merges Apify page captures with harvest/curated_dpdpa_reading_list.json.
Does not publish Knowledge Objects. DPDPA.com and other competitor pages stay
in the competitive-intelligence corpus. Independent articles become Layer 4
Knowledge Infra opinions. Verbatim text is kept for internal evidence only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse, urlunparse

from classify_pages import _text_of, _title_of, _url_of, classify_item

ROOT = Path(__file__).resolve().parent
SEED_PATH = ROOT / "curated_dpdpa_reading_list.json"


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    path = unquote(parsed.path).rstrip("/") or "/"
    query = parsed.query
    if parsed.hostname and "dlapiperdataprotection.com" in parsed.hostname:
        query = query  # keep country selector
    else:
        # Drop tracking params; keep meaningful selectors such as t=law&c=IN.
        keep = []
        for pair in query.split("&") if query else []:
            key = pair.split("=", 1)[0].lower()
            if key in {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"}:
                continue
            keep.append(pair)
        query = "&".join(keep)
    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return urlunparse((parsed.scheme.lower(), host, path.lower(), "", query, ""))


def seed_index(seed: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for bucket in ("knowledge_infra", "competitive_intelligence"):
        for item in seed.get(bucket, []):
            urls = [item["url"], *item.get("alt_urls", [])]
            for url in urls:
                indexed[normalize_url(url)] = item
    return indexed


def load_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    stripped = raw.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        data = json.loads(stripped)
        return [row for row in data if isinstance(row, dict)]
    items: list[dict[str, Any]] = []
    for line in stripped.splitlines():
        if not line.strip():
            continue
        parsed = json.loads(line)
        if isinstance(parsed, dict):
            items.append(parsed)
    return items


def match_seed(item: dict[str, Any], indexed: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [
        item.get("url"),
        item.get("loadedUrl"),
        item.get("canonicalUrl"),
        (item.get("crawl") or {}).get("loadedUrl") if isinstance(item.get("crawl"), dict) else None,
        (item.get("metadata") or {}).get("canonicalUrl") if isinstance(item.get("metadata"), dict) else None,
    ]
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.startswith("http"):
            matched = indexed.get(normalize_url(candidate))
            if matched:
                return matched
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify curated reading-list harvest.")
    parser.add_argument("input_paths", nargs="+", help="JSON/JSONL Apify dataset exports")
    parser.add_argument("--seed", default=str(SEED_PATH))
    parser.add_argument("--ki-out", default="staging/harvest/classified_curated_ki.jsonl")
    parser.add_argument("--ci-out", default="staging/harvest/classified_curated_ci.jsonl")
    args = parser.parse_args()

    seed = json.loads(Path(args.seed).read_text(encoding="utf-8"))
    indexed = seed_index(seed)

    crawled: list[dict[str, Any]] = []
    for path_str in args.input_paths:
        crawled.extend(load_json_or_jsonl(Path(path_str)))

    ki_records: list[dict[str, Any]] = []
    ci_records: list[dict[str, Any]] = []
    unmatched = 0
    dropped = 0

    seen_urls: set[str] = set()
    for item in crawled:
        seed_row = match_seed(item, indexed)
        if seed_row is None:
            unmatched += 1
            continue
        record = classify_item(item)
        if record is None:
            # Curated list includes a Latham PDF under /admin/; keep it if seed matched.
            url = _url_of(item)
            text = _text_of(item)
            if not url or len(text.strip()) < 80:
                dropped += 1
                continue
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            record = {
                "suggested_urn": f"urn:ki:in:dpdp:opinion:harvest:lw-com:{digest[:12]}",
                "title": _title_of(item, url),
                "source": {
                    "name": "lw-com",
                    "layer": seed_row["layer"],
                    "url": url,
                    "hash": digest,
                },
                "date": date.today().isoformat(),
                "page_type": "explainer",
                "topics": seed_row.get("themes", []),
                "entities": ["Opinion", "Organization"],
                "summary": text.strip().replace("\n", " ")[:400],
                "confidence_score": 0.5,
                "stack_eligible": True,
                "exclude_reason": None,
                "review_status": "pending",
                "verbatim_kept_for": "internal_evidence_only",
                "evidence_excerpt": text.strip()[:1200],
            }

        title_blob = f"{record.get('title', '')} {(item.get('metadata') or {}).get('title', '')}".lower()
        if "page not found" in title_blob:
            dropped += 1
            continue

        list_id = seed_row["list_id"]
        source_url = record["source"]["url"]
        key = normalize_url(source_url)
        if key in seen_urls:
            continue
        seen_urls.add(key)
        existing = next((row for row in ki_records + ci_records if row.get("list_id") == list_id), None)
        if existing and len(existing.get("evidence_excerpt") or "") >= len(record.get("evidence_excerpt") or ""):
            continue
        if existing:
            for bucket in (ki_records, ci_records):
                if existing in bucket:
                    bucket.remove(existing)

        record["list_id"] = seed_row["list_id"]
        record["title"] = seed_row["title"]
        record["tray"] = seed_row["tray"]
        record["corpus"] = seed_row["corpus"]
        record["themes"] = seed_row.get("themes", [])
        record["source"]["name"] = seed_row["source"]
        record["source"]["layer"] = seed_row["layer"]
        record["confidence_score"] = 0.5 if seed_row["layer"] == 4 else 0.3
        record["publish"] = False
        record["review_status"] = "pending"
        if seed_row.get("note"):
            record["note"] = seed_row["note"]

        if seed_row["corpus"] == "knowledge_infra":
            ki_records.append(record)
        else:
            ci_records.append(record)

    for out_path, records in ((args.ki_out, ki_records), (args.ci_out, ci_records)):
        dest = Path(out_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Read {len(crawled)} crawled pages")
    print(f"Knowledge Infra opinions: {len(ki_records)} -> {args.ki_out}")
    print(f"Competitive intelligence: {len(ci_records)} -> {args.ci_out}")
    print(f"Unmatched crawled pages: {unmatched}")
    print(f"Dropped thin/empty pages: {dropped}")
    print("Publish=false. Nothing entered Setu.")


if __name__ == "__main__":
    main()
