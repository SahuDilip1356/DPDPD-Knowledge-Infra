"""Build the Setu question map (training guide step 1).

Takes question text only from two internal sources and writes a labelled, deduplicated
map of about 1,000 questions to a gitignored file:

- the canonical question graph (staging/competitive_intel/questions/unified_questions.jsonl)
- the classified street searches (classified-street.csv)

Both are market-lane data. Only the question wording is kept: no answers, no competitor
names or URLs, no variants. Labels are rule-made drafts (label_source "rule", review
"pending") for Dilip to approve; nothing here is trusted as law.

Usage:
  python3 scripts/question_map/build_question_map.py \
      --graph <unified_questions.jsonl> --street <classified-street.csv> \
      [--name question_map]   # writes staging/question-map/<name>{.jsonl,_summary.json,_review.csv}
"""

import argparse
import collections
import csv
import io
import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

INTENT_KIND = {
    "applicability": "who",
    "how-to": "how",
    "deadline": "what",  # only a time word in the question makes it "when"
    "definition": "what",
    "obligation": "what",
    "penalty": "what",
    "rights": "what",
    "comparison": "what",
}
WHERE_HINT = re.compile(
    r"\b(abroad|outside india|cross[- ]border|data transfers?|transfer(red|ring)? (of )?(personal )?data|"
    r"transfer(red|ring)? .{0,40}\b(outside|abroad|overseas)|which countr|where)\b",
    re.I,
)
# "when" inside a sentence ("what happens when ...") is a condition, not a time question.
WHEN_HINT = re.compile(
    r"\b(by when|from when|date|deadline|timeline|commence\w*|effective (date|from)|in force|come into force)\b",
    re.I,
)
WHO_HINT = re.compile(r"\b(who|whom|apply to|applies to|applicable to)\b", re.I)

COMPARISON = re.compile(
    r"\b(gdpr|ccpa|cpra|fadp|lgpd|pipl|pipeda|appi|popia|pdpa|uk dpa|eu law|european|"
    r"compared? (to|with)|vs\.?|versus)\b",
    re.I,
)
# A question about one organisation's own facts: the engine explains the law, a lawyer
# applies it. Kept narrow on purpose; first-person questions are flagged for review instead.
NEEDS_LAWYER = re.compile(
    r"\b(is|are) (my|our) [\w -]{1,40}\b(compliant|legal|allowed)\b"
    r"|\b(will|could|can) (we|i|my \w+|our \w+)( \w+){0,2} be (fined|penali[sz]ed|sued|liable|prosecuted)\b"
    r"|\b(am i|are we) (compliant|liable|at risk)\b",
    re.I,
)
FOREIGN = re.compile(r"\b(gdpr|ccpa|cpra|fadp|lgpd|pipl|pipeda|appi|popia|pdpa|uk dpa|eu|european|foreign)\b", re.I)
FIRST_PERSON = re.compile(r"\b(i|we|my|our|us)\b", re.I)
LEARNER = re.compile(
    r"\b(course|courses|certification|certificate|exam|upsc|syllabus|study notes|lecture|"
    r"class notes|for students|tutorial)\b",
    re.I,
)
ON_TOPIC = re.compile(
    r"\b(dpdp\w*|data|privacy|personal|consent|breach|fiduciar\w*|principal|dpo|"
    r"protection|board|notice|children|child|minor|guardian|retention|erasure|processor|"
    r"cookie|grievance|penalt\w*|complian\w*|rules?|act|meity|gdpr|surveillance|kyc|dpbi|"
    r"security|encrypt\w*|cyber|cert-in|aadhaar|vendor\w*|information|dpia|audit)\b",
    re.I,
)
# Wording lifted from one page ("the report", "this guide") is not a question a person asks.
PAGE_BOUND = re.compile(r"\b(the|this) (report|article|guide|blog|webinar|whitepaper|ebook|video)\b", re.I)
URL = re.compile(r"https?://|www\.|\b[\w-]+\.(com|in|io|ai|org|net|co)\b", re.I)

AUDIENCE_READER = {
    "compliance/DPO": "business",
    "business owner": "business",
    "legal": "business",
    "developer/IT": "business",
    "HR": "business",
    "individual": "public",
}
STREET_SILENT = {"india_shopping", "shopping"}
STREET_COMPARISON = {"foreign_only", "mixed_foreign"}
STREET_NOISE_GRADES = {"throw_out"}
STREET_NOISE_QUALITY = {"exam_noise", "seed_drift"}


def norm(text):
    t = text.lower().replace("-", " ")
    t = re.sub(r"[^a-z0-9 ]", "", t)
    t = re.sub(r"\bdpdpa\b", "dpdp", t)
    return re.sub(r"\s+", " ", t).strip()


def label_kind(question, intent):
    q = question.strip().lower()
    first = q.split(" ", 1)[0] if q else ""
    if first in ("who", "whom", "whose"):
        return "who"
    if first == "why":
        return "why"
    if first == "how":
        return "how"
    if first == "where":
        return "where"
    if first == "when":
        return "when"
    if WHERE_HINT.search(q):
        return "where"
    if WHEN_HINT.search(q):
        return "when"
    if intent == "applicability" or WHO_HINT.search(q):
        return "who"
    return INTENT_KIND.get(intent, "what")


def label_lane(question, intent, source, street_grade):
    if source == "street" and street_grade in STREET_NOISE_GRADES:
        return "out_of_scope"
    if not ON_TOPIC.search(question) or PAGE_BOUND.search(question):
        return "out_of_scope"
    if source == "street" and street_grade == "myth_jar":
        return "law_silent"
    # Only a foreign law makes it the comparison shelf; "consent vs legitimate use" is DPDPA.
    if COMPARISON.search(question) and FOREIGN.search(question):
        return "comparison"
    if NEEDS_LAWYER.search(question):
        return "needs_lawyer"
    return "law_answers"


def label_reader(audience, question):
    if LEARNER.search(question):
        return "learner"
    return AUDIENCE_READER.get(audience, "public")


def _row(qid, question, intent, source, topic, provisions, demand, grade=None, audience=None):
    return {
        "id": qid,
        "question": question.strip(),
        "kind": label_kind(question, intent),
        "reader": label_reader(audience, question),
        "lane": label_lane(question, intent, source, grade),
        "topic": topic,
        "provision_hints": list(provisions or []),
        "source": source,
        "demand": demand,
        "first_person": bool(FIRST_PERSON.search(question)),
        "label_source": "rule",
        "review": "pending",
    }


def street_rows(street):
    out = []
    for s in street:
        r = _row(s["id"], s["text"], "obligation", "street", "Street search", [],
                 3 * int(s.get("hits") or 0), grade=s.get("grade"))
        if s.get("quality") in STREET_NOISE_QUALITY:
            r["lane"] = "out_of_scope"
        elif r["lane"] == "out_of_scope":
            pass
        elif s.get("quality") in STREET_SILENT:
            r["lane"] = "law_silent"
        elif s.get("quality") in STREET_COMPARISON:
            r["lane"] = "comparison"
        out.append(r)
    return out


def graph_rows(graph):
    out = []
    for g in graph:
        demand = int(g.get("demand_sites") or 0) + 3 * int(g.get("street_hits") or 0)
        demand += 2 if g.get("saralprivacy_asks") else 0
        out.append(_row(g["question_id"], g["question"], g.get("intent"), "graph",
                        g.get("topic") or "Unsorted", g.get("provisions"), demand,
                        audience=g.get("audience")))
    return out


def build(graph, street, target=1000, topic_floor=15):
    """Every kept street question, then graph questions: a floor per topic, then by demand."""
    seen, picked = set(), []

    def add(r):
        k = norm(r["question"])
        if not k or k in seen or URL.search(r["question"]):
            return False
        seen.add(k)
        picked.append(r)
        return True

    for r in sorted(street_rows(street), key=lambda r: -r["demand"]):
        if len(picked) < target:
            add(r)

    pool = sorted(graph_rows(graph), key=lambda r: (-r["demand"], r["id"]))
    by_topic = collections.defaultdict(list)
    for r in pool:
        by_topic[r["topic"]].append(r)
    for topic in sorted(by_topic):
        n = 0
        for r in by_topic[topic]:
            if n >= topic_floor or len(picked) >= target:
                break
            n += add(r)
    for r in pool:
        if len(picked) >= target:
            break
        add(r)
    return picked


OUT_REL = ("staging", "question-map")
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
import safe_output  # noqa: E402  (shared: plain names, no symlinks or hard links written through)


def summary(rows):
    c = collections.Counter
    return {
        "total": len(rows),
        "by_source": dict(c(r["source"] for r in rows)),
        "by_kind": dict(c(r["kind"] for r in rows)),
        "by_reader": dict(c(r["reader"] for r in rows)),
        "by_lane": dict(c(r["lane"] for r in rows)),
        "first_person": sum(r["first_person"] for r in rows),
        "by_topic": dict(c(r["topic"] for r in rows).most_common()),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--graph", required=True)
    ap.add_argument("--street", required=True)
    ap.add_argument("--name", default="question_map",
                    help="file name stem; files go only in staging/question-map/")
    ap.add_argument("--target", type=int, default=1000)
    ap.add_argument("--topic-floor", type=int, default=15)
    a = ap.parse_args()

    names = {k: f"{a.name}{k}" for k in (".jsonl", "_summary.json", "_review.csv")}
    for n in names.values():
        if not safe_output.PLAIN_NAME.match(n):
            sys.exit(f"Refusing to write: {n!r} is not a plain file name.")
    with open(a.graph) as f:
        graph = [json.loads(line) for line in f if line.strip()]
    with open(a.street, newline="") as f:
        street = list(csv.DictReader(f))
    rows = build(graph, street, a.target, a.topic_floor)
    s = summary(rows)

    review = io.StringIO()
    w = csv.writer(review)
    w.writerow(["id", "question", "kind", "reader", "lane", "first_person", "topic", "demand",
                "your_call (ok / change to ... / drop)"])
    for r in rows:
        w.writerow([r["id"], r["question"], r["kind"], r["reader"], r["lane"],
                    "yes" if r["first_person"] else "", r["topic"], r["demand"], ""])
    safe_output.write_files(REPO_ROOT, OUT_REL, {
        names[".jsonl"]: "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        names["_summary.json"]: json.dumps(s, indent=2),
        names["_review.csv"]: review.getvalue(),
    })
    print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
