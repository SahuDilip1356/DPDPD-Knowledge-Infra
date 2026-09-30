"""
Unifies every DPDPA question source into one registry and reports what each source
contributes that the others don't.

Sources
  graph    questions/question_graph.jsonl           1,779 canonical questions (competitor + SaralPrivacy pages)
  street   imports/jv-content-intelligence-*/…/street-questions-unique.csv   186 Google PAA + related searches
  organic  imports/jv-content-intelligence-*/…/organic-results.jsonl         223 Google result titles
  harvest  imports/harvest-*/classified_*.jsonl     1,648 classified pages — contributes pages/domains, not questions

Matching is semantic when --semantic is passed (text-embedding-3-small, cosine ≥ 0.86 =
in graph, ≥ 0.75 = near; costs well under a cent) and lexical otherwise (token Jaccard ≥ 0.6 /
≥ 0.35). Semantic is the one to trust; lexical is the fallback with no API access.

Writes  questions/unified_questions.jsonl   one row per canonical question with `sources`,
                                             `street_hits`, `street_paa`, `street_related`
        questions/street_unique.csv          street questions not in the graph, classified
        docs/competitive_intel/question_sources.md

Usage:  python3 src/competitive_intel/unify_sources.py
"""
import csv
import glob
import sys
import json
import os
import re
from collections import Counter, defaultdict

from fetch import REPO_ROOT

CI = os.path.join(REPO_ROOT, "staging/competitive_intel")
GRAPH = os.path.join(CI, "questions/question_graph.jsonl")
UNIFIED = os.path.join(CI, "questions/unified_questions.jsonl")
STREET_OUT = os.path.join(CI, "questions/street_unique.csv")
REPORT = os.path.join(REPO_ROOT, "docs/competitive_intel/question_sources.md")
PAGES = os.path.join(CI, "classified/pages.jsonl")

STOP = set("the a an of to in for on by with is are be under what who how does do can i my it "
           "its and or vs act rules india indian dpdp dpdpa data".split())
STRONG, NEAR = 0.6, 0.35
SEM_STRONG, SEM_NEAR = 0.86, 0.75

# Street intents that are not questions a knowledge base answers, but tell us what pages to build.
NAVIGATIONAL = re.compile(r"(?i)\b(pdf|download|portal|website|news|latest|update|bare act|summary|"
                          r"notification|gazette|official|login|site)\b")
SHOPPING = re.compile(r"(?i)certif|course|training|software|tool|vendor|consultant|interview|exam|salary|job")


def toks(text: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 2}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def find(pattern: str) -> str:
    matches = glob.glob(os.path.join(CI, "imports", pattern), recursive=True)
    if not matches:
        raise SystemExit(f"missing import: {pattern}")
    return sorted(matches)[-1]


def load_street() -> list:
    rows = list(csv.DictReader(open(find("jv-content-intelligence-*/clusters/*Street-Gap-Pack/street-questions-unique.csv"))))
    return [{"question": r["question"].strip(), "hits": int(r["hits"] or 0),
             "paa": int(r["paa_hits"] or 0), "related": int(r["related_hits"] or 0),
             "quality": r.get("quality", ""), "concept": r.get("concept", ""),
             "calendar": r.get("calendar_status", "")} for r in rows if r["question"].strip()]


def load_organic() -> list:
    titles = []
    for line in open(find("jv-content-intelligence-*/raw/*SERP-DPDPA-Questions/organic-results.jsonl")):
        try:
            titles.append(json.loads(line).get("title", "").strip())
        except ValueError:
            pass
    return [t for t in titles if t.endswith("?")]


def load_harvest() -> list:
    rows = []
    for path in glob.glob(os.path.join(find("harvest-*"), "classified_*.jsonl")):
        for line in open(path):
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows


def kind(street: dict) -> str:
    q = street["question"]
    if street["quality"] in ("foreign_only", "exam_noise", "seed_drift"):
        return "noise"
    if SHOPPING.search(q) or street["quality"] == "india_shopping":
        return "shopping"
    asks = q.rstrip().endswith("?") or re.match(r"(?i)\s*(what|who|when|where|which|why|how|is|are|does|do|can)\b", q)
    if NAVIGATIONAL.search(q) or (len(toks(q)) <= 2 and not asks):
        return "navigational"
    return "question"


def main():
    semantic = "--semantic" in sys.argv
    graph = [json.loads(l) for l in open(GRAPH)]
    street = load_street()
    organic = load_organic()

    if semantic:
        import numpy as np
        from question_graph import embed
        # One vector per canonical question AND per variant, so a street query can match any wording.
        labels = [(g, v) for g in graph for v in [g["question"]] + g["variants"]]
        matrix = embed([v for _, v in labels])
        queries = [s["question"] for s in street] + organic
        qvec = embed(queries)
        sims = qvec @ matrix.T
        cache = {}
        for i, q in enumerate(queries):
            j = int(np.argmax(sims[i]))
            cache[q] = (float(sims[i, j]), labels[j][0])
        strong, near = SEM_STRONG, SEM_NEAR

        def best(text: str):
            return cache.get(text, (0.0, None))
    else:
        index = [(toks(v), g) for g in graph for v in [g["question"]] + g["variants"]]
        strong, near = STRONG, NEAR

        def best(text: str):
            t = toks(text)
            top, hit = 0.0, None
            for ct, g in index:
                j = jaccard(t, ct)
                if j > top:
                    top, hit = j, g
            return top, hit

    # --- street → graph
    for g in graph:
        g["sources"] = ["graph"]
        g["street_hits"] = g["street_paa"] = g["street_related"] = 0
        g["street_matches"] = []
    unique_street, near_street = [], []
    for s in street:
        score, g = best(s["question"])
        if score >= strong and g:
            g["sources"] = sorted(set(g["sources"] + ["street"]))
            g["street_hits"] += s["hits"]; g["street_paa"] += s["paa"]; g["street_related"] += s["related"]
            g["street_matches"].append(s["question"])
            s["status"] = "in_graph"; s["matched"] = g["question"]
        elif score >= near and g:
            s["status"] = "near"; s["matched"] = g["question"]
            near_street.append(s)
        else:
            s["status"] = "unique"; s["matched"] = ""
            unique_street.append(s)
        s["kind"] = kind(s)

    # --- organic titles that are questions
    organic_unique = [t for t in organic if best(t)[0] < strong]

    # --- harvest pages vs our crawl (by URL and by domain)
    our_urls = {json.loads(l)["url"].rstrip("/") for l in open(PAGES)}
    harvest = load_harvest()
    harvest_urls = {h.get("source", {}).get("url", "").rstrip("/") for h in harvest}
    harvest_only = sorted(u for u in harvest_urls if u and u not in our_urls)
    harvest_domains = Counter(h.get("source", {}).get("name", "?") for h in harvest)

    # --- write unified registry
    with open(UNIFIED, "w") as f:
        for g in graph:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    with open(STREET_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["question", "hits", "paa", "related", "kind", "quality", "status", "matched"])
        w.writeheader()
        for s in sorted(unique_street + near_street, key=lambda s: (-s["hits"], s["question"])):
            w.writerow({k: s[k] for k in w.fieldnames})

    # --- report
    demand = sorted((g for g in graph if g["street_hits"]), key=lambda g: -g["street_hits"])
    kinds = Counter(s["kind"] for s in unique_street)
    lines = [
        "# Question sources — what each one adds", "",
        f"Matching: {'semantic (text-embedding-3-small, cosine ≥ ' + str(SEM_STRONG) + ')' if semantic else 'lexical (token Jaccard ≥ ' + str(STRONG) + ')'}.", "",
        f"Unified registry: `staging/competitive_intel/questions/unified_questions.jsonl` "
        f"({len(graph)} canonical questions, each tagged with the sources that ask it).", "",
        "## Sources", "",
        "| Source | Items | What it is | Unique contribution |", "|---|---|---|---|",
        f"| Canonical graph | {len(graph)} | Questions competitors and SaralPrivacy write, deduplicated and mapped to provisions | The taxonomy, the provision mapping, 252 law-only answers |",
        f"| Google street (JV) | {len(street)} | People Also Ask + related searches, with hit counts | **Search demand.** {len(unique_street)} not in the graph, {len(near_street)} near-matches |",
        f"| Google organic titles (JV) | {len(organic)} question-form titles of 223 | What already ranks | {len(organic_unique)} not in the graph |",
        f"| Harvest (19 Sep) | {len(harvest)} pages | Classified competitor pages, trust layers 4–5 | {len(harvest_only)} URLs our crawl did not fetch; no questions |",
        "",
        "## Street questions the graph doesn't have", "",
        f"{len(unique_street)} of {len(street)} street questions have no match in the canonical graph. By kind:", "",
        "| Kind | Count | What to do |", "|---|---|---|",
        f"| question | {kinds['question']} | Add to the graph and answer from the law |",
        f"| navigational | {kinds['navigational']} | Not questions — people want the law itself, dates, an official home. Served by the /act, /rules and \"Applies from\" pages |",
        f"| shopping | {kinds['shopping']} | Certificates, courses, tools. One \"there is no DPDPA certificate\" page answers most of it |",
        f"| noise | {kinds['noise']} | GDPR-only, UPSC exam prep, drifted searches — ignore |",
        "", "### Real questions to add", "",
        "| Hits | Question |", "|---|---|",
    ]
    lines += [f"| {s['hits']} | {s['question']} |" for s in sorted(unique_street, key=lambda s: -s["hits"]) if s["kind"] == "question"]
    lines += ["", "### Navigational and shopping intents (page ideas, not questions)", "", "| Hits | Kind | Intent |", "|---|---|---|"]
    lines += [f"| {s['hits']} | {s['kind']} | {s['question']} |" for s in sorted(unique_street, key=lambda s: -s["hits"]) if s["kind"] in ("navigational", "shopping")][:40]
    lines += ["", "## Graph questions with the most Google demand", "",
              "Canonical questions that street searches match, ranked by hits. These should lead the course modules.", "",
              "| Street hits | Sites asking | Question | Provisions |", "|---|---|---|---|"]
    lines += [f"| {g['street_hits']} | {g['demand_sites']} | {g['question']} | {', '.join(g['provisions'][:3]) or '—'} |" for g in demand[:40]]
    lines += ["", "## Harvest pages our crawl missed", "",
              f"{len(harvest_only)} URLs, across: " + ", ".join(f"{d} ({n})" for d, n in harvest_domains.most_common(8)), "",
              "Sample:", ""] + [f"- {u}" for u in harvest_only[:15]]
    lines += ["", "## Organic result titles not in the graph", ""] + [f"- {t}" for t in organic_unique[:30]]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(lines) + "\n")

    print(f"graph {len(graph)} | street {len(street)}: in-graph {len(street) - len(unique_street) - len(near_street)}, "
          f"near {len(near_street)}, unique {len(unique_street)} {dict(kinds)} | organic ?-titles {len(organic)}, "
          f"unique {len(organic_unique)} | harvest {len(harvest)} pages, {len(harvest_only)} URLs we lack")
    print(f"-> {UNIFIED}\n-> {STREET_OUT}\n-> {REPORT}")


if __name__ == "__main__":
    main()
