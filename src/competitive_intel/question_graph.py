"""
Builds the canonical DPDPA question graph from every question found across the crawl.

  1. screen   — keep questions about Indian data-protection compliance; drop other
                jurisdictions, vendor/product questions, and generic tech. Tag topic,
                audience and intent at the same time.
  2. embed    — text-embedding-3-small.
  3. cluster  — greedy cosine clustering, most-asked questions seeding clusters, so a question
                asked on six sites becomes one node that knows it was asked six times.
  4. canonicalise — one clean, self-contained question per cluster, mapped to the provisions
                of the Act and Rules that answer it.

A cluster, not a string, is the unit of "no duplicates": every surviving canonical question
sits below SIMILARITY of every other one.

Writes  staging/competitive_intel/questions/screened.jsonl
        staging/competitive_intel/questions/embeddings.npy (+ .ids.json)
        staging/competitive_intel/questions/question_graph.jsonl   <- the product

Usage:  python3 src/competitive_intel/question_graph.py [screen|embed|cluster|canonical|all]
"""
import json
import os
import re
import sys
import threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import requests

from fetch import REPO_ROOT
from llm import EMBED_ENDPOINT, Usage, api_key, ask_json, provider_model
from verify_claims import load_law

QUESTIONS_IN = os.path.join(REPO_ROOT, "staging/competitive_intel/classified/questions.jsonl")
OUT_DIR = os.path.join(REPO_ROOT, "staging/competitive_intel/questions")
SCREENED = os.path.join(OUT_DIR, "screened.jsonl")
EMBEDDINGS = os.path.join(OUT_DIR, "embeddings.npy")
EMBED_IDS = os.path.join(OUT_DIR, "embeddings.ids.json")
CLUSTERS = os.path.join(OUT_DIR, "clusters.json")
GRAPH = os.path.join(OUT_DIR, "question_graph.jsonl")
EMBED_MODEL = "text-embedding-3-small"
SIMILARITY = 0.86   # two questions this close are the same question worded differently
SCREEN_BATCH = 40
CANON_BATCH = 20

TOPICS = ["Applicability & scope", "Definitions", "Consent", "Consent Manager", "Notice",
          "Legitimate uses", "Data Fiduciary obligations", "Security safeguards", "Breach",
          "Retention & erasure", "Children & guardians", "Persons with disability",
          "Significant Data Fiduciary & DPIA", "Data Principal rights", "Grievance & DPO",
          "Cross-border transfer", "Exemptions", "Processors & vendors", "Data Protection Board",
          "Penalties & enforcement", "Appeals", "Timelines & commencement", "State processing",
          "Research & statistics", "Sector application", "Implementation & operations",
          "Comparison with GDPR & other laws", "AI & automated processing"]
AUDIENCES = ["business owner", "compliance/DPO", "developer/IT", "legal", "HR", "individual"]
INTENTS = ["definition", "applicability", "obligation", "how-to", "deadline", "penalty",
           "comparison", "rights"]

SCREEN_SYSTEM = f"""You screen questions for a knowledge base about India's Digital Personal
Data Protection Act, 2023 and DPDP Rules, 2025.

For each question decide `keep`:
  true  — about complying with, understanding, or being protected by Indian data-protection
          law. Includes comparisons of DPDPA with GDPR or other laws, sector-specific DPDPA
          application, and general privacy concepts asked in an Indian context.
  false — about another jurisdiction only (GDPR-only, US state laws such as CCPA/VCDPA/MCDPA,
          PDPL, etc.), about a specific vendor, product, plan, price or comparison of vendors,
          about the website itself, or generic technology with no data-protection angle.

For kept questions also give:
  topic    — one of {TOPICS}
  audience — one of {AUDIENCES}
  intent   — one of {INTENTS}

Return JSON: {{"results": [{{"i": int, "keep": bool, "topic": str, "audience": str,
"intent": str}}]}} with one entry per input question, using its index i."""

CANON_SYSTEM = """You write canonical questions for a DPDPA knowledge base.

Each input is a CLUSTER of questions grouped by wording similarity, asked on different websites.
Usually they are one question. Sometimes they mix genuinely different questions, e.g.
"What is a Consent Manager?" and "Is a Consent Manager mandatory?" — those need different answers.

For each cluster return 1 to 3 canonical questions:
  - one per genuinely different information need; never split mere rewordings
  - self-contained and specific; say "under the DPDP Act" or "under the DPDP Rules" where the
    question is legal; never name a website, vendor or product
  - plain English a business owner would type; no marketing
  - keep the scope actually asked — do not broaden a narrow question into a general one
  - `members`: indices of the cluster questions this canonical question covers

`provisions`: labels from the supplied index that would answer it, e.g. ["S6", "R3"]. Only labels
from the index. Empty if the law does not directly answer it (e.g. a how-to about tooling).

Return JSON: {"results": [{"c": int, "questions": [{"question": str, "members": [int],
"provisions": [str]}]}]}"""

JUDGE_SYSTEM = """You deduplicate a DPDPA question bank. For each numbered PAIR decide whether the
two questions would be fully answered by the SAME answer. Rewordings, singular/plural, with or
without "under the DPDP Act", "what is X" vs "who is X" are the SAME. Questions that differ in
what is asked (definition vs obligation vs deadline vs penalty), in who it applies to, or in
scope (one sector vs all) are DIFFERENT.

Return JSON: {"results": [{"p": int, "same": bool}]}"""

lock = threading.Lock()


def _norm(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower()).strip()


# ---------------------------------------------------------------- 1. screen
def screen(usage: Usage):
    os.makedirs(OUT_DIR, exist_ok=True)
    grouped = defaultdict(list)
    for line in open(QUESTIONS_IN):
        row = json.loads(line)
        grouped[_norm(row["question_text"])].append(row)
    done = set()
    if os.path.exists(SCREENED):
        done = {json.loads(l)["key"] for l in open(SCREENED)}
    pending = [(key, rows) for key, rows in grouped.items() if key not in done]
    print(f"screen: {len(grouped)} distinct, {len(pending)} to screen", flush=True)

    batches = [pending[i:i + SCREEN_BATCH] for i in range(0, len(pending), SCREEN_BATCH)]

    def run(batch):
        listing = "\n".join(f"{i}. {rows[0]['question_text']}" for i, (key, rows) in enumerate(batch))
        result = ask_json(SCREEN_SYSTEM, listing, usage, max_tokens=4000) or {}
        by_index = {r.get("i"): r for r in result.get("results", []) if isinstance(r, dict)}
        out = []
        for i, (key, rows) in enumerate(batch):
            verdict = by_index.get(i)
            if verdict is None:
                continue  # left for a later resume rather than guessed
            out.append({
                "key": key,
                "question_text": rows[0]["question_text"],
                "keep": bool(verdict.get("keep")),
                "topic": verdict.get("topic") if verdict.get("topic") in TOPICS else "Implementation & operations",
                "audience": verdict.get("audience") if verdict.get("audience") in AUDIENCES else "business owner",
                "intent": verdict.get("intent") if verdict.get("intent") in INTENTS else "how-to",
                "asked_on": sorted({r["found_on"] for r in rows}),
                "urls": sorted({r["original_url"] for r in rows})[:5],
            })
        with lock, open(SCREENED, "a") as f:
            f.writelines(json.dumps(o, ensure_ascii=False) + "\n" for o in out)
        return len(out)

    with ThreadPoolExecutor(max_workers=4) as pool:
        total = sum(pool.map(run, batches))
    print(f"screen: wrote {total} · {usage}", flush=True)


def load_screened() -> list:
    rows = {}
    for line in open(SCREENED):
        row = json.loads(line)
        rows[row["key"]] = row
    return list(rows.values())


# ---------------------------------------------------------------- 2. embed
def embed(texts: list) -> np.ndarray:
    key = api_key()
    vectors = []
    for start in range(0, len(texts), 500):
        chunk = texts[start:start + 500]
        for attempt in range(6):
            resp = requests.post(EMBED_ENDPOINT, timeout=120,
                                 headers={"Authorization": f"Bearer {key}"},
                                 json={"model": provider_model(EMBED_MODEL), "input": chunk})
            if resp.status_code == 200:
                break
            import time
            time.sleep(min(60, 2 ** attempt * 3))
        resp.raise_for_status()
        vectors += [item["embedding"] for item in sorted(resp.json()["data"], key=lambda d: d["index"])]
    matrix = np.array(vectors, dtype=np.float32)
    return matrix / np.linalg.norm(matrix, axis=1, keepdims=True)


def _is_english(text: str) -> bool:
    """consentx.io publishes translated FAQs; those duplicate English ones and aren't our audience."""
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and sum(c.isascii() for c in letters) / len(letters) > 0.9


def run_embed():
    kept = [r for r in load_screened() if r["keep"] and _is_english(r["question_text"])]
    matrix = embed([r["question_text"] for r in kept])
    np.save(EMBEDDINGS, matrix)
    json.dump([r["key"] for r in kept], open(EMBED_IDS, "w"))
    print(f"embed: {matrix.shape[0]} kept questions embedded", flush=True)


# ---------------------------------------------------------------- 3. cluster
def cluster(threshold: float = SIMILARITY) -> list:
    rows = {r["key"]: r for r in load_screened()}
    ids = json.load(open(EMBED_IDS))
    matrix = np.load(EMBEDDINGS)

    # Most-asked first, so the question asked on the most sites seeds its cluster.
    order = sorted(range(len(ids)), key=lambda i: (-len(rows[ids[i]]["asked_on"]), len(ids[i])))
    # Seed-anchored: a question joins only if it is close to the cluster's SEED (the most-asked
    # wording). A drifting centroid lets clusters wander and swallow neighbouring questions.
    seeds, members = [], []
    for i in order:
        vector = matrix[i]
        if seeds:
            sims = matrix[seeds] @ vector
            best = int(np.argmax(sims))
            if sims[best] >= threshold:
                members[best].append(i)
                continue
        seeds.append(i)
        members.append([i])

    clusters = []
    for group in members:
        keys = [ids[i] for i in group]
        sites = sorted({s for k in keys for s in rows[k]["asked_on"]})
        topics = Counter(rows[k]["topic"] for k in keys)
        clusters.append({
            "members": [rows[k]["question_text"] for k in keys],
            "asked_on": sites,
            "topic": topics.most_common(1)[0][0],
            "audience": Counter(rows[k]["audience"] for k in keys).most_common(1)[0][0],
            "intent": Counter(rows[k]["intent"] for k in keys).most_common(1)[0][0],
            "urls": sorted({u for k in keys for u in rows[k]["urls"]})[:5],
        })
    clusters.sort(key=lambda c: (-len(c["asked_on"]), -len(c["members"])))
    json.dump(clusters, open(CLUSTERS, "w"), ensure_ascii=False)
    return clusters


# ---------------------------------------------------------------- 4. canonicalise
def canonicalise(usage: Usage) -> list:
    clusters = json.load(open(CLUSTERS))
    law, _ = load_law()
    index = "\n".join(f"{k}: {law[k]['title']}" for k in law)
    system = CANON_SYSTEM + "\n\nPROVISION INDEX:\n" + index

    # Every batch is cached to disk as it returns, so a crash never throws paid work away.
    cache_path = os.path.join(OUT_DIR, "canonical_cache.jsonl")
    results = {}
    if os.path.exists(cache_path):
        for line in open(cache_path):
            row = json.loads(line)
            results[row["c"]] = row["questions"]
    todo = [c for c in range(len(clusters)) if c not in results]
    batches = [todo[i:i + CANON_BATCH] for i in range(0, len(todo), CANON_BATCH)]
    print(f"canonical: {len(results)} clusters cached, {len(todo)} to do", flush=True)

    def run(batch):
        listing = "\n\n".join(
            f"CLUSTER {c}:\n" + "\n".join(f"  [{j}] {m}" for j, m in enumerate(clusters[c]["members"][:8]))
            for c in batch)
        result = ask_json(system, listing, usage, max_tokens=4000) or {}
        for item in result.get("results", []):
            if isinstance(item, dict) and item.get("c") in batch and item.get("questions"):
                with lock:
                    results[item["c"]] = item["questions"]
                    with open(cache_path, "a") as cache:
                        cache.write(json.dumps({"c": item["c"], "questions": item["questions"]},
                                               ensure_ascii=False) + "\n")

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run, batches))

    rows = []
    for c, info in enumerate(clusters):
        made = [q for q in results.get(c, []) if isinstance(q, dict) and (q.get("question") or "").strip()]
        if not made:  # the model skipped it: keep the most-asked wording rather than lose it
            made = [{"question": info["members"][0], "members": list(range(len(info["members"]))),
                     "provisions": []}]
            how = "most-asked-member"
        else:
            how = "llm"
        for q in made[:3]:
            picked = [info["members"][j] for j in q.get("members", []) if isinstance(j, int)
                      and 0 <= j < len(info["members"])] or info["members"]
            rows.append({
                "question": q["question"].strip(),
                "topic": info["topic"], "audience": info["audience"], "intent": info["intent"],
                "provisions": _labels(q.get("provisions"), law),
                "asked_on": info["asked_on"], "variants": picked,
                "example_urls": info["urls"], "canonicalised_by": how,
            })
    print(f"canonical: {len(clusters)} clusters -> {len(rows)} canonical questions · {usage}", flush=True)
    return rows


def _labels(raw, law: dict) -> list:
    """Provision labels from model output that may be strings, dicts, or junk."""
    out = []
    for item in raw if isinstance(raw, list) else []:
        if isinstance(item, dict):
            item = item.get("label") or item.get("provision") or item.get("id") or ""
        if isinstance(item, str):
            label = item.strip().upper().replace(" ", "")
            if label in law and label not in out:
                out.append(label)
    return out


def dedup(rows: list, usage: Usage, auto: float = 0.94, review: float = 0.87) -> list:
    """Collapse canonical questions that are the same question. >= auto merges outright;
    between review and auto an LLM judges the pair; below review they stay distinct."""
    matrix = embed([r["question"] for r in rows])
    sims = matrix @ matrix.T
    np.fill_diagonal(sims, 0)

    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    upper = np.triu(sims, 1)
    for a, b in zip(*np.where(upper >= auto)):
        union(int(a), int(b))
    pairs = [(int(a), int(b)) for a, b in zip(*np.where((upper >= review) & (upper < auto)))]
    print(f"dedup: {int((upper >= auto).sum())} auto-merged pairs, {len(pairs)} pairs to judge", flush=True)

    def judge(batch):
        listing = "\n".join(f"{p}. A: {rows[a]['question']}\n   B: {rows[b]['question']}"
                            for p, (a, b) in enumerate(batch))
        result = ask_json(JUDGE_SYSTEM, listing, usage, max_tokens=2500) or {}
        return [batch[r["p"]] for r in result.get("results", [])
                if isinstance(r, dict) and r.get("same") and isinstance(r.get("p"), int)
                and 0 <= r["p"] < len(batch)]

    batches = [pairs[i:i + 40] for i in range(0, len(pairs), 40)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for same in pool.map(judge, batches):
            for a, b in same:
                union(a, b)

    groups = defaultdict(list)
    for i in range(len(rows)):
        groups[find(i)].append(i)

    merged = []
    for members in groups.values():
        members.sort(key=lambda i: (-len(rows[i]["asked_on"]), -len(rows[i]["variants"])))
        head = dict(rows[members[0]])
        head["asked_on"] = sorted({s for i in members for s in rows[i]["asked_on"]})
        head["variants"] = list(dict.fromkeys(v for i in members for v in rows[i]["variants"]))
        head["provisions"] = list(dict.fromkeys(p for i in members for p in rows[i]["provisions"]))
        head["example_urls"] = list(dict.fromkeys(u for i in members for u in rows[i]["example_urls"]))[:5]
        head["merged_from"] = len(members)
        merged.append(head)
    return merged


FILTER_SYSTEM = """You curate a public DPDPA question bank. For each numbered question decide `keep`:
  true  — a real question a business or individual could ask about India's DPDP Act / Rules or
          Indian data-protection practice.
  false — names or is about a specific vendor, product or tool (ConsentX, OneTrust, dcomply,
          Vishwaas, "our platform"); a sales or rhetorical hook ("Are you ready for…",
          "Why does X matter for your business"); about an event, contest or website; or so
          vague it cannot be answered.
Return JSON: {"results": [{"i": int, "keep": bool}]}"""

SPLIT_SYSTEM = """You deduplicate a DPDPA question bank. The numbered questions below were grouped
as possible duplicates. Split them into sets where every question in a set is fully answered by
the SAME answer. Rewordings, singular/plural, "what is X" vs "who is X", with or without
"under the DPDP Act" are the same. Different information needs (definition vs obligation vs
deadline vs penalty vs how-to), different parties, or different scope are different sets.
Every index must appear in exactly one set.
Return JSON: {"sets": [[int, ...], ...]}"""


def filter_questions(rows: list, usage: Usage) -> list:
    keep = {}
    batches = [list(range(i, min(i + 60, len(rows)))) for i in range(0, len(rows), 60)]

    def run(batch):
        listing = "\n".join(f"{i}. {rows[i]['question']}" for i in batch)
        result = ask_json(FILTER_SYSTEM, listing, usage, max_tokens=3000) or {}
        found = {r.get("i"): bool(r.get("keep")) for r in result.get("results", []) if isinstance(r, dict)}
        with lock:
            for i in batch:
                keep[i] = found.get(i, True)  # unjudged: keep rather than silently drop

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run, batches))
    kept = [r for i, r in enumerate(rows) if keep.get(i, True)]
    print(f"filter: {len(rows)} -> {len(kept)} (dropped {len(rows) - len(kept)} vendor/marketing/vague)", flush=True)
    return kept


def semantic_dedup(rows: list, usage: Usage, neighbours: int = 8, floor: float = 0.72,
                   max_group: int = 4) -> list:
    """Meaning-level dedup: each question's nearest neighbours are judged by an LLM, then any
    merged group bigger than max_group is re-split so chained pairs cannot glue distinct
    questions together."""
    matrix = embed([r["question"] for r in rows])
    sims = matrix @ matrix.T
    np.fill_diagonal(sims, -1)
    pairs = set()
    for i in range(len(rows)):
        for j in np.argsort(-sims[i])[:neighbours]:
            if sims[i, j] >= floor:
                pairs.add((min(i, int(j)), max(i, int(j))))
    pairs = sorted(pairs)
    print(f"semantic dedup: {len(pairs)} neighbour pairs to judge", flush=True)

    same = []
    batches = [pairs[k:k + 40] for k in range(0, len(pairs), 40)]

    def judge(batch):
        listing = "\n".join(f"{p}. A: {rows[a]['question']}\n   B: {rows[b]['question']}"
                            for p, (a, b) in enumerate(batch))
        result = ask_json(JUDGE_SYSTEM, listing, usage, max_tokens=2500) or {}
        return [batch[r["p"]] for r in result.get("results", [])
                if isinstance(r, dict) and r.get("same") and isinstance(r.get("p"), int)
                and 0 <= r["p"] < len(batch)]

    with ThreadPoolExecutor(max_workers=4) as pool:
        for found in pool.map(judge, batches):
            same += found

    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a, b in same:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    groups = defaultdict(list)
    for i in range(len(rows)):
        groups[find(i)].append(i)

    final_groups, big = [], [g for g in groups.values() if len(g) > max_group]
    final_groups += [g for g in groups.values() if len(g) <= max_group]
    print(f"semantic dedup: {len(same)} same-pairs, {len(big)} large groups to re-split", flush=True)

    def split(group):
        listing = "\n".join(f"{n}. {rows[i]['question']}" for n, i in enumerate(group))
        result = ask_json(SPLIT_SYSTEM, listing, usage, max_tokens=2500) or {}
        sets, seen = [], set()
        for s_ in result.get("sets", []):
            members = [group[n] for n in s_ if isinstance(n, int) and 0 <= n < len(group)
                       and group[n] not in seen]
            seen.update(members)
            if members:
                sets.append(members)
        sets += [[i] for i in group if i not in seen]  # anything unassigned stays its own question
        return sets

    with ThreadPoolExecutor(max_workers=4) as pool:
        for sets in pool.map(split, big):
            final_groups += sets

    merged = []
    for members in final_groups:
        members.sort(key=lambda i: (-len(rows[i]["asked_on"]), -len(rows[i]["variants"]), len(rows[i]["question"])))
        head = dict(rows[members[0]])
        head["asked_on"] = sorted({s for i in members for s in rows[i]["asked_on"]})
        head["variants"] = list(dict.fromkeys(v for i in members for v in rows[i]["variants"]))
        head["provisions"] = list(dict.fromkeys(p for i in members for p in rows[i]["provisions"]))
        head["example_urls"] = list(dict.fromkeys(u for i in members for u in rows[i]["example_urls"]))[:5]
        head["merged_from"] = sum(rows[i].get("merged_from", 1) for i in members)
        merged.append(head)
    print(f"semantic dedup: {len(rows)} -> {len(merged)} questions", flush=True)
    return merged


VENDORS = re.compile(
    r"(?i)\b(complynz|privy|idfy|redacto|consentx|consently|dpdp ?comply|askme|dpdpa\.com|cadp|"
    r"gotrust|seqrite|leegality|consentin|concur\.live|dpdpa ?shield|dpo[- ]india|consentos|"
    r"complydp|dcomply|tsaaro|perfios|consentiqo|kavachone|miniorange|onetrust|vishwaas|"
    r"securiti|trustarc|osano|cookiebot|usercentrics)\b")

CONSOLIDATE_SYSTEM = """You are the final editor of a DPDPA question bank. The numbered questions
below are near neighbours on one topic. Sort them into sets where ONE answer fully serves
every question in the set.

SAME set:
  - rewordings, synonyms, singular/plural, with or without "under the DPDP Act/Rules"
  - "what is X" / "who is X" / "define X"
  - the same question asked by a different sector, company size or role ("do businesses need
    to…" = "does our fintech need to…" = "do SaaS companies need to…"), because the law gives
    the same answer
DIFFERENT sets:
  - different information needs: definition vs obligation vs deadline vs penalty vs how-to vs
    comparison
  - a party the law treats DIFFERENTLY: children or persons with disability, Significant Data
    Fiduciaries, the State and its instrumentalities, startups notified under section 17(3),
    Consent Managers as regulated entities, Data Processors
  - a genuinely narrower scope (a specific right, a specific deadline, a specific document)

For each set give `canonical`: the best self-contained wording — specific, plain English,
naming the DPDP Act or Rules where legal, no vendor names, preferring the most common phrasing.
Every index must appear in exactly one set.

Return JSON: {"sets": [{"members": [int], "canonical": str}]}"""


def consolidate(rows: list, usage: Usage, chunk: int = 30, floor: float = 0.55,
                model: str = "gpt-4o") -> list:
    """Final same-answer consolidation, per topic, on chunks of mutually close questions."""
    before = len(rows)
    rows = [r for r in rows if not VENDORS.search(r["question"])]
    print(f"consolidate: vendor filter {before} -> {len(rows)}", flush=True)
    matrix = embed([r["question"] for r in rows])
    by_topic = defaultdict(list)
    for i, r in enumerate(rows):
        by_topic[r["topic"]].append(i)

    chunks = []
    for members in by_topic.values():
        unassigned = sorted(members, key=lambda i: (-len(rows[i]["asked_on"]), -len(rows[i]["variants"])))
        while unassigned:
            seed = unassigned[0]
            rest = unassigned[1:]
            if rest:
                sims = matrix[rest] @ matrix[seed]
                near = [rest[j] for j in np.argsort(-sims)[:chunk - 1] if sims[j] >= floor]
            else:
                near = []
            group = [seed] + near
            chunks.append(group)
            taken = set(group)
            unassigned = [i for i in unassigned if i not in taken]
    print(f"consolidate: {len(chunks)} chunks ({sum(len(c) > 1 for c in chunks)} to review) "
          f"with {model}", flush=True)

    def run(group):
        if len(group) == 1:
            return [(group, None)]
        listing = "\n".join(f"{n}. {rows[i]['question']}" for n, i in enumerate(group))
        result = ask_json(CONSOLIDATE_SYSTEM, listing, usage, max_tokens=3500, model=model) or {}
        sets, seen = [], set()
        for item in result.get("sets", []):
            if not isinstance(item, dict):
                continue
            members = [group[n] for n in item.get("members", []) if isinstance(n, int)
                       and 0 <= n < len(group) and group[n] not in seen]
            seen.update(members)
            if members:
                canonical = (item.get("canonical") or "").strip()
                sets.append((members, canonical if canonical and not VENDORS.search(canonical) else None))
        sets += [([i], None) for i in group if i not in seen]
        return sets

    merged = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for sets in pool.map(run, chunks):
            for members, canonical in sets:
                members.sort(key=lambda i: (-len(rows[i]["asked_on"]), -len(rows[i]["variants"])))
                head = dict(rows[members[0]])
                if canonical:
                    head["question"] = canonical
                head["asked_on"] = sorted({x for i in members for x in rows[i]["asked_on"]})
                head["variants"] = list(dict.fromkeys(
                    [rows[i]["question"] for i in members] + [v for i in members for v in rows[i]["variants"]]))
                head["provisions"] = list(dict.fromkeys(p for i in members for p in rows[i]["provisions"]))
                head["example_urls"] = list(dict.fromkeys(u for i in members for u in rows[i]["example_urls"]))[:5]
                head["merged_from"] = sum(rows[i].get("merged_from", 1) for i in members)
                merged.append(head)
    print(f"consolidate: {len(rows)} -> {len(merged)} questions", flush=True)
    return merged


PAIR_SYSTEM = CONSOLIDATE_SYSTEM.split("For each set give")[0] + """For each numbered PAIR answer
`same`: true if ONE answer fully serves both questions under the rules above.
Return JSON: {"results": [{"p": int, "same": bool}]}"""


def finalize(rows: list, usage: Usage, neighbours: int = 5, floor: float = 0.86,
             model: str = "gpt-4o") -> list:
    """Cross-topic pass: judge only each question's closest neighbours in the whole bank."""
    exact, unique = {}, []
    for r in rows:                                     # exact-text duplicates first, no model needed
        key = _norm(r["question"])
        if key in exact:
            head = exact[key]
            head["asked_on"] = sorted(set(head["asked_on"]) | set(r["asked_on"]))
            head["variants"] = list(dict.fromkeys(head["variants"] + r["variants"]))
        else:
            exact[key] = dict(r)
            unique.append(exact[key])
    rows = unique
    matrix = embed([r["question"] for r in rows])
    sims = matrix @ matrix.T
    np.fill_diagonal(sims, -1)
    pairs = sorted({(min(i, int(j)), max(i, int(j))) for i in range(len(rows))
                    for j in np.argsort(-sims[i])[:neighbours] if sims[i, j] >= floor})
    print(f"finalize: {len(pairs)} cross-topic pairs to judge with {model}", flush=True)

    same = []
    batches = [pairs[k:k + 30] for k in range(0, len(pairs), 30)]

    def judge(batch):
        listing = "\n".join(f"{p}. A: {rows[a]['question']}\n   B: {rows[b]['question']}"
                            for p, (a, b) in enumerate(batch))
        result = ask_json(PAIR_SYSTEM, listing, usage, max_tokens=2000, model=model) or {}
        return [batch[r["p"]] for r in result.get("results", [])
                if isinstance(r, dict) and r.get("same") and isinstance(r.get("p"), int)
                and 0 <= r["p"] < len(batch)]

    with ThreadPoolExecutor(max_workers=4) as pool:
        for found in pool.map(judge, batches):
            same += found

    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a, b in same:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    groups = defaultdict(list)
    for i in range(len(rows)):
        groups[find(i)].append(i)

    def resplit(chain):
        """A chain of pairwise matches isn't proof the ends match; let the editor sort it."""
        listing = "\n".join(f"{n}. {rows[i]['question']}" for n, i in enumerate(chain))
        result = ask_json(CONSOLIDATE_SYSTEM, listing, usage, max_tokens=2500, model=model) or {}
        sets, seen = [], set()
        for item in result.get("sets", []):
            if isinstance(item, dict):
                picked = [chain[n] for n in item.get("members", []) if isinstance(n, int)
                          and 0 <= n < len(chain) and chain[n] not in seen]
                seen.update(picked)
                if picked:
                    sets.append(picked)
        return sets + [[i] for i in chain if i not in seen]

    final = []
    for members in groups.values():
        if len(members) > 4:
            parts = resplit(members)
            print(f"finalize: {len(members)}-way chain re-split into {len(parts)} sets", flush=True)
            final += parts
        else:
            final.append(members)

    merged = []
    for members in final:
        members.sort(key=lambda i: (-len(rows[i]["asked_on"]), -len(rows[i]["variants"])))
        head = dict(rows[members[0]])
        head["asked_on"] = sorted({x for i in members for x in rows[i]["asked_on"]})
        head["variants"] = list(dict.fromkeys(v for i in members for v in [rows[i]["question"]] + rows[i]["variants"]))
        head["provisions"] = list(dict.fromkeys(p for i in members for p in rows[i]["provisions"]))
        head["example_urls"] = list(dict.fromkeys(u for i in members for u in rows[i]["example_urls"]))[:5]
        head["merged_from"] = sum(rows[i].get("merged_from", 1) for i in members)
        merged.append(head)
    print(f"finalize: {len(same)} same-pairs · {len(rows)} -> {len(merged)} questions", flush=True)
    return merged


def write_graph(rows: list):
    rows.sort(key=lambda r: (-len(r["asked_on"]), -len(r["variants"]), r["question"]))
    out = []
    for n, r in enumerate(rows, 1):
        out.append({
            "question_id": f"Q-{n:05d}",
            "question": r["question"],
            "topic": r["topic"], "audience": r["audience"], "intent": r["intent"],
            "provisions": r["provisions"],
            "demand_sites": len(r["asked_on"]),
            "demand_variants": len(r["variants"]),
            "asked_on": r["asked_on"],
            "saralprivacy_asks": any(s in ("saralprivacy.com", "dpdpa.wiki") for s in r["asked_on"]),
            "variants": r["variants"][:12],
            "example_urls": r["example_urls"],
            "canonicalised_by": r["canonicalised_by"],
            "merged_from": r.get("merged_from", 1),
        })
    with open(GRAPH, "w") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in out)
    print(f"graph: {len(out)} canonical questions -> {GRAPH}", flush=True)


def main():
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    usage = Usage()
    if step in ("screen", "all"):
        screen(usage)
    if step in ("embed", "all"):
        run_embed()
    if step in ("cluster", "all"):
        clusters = cluster()
        print(f"cluster: {len(clusters)} clusters at similarity {SIMILARITY}", flush=True)
    if step in ("canonical", "all"):
        rows = canonicalise(usage)
        json.dump(rows, open(os.path.join(OUT_DIR, "canonical_pre_dedup.json"), "w"), ensure_ascii=False)
        rows = dedup(rows, usage)
        json.dump(rows, open(os.path.join(OUT_DIR, "canonical_after_dedup.json"), "w"), ensure_ascii=False)
        rows = semantic_dedup(filter_questions(rows, usage), usage)
        write_graph(rows)
        print(f"total LLM spend this run · {usage}", flush=True)
    if step == "refine":  # re-run only the filter + semantic dedup on the saved dedup output
        rows = json.load(open(os.path.join(OUT_DIR, "canonical_after_dedup.json")))
        rows = semantic_dedup(filter_questions(rows, usage), usage)
        json.dump(rows, open(os.path.join(OUT_DIR, "canonical_after_semantic.json"), "w"), ensure_ascii=False)
        write_graph(rows)
        print(f"total LLM spend this run · {usage}", flush=True)
    if step == "finalize":  # cross-topic duplicate pass on the current graph
        graph = [json.loads(l) for l in open(GRAPH)]
        rows = [{"question": g["question"], "topic": g["topic"], "audience": g["audience"],
                 "intent": g["intent"], "provisions": g["provisions"], "asked_on": g["asked_on"],
                 "variants": g["variants"], "example_urls": g["example_urls"],
                 "canonicalised_by": g["canonicalised_by"], "merged_from": g.get("merged_from", 1)}
                for g in graph]
        json.dump(rows, open(os.path.join(OUT_DIR, "canonical_before_finalize.json"), "w"), ensure_ascii=False)
        big = Usage("gpt-4o")
        write_graph(finalize(rows, big))
        print(f"total LLM spend this run · {big}", flush=True)
    if step == "consolidate":  # final same-answer pass on the current graph
        graph = [json.loads(l) for l in open(GRAPH)]
        rows = [{"question": g["question"], "topic": g["topic"], "audience": g["audience"],
                 "intent": g["intent"], "provisions": g["provisions"], "asked_on": g["asked_on"],
                 "variants": g["variants"], "example_urls": g["example_urls"],
                 "canonicalised_by": g["canonicalised_by"], "merged_from": g.get("merged_from", 1)}
                for g in graph]
        json.dump(rows, open(os.path.join(OUT_DIR, "canonical_before_consolidate.json"), "w"), ensure_ascii=False)
        big = Usage("gpt-4o")
        write_graph(consolidate(rows, big))
        print(f"total LLM spend this run · {big}", flush=True)


if __name__ == "__main__":
    main()
