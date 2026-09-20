"""Rebuild cards-adjacent factory outputs: truth, questions, gaps, counsel queue."""

from __future__ import annotations

import json
import os
import sys

from src.competitive_intel.build_cards import DEFAULT_OUT_DIR as DEFAULT_CARDS_DIR
from src.competitive_intel.build_cards import DEFAULT_RAW_DIR, load_jsonl_dir
from src.competitive_intel.build_source_truth import mark_used_by_saralprivacy
from src.competitive_intel.content_gap import build_content_gaps, gap_summary
from src.competitive_intel.knowledge_cards import build_cards, write_card_export
from src.competitive_intel.legal_review import (
    build_counsel_queue,
    counsel_summary,
    render_counsel_markdown,
)
from src.competitive_intel.question_universe import (
    build_question_universe,
    question_summary,
)
from src.competitive_intel.source_truth import register_claims
from src.competitive_intel.topic_matrix import (
    build_topic_matrix,
    load_saralprivacy_corpus,
    matrix_summary,
)

DEFAULT_CARDS = os.path.join(DEFAULT_CARDS_DIR, "knowledge_cards.json")
DEFAULT_TRUTH = os.path.join(
    os.path.dirname(__file__), "..", "..", "competitive_intel", "dpdpa_com", "truth"
)
DEFAULT_QUESTIONS = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "competitive_intel",
    "dpdpa_com",
    "questions",
)
DEFAULT_GAPS = os.path.join(
    os.path.dirname(__file__), "..", "..", "competitive_intel", "dpdpa_com", "gaps"
)


def _write_json(path: str, payload: object) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)
        handle.write("\n")


def _write_jsonl(path: str, rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def main() -> int:
    raw_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RAW_DIR)
    cards_dir = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CARDS_DIR)
    truth_dir = os.path.abspath(sys.argv[3] if len(sys.argv) > 3 else DEFAULT_TRUTH)
    questions_dir = os.path.abspath(DEFAULT_QUESTIONS)
    gaps_dir = os.path.abspath(DEFAULT_GAPS)

    pages = load_jsonl_dir(raw_dir)
    cards, skipped = build_cards(pages)
    write_card_export(cards, cards_dir)

    saral_blob = load_saralprivacy_corpus()
    claims = register_claims(cards)
    mark_used_by_saralprivacy(claims, saral_blob)
    matrix = build_topic_matrix(cards, saral_blob)
    questions = build_question_universe(cards, raw_dir=raw_dir)
    briefs = build_content_gaps(matrix, questions)
    queue = build_counsel_queue(claims)

    summary = {
        "cards": {
            "count": len(cards),
            "skipped": skipped,
            "publication_eligible": False,
        },
        "claims": {
            "count": len(claims),
            "by_status": {},
            "publication_allowed": sum(1 for row in claims if row["publication_allowed"]),
        },
        "matrix": matrix_summary(matrix),
        "questions": question_summary(questions),
        "gaps": gap_summary(briefs),
        "counsel": counsel_summary(queue, claims),
    }
    for row in claims:
        status = row["verification_status"]
        summary["claims"]["by_status"][status] = (
            summary["claims"]["by_status"].get(status, 0) + 1
        )

    _write_jsonl(os.path.join(truth_dir, "claims_registry.jsonl"), claims)
    _write_json(os.path.join(truth_dir, "claims_registry.json"), claims)
    _write_json(os.path.join(truth_dir, "competitor_topic_matrix.json"), matrix)
    _write_jsonl(os.path.join(questions_dir, "question_universe.jsonl"), questions)
    _write_json(os.path.join(questions_dir, "question_universe.json"), questions)
    _write_jsonl(os.path.join(gaps_dir, "content_gap_briefs.jsonl"), briefs)
    _write_json(os.path.join(gaps_dir, "content_gap_briefs.json"), briefs)
    _write_json(os.path.join(truth_dir, "counsel_queue.json"), queue)
    with open(os.path.join(truth_dir, "counsel_queue.md"), "w", encoding="utf-8") as handle:
        handle.write(render_counsel_markdown(queue, summary["counsel"]))
    _write_json(os.path.join(truth_dir, "summary.json"), summary)

    print("Cards:", len(cards), "skipped", skipped)
    print(summary["matrix"]["headline"])
    print(summary["questions"]["headline"])
    print(summary["gaps"]["headline"])
    print(summary["counsel"]["headline"])
    print("Claims:", summary["claims"]["by_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
