"""
Corpus contract — what every live Knowledge Object must satisfy.

Two layers:
  1. Shape: stored_object_schema.json.
  2. Evidence: every quote attributed to the Act or the Rules is checked against the
     gazette text itself. The quote must appear in the provision it names, word for
     word, and its hash must be the hash of that provision's current text. A verbatim
     object must carry the provision's full text, unchanged.

The gazette text is the verified law file the public site is built from
(deployments/dpdpa-wiki/src/data/law/provisions.json), so the store and the site are
held to the same words.

Usage:  python -m src.schemas.corpus_contract <objects.jsonl[.gz]> [--law provisions.json]
"""

import gzip
import hashlib
import json
import os
import re
import sys
from collections import Counter
from typing import Dict, Iterable, List, Optional

from jsonschema import Draft7Validator

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, "stored_object_schema.json")
PROVISIONS_PATH = os.path.abspath(os.path.join(
    HERE, "..", "..", "..", "dpdpa-wiki", "src", "data", "law", "provisions.json"))

ACT_SOURCE = "urn:ki:in:dpdp:source:gazette-dpdpa-2023"
RULES_SOURCE = "urn:ki:in:dpdp:source:gazette-gsr-846e-2025"
GAZETTE_SOURCES = (ACT_SOURCE, RULES_SOURCE)

_validator: Optional[Draft7Validator] = None


def validator() -> Draft7Validator:
    global _validator
    if _validator is None:
        with open(SCHEMA_PATH) as f:
            _validator = Draft7Validator(json.load(f))
    return _validator


def load_law(path: str = PROVISIONS_PATH) -> Dict[str, Dict]:
    """Provisions keyed by label ("S6", "R7", "SCH-FIRST", "ACT-SCHEDULE")."""
    with open(path) as f:
        return {p["label"]: p for p in json.load(f)["provisions"]}


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalise(text: str) -> str:
    """Whitespace- and case-insensitive; rejoins the gazette's line-break hyphens."""
    return re.sub(r"\s+", " ", re.sub(r"(\w) -(\w)", r"\1-\2", text)).strip().lower()


def quote_fragments(quote: str) -> List[str]:
    """A quote may elide with "…"; each piece must stand on its own."""
    return [f for f in (p.strip() for p in re.split(r"\s*(?:\.{3}|…)\s*", quote)) if f]


def evidence_label(item: Dict) -> Optional[str]:
    """The provision an evidence item points at, or None if its coordinates name none."""
    coordinates = item.get("coordinates") or {}
    act = item.get("source_urn") == ACT_SOURCE
    if "section" in coordinates:
        return f"S{str(coordinates['section']).split()[-1]}"  # "Section 8" -> "S8"
    if "rule" in coordinates:
        return f"R{str(coordinates['rule']).split()[-1]}"
    if "schedule" in coordinates:
        return "ACT-SCHEDULE" if act else f"SCH-{str(coordinates['schedule']).upper()}"
    return None


def check_object(row: Dict, law: Dict[str, Dict]) -> List[str]:
    """Every way `row` breaks the contract; empty when it conforms."""
    problems = []
    for error in sorted(validator().iter_errors(row), key=lambda e: list(map(str, e.absolute_path))):
        where = "/".join(map(str, error.absolute_path)) or "object"
        problems.append(f"shape: {where}: {error.message[:160]}")

    body = row.get("body") if isinstance(row.get("body"), dict) else {}
    evidence = [e for e in (row.get("evidence") or []) if isinstance(e, dict)]

    quoted = set()
    for item in evidence:
        if item.get("source_urn") not in GAZETTE_SOURCES:
            continue
        name = item.get("id") or "evidence"
        label = evidence_label(item)
        if label not in law:
            problems.append(f"evidence: {name} names no provision of the Act or Rules ({label})")
            continue
        quoted.add(label)
        text = law[label]["text"]
        if item.get("chunk_sha256") != sha256(text):
            problems.append(f"evidence: {name} hash is not the current gazette text of {label}")
        haystack = normalise(text)
        if not all(normalise(f) in haystack for f in quote_fragments(item.get("citation_text") or "")):
            problems.append(f"evidence: {name} quote is not in the gazette text of {label}")

    if row.get("interpretation_stance") == "verbatim":
        label = body.get("provision")
        if label not in law:
            problems.append(f"verbatim: body.provision is not a provision ({label})")
        else:
            if row.get("urn") != law[label]["urn"]:
                problems.append(f"verbatim: urn is not the urn of {label}")
            if body.get("full_text") != law[label]["text"]:
                problems.append(f"verbatim: full_text is not the gazette text of {label}")

    if row.get("type") == "Answer":
        for label in (c for c in (body.get("cited") or []) if isinstance(c, str)):
            if label not in law:
                problems.append(f"answer: cites {label}, which is not a provision")
            elif label not in quoted:
                problems.append(f"answer: cites {label} without a quote from it")
        for label, stated in (body.get("rules_in_force_from") or {}).items():
            actual = (law.get(label) or {}).get("in_force_from")
            if actual != stated:
                problems.append(f"answer: says {label} is in force from {stated}; the Rules say {actual}")
    return problems


def check_corpus(rows: Iterable[Dict], law: Dict[str, Dict]) -> Dict[str, List[str]]:
    """Violations by "urn vN", for the objects that have any."""
    failures = {}
    for row in rows:
        problems = check_object(row, law)
        if problems:
            failures[f"{row.get('urn')} v{row.get('version')}"] = problems
    return failures


def kind(problem: str) -> str:
    """A violation with its object-specific detail removed, for counting."""
    problem = re.sub(r"\bev-[a-z0-9-]+|\bevidence/\d+", "<item>", problem)
    problem = re.sub(r"\b[SR]\d+\b|\bSCH-[A-Z]+\b|\bACT-SCHEDULE\b", "<provision>", problem)
    return re.sub(r"'[^']*'|\([^)]*\)|\d{4}-\d{2}-\d{2}|\bNone\b", "…", problem)


def report(failures: Dict[str, List[str]], total: int) -> str:
    lines = [f"{total - len(failures)}/{total} objects conform"]
    counts = Counter(kind(p) for problems in failures.values() for p in problems)
    lines += [f"  {n:5d}  {k}" for k, n in counts.most_common()]
    return "\n".join(lines)


def read_jsonl(path: str) -> List[Dict]:
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main(argv: List[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    law_path = argv[argv.index("--law") + 1] if "--law" in argv else PROVISIONS_PATH
    rows = read_jsonl(argv[0])
    failures = check_corpus(rows, load_law(law_path))
    print(report(failures, len(rows)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
