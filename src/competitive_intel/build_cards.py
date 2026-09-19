"""Read exported DPDPA.com pages and write unpublished Knowledge Cards."""

from __future__ import annotations

import json
import os
import sys

from src.competitive_intel.knowledge_cards import build_cards, write_card_export

DEFAULT_RAW_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "competitive_intel", "dpdpa_com", "raw"
)
DEFAULT_OUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "competitive_intel", "dpdpa_com", "cards"
)


def load_jsonl_dir(raw_dir: str) -> list[dict]:
    if not os.path.isdir(raw_dir):
        raise FileNotFoundError(f"raw page store not found: {raw_dir}")
    pages: list[dict] = []
    for name in sorted(os.listdir(raw_dir)):
        if not name.endswith(".jsonl"):
            continue
        path = os.path.join(raw_dir, name)
        with open(path, encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    pages.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid jsonl {path}:{line_no}") from exc
    if not pages:
        raise ValueError(f"no pages in {raw_dir}")
    return pages


def main() -> int:
    raw_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RAW_DIR)
    out_dir = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT_DIR)
    pages = load_jsonl_dir(raw_dir)
    cards, skipped = build_cards(pages)
    write_card_export(cards, out_dir)
    print(f"Wrote {len(cards)} unpublished Knowledge Cards to {out_dir}")
    if skipped:
        print("Skipped:", skipped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
