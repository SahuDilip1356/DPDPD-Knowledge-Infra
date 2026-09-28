"""
Builds canonical Knowledge Objects and loads them into Supabase and Pinecone.

  primary  — one KO per provision of the Act, Rules and Schedules that the live graph lacks.
             Summary is the verbatim gazette text: no model touches it. Hashed per chunk.
  answers  — one KO per canonical question (question_graph.jsonl), answered ONLY from the
             text of the provisions it maps to. Rejected in code unless:
               * every evidence quote appears verbatim in the provision it cites, and
               * every "Section N" / "Rule N" the answer mentions was actually supplied.
  push     — upsert KOs + graph edges into Supabase, embed + upsert into Pinecone (vector id =
             URN, same text recipe and metadata as src/reasoning/index_vectors.py).
  rollback — delete everything this script wrote (by URN prefix) from Supabase and Pinecone.

Namespaces (new, so nothing links into the draft-numbered rule KOs already in the graph):
  urn:ki:in:dpdp:act:2023:sec:N            (matches the existing Act section KOs)
  urn:ki:in:dpdp:rules:2025:rule:N         notified G.S.R. 846(E) numbering
  urn:ki:in:dpdp:rules:2025:schedule:NAME
  urn:ki:in:dpdp:qa:<slug>-<hash>          canonical question answers

Usage:  python3 src/competitive_intel/build_knowledge_objects.py primary
        python3 src/competitive_intel/build_knowledge_objects.py answers [--limit N]
        python3 src/competitive_intel/build_knowledge_objects.py push [--dry-run]
        python3 src/competitive_intel/build_knowledge_objects.py rollback
"""
import argparse
import hashlib
import json
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import requests

from fetch import REPO_ROOT
from llm import Usage, ask_json
from question_graph import GRAPH, embed
from verify_claims import load_law

OUT_DIR = os.path.join(REPO_ROOT, "staging/competitive_intel/knowledge_objects")
PRIMARY_FILE = os.path.join(OUT_DIR, "primary_kos.jsonl")
ANSWERS_FILE = os.path.join(OUT_DIR, "answer_kos.jsonl")
REJECTS_FILE = os.path.join(OUT_DIR, "answer_rejects.jsonl")
MANIFEST = os.path.join(OUT_DIR, "pushed_urns.json")
GT_DIR = os.path.join(REPO_ROOT, "staging/competitive_intel/ground_truth")
ANSWER_MODEL = os.getenv("CI_ANSWER_MODEL") or "gpt-4o"
DEFAULT_ANSWERS = 500
MAX_SUPPLIED = 6
PROVISION_CHARS = 3000
DEFINITIONS_CHARS = 5000
ANSWER_WORKERS = 2

ACT_DOC = "urn:ki:in:dpdp:act:dpdpa-2023"
RULES_DOC = "urn:ki:in:dpdp:rule:dpdp-rules-2025"
ACT_SOURCE = "urn:ki:in:dpdp:source:gazette-dpdpa-2023"
RULES_SOURCE = "urn:ki:in:dpdp:source:gazette-gsr-846e-2025"
QA_PREFIX = "urn:ki:in:dpdp:qa:"
OWNED_PREFIXES = (QA_PREFIX, "urn:ki:in:dpdp:rules:2025:")

ANSWER_SYSTEM = """You answer questions about India's Digital Personal Data Protection Act, 2023
("the Act") and the DPDP Rules, 2025 ("the Rules") for Indian small-business owners.

You are given ONE question and the verbatim text of the provisions that govern it. That text is
your only source. Do not use memory, draft rules, news, or anything not in the supplied text.

Write:
  answer      80-200 words of plain English. Lead with the direct answer. Cite provisions inline
              exactly as "Section 6(4)" or "Rule 7(1)". Only cite provisions you were given.
              If a governing Rule is not yet in force (see COMMENCEMENT), say from when it applies.
              Calm and practical: no fear-mongering, no marketing, no "consult a lawyer" filler.
              Use the Act's own terms: "Data Principal" (never "data subject"), "Data Fiduciary"
              (never "controller"), "Data Processor", "Board".
  key_points  3-5 short bullets a business can act on.
  evidence    1-4 items: {"provision": the bracketed label of the provision, e.g. "S10" or "R7",
              "quote": text copied VERBATIM from that provision, 40-300 characters}. Each quote
              must support a specific statement in the answer.
  impact_summary   one sentence on what this means for a business.
  action_required  one sentence on what to do.
  entities    3-6 legal terms the answer relies on (e.g. "Data Fiduciary", "consent").
  answerable  false if the supplied text does not actually answer the question; then leave the
              other fields empty. Do not stretch the law to fit.

Return JSON: {"answerable": bool, "answer": str, "key_points": [str], "evidence":
[{"provision": str, "quote": str}], "impact_summary": str, "action_required": str,
"entities": [str]}"""

lock = threading.Lock()
TODAY = date.today().isoformat()


def pretty(iso: str) -> str:
    y, m, d = iso.split("-")
    months = ["January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December"]
    return f"{int(d)} {months[int(m) - 1]} {y}"


# ---------------------------------------------------------------- helpers
def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"(\w) -(\w)", r"\1-\2", text)).strip().lower()


def is_act(label: str) -> bool:
    return label == "ACT-SCHEDULE" or bool(re.fullmatch(r"S\d+", label))


def provision_urn(label: str) -> str:
    if label == "ACT-SCHEDULE":
        return "urn:ki:in:dpdp:act:2023:schedule"
    if label.startswith("SCH-"):
        return f"urn:ki:in:dpdp:rules:2025:schedule:{label[4:].lower()}"
    if label.startswith("S"):
        return f"urn:ki:in:dpdp:act:2023:sec:{label[1:]}"
    return f"urn:ki:in:dpdp:rules:2025:rule:{label[1:]}"


def provision_ref(label: str) -> str:
    if label == "ACT-SCHEDULE":
        return "The Schedule, DPDPA 2023"
    if label.startswith("SCH-"):
        return f"{label[4:].title()} Schedule, DPDP Rules 2025"
    if label.startswith("S"):
        return f"Section {label[1:]}, DPDPA 2023"
    return f"Rule {label[1:]}, DPDP Rules 2025"


def evidence_item(label: str, quote: str, law: dict, n: int) -> dict:
    act_provision = is_act(label)
    coordinates = ({"schedule": "The Schedule (penalties)"} if label == "ACT-SCHEDULE" else
                   {"section": f"Section {label[1:]}"} if act_provision else
                   {"schedule": label[4:].title()} if label.startswith("SCH") else
                   {"rule": f"Rule {label[1:]}"})
    return {
        "id": f"ev-{label.lower()}-{n}",
        "source_urn": ACT_SOURCE if act_provision else RULES_SOURCE,
        "coordinates": coordinates,
        "source_name": ("Gazette of India — DPDPA 2023" if act_provision else
                        "Gazette of India — G.S.R. 846(E), DPDP Rules 2025 (corrected by G.S.R. 892(E))"),
        "source_tier": "primary",
        "citation_text": quote,
        "chunk_sha256": sha256(law[label]["text"]),
        "verification_status": "verified",
    }


def existing_urns() -> set:
    """URNs already live, so primary KOs never overwrite a curated row."""
    from supabase import create_client
    client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
    rows = client.table("knowledge_objects").select("urn").is_("system_time_end", "null").execute().data
    return {r["urn"] for r in rows}


# ---------------------------------------------------------------- primary
def build_primary():
    law, commencement = load_law()
    live = existing_urns()
    os.makedirs(OUT_DIR, exist_ok=True)
    rows, skipped = [], []
    for label, provision in law.items():
        urn = provision_urn(label)
        if urn in live:
            skipped.append(urn)
            continue
        act_provision = is_act(label)
        text = provision["text"]
        in_force = commencement.get(label)
        title = ("The Schedule — Penalties (DPDPA 2023)" if label == "ACT-SCHEDULE" else
                 f"Section {label[1:]} — {provision['title']}" if act_provision else
                 f"{provision['title']} — DPDP Rules 2025" if label.startswith("SCH") else
                 f"Rule {label[1:]} — {provision['title']} (DPDP Rules 2025)")
        rows.append({
            "urn": urn, "version": 1,
            "type": "Act" if act_provision else "Rule",
            "title": title,
            "summary": text[:1500] + (" …" if len(text) > 1500 else ""),
            "confidence_score": 1.0,
            "source_credibility": "primary",
            "interpretation_stance": "verbatim",
            "legal_time_start": "2023-08-11" if act_provision else (in_force or "2025-11-13"),
            "body": {"full_text": text, "provision": label, "reference": provision_ref(label),
                     "in_force_from": in_force, "entities": []},
            "business_impact": {},
            "evidence": [evidence_item(label, text[:300], law, 1)],
            "linked_objects": [ACT_DOC if act_provision else RULES_DOC],
            "entities": [],
            "relations": [{"edge_type": "Depends On", "target_urn": ACT_DOC if act_provision else RULES_DOC}],
        })
    with open(PRIMARY_FILE, "w") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    print(f"primary: {len(rows)} new provision KOs, {len(skipped)} already live (left untouched)")


# ---------------------------------------------------------------- answers
def answer_urn(question: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", question.lower()).strip("-")[:60].rstrip("-")
    return f"{QA_PREFIX}{slug}-{sha256(normalise(question))[:8]}"


MIN_VERIFIED = 30


def verified_citation(quote: str, law_text: str) -> str:
    """The part of `quote` that is provably in the law, re-sliced FROM the law so the stored
    citation is the gazette's exact wording. Handles elision ("…"): each fragment is matched on
    its own. A fragment that drifts from the text keeps only its longest verbatim prefix, and
    only if that prefix is at least MIN_VERIFIED characters. Returns "" if nothing verifies."""
    source = re.sub(r"\s+", " ", re.sub(r"(\w) -(\w)", r"\1-\2", law_text)).strip()
    haystack = source.lower()
    pieces = []
    for fragment in re.split(r"\s*(?:\.{3}|…)\s*", quote):
        needle = re.sub(r"\s+", " ", re.sub(r"(\w) -(\w)", r"\1-\2", fragment)).strip().lower()
        if len(needle) < MIN_VERIFIED:
            continue
        low, high = 0, len(needle)          # longest prefix of needle present in haystack
        while low < high:
            mid = (low + high + 1) // 2
            if needle[:mid] in haystack:
                low = mid
            else:
                high = mid - 1
        if low >= MIN_VERIFIED:
            at = haystack.find(needle[:low])
            pieces.append(source[at:at + low].strip())
    return " … ".join(pieces)[:400]


def to_label(raw) -> str:
    """"S10", "Section 10(1)", "Rule 7(2)", "R7", "First Schedule" -> S10 / R7 / SCH-FIRST."""
    text = str(raw or "").strip()
    upper = text.upper().replace(" ", "")
    if re.fullmatch(r"(S|R)\d{1,2}", upper) or upper.startswith("SCH-"):
        return upper
    match = re.match(r"(S|R)(\d{1,2})\b", upper)          # "S8(6)", "R7(1)(a)"
    if match:
        return match.group(1) + match.group(2)
    match = re.match(r"(?i)\s*(section|sec\.?|rule|r\.?)\s*(\d{1,2})", text)
    if match:
        return ("S" if match.group(1).lower().startswith("s") else "R") + match.group(2)
    match = re.match(r"(?i)\s*(first|second|third|fourth|fifth|sixth|seventh)\s+schedule", text)
    if match:
        return "SCH-" + match.group(1).upper()
    if upper in ("ACT-SCHEDULE", "SCHEDULE", "THESCHEDULE") or re.match(r"(?i)\s*(the\s+)?schedule\b", text):
        return "ACT-SCHEDULE"
    return upper


def check(result: dict, supplied: list, law: dict) -> tuple:
    """Return (evidence, reason). reason is None when the answer passes every gate."""
    if not result or not result.get("answerable"):
        return [], "not answerable from the supplied law"
    answer = result.get("answer") or ""
    if len(answer.split()) < 40:
        return [], "answer too short"

    evidence = []
    for n, item in enumerate(result.get("evidence") or [], 1):
        if not isinstance(item, dict):
            continue
        label = to_label(item.get("provision"))
        quote = (item.get("quote") or "").strip()
        if label in supplied:
            citation = verified_citation(quote, law[label]["text"])
            if citation:
                evidence.append(evidence_item(label, citation, law, n))
    if not evidence:
        return [], "no evidence quote matched the law verbatim"

    mentioned = {f"S{n}" for n in re.findall(r"\bSection\s+(\d{1,2})", answer)}
    mentioned |= {f"R{n}" for n in re.findall(r"\bRule\s+(\d{1,2})", answer)}
    # A provision the supplied law itself cross-refers to ("sub-section (5) of section 8") may be named.
    referenced = {f"S{n}" for p in supplied for n in re.findall(r"(?i)\bsection\s+(\d{1,2})\b", law[p]["text"])}
    referenced |= {f"R{n}" for p in supplied for n in re.findall(r"(?i)\brule\s+(\d{1,2})\b", law[p]["text"])}
    stray = sorted(mentioned - set(supplied) - referenced)
    if stray:
        return [], f"answer cites provisions it was not given: {stray}"
    return evidence, None


class ProvisionRetriever:
    """Embedding search over every provision, so an answer is not hostage to a bad mapping
    (e.g. "Who needs to comply?" belongs to Section 3, which the mapping missed)."""

    def __init__(self, law: dict):
        self.labels = list(law)
        self.matrix = embed([f"{law[k]['title']}. {law[k]['text'][:1500]}" for k in self.labels])

    def top(self, vectors, k: int = 4) -> list:
        scores = vectors @ self.matrix.T
        return [[self.labels[j] for j in row.argsort()[::-1][:k]] for row in scores]


DEFINITION = re.compile(r"(?i)^\s*(what|who)\s+(is|are|does|do)\b|\bdefin|\bmeaning\b|\bmean\b")
PENALTY = re.compile(r"(?i)penalt|fine[sd]?\b|crore|punish")
DEADLINE = re.compile(r"(?i)\bwhen\b|deadline|timeline|in force|come into|commence|effective|by when|how long do")
BREACH = re.compile(r"(?i)breach|72.hour|seventy.two")
OVERVIEW = re.compile(r"(?i)what (topics|areas|matters)|what do(es)? the dpdp (act|rules)\b.*\bcover|overview|"
                      r"key (provisions|features|components)|structure of|summar")


def answer_one(q: dict, law: dict, commencement: dict, usage: Usage, retrieved: list) -> dict:
    mapped = [p for p in q["provisions"] if p in law]
    forced = []
    if q.get("intent") == "definition" or DEFINITION.search(q["question"]):
        forced += ["S2", "R2"]
    if q.get("intent") == "penalty" or PENALTY.search(q["question"]):
        forced += ["S33", "ACT-SCHEDULE"]
    if q.get("intent") == "deadline" or DEADLINE.search(q["question"]):
        forced += ["R1"]                   # the Rules' own commencement clause
    if BREACH.search(q["question"]):
        forced += ["S8", "R7"]
    supplied = list(dict.fromkeys(forced + mapped[:4] + retrieved))[:MAX_SUPPLIED]
    # gpt-4o on this key allows 30k tokens/minute: keep each prompt near 4k tokens.
    texts = "\n\n".join(
        f"=== [{p}] {provision_ref(p)} — {law[p]['title']} ===\n"
        f"{law[p]['text'][:DEFINITIONS_CHARS if p == 'S2' else PROVISION_CHARS]}"
        for p in supplied)
    starts = [f"{p}: in force from {commencement[p]}" for p in supplied if p in commencement]
    index = ""
    if OVERVIEW.search(q["question"]):
        index = "--- INDEX OF EVERY SECTION AND RULE (headings only) ---\n" + "\n".join(
            f"{provision_ref(k)}: {law[k]['title']}" for k in law) + "\n\n"
    prompt = (f"QUESTION: {q['question']}\n\nTODAY: {TODAY}\n"
              f"COMMENCEMENT OF RULES: {'; '.join(starts) or 'n/a (Act provisions only)'}\n\n"
              f"{index}--- GOVERNING PROVISIONS ---\n{texts}")
    result = ask_json(ANSWER_SYSTEM, prompt, usage, max_tokens=1400, model=ANSWER_MODEL, retries=10)
    if result is None:  # the API never answered: leave it for the next run, don't reject it
        return {"retry": q["question_id"]}
    evidence, reason = check(result, supplied, law)
    gdpr_terms = r"(?i)\bdata subjects?\b|\bdata controllers?\b|\bcontrollers?\b"
    if not reason and re.search(gdpr_terms, result.get("answer") or "") \
            and not re.search(gdpr_terms, q["question"]):   # echoing the asker's own term is fine
        reason = "uses GDPR terminology instead of the Act's terms"
    if reason:
        return {"reject": {"question_id": q["question_id"], "question": q["question"], "reason": reason}}

    used = list(dict.fromkeys(e_label for e_label in supplied
                              if any(e["id"].startswith(f"ev-{e_label.lower()}-") for e in evidence)))
    rule_dates = [commencement[p] for p in supplied if p in commencement]
    answer_text = result["answer"].strip()
    named = {f"R{n}" for n in re.findall(r"\bRule\s+(\d{1,2})", answer_text)}
    pending = sorted({(commencement[p], p) for p in set(used) | named
                      if p in commencement and commencement[p] > TODAY})
    # Add the date only where the answer hasn't already said it.
    pending = [(d, p) for d, p in pending if d[:4] not in answer_text]
    if pending:
        when = "; ".join(f"Rule {p[1:]} applies from {pretty(d)}" for d, p in pending)
        answer_text += f" Note: {when}."
    entities = [e for e in (result.get("entities") or []) if isinstance(e, str)][:6]
    key_points = [k for k in (result.get("key_points") or []) if isinstance(k, str)][:5]
    return {"ko": {
        "urn": answer_urn(q["question"]), "version": 1,
        "type": "Answer",
        "title": q["question"],
        "summary": answer_text,
        "confidence_score": 0.9,
        "source_credibility": "primary-derived",
        "interpretation_stance": "plain-language synthesis of primary law",
        "legal_time_start": "2025-11-13" if any(not is_act(p) for p in used) else "2023-08-11",
        "body": {
            "question_id": q["question_id"], "key_points": key_points,
            "topic": q["topic"], "audience": q["audience"], "intent": q["intent"],
            "provisions": supplied, "cited": used,
            "rules_in_force_from": {p: commencement[p] for p in supplied if p in commencement},
            "demand_sites": q["demand_sites"], "asked_on": q["asked_on"],
            "question_variants": q["variants"], "entities": entities,
            "generated_by": ANSWER_MODEL, "review_status": "pending",
        },
        "business_impact": {"impact_summary": (result.get("impact_summary") or "").strip(),
                            "action_required": (result.get("action_required") or "").strip()},
        "evidence": evidence,
        "linked_objects": [provision_urn(p) for p in used],
        "entities": entities,
        "relations": [{"edge_type": "Interprets", "target_urn": provision_urn(p)} for p in used],
    }}


def build_answers(limit: int):
    law, commencement = load_law()
    graph = [json.loads(line) for line in open(GRAPH)]
    done = set()
    if os.path.exists(ANSWERS_FILE):
        done |= {json.loads(l)["body"]["question_id"] for l in open(ANSWERS_FILE)}
    if os.path.exists(REJECTS_FILE):
        done |= {json.loads(l)["question_id"] for l in open(REJECTS_FILE)}

    # Most-asked answerable questions first; SaralPrivacy's own questions ride along.
    eligible = list(graph)
    eligible.sort(key=lambda q: (-q["demand_sites"], -q["demand_variants"]))
    todo = [q for q in eligible[:limit] if q["question_id"] not in done]
    print(f"answers: {len(eligible)} canonical questions, building top {limit} by demand "
          f"({len(todo)} to do) with {ANSWER_MODEL}", flush=True)

    usage, made, rejected, retry = Usage(ANSWER_MODEL), 0, 0, 0
    os.makedirs(OUT_DIR, exist_ok=True)

    retriever = ProvisionRetriever(law)
    nearest = dict(zip((q["question_id"] for q in todo),
                       retriever.top(embed([q["question"] for q in todo])) if todo else []))

    def run(q):
        return answer_one(q, law, commencement, usage, nearest[q["question_id"]])

    with ThreadPoolExecutor(max_workers=ANSWER_WORKERS) as pool:
        for n, out in enumerate(pool.map(run, todo), 1):
            with lock:
                if "retry" in out:
                    retry += 1
                elif "ko" in out:
                    made += 1
                    with open(ANSWERS_FILE, "a") as f:
                        f.write(json.dumps(out["ko"], ensure_ascii=False) + "\n")
                else:
                    rejected += 1
                    with open(REJECTS_FILE, "a") as f:
                        f.write(json.dumps(out["reject"], ensure_ascii=False) + "\n")
            if n % 50 == 0:
                print(f"  {n}/{len(todo)} · {made} built, {rejected} rejected, {retry} to retry "
                      f"· ${usage.cost_usd:.2f}", flush=True)
    print(f"answers: {made} built, {rejected} rejected, {retry} left for a rerun · {usage}")


# ---------------------------------------------------------------- answer-level dedup
def dedup_answers(threshold: float = 0.95):
    """Two questions whose answers cite the same provisions and read near-identically are one
    question. Keep the higher-demand one; fold the other in as a variant."""
    kos = [json.loads(l) for l in open(ANSWERS_FILE)]
    vectors = embed([k["summary"] for k in kos])
    sims = vectors @ vectors.T
    order = sorted(range(len(kos)), key=lambda i: -kos[i]["body"]["demand_sites"])
    absorbed, kept = set(), []
    for i in order:
        if i in absorbed:
            continue
        for j in order:
            if j == i or j in absorbed or sims[i, j] < threshold:
                continue
            if set(kos[i]["body"]["cited"]) == set(kos[j]["body"]["cited"]):
                absorbed.add(j)
                body = kos[i]["body"]
                body["question_variants"] = list(dict.fromkeys(
                    body["question_variants"] + [kos[j]["title"]] + kos[j]["body"]["question_variants"]))
                body["asked_on"] = sorted(set(body["asked_on"]) | set(kos[j]["body"]["asked_on"]))
                body["demand_sites"] = len(body["asked_on"])
                body.setdefault("merged_questions", []).append(kos[j]["body"]["question_id"])
        kept.append(kos[i])
    with open(ANSWERS_FILE, "w") as f:
        f.writelines(json.dumps(k, ensure_ascii=False) + "\n" for k in kept)
    print(f"answer dedup: {len(kos)} -> {len(kept)} ({len(absorbed)} same-answer questions folded in)")


# ---------------------------------------------------------------- push / rollback
def pinecone_host() -> str:
    name = os.getenv("PINECONE_INDEX_NAME") or "dpdpa-knowledge"
    resp = requests.get(f"https://api.pinecone.io/indexes/{name}", timeout=20,
                        headers={"Api-Key": os.getenv("PINECONE_API_KEY"), "X-Pinecone-API-Version": "2024-07"})
    resp.raise_for_status()
    return resp.json()["host"]


def push(dry_run: bool):
    from supabase import create_client
    kos = []
    for path in (PRIMARY_FILE, ANSWERS_FILE):
        if os.path.exists(path):
            kos += [json.loads(l) for l in open(path)]
    print(f"push: {len(kos)} KOs ({sum(k['type'] == 'Answer' for k in kos)} answers)")
    if dry_run:
        return

    client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
    for start in range(0, len(kos), 100):
        client.table("knowledge_objects").upsert(kos[start:start + 100], on_conflict="urn,version").execute()
    edges = [{"source_urn": k["urn"], "source_version": k["version"], "target_urn": r["target_urn"],
              "edge_type": r["edge_type"]} for k in kos for r in k["relations"]]
    urns = [k["urn"] for k in kos]
    for start in range(0, len(urns), 100):  # replace, don't duplicate, this script's own edges
        client.table("graph_edges").delete().in_("source_urn", urns[start:start + 100]).execute()
    for start in range(0, len(edges), 200):
        client.table("graph_edges").insert(edges[start:start + 200]).execute()
    print(f"push: supabase ok — {len(kos)} KOs, {len(edges)} edges")

    # Same text recipe and metadata as src/reasoning/index_vectors.py, so retrieval is consistent.
    texts = [f"Title: {k['title']}. Type: {k['type']}. Summary: {k['summary']}. "
             f"Entities: {', '.join(k['body'].get('entities', []))}" for k in kos]
    vectors = embed(texts)
    host = pinecone_host()
    headers = {"Api-Key": os.getenv("PINECONE_API_KEY"), "Content-Type": "application/json"}
    for start in range(0, len(kos), 100):
        batch = [{"id": k["urn"], "values": vectors[i].tolist(),
                  "metadata": {"title": k["title"], "type": k["type"], "version": k["version"],
                               "summary": k["summary"][:2000]}}
                 for i, k in enumerate(kos[start:start + 100], start)]
        resp = requests.post(f"https://{host}/vectors/upsert", headers=headers,
                             json={"vectors": batch}, timeout=60)
        resp.raise_for_status()
    json.dump(urns, open(MANIFEST, "w"), indent=1)
    print(f"push: pinecone ok — {len(kos)} vectors; manifest -> {MANIFEST}")


def rollback():
    from supabase import create_client
    urns = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else []
    client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
    for start in range(0, len(urns), 100):
        chunk = urns[start:start + 100]
        client.table("graph_edges").delete().in_("source_urn", chunk).execute()
        client.table("knowledge_objects").delete().in_("urn", chunk).execute()
    host = pinecone_host()
    headers = {"Api-Key": os.getenv("PINECONE_API_KEY"), "Content-Type": "application/json"}
    for start in range(0, len(urns), 1000):
        requests.post(f"https://{host}/vectors/delete", headers=headers,
                      json={"ids": urns[start:start + 1000]}, timeout=60).raise_for_status()
    print(f"rollback: removed {len(urns)} KOs, their edges, and their vectors")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("step", choices=["primary", "answers", "dedup", "push", "rollback"])
    parser.add_argument("--limit", type=int, default=DEFAULT_ANSWERS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    {"primary": build_primary,
     "answers": lambda: build_answers(args.limit),
     "dedup": dedup_answers,
     "push": lambda: push(args.dry_run),
     "rollback": rollback}[args.step]()


if __name__ == "__main__":
    main()
