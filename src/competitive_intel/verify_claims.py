"""
Stage 2: the Source Truth agent. Checks each extracted claim against primary law only:

  DPDPA 2023 (MeitY text)                          -> provisions S1..S44
  DPDP Rules 2025, G.S.R. 846(E) as corrected by   -> provisions R1..R23 and the Schedules
  G.S.R. 892(E)

Never against another competitor page, and never against a plain-English guide.

The agent sees the claim, an index of every section and rule heading, and the full text of
the provisions most likely to govern it (the ones the page cited, plus the best keyword
matches), so it can catch a claim that cites the wrong provision.

Verdicts:
  VERIFIED_PRIMARY         the law states this; the quote proves it
  SUPPORTED_INTERPRETATION a fair reading, but the law does not state it outright
  CONTESTED                the law is genuinely ambiguous, or provisions pull against each other
  UNSUPPORTED              nothing in the supplied provisions supports it
  INCORRECT                the law contradicts it, or it cites the wrong provision
  OUT_OF_SCOPE             not a claim about the Act or Rules (market data, other statutes, vendors)

Two safeguards sit in code, not in the prompt:
  - VERIFIED_PRIMARY is downgraded unless its quote really appears in the supplied law.
  - Commencement of each governing Rule is attached from Rule 1, so a reader can see when a
    stated obligation actually bites.

Only VERIFIED_PRIMARY LEGAL claims get publication_allowed.

Writes  staging/competitive_intel/claims/claims_registry.jsonl   (resumable)

Usage:  python3 src/competitive_intel/verify_claims.py [--limit N] [--workers N]
"""
import argparse
import json
import os
import re
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from fetch import REPO_ROOT
from llm import MODEL, Usage, ask_json

CLAIMS_DIR = os.path.join(REPO_ROOT, "staging/competitive_intel/claims")
CLAIMS_FILE = os.path.join(CLAIMS_DIR, "claims.jsonl")
OUT_FILE = os.path.join(CLAIMS_DIR, "claims_registry.jsonl")
GT_DIR = os.path.join(REPO_ROOT, "staging/competitive_intel/ground_truth")
CANDIDATES = 4         # keyword-matched provisions supplied alongside any cited ones
MAX_PROVISIONS = 7
PROVISION_CHARS = 4500
VERIFIED_AGAINST = "DPDPA 2023 (MeitY) + DPDP Rules 2025 (G.S.R. 846(E) as corrected by G.S.R. 892(E))"

STOPWORDS = set("the a an and or of to in for on by with is are be shall must may not that this "
                "it as from at under any all such which who whom whose data personal act india "
                "indian dpdp dpdpa section rule rules if then than their its his her they them "
                "also into been being have has had will would should could within other".split())

SYSTEM = """You are a verification agent for Indian data-protection law.

You are given ONE claim taken from a commercial website, plus authoritative primary law:
  - the Digital Personal Data Protection Act, 2023 (provisions labelled S1..S44)
  - the Digital Personal Data Protection Rules, 2025 (provisions labelled R1..R23, and Schedules)

The supplied text is the ONLY authority. Do not rely on memory, news, draft rules, other
websites, or what the site says about itself. If the answer is not in the supplied text, say so.

verdict — choose exactly one:
  VERIFIED_PRIMARY          the supplied law STATES this, near enough word for word that your
                            quote alone convinces a sceptical reader. If you had to reason from
                            the text to the claim, this is not the verdict.
  SUPPORTED_INTERPRETATION  a fair reading of the law, but it does not state it outright.
                            Anything inferred, generalised, or summarised belongs here.
  CONTESTED                 the law is genuinely ambiguous, or provisions pull against each other.
  UNSUPPORTED               the supplied law neither supports nor contradicts it.
  INCORRECT                 the law CONTRADICTS the claim (a wrong number, deadline, amount,
                            threshold, or party), or the claim cites a provision that plainly
                            does not say what it says. Name the provision that governs.
                            Silence is not contradiction: if the law does not address the point,
                            that is UNSUPPORTED or OUT_OF_SCOPE, never INCORRECT.
  OUT_OF_SCOPE              not a claim the supplied law can settle: market conditions, other
                            statutes (GDPR, IT Act, RTI Act), a vendor's product, gazette dates,
                            who has been appointed to the Board, or WHEN a section of the ACT
                            comes into force (the Act's commencement is set by a separate
                            notification that is not supplied). The RULES' own commencement IS
                            supplied, in R1, and can be judged.

Rules:
- A claim that attributes something to the Act when it is actually in the Rules (or the reverse)
  is INCORRECT only if it names a specific section/rule number that is wrong. If it just says
  "under the DPDP law", judge the substance.
- A claim citing the wrong provision number is INCORRECT even when its substance is right.
- act_quote: copied VERBATIM from the supplied law, 300 characters or fewer. Empty for
  UNSUPPORTED and OUT_OF_SCOPE.
- governing: the provision labels that actually decide the claim, e.g. ["S8", "R7"].
  Empty for OUT_OF_SCOPE.
- When torn between VERIFIED_PRIMARY and SUPPORTED_INTERPRETATION, choose the latter. A false
  VERIFIED_PRIMARY is the most costly mistake you can make.
- reasoning: one or two sentences. No hedging, no restating the claim.
- confidence: 0.0-1.0, how sure you are of this verdict given only the supplied text.

Return JSON: {"verdict": str, "governing": [str], "act_quote": str, "reasoning": str,
"confidence": float}"""

write_lock = threading.Lock()


def load_law() -> tuple:
    """All provisions keyed "S6", "R7", "SCH-FIRST", plus Rules commencement dates."""
    act_path = os.path.join(GT_DIR, "act_sections.json")
    rules_path = os.path.join(GT_DIR, "rules_sections.json")
    for path in (act_path, rules_path):
        if not os.path.exists(path):
            raise SystemExit(f"Missing ground truth {path} — run ground_truth.py and rules_ground_truth.py")

    law = {}
    for number, section in json.load(open(act_path))["sections"].items():
        law[f"S{number}"] = {"label": f"Section {number} of the Act", "title": section["title"],
                             "text": section["text"]}
    act = json.load(open(act_path))
    if act.get("schedule"):
        law["ACT-SCHEDULE"] = {"label": "The Schedule to the Act (penalties)",
                               "title": act["schedule"]["title"], "text": act["schedule"]["text"]}
    rules = json.load(open(rules_path))
    for number, rule in rules["rules"].items():
        law[f"R{number}"] = {"label": f"Rule {number} of the DPDP Rules", "title": rule["title"],
                             "text": rule["text"]}
    for name, schedule in rules["schedules"].items():
        law[f"SCH-{name.upper()}"] = {"label": f"{name} Schedule to the DPDP Rules",
                                      "title": f"{name} Schedule", "text": schedule["text"]}

    commencement = {}
    for key, numbers in rules["commencement"].items():
        in_force = key.replace("in_force_from_", "")
        for number in numbers:
            commencement[f"R{number}"] = in_force
    return law, commencement


def candidates(claim: dict, law: dict) -> list:
    """Cited provisions first, then the best keyword overlaps, so miscitations get caught."""
    chosen = [f"S{n}" for n in claim["cited_sections"] if f"S{n}" in law]
    chosen += [f"R{n}" for n in claim["cited_rules"] if f"R{n}" in law]
    words = {w for w in re.findall(r"[a-z]{4,}", claim["claim_text"].lower()) if w not in STOPWORDS}
    if words:
        scored = []
        for key, provision in law.items():
            if key in chosen:
                continue
            title = provision["title"].lower()
            body = provision["text"].lower()
            score = sum(3 for w in words if w in title) + sum(1 for w in words if w in body)
            scored.append((score, key))
        scored.sort(reverse=True)
        chosen += [key for score, key in scored[:CANDIDATES] if score > 0]
    seen = []
    for key in chosen:
        if key not in seen:
            seen.append(key)
    return seen[:MAX_PROVISIONS]


def normalise(text: str) -> str:
    text = re.sub(r"(\w) -(\w)", r"\1-\2", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def verify(claim: dict, law: dict, commencement: dict, index: str, usage: Usage, out) -> str:
    """One claim. Any failure is contained to this claim, never the whole run."""
    try:
        return _verify(claim, law, commencement, index, usage, out)
    except Exception as error:  # noqa: BLE001 — a bad row must not kill 15k others
        with write_lock:
            with open(OUT_FILE.replace(".jsonl", ".errors.jsonl"), "a") as log:
                log.write(json.dumps({"claim_id": claim["claim_id"], "error": repr(error)}) + "\n")
        return "ERROR"


def _verify(claim: dict, law: dict, commencement: dict, index: str, usage: Usage, out) -> str:
    supplied_keys = candidates(claim, law)
    supplied = "\n\n".join(
        f"=== [{key}] {law[key]['label']} — {law[key]['title']} ===\n{law[key]['text'][:PROVISION_CHARS]}"
        for key in supplied_keys) or "(no provision matched)"

    prompt = (
        f"CLAIM: {claim['claim_text']}\n"
        f"CLAIM TYPE (as extracted): {claim['claim_type']}\n"
        f"SECTIONS THE PAGE CITED: {claim['cited_sections'] or 'none'}\n"
        f"RULES THE PAGE CITED: {claim['cited_rules'] or 'none'}\n\n"
        f"--- INDEX OF ALL PROVISIONS ---\n{index}\n\n"
        f"--- FULL TEXT OF THE PROVISIONS MOST LIKELY TO GOVERN ---\n{supplied}"
    )
    result = ask_json(SYSTEM, prompt, usage, max_tokens=800)
    if not result:
        return "ERROR"
    return record(claim, result, supplied_keys, law, commencement, out)


def record(claim: dict, result: dict, supplied_keys: list, law: dict, commencement: dict, out) -> str:
    """Apply the code-level safeguards to one verdict and append it to the registry."""
    verdict = (result.get("verdict") or "NEEDS_REVIEW").upper()
    quote = (result.get("act_quote") or "")[:300]
    governing = [g.upper().replace(" ", "") for g in result.get("governing", []) if isinstance(g, str)]
    governing = [g for g in governing if g in law]

    # A VERIFIED_PRIMARY must quote the law it relied on. Otherwise it isn't verified.
    if verdict == "VERIFIED_PRIMARY":
        body = normalise(" ".join(law[k]["text"] for k in (governing or supplied_keys)))
        probe = normalise(quote)[:70]
        if len(probe) < 20 or probe not in body:
            verdict = "SUPPORTED_INTERPRETATION"

    in_force = {g: commencement[g] for g in governing if g in commencement}
    not_yet = sorted(g for g, when in in_force.items() if when > date.today().isoformat())

    row = dict(claim)
    row.update({
        "verification_status": verdict,
        "governing": governing,
        "governing_sections": [int(g[1:]) for g in governing if re.fullmatch(r"S\d+", g)],
        "governing_rules": [int(g[1:]) for g in governing if re.fullmatch(r"R\d+", g)],
        "governing_schedules": [g[4:].title() for g in governing if g.startswith("SCH-")],
        "act_quote": quote,
        "reasoning": (result.get("reasoning") or "")[:600],
        "confidence": round(float(result.get("confidence") or 0), 2),
        "rules_in_force_from": in_force,
        "rules_not_yet_in_force": not_yet,
        "provisions_supplied": supplied_keys,
        "miscited": bool(claim["cited_sections"] or claim["cited_rules"]) and verdict == "INCORRECT",
        "verified_against": VERIFIED_AGAINST,
        "verified_by": MODEL,
        # Publishable only as our own wording citing the Act/Rules — never the competitor's.
        "publication_allowed": verdict == "VERIFIED_PRIMARY" and claim["claim_type"] == "LEGAL",
    })
    with write_lock:
        out.write(json.dumps(row, ensure_ascii=False) + "\n")
        out.flush()
    return verdict


BATCH_SYSTEM = SYSTEM.replace(
    "You are given ONE claim taken from a commercial website",
    "You are given SEVERAL numbered claims taken from commercial websites; judge each one "
    "independently").replace(
    'Return JSON: {"verdict": str, "governing": [str], "act_quote": str, "reasoning": str,\n"confidence": float}',
    'Return JSON: {"results": [{"i": int, "verdict": str, "governing": [str], "act_quote": str, '
    '"reasoning": str, "confidence": float}]} with one entry per claim, using its number i.')
BATCH_SIZE = 6
BATCH_PROVISIONS = 7


def pack(claims: list, law: dict) -> list:
    """Group claims into batches whose combined provisions stay small, so each request sends
    the governing law once for several claims."""
    keyed = sorted(((tuple(sorted(candidates(c, law))), c) for c in claims), key=lambda kc: kc[0])
    batches, current, keys = [], [], set()
    for provision_keys, claim in keyed:
        union = keys | set(provision_keys)
        if current and (len(current) >= BATCH_SIZE or len(union) > BATCH_PROVISIONS):
            batches.append((current, sorted(keys)))
            current, union = [], set(provision_keys)
        current.append(claim)
        keys = union
    if current:
        batches.append((current, sorted(keys)))
    return batches


def verify_batch(batch: tuple, law: dict, commencement: dict, index: str, usage: Usage, out) -> list:
    claims, supplied_keys = batch
    try:
        supplied = "\n\n".join(
            f"=== [{key}] {law[key]['label']} — {law[key]['title']} ===\n{law[key]['text'][:PROVISION_CHARS]}"
            for key in supplied_keys) or "(no provision matched)"
        listing = "\n\n".join(
            f"CLAIM {i}: {c['claim_text']}\n  type: {c['claim_type']} · page cited sections: "
            f"{c['cited_sections'] or 'none'} · rules: {c['cited_rules'] or 'none'}"
            for i, c in enumerate(claims))
        prompt = (f"{listing}\n\n--- INDEX OF ALL PROVISIONS ---\n{index}\n\n"
                  f"--- FULL TEXT OF THE PROVISIONS MOST LIKELY TO GOVERN ---\n{supplied}")
        result = ask_json(BATCH_SYSTEM, prompt, usage, max_tokens=700 * len(claims), retries=10)
        if not result:
            return ["ERROR"] * len(claims)       # nothing recorded: the next run retries them
        by_index = {r.get("i"): r for r in result.get("results", []) if isinstance(r, dict)}
        return [record(c, by_index[i], supplied_keys, law, commencement, out) if i in by_index else "ERROR"
                for i, c in enumerate(claims)]
    except Exception as error:  # noqa: BLE001 — one bad batch must not stop the run
        with write_lock:
            with open(OUT_FILE.replace(".jsonl", ".errors.jsonl"), "a") as log:
                log.write(json.dumps({"claim_ids": [c["claim_id"] for c in claims],
                                      "error": repr(error)}) + "\n")
        return ["ERROR"] * len(claims)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--single", action="store_true", help="one claim per request (old mode)")
    args = parser.parse_args()

    law, commencement = load_law()
    index = "\n".join(f"{key}: {law[key]['title']}" for key in law)

    done = set()
    if os.path.exists(OUT_FILE):
        done = {json.loads(line)["claim_id"] for line in open(OUT_FILE)}

    seen, claims = set(), []
    for line in open(CLAIMS_FILE):
        claim = json.loads(line)
        if claim["claim_id"] in done or claim["claim_id"] in seen:
            continue
        seen.add(claim["claim_id"])
        claims.append(claim)
    if args.limit:
        claims = claims[: args.limit]
    print(f"{len(claims)} claims to verify ({len(done)} already done) · {len(law)} provisions · "
          f"model {MODEL}", flush=True)

    usage, tally = Usage(), Counter()
    with open(OUT_FILE, "a") as out:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            if args.single:
                results = pool.map(lambda c: [verify(c, law, commencement, index, usage, out)], claims)
            else:
                batches = pack(claims, law)
                print(f"  packed into {len(batches)} requests", flush=True)
                results = pool.map(lambda b: verify_batch(b, law, commencement, index, usage, out), batches)
            done_count = 0
            for verdicts in results:
                for verdict in verdicts:
                    tally[verdict] += 1
                done_count += len(verdicts)
                if done_count // 500 != (done_count - len(verdicts)) // 500:
                    print(f"  {done_count}/{len(claims)} · ${usage.cost_usd:.2f}", flush=True)

    print(f"\n{usage}")
    for verdict, count in tally.most_common():
        print(f"{count:>6}  {verdict}")


if __name__ == "__main__":
    main()
