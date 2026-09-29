"""
Builds the real-corpus golden set and the committed corpus snapshot it runs against.

Reads the gitignored staging data (main checkout: staging/competitive_intel/) and writes:

  evals/golden_corpus.jsonl          the golden cases
  evals/corpus/answer_kos.jsonl.gz   the 511 verified answer knowledge objects, without the
                                     competitor provenance fields (asked_on, question_variants,
                                     demand_sites), so CI can run the eval without staging/

The law half of the corpus is not snapshotted: it is the committed
deployments/dpdpa-wiki/src/data/law/provisions.json (all 75 provisions, clean gazette text).

Nothing here is hand-written. Every expected label comes from a verified answer object:
  answer            a question sampled per topic from the answer objects (the question graph's
                    canonical wording); expected provisions = the answer's `cited` labels, the
                    provisions whose verbatim quotes passed verification.
  support_withheld  an answered question whose support the runner removes for that case (see
                    withheld_cases), so the corpus holds none and the engine must refuse.

Refusal cases are not drawn from answer_rejects.jsonl: "rejected" does not mean "unsupported".
The answer pipeline rejected questions the law does answer when its retrieval missed the
provision (anonymised research data: Section 17(2)(b); startups: Section 17(3)).

Competitor content is never ground truth: only question wording comes from the question graph.

Usage:  python3 evals/build_golden.py [--staging PATH]
"""

import argparse
import gzip
import hashlib
import json
import os
import re
from collections import Counter, defaultdict

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GOLDEN_PATH = os.path.join(PROJECT_ROOT, "evals", "golden_corpus.jsonl")
SNAPSHOT_PATH = os.path.join(PROJECT_ROOT, "evals", "corpus", "answer_kos.jsonl.gz")
PROVISIONS_PATH = os.path.join(
    PROJECT_ROOT, "deployments", "dpdpa-wiki", "src", "data", "law", "provisions.json"
)

ANSWER_CASES = 60
WITHHELD_CASES = 8
# A withheld case removes one narrow subject, not a pillar of the Act
# (S8 alone is cited by 106 of the 511 answers).
MAX_WITHHELD_PROVISIONS = 6
MAX_WITHHELD_ANSWERS = 80

COMPETITOR_FIELDS = ("asked_on", "question_variants", "demand_sites")
STOPWORDS = set(
    "a an and are as at be by can do does for from how i in is it of on or the to under what "
    "when which who why with we our my dpdp dpdpa act 2023 rules 2025 india indian data "
    # question framing, not legal terms
    "important allowed required needed happens difference between business businesses "
    "company companies organisation organisations organization organizations".split()
)


def default_staging() -> str:
    here = os.path.join(PROJECT_ROOT, "staging", "competitive_intel")
    if os.path.isdir(here):
        return here
    # A worktree has no staging/ (it is gitignored); the main checkout holds it.
    main = os.path.abspath(os.path.join(PROJECT_ROOT, "..", "..", ".."))
    return os.path.join(main, "staging", "competitive_intel")


def read_jsonl(path: str) -> list:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def stable_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stems(text: str) -> set:
    """Crude stems (first six letters of words of five or more letters): enough to tell
    whether two texts share a legal term such as "nominate" / "nomination"."""
    return {w[:6] for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 5 and w not in STOPWORDS}


def allocate(counts: Counter, total: int) -> dict:
    """At least one case per topic, the rest in proportion (largest remainder)."""
    topics = sorted(counts)
    alloc = {t: 1 for t in topics}
    spare = total - len(topics)
    pool = sum(counts.values())
    shares = {t: spare * counts[t] / pool for t in topics}
    for t in topics:
        alloc[t] += int(shares[t])
    left = total - sum(alloc.values())
    for t in sorted(topics, key=lambda t: (-(shares[t] - int(shares[t])), t))[:left]:
        alloc[t] += 1
    return alloc


def answer_cases(answers: list, graph: dict) -> list:
    by_topic = defaultdict(list)
    for a in answers:
        by_topic[a["body"]["topic"]].append(a)
    alloc = allocate(Counter({t: len(v) for t, v in by_topic.items()}), ANSWER_CASES)
    cases = []
    for topic in sorted(by_topic):
        pool = sorted(by_topic[topic], key=lambda a: stable_key(a["body"]["question_id"]))
        for a in pool[:alloc[topic]]:
            qid = a["body"]["question_id"]
            cases.append({
                "id": f"ans_{qid}",
                "kind": "answer",
                "input": graph[qid]["question"],
                "topic": topic,
                "question_id": qid,
                "answer_urn": a["urn"],
                "expect_sufficient": True,
                "expect_provisions": sorted(a["body"]["cited"]),
            })
    return cases


def withheld_cases(answers: list, graph: dict, law: dict, taken: set) -> list:
    """Questions whose support is removed from the corpus for the run.

    Withholding only the cited provisions is not enough: the law cross-refers (Section 8(9)
    also covers the DPO contact that Rule 9 details) and other answers restate the same
    point. So a case withholds every provision and every answer object that mentions any of
    the question's distinctive terms (those in at most a fifth of provisions), plus the
    provisions its verified answer cites and every answer citing those. What remains shares
    no distinctive term with the question.
    """
    law_stems = {label: stems(p["title"] + " " + p["text"]) for label, p in law.items()}
    answer_stems = {a["urn"]: stems(" ".join([a["title"], a["summary"]] + [
        e["citation_text"] for e in a["evidence"]])) for a in answers}
    df = Counter(s for v in law_stems.values() for s in v)
    generic = {s for s, n in df.items() if n > len(law) / 5}
    citing = defaultdict(set)
    for a in answers:
        for label in a["body"]["cited"]:
            citing[label].add(a["urn"])

    candidates = []
    for a in answers:
        qid = a["body"]["question_id"]
        cited = set(a["body"]["cited"])
        terms = stems(graph[qid]["question"]) - generic
        # The question must share a distinctive term with the law that answers it,
        # or withholding that term would not remove the support.
        if qid in taken or not any(terms & law_stems[label] for label in cited):
            continue
        labels = cited | {label for label, s in law_stems.items() if s & terms}
        urns = set().union(*(citing[label] for label in labels))
        urns |= {urn for urn, s in answer_stems.items() if s & terms}
        if len(labels) > MAX_WITHHELD_PROVISIONS or len(urns) > MAX_WITHHELD_ANSWERS:
            continue
        candidates.append((len(labels) + len(urns) / 10, stable_key(qid), a, terms, labels, urns))

    cases, used = [], set()
    for _, _, a, terms, labels, urns in sorted(candidates, key=lambda c: c[:2]):
        if used & labels:
            continue  # one case per provision, so the set spans different parts of the law
        used |= labels
        qid = a["body"]["question_id"]
        cases.append({
            "id": f"withheld_{qid}",
            "kind": "support_withheld",
            "input": graph[qid]["question"],
            "topic": a["body"]["topic"],
            "question_id": qid,
            "expect_sufficient": False,
            "withheld_terms": sorted(terms),
            "withheld_provisions": sorted(labels),
            "withheld_urns": sorted({law[label]["urn"] for label in labels} | urns),
        })
        if len(cases) == WITHHELD_CASES:
            break
    return cases


def snapshot(answers: list) -> None:
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
    lines = []
    for a in sorted(answers, key=lambda a: a["urn"]):
        body = {k: v for k, v in a["body"].items() if k not in COMPETITOR_FIELDS}
        lines.append(json.dumps({**a, "body": body}, ensure_ascii=False, sort_keys=True))
    data = ("\n".join(lines) + "\n").encode("utf-8")
    # mtime=0 keeps the file byte-identical across rebuilds of the same data.
    with open(SNAPSHOT_PATH, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as f:
        f.write(data)


def main():
    parser = argparse.ArgumentParser(description="Build the real-corpus golden set.")
    parser.add_argument("--staging", default=default_staging(),
                        help="staging/competitive_intel directory (gitignored; main checkout)")
    args = parser.parse_args()

    answers = read_jsonl(os.path.join(args.staging, "knowledge_objects", "answer_kos.jsonl"))
    graph = {q["question_id"]: q for q in read_jsonl(
        os.path.join(args.staging, "questions", "question_graph.jsonl"))}

    with open(PROVISIONS_PATH) as f:
        law = {p["label"]: p for p in json.load(f)["provisions"]}
    for a in answers:
        stray = set(a["body"]["cited"]) - set(law)
        if stray:
            raise SystemExit(f"{a['urn']} cites provisions that do not exist: {sorted(stray)}")

    cases = answer_cases(answers, graph)
    cases += withheld_cases(answers, graph, law, {c["question_id"] for c in cases})

    with open(GOLDEN_PATH, "w") as f:
        f.writelines(json.dumps(c, ensure_ascii=False) + "\n" for c in cases)
    snapshot(answers)

    kinds = Counter(c["kind"] for c in cases)
    print(f"golden: {len(cases)} cases {dict(kinds)} across "
          f"{len({c['topic'] for c in cases})} topics -> {os.path.relpath(GOLDEN_PATH, PROJECT_ROOT)}")
    print(f"corpus: {len(answers)} answer objects -> {os.path.relpath(SNAPSHOT_PATH, PROJECT_ROOT)} "
          f"({os.path.getsize(SNAPSHOT_PATH):,} bytes)")


if __name__ == "__main__":
    main()
