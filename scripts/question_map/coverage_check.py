"""Coverage check for the Setu questionnaire.

Counts questions per provision of the Act and Rules, per lane, reader and kind, and lists
every target that is missed. Written questions carry the provisions they test; graph
questions count through their provision hints (S8 -> act-s8, R7 -> rules-r7).

Usage:
  python3 scripts/question_map/coverage_check.py --law <law-import dir> [--map staging/question-map/question_map.jsonl]
"""

import argparse
import collections
import json
import os
import re
import sys

KINDS = {"who", "why", "how", "what", "when", "where"}
READERS = {"business", "learner", "public"}
LANES = {"law_answers", "law_silent", "needs_lawyer", "comparison", "out_of_scope"}

# Provisions that carry the main duties and rights get more questions.
CORE = {f"act-s{i}" for i in range(2, 18)} | {"act-s27", "act-s29", "act-s33", "act-schedule"} | \
       {f"rules-r{i}" for i in range(3, 17)} | {"rules-r22", "rules-sch3", "rules-sch4-a", "rules-sch4-b"}
MIN_PER_PROVISION = 2
MIN_PER_CORE = 4
MIN_LANE = {"law_silent": 150, "needs_lawyer": 100, "out_of_scope": 50}
MIN_READER = {"learner": 100, "public": 250}
MIN_KIND = 60


def norm(text):
    t = text.lower().replace("-", " ")
    t = re.sub(r"[^a-z0-9 ]", "", t)
    t = re.sub(r"\bdpdpa\b", "dpdp", t)
    return re.sub(r"\s+", " ", t).strip()


def law_ids(law_dir):
    ids = []
    for name in ("dpdp-act-2023.jsonl", "dpdp-rules-2025.jsonl"):
        with open(os.path.join(law_dir, name)) as f:
            ids += [json.loads(line)["id"] for line in f if line.strip()]
    return ids


def hint_to_id(hint):
    m = re.fullmatch(r"([SR])(\d+)", hint or "")
    if not m:
        return None
    return ("act-s" if m.group(1) == "S" else "rules-r") + m.group(2)


def report(written, mapped, ids):
    rows = list(written) + list(mapped)
    per = collections.Counter()
    for r in written:
        for p in r.get("provisions", []):
            per[p] += 1
    for r in mapped:
        for h in r.get("provision_hints", []):
            pid = hint_to_id(h)
            if pid:
                per[pid] += 1
    misses = []
    for pid in ids:
        if pid == "act-long-title":
            continue
        need = MIN_PER_CORE if pid in CORE else MIN_PER_PROVISION
        if per[pid] < need:
            misses.append(f"{pid}: {per[pid]} questions, needs {need}")
    lanes = collections.Counter(r["lane"] for r in rows)
    readers = collections.Counter(r["reader"] for r in rows)
    kinds = collections.Counter(r["kind"] for r in rows)
    for lane, need in MIN_LANE.items():
        if lanes[lane] < need:
            misses.append(f"lane {lane}: {lanes[lane]}, needs {need}")
    for reader, need in MIN_READER.items():
        if readers[reader] < need:
            misses.append(f"reader {reader}: {readers[reader]}, needs {need}")
    for kind in sorted(KINDS):
        if kinds[kind] < MIN_KIND:
            misses.append(f"kind {kind}: {kinds[kind]}, needs {MIN_KIND}")
    return {"total": len(rows), "lanes": dict(lanes), "readers": dict(readers), "kinds": dict(kinds),
            "per_provision": dict(per), "misses": misses}


def main():
    sys.path.insert(0, os.path.dirname(__file__))
    import written_questions as wq
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True)
    ap.add_argument("--map", default=None, help="the built question map, to count graph and street questions too")
    a = ap.parse_args()
    mapped = []
    if a.map:
        with open(a.map) as f:
            mapped = [json.loads(line) for line in f if line.strip() and json.loads(line)["source"] != "written"]
    r = report(wq.rows(), mapped, law_ids(a.law))
    print(json.dumps({k: v for k, v in r.items() if k != "per_provision"}, indent=2))
    sys.exit(1 if r["misses"] else 0)


if __name__ == "__main__":
    main()
