"""Build the claims registry and competitor topic matrix."""

from __future__ import annotations

import json
import os
import sys

from src.competitive_intel.source_truth import register_claims
from src.competitive_intel.topic_matrix import build_topic_matrix, load_saralprivacy_corpus, matrix_summary

DEFAULT_CARDS = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "competitive_intel",
    "dpdpa_com",
    "cards",
    "knowledge_cards.json",
)
DEFAULT_OUT = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "competitive_intel",
    "dpdpa_com",
    "truth",
)


def _write_json(path: str, payload: object) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)
        handle.write("\n")


def _write_jsonl(path: str, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def mark_used_by_saralprivacy(claims: list[dict], saral_blob: str) -> None:
    for claim in claims:
        hay = f"{claim['claim_text']} {claim.get('dpdpa_section') or ''}".lower()
        claim["used_by_saralprivacy"] = any(
            token in saral_blob and token in hay
            for token in (
                "consent",
                "notice",
                "child",
                "penalty",
                "250 crore",
                "data fiduciary",
                "whatsapp",
                "recruitment",
            )
        )


def main() -> int:
    cards_path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CARDS)
    out_dir = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT)
    with open(cards_path, encoding="utf-8") as handle:
        cards = json.load(handle)
    if not isinstance(cards, list) or not cards:
        raise ValueError("knowledge cards file is empty")

    saral_blob = load_saralprivacy_corpus()
    claims = register_claims(cards)
    mark_used_by_saralprivacy(claims, saral_blob)
    matrix = build_topic_matrix(cards, saral_blob)
    summary = {
        "claims": {
            "count": len(claims),
            "by_status": {},
            "publication_allowed": sum(1 for row in claims if row["publication_allowed"]),
        },
        "matrix": matrix_summary(matrix),
    }
    for row in claims:
        status = row["verification_status"]
        summary["claims"]["by_status"][status] = summary["claims"]["by_status"].get(status, 0) + 1

    os.makedirs(out_dir, exist_ok=True)
    _write_jsonl(os.path.join(out_dir, "claims_registry.jsonl"), claims)
    _write_json(os.path.join(out_dir, "claims_registry.json"), claims)
    _write_json(os.path.join(out_dir, "competitor_topic_matrix.json"), matrix)
    _write_json(os.path.join(out_dir, "summary.json"), summary)
    print(summary["matrix"]["headline"])
    print("Claims:", summary["claims"]["by_status"])
    print("Wrote", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
