"""Quote checker for Setu training examples (training guide step 2).

Every example must pass before Dilip sees it:
- each claim cites a real provision id and quotes it word for word: one unbroken run of at
  least 6 words, exact case, whitespace normalised, no "…" or "..." elision;
- the answer names no section or rule it does not cite, and no rupee amount that is not in
  one of its quotes;
- the answer uses no capitalised legal-looking term that the law text does not contain
  (catches inventions such as "Data Personal Breach Inquiry");
- labels are from the approved sets, and refusal lanes say plainly that the law does not
  answer or that a lawyer is needed.

Usage:
  python3 scripts/training_examples/check_examples.py --law <law-import dir> <examples.jsonl>
"""

import argparse
import ast
import datetime
import json
import os
import re
import sys

KINDS = {"who", "why", "how", "what", "when", "where"}
READERS = {"business", "learner", "public"}
LANES = {"law_answers", "law_silent", "needs_lawyer", "comparison", "out_of_scope"}
REFUSAL_LANES = {"law_silent", "needs_lawyer", "out_of_scope"}
MIN_QUOTE_WORDS = 6

ELISION = re.compile(r"…|\.\.\.|\[\s*\.\.\.\s*\]")
SECTION_REF = re.compile(r"\bSection\s+(\d+)", re.I)
RULE_REF = re.compile(r"\bRule\s+(\d+)", re.I)
AMOUNT = re.compile(r"₹\s?([\d,]+(?:\.\d+)?)\s*(crore|lakh)", re.I)
CAP_RUN = re.compile(r"\b(?:[A-Z][a-z]+|[A-Z]{2,})(?:\s+(?:of|and|for|to)?\s*(?:[A-Z][a-z]+|[A-Z]{2,}))+\b")
REFUSAL = re.compile(
    r"\b(do(es)? not|don't|doesn't|is not|isn't|no provision|not cover|silent|a lawyer|"
    r"legal advice|outside (the )?(dpdp|scope)|cannot answer)\b",
    re.I,
)
LEADING = {"The", "A", "An", "This", "That", "These", "Your", "Our", "If", "In", "Under", "For",
           "When", "Yes", "No", "So", "But", "And", "Each", "Every", "Any", "From", "Until", "Once",
           "Tell", "Ask", "Check", "Give", "Keep", "Get", "Send", "Use", "Note", "Then", "Only",
           "Before", "After", "Both", "Also", "Most", "Some", "Today", "From"}
ALLOWED_NAMES = {
    "SaralPrivacy", "Setu", "India", "Indian", "RBI", "SEBI", "IRDAI", "Aadhaar", "MeitY",
    "CERT-In", "GDPR", "WhatsApp", "UPSC", "DPDP Act", "DPDP Rules", "DPDPA", "Gazette",
    "Data Protection Board", "Data Protection Board of India", "Board", "Act", "Rules",
}
ALLOWED_WORDS = {w for name in ALLOWED_NAMES for w in name.split()}
AMOUNT_WORDS = {"10,000": "ten thousand", "50": "fifty", "150": "one hundred and fifty",
                "200": "two hundred", "250": "two hundred and fifty", "500": "five hundred"}


def squash(text):
    return re.sub(r"\s+", " ", text).strip()


def load_law(law_dir):
    law = {}
    for name in ("dpdp-act-2023.jsonl", "dpdp-rules-2025.jsonl"):
        with open(os.path.join(law_dir, name)) as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    law[r["id"]] = r
    return law


def _cited_numbers(cites, law, prefix):
    return {str(law[c].get("number")) for c in cites if c in law and c.startswith(prefix)}


def _invented_terms(answer, law_blob):
    found = []
    for m in CAP_RUN.finditer(answer):
        words = m.group(0).split()
        while words and words[0] in LEADING:
            words = words[1:]
        if len(words) < 2:
            continue
        term = " ".join(words)
        singular = re.sub(r"ies$", "y", term) if term.endswith("ies") else re.sub(r"s$", "", term)
        if term in ALLOWED_NAMES or term in law_blob or singular in law_blob:
            continue
        if all(w in ALLOWED_WORDS or w in ("of", "and", "for", "to") for w in words):
            continue
        found.append(term)
    return found


def _in_force(record):
    v = record.get("in_force") or []
    if isinstance(v, str):
        try:
            v = ast.literal_eval(v)
        except (ValueError, SyntaxError):
            return []
    return [x.get("from") for x in v if isinstance(x, dict) and x.get("from")]


def _human(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B')} {d.year}"


def check(example, law, as_of=None):
    """as_of: ISO date the answer is read on; defaults to the example's as_of, then today."""
    as_of = as_of or example.get("as_of") or datetime.date.today().isoformat()
    errs = []
    for field, allowed in (("kind", KINDS), ("reader", READERS), ("lane", LANES)):
        if example.get(field) not in allowed:
            errs.append(f"label {field}={example.get(field)!r} not in approved set")

    claims = example.get("claims") or []
    cites = [cl.get("cite") for cl in claims]
    quotes = []
    for i, cl in enumerate(claims, 1):
        cite, quote = cl.get("cite"), squash(cl.get("quote") or "")
        if cite not in law:
            errs.append(f"claim {i}: unknown provision {cite!r}")
            continue
        if ELISION.search(quote):
            errs.append(f"claim {i}: quote uses elision")
            continue
        if len(quote.split()) < MIN_QUOTE_WORDS:
            errs.append(f"claim {i}: quote shorter than {MIN_QUOTE_WORDS} words")
            continue
        if quote not in squash(law[cite]["text"]):
            errs.append(f"claim {i}: quote not found in {law[cite]['citation']}")
            continue
        quotes.append(quote)

    if example.get("lane") == "law_answers" and not claims:
        errs.append("law_answers needs at least one quoted claim")
    if example.get("lane") in REFUSAL_LANES and not REFUSAL.search(example.get("answer", "")):
        errs.append("refusal lane must say plainly that the law does not answer or a lawyer is needed")

    answer = example.get("answer", "")
    sections = _cited_numbers(cites, law, "act-s")
    rules = _cited_numbers(cites, law, "rules-r")
    for m in SECTION_REF.finditer(answer):
        if m.group(1) not in sections:
            errs.append(f"answer names Section {m.group(1)} without citing it")
    for m in RULE_REF.finditer(answer):
        if m.group(1) not in rules:
            errs.append(f"answer names Rule {m.group(1)} without citing it")
    joined = " ".join(quotes)
    for m in AMOUNT.finditer(answer):
        num = m.group(1)
        words = AMOUNT_WORDS.get(num)
        if num not in joined and not (words and words in joined):
            errs.append(f"answer names ₹{num} {m.group(2)} but no quote contains it")

    # A duty that has not started yet must be dated, or readers act on it too early.
    for cite in dict.fromkeys(cites):
        if cite not in law:
            continue
        dates = _in_force(law[cite])
        pending = [d for d in dates if d > as_of]
        if pending and not any(_human(d) in answer for d in dates):
            errs.append(f"{law[cite]['citation']} is not in force until {_human(max(pending))}; "
                        "the answer must say when it applies")

    law_blob = " ".join(squash(r["text"]) + " " + r.get("title", "") for r in law.values())
    for term in _invented_terms(answer, law_blob):
        errs.append(f"answer uses {term!r}, which is not in the law text")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True, help="folder holding dpdp-act-2023.jsonl and dpdp-rules-2025.jsonl")
    ap.add_argument("--as-of", default=None, help="ISO date the answers are read on (default today)")
    ap.add_argument("examples")
    a = ap.parse_args()
    law = load_law(a.law)
    bad = 0
    with open(a.examples) as f:
        for line in f:
            if not line.strip():
                continue
            e = json.loads(line)
            errs = check(e, law, a.as_of)
            if errs:
                bad += 1
                print(f"FAIL {e.get('id')}: " + "; ".join(errs))
    print(f"{bad} failing")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
