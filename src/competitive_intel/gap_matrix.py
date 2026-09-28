"""
SaralPrivacy vs competitors: where the market writes, where SaralPrivacy writes, and which
questions buyers ask that SaralPrivacy does not yet answer.

Inputs  staging/competitive_intel/classified/pages.jsonl        (topic/sector tags per page)
        staging/competitive_intel/questions/question_graph.jsonl (canonical questions + demand)
Output  docs/competitive_intel/gap_matrix.md

Emphasis index = SaralPrivacy's share of its pages on a topic ÷ the market's share of its pages on
that topic. 1.0 = same emphasis as the market; >1 = SaralPrivacy leans in; 0 = absent.

Usage:  python3 src/competitive_intel/gap_matrix.py
"""
import json
import os
from collections import Counter, defaultdict

from classify import SECTORS, TOPICS
from fetch import REPO_ROOT

PAGES = os.path.join(REPO_ROOT, "staging/competitive_intel/classified/pages.jsonl")
GRAPH = os.path.join(REPO_ROOT, "staging/competitive_intel/questions/question_graph.jsonl")
REPORT = os.path.join(REPO_ROOT, "docs/competitive_intel/gap_matrix.md")
SELF = {"saralprivacy.com", "dpdpa.wiki"}


def verdict(sp_pages: int, market_sites: int, emphasis: float) -> str:
    if sp_pages == 0:
        return "GAP — market covers it, you don't" if market_sites >= 8 else "OPEN FIELD — few cover it"
    if emphasis >= 1.5:
        return "ADVANTAGE — you lean in harder"
    if emphasis < 0.5:
        return "THIN — covered, under-weighted"
    return "PARITY"


def matrix(pages: list, key: str, names: dict) -> list:
    usable = [p for p in pages if not p["thin"] and not p["duplicate_of"] and p["box"] != "TRAINING"
              and "/dpdp-index/" not in p["url"] and "/your-rights/" not in p["url"]]
    sp = [p for p in usable if p["source_domain"] in SELF]
    market = [p for p in usable if p["source_domain"] not in SELF]
    rows = []
    for name in names:
        sp_n = sum(1 for p in sp if name in p[key])
        mk_n = sum(1 for p in market if name in p[key])
        sites = len({p["source_domain"] for p in market if name in p[key]})
        sp_share = sp_n / len(sp) if sp else 0
        mk_share = mk_n / len(market) if market else 0
        emphasis = sp_share / mk_share if mk_share else 0
        rows.append({"name": name, "sp": sp_n, "market": mk_n, "sites": sites,
                     "sp_share": sp_share, "mk_share": mk_share, "emphasis": emphasis,
                     "verdict": verdict(sp_n, sites, emphasis)})
    return sorted(rows, key=lambda r: (r["sp"] > 0, r["emphasis"]))


def main():
    pages = [json.loads(line) for line in open(PAGES)]
    graph = [json.loads(line) for line in open(GRAPH)]
    competitors = sorted({p["source_domain"] for p in pages} - SELF)
    sp_pages = [p for p in pages if p["source_domain"] in SELF and not p["thin"] and not p["duplicate_of"]]

    lines = ["# SaralPrivacy vs the market — gap matrix", "",
             f"SaralPrivacy corpus: {len(sp_pages)} pages (saralprivacy.com + dpdpa.wiki). "
             f"Market: {len(competitors)} competitor domains. Tagging is rule-based on titles, "
             "headings and body text; treat counts as directional.", "",
             "**Emphasis** = SaralPrivacy's share of its own pages on a topic ÷ the market's share. "
             "1.0 is market-average emphasis.", ""]

    for title, key, names in (("Topics", "topics", TOPICS), ("Sectors and channels", "sectors", SECTORS)):
        rows = matrix(pages, key, names)
        lines += [f"## {title}", "",
                  "| | SaralPrivacy pages | Market pages | Competitor sites | Emphasis | Verdict |",
                  "|---|---|---|---|---|---|"]
        for r in rows:
            lines.append(f"| {r['name']} | {r['sp']} | {r['market']} | {r['sites']}/{len(competitors)} | "
                         f"{r['emphasis']:.1f}× | {r['verdict']} |")
        lines.append("")

    # Question-level backlog: what buyers ask across the market that SaralPrivacy doesn't.
    by_topic = defaultdict(list)
    for q in graph:
        by_topic[q["topic"]].append(q)
    lines += ["## Question coverage by topic", "",
              "Canonical questions (from the deduplicated question graph) and how many SaralPrivacy "
              "already asks/answers on its own pages.", "",
              "| Topic | Canonical questions | Asked on 2+ sites | SaralPrivacy asks | Coverage |",
              "|---|---|---|---|---|"]
    for topic, qs in sorted(by_topic.items(), key=lambda kv: -len(kv[1])):
        mine = sum(q["saralprivacy_asks"] for q in qs)
        lines.append(f"| {topic} | {len(qs)} | {sum(q['demand_sites'] >= 2 for q in qs)} | {mine} | "
                     f"{100 * mine / len(qs):.0f}% |")

    backlog = [q for q in graph if not q["saralprivacy_asks"]]
    backlog.sort(key=lambda q: (-q["demand_sites"], -q["demand_variants"]))
    lines += ["", "## Content backlog — most-asked questions SaralPrivacy doesn't answer yet", "",
              "Ranked by how many competitor sites ask it. Provisions are the Act/Rules labels mapped "
              "to the question (S = section, R = rule).", "",
              "| # | Question | Sites | Topic | Provisions |", "|---|---|---|---|---|"]
    for n, q in enumerate(backlog[:100], 1):
        lines.append(f"| {n} | {q['question']} | {q['demand_sites']} | {q['topic']} | "
                     f"{', '.join(q['provisions'][:4]) or '—'} |")

    total_sp = sum(q["saralprivacy_asks"] for q in graph)
    lines += ["", f"_{len(graph)} canonical questions; SaralPrivacy asks {total_sp} "
              f"({100 * total_sp / len(graph):.0f}%). {len(backlog)} are unaddressed._", ""]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w") as f:
        f.write("\n".join(lines))
    print(f"gap matrix -> {REPORT}")


if __name__ == "__main__":
    main()
