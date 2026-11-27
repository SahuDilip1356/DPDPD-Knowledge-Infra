"""Turn a batch of checked training examples into a review sheet for Dilip.

Writes a Markdown file next to the batch: one block per example with the question, the
answer, each quote with its citation, and a line to tick. The sheet is written only
directly inside staging/training-examples/; symlinks and other folders are refused.

Usage:
  python3 scripts/training_examples/make_review_sheet.py --law <law-import dir> <batch.jsonl>
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import check_examples as c  # noqa: E402

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LANE_NAMES = {
    "law_answers": "The law answers it",
    "law_silent": "The law is silent",
    "needs_lawyer": "Needs a lawyer",
    "comparison": "Comparison",
    "out_of_scope": "Off-topic or a trick",
}


def render(examples, law):
    out = ["# Training examples for review", "",
           "For each one, tick **OK**, or write what to change, or mark **Drop**.", ""]
    for i, e in enumerate(examples, 1):
        errs = c.check(e, law)
        out.append(f"## {i}. {e['question']}")
        out.append(f"`{e['id']}` · {e['kind']} · {e['reader']} · {LANE_NAMES.get(e['lane'], e['lane'])}"
                   + ("" if not errs else " · **CHECKER FAILED: " + "; ".join(errs) + "**"))
        out.append("")
        out.append(f"**Answer:** {e['answer']}")
        out.append("")
        for cl in e.get("claims", []):
            cit = law.get(cl["cite"], {}).get("citation", cl["cite"])
            out.append(f"- {cit}: \"{c.squash(cl['quote'])}\"")
        out.append("")
        out.append("- [ ] OK   - [ ] Drop   Change: ______")
        out.append("")
    return "\n".join(out)


OUT_REL = ("staging", "training-examples")
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
import safe_output  # noqa: E402


def sheet_name(batch):
    return os.path.splitext(os.path.basename(batch))[0] + "_review.md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True)
    ap.add_argument("batch")
    a = ap.parse_args()
    batch_dir = os.path.realpath(os.path.dirname(os.path.abspath(a.batch)))
    if batch_dir != os.path.realpath(os.path.join(REPO_ROOT, *OUT_REL)):
        sys.exit("Refusing: the batch must sit directly in staging/training-examples/.")
    law = c.load_law(a.law)
    with open(a.batch) as f:
        examples = [json.loads(line) for line in f if line.strip()]
    out = safe_output.write_files(REPO_ROOT, OUT_REL, {sheet_name(a.batch): render(examples, law)})[0]
    print(out)


if __name__ == "__main__":
    main()
