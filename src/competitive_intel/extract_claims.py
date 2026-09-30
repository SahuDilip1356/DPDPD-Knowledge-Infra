"""
Stage 1 of the claim pipeline: pull checkable assertions out of competitor pages.

Extraction only — nothing here judges whether a claim is true. That is verify_claims.py.
Every claim keeps the competitor's own wording plus a verbatim quote, so the Source Truth
agent can check the claim as made rather than a paraphrase of it.

Writes  staging/competitive_intel/claims/claims.jsonl   (append-only; resumable)

Usage:  python3 src/competitive_intel/extract_claims.py            # all eligible pages
        python3 src/competitive_intel/extract_claims.py --limit 25 # pilot
"""
import argparse
import glob
import hashlib
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

from fetch import REPO_ROOT
from llm import MODEL, Usage, ask_json

CLASSIFIED = os.path.join(REPO_ROOT, "staging/competitive_intel/classified/pages.jsonl")
RAW = os.path.join(REPO_ROOT, "staging/competitive_intel/raw")
OUT_DIR = os.path.join(REPO_ROOT, "staging/competitive_intel/claims")
OUT_FILE = os.path.join(OUT_DIR, "claims.jsonl")
MAX_CHARS = 14000  # ~3.5k tokens; longer pages are truncated, not split

SYSTEM = """You extract checkable factual claims about Indian data-protection law from a web page.

A CLAIM is a specific assertion that could be shown true or false against a source.
Extract only claims that matter to someone deciding how to comply.

claim_type:
  LEGAL     - what the DPDPA 2023 or DPDP Rules require, permit, prohibit, or penalise
  STATISTIC - a number about the world (adoption rates, breach counts, survey figures)
  MARKET    - a claim about timelines, enforcement activity, or what regulators are doing
  OPINION   - normative advice presented as fact ("you must appoint a DPO by March")

Rules:
- Write claim_text as a single self-contained sentence. Resolve pronouns and context.
- quote must be copied VERBATIM from the page, 200 characters or fewer.
- cited_sections / cited_rules: only numbers the page itself attaches to THIS claim. Empty if none.
- Skip marketing puffery ("India's leading platform"), feature lists, calls to action, and
  anything that is only about the vendor's own product.
- A page may yield zero claims. Returning an empty list is correct and expected.
- At most 12 claims per page: the most specific and checkable ones.

Return JSON: {"claims": [{"claim_text": str, "claim_type": str, "quote": str,
"cited_sections": [int], "cited_rules": [int], "topic": str}]}"""

write_lock = threading.Lock()


def eligible_pages() -> list:
    """Pages worth spending a call on: those that engage with the law or answer questions."""
    pages = []
    for line in open(CLASSIFIED):
        page = json.loads(line)
        if page["box"] == "TRAINING" or page["thin"] or page["duplicate_of"]:
            continue
        if page["capture_mode"] != "FULL" or page["word_count"] < 120:
            continue
        # Skip the askmeidentity per-company scans: one template x 3,500 companies,
        # already summarised in aggregate. Their editorial pages still qualify.
        if "askmeidentity" in page["source_domain"] and "/dpdp-index/" in page["url"]:
            continue
        if page["dpdpa_sections"] or page["dpdp_rules"] or page["question_count"] >= 3 \
                or page["content_type"] in ("LAW", "RULES", "FAQ", "GUIDE"):
            pages.append(page)
    return pages


def raw_markdown(page: dict) -> str:
    matches = sorted(glob.glob(os.path.join(RAW, page["source_domain"], "*")))
    if not matches:
        return ""
    from urllib.parse import urlparse
    import re
    path = urlparse(page["url"]).path or "/"
    slug = (re.sub(r"[^a-zA-Z0-9]+", "_", path).strip("_") or "index")[:150]
    file_path = os.path.join(matches[-1], f"{slug}.json")
    if not os.path.exists(file_path):
        return ""
    return json.load(open(file_path)).get("markdown") or ""


def claim_id(url: str, claim_text: str) -> str:
    return "CLM-" + hashlib.sha256(f"{url}|{claim_text}".encode()).hexdigest()[:12]


def extract(page: dict, usage: Usage, out) -> int:
    body = raw_markdown(page)
    if not body:
        return 0
    prompt = (f"URL: {page['url']}\nSite: {page['source_domain']}\n"
              f"Title: {page['title']}\n\n---\n{body[:MAX_CHARS]}")
    result = ask_json(SYSTEM, prompt, usage)
    if not result:
        return 0

    rows = []
    for claim in result.get("claims", []):
        text = (claim.get("claim_text") or "").strip()
        if len(text) < 20:
            continue
        rows.append({
            "claim_id": claim_id(page["url"], text),
            "claim_text": text,
            "claim_type": (claim.get("claim_type") or "OPINION").upper(),
            "topic": claim.get("topic") or "",
            "quote": (claim.get("quote") or "")[:200],
            "cited_sections": [n for n in claim.get("cited_sections", []) if isinstance(n, int) and 1 <= n <= 44],
            "cited_rules": [n for n in claim.get("cited_rules", []) if isinstance(n, int) and 1 <= n <= 23],
            "found_on": page["source_domain"],
            "original_url": page["url"],
            "page_content_type": page["content_type"],
            "first_seen": page.get("crawl_date") or "2026-09-19",
            "extracted_by": MODEL,
            # Set by verify_claims.py. Until then nothing here may be published.
            "verification_status": "NEEDS_REVIEW",
            "publication_allowed": False,
        })
    with write_lock:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
        out.flush()
    return len(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="process at most N pages (pilot runs)")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    done = set()
    if os.path.exists(OUT_FILE):
        done = {json.loads(l)["original_url"] for l in open(OUT_FILE)}

    pages = [p for p in eligible_pages() if p["url"] not in done]
    if args.limit:
        pages = pages[: args.limit]
    print(f"{len(pages)} pages to extract ({len(done)} already done) · model {MODEL}", flush=True)

    usage, total = Usage(), 0
    with open(OUT_FILE, "a") as out:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for index, count in enumerate(pool.map(lambda p: extract(p, usage, out), pages), 1):
                total += count
                if index % 50 == 0:
                    print(f"  {index}/{len(pages)} pages · {total} claims · ${usage.cost_usd:.2f}", flush=True)

    print(f"\n{total} claims from {len(pages)} pages\n{usage}")


if __name__ == "__main__":
    sys.exit(main())
