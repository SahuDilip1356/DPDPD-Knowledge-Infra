#!/usr/bin/env python3
"""Classify harvested competitor pages into staging Opinion records.

Drops training/certification/course/academy URLs. Does not publish Knowledge
Objects and does not fine-tune a model. Output is Layer 4–5 harvest JSONL
ready for human review, then factory structuring.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

DROP_SUBSTRINGS = (
    "login",
    "signin",
    "signup",
    "/app/",
    "/admin",
    "/dashboard",
    "course",
    "certif",
    "training",
    "academy",
    "career",
    "/cart",
    "checkout",
    "wp-login",
    "wp-admin",
    "examination",
    "dpdpa-module",
    "/ccl.html",
    "cookiepolicy",
    "disclaimer.html",
)

STACK_EXCLUDE = (
    "training",
    "certification",
    "certificate",
    "certified",
    "course",
    "academy",
    "examination",
    "quiz",
)

LAYER_OVERRIDES = {
    "cadp.in": 4,
    "dpdpacomplianceanalyser.com": 4,
}

TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Consent": ("consent", "purpose limitation", "withdraw"),
    "Notice": ("privacy notice", "itemised notice", "section 5"),
    "Children": ("children", "parental", "section 9", "age-gat"),
    "Rights": ("data principal", "erasure", "correction", "grievance", "dsar", "dsr"),
    "Breach": ("breach", "72 hour", "72-hour", "cert-in"),
    "SDF": ("significant data fiduciary", "sdf", "section 10"),
    "Cross-border": ("cross-border", "section 16", "transfer"),
    "DPO": ("data protection officer", "dpo"),
    "Vendor": ("processor", "vendor", "dpa", "third-party"),
    "Cookie": ("cookie", "tracker", "consent mode"),
}

PAGE_TYPE_HINTS: dict[str, tuple[str, ...]] = {
    "pricing": ("pricing", "plans", "/price"),
    "product": ("platform", "features", "modules", "cmp"),
    "blog": ("/blog", "/blogs", "/articles", "/news"),
    "explainer": ("guide", "what is", "act 2023", "rules 2025", "section"),
}


def _text_of(item: dict[str, Any]) -> str:
    for key in ("markdown", "text", "content"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _url_of(item: dict[str, Any]) -> str:
    for key in (
        "url",
        "loadedUrl",
        "canonicalUrl",
        "requestUrl",
        "crawl.loadedUrl",
        "metadata.canonicalUrl",
    ):
        value = item.get(key)
        if isinstance(value, str) and value.startswith("http"):
            return value
    return ""


def _title_of(item: dict[str, Any], url: str) -> str:
    metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
    for key in ("title", "metadata.title"):
        value = item.get(key) or metadata.get(key.split(".")[-1])
        if isinstance(value, str) and len(value.strip()) >= 3:
            return value.strip()[:180]
    path = urlparse(url).path.strip("/") or "home"
    return path.replace("-", " ").replace("/", " · ")[:180]


def should_drop(url: str) -> bool:
    lowered = url.lower()
    return any(token in lowered for token in DROP_SUBSTRINGS)


def is_stack_excluded(url: str, title: str) -> bool:
    blob = f"{url} {title}".lower()
    return any(token in blob for token in STACK_EXCLUDE)


def detect_topics(text: str) -> list[str]:
    lowered = text.lower()
    return [topic for topic, keys in TOPIC_KEYWORDS.items() if any(k in lowered for k in keys)]


def detect_page_type(url: str, title: str, text: str) -> str:
    blob = f"{url} {title} {text[:1200]}".lower()
    for page_type, hints in PAGE_TYPE_HINTS.items():
        if any(hint in blob for hint in hints):
            return page_type
    return "other"


def trust_layer(url: str) -> int:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return LAYER_OVERRIDES.get(host, 5)


def slug_host(url: str) -> str:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return re.sub(r"[^a-z0-9]+", "-", host).strip("-") or "source"


def classify_item(item: dict[str, Any]) -> dict[str, Any] | None:
    url = _url_of(item)
    if not url or should_drop(url):
        return None

    title = _title_of(item, url)
    if is_stack_excluded(url, title):
        return None

    text = _text_of(item)
    if len(text.strip()) < 80:
        return None

    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    host = slug_host(url)
    layer = trust_layer(url)
    topics = detect_topics(text)
    page_type = detect_page_type(url, title, text)

    return {
        "suggested_urn": f"urn:ki:in:dpdp:opinion:harvest:{host}:{digest[:12]}",
        "title": title,
        "source": {
            "name": host,
            "layer": layer,
            "url": url,
            "hash": digest,
        },
        "date": date.today().isoformat(),
        "page_type": page_type,
        "topics": topics,
        "entities": ["Opinion", "Organization"] + (["Consent"] if "Consent" in topics else []),
        "summary": text.strip().replace("\n", " ")[:400],
        "confidence_score": 0.5 if layer == 4 else 0.3,
        "stack_eligible": True,
        "exclude_reason": None,
        "review_status": "pending",
        "verbatim_kept_for": "internal_evidence_only",
        "evidence_excerpt": text.strip()[:1200],
    }


def load_items(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    stripped = raw.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        data = json.loads(stripped)
        if not isinstance(data, list):
            raise ValueError("JSON array expected")
        return [row for row in data if isinstance(row, dict)]

    items: list[dict[str, Any]] = []
    for line in stripped.splitlines():
        if not line.strip():
            continue
        parsed = json.loads(line)
        if isinstance(parsed, dict):
            items.append(parsed)
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify competitor harvest pages.")
    parser.add_argument("input_path", help="JSON array or JSONL from Apify dataset export")
    parser.add_argument(
        "--out",
        default="staging/harvest/classified.jsonl",
        help="JSONL path for classified Opinion records",
    )
    args = parser.parse_args()

    source = Path(args.input_path)
    items = load_items(source)
    classified = []
    dropped = 0
    for item in items:
        record = classify_item(item)
        if record is None:
            dropped += 1
            continue
        classified.append(record)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for record in classified:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Read {len(items)} pages")
    print(f"Stacked {len(classified)} Opinion records (training/certification dropped)")
    print(f"Dropped {dropped}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
