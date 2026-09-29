"""
Real-corpus eval: the deployed GroundedReasoningEngine over the verified corpus.

The corpus is the verified law (deployments/dpdpa-wiki/src/data/law/provisions.json, one
knowledge object per provision, built the way build_knowledge_objects.py builds them) plus
the 511 verified answer objects (evals/corpus/answer_kos.jsonl.gz). It is loaded into an
in-memory SQLite DatabaseClient; nothing is written to Supabase or Pinecone.

Offline (the default) runs retrieval and the engine with MockModelClient: no network, no
cost, deterministic. It measures retrieval and the pipeline, not the model; the mock cites
the first object retrieved. --live calls the configured model and prints the cost.

Scores, per case (see evals/scorers.py):
  cited_subset_retrieved   every cited object was retrieved for this query      (must be 100%)
  no_nonexistent_provision no cited or named provision outside the 75 that exist (must be 100%)
  provision_recall         share of the answer object's verified provisions cited
  refusal_correct          answers the supported cases, refuses the withheld ones

Each answer case holds out its own answer object by default (--no-holdout keeps it), so the
engine has to reach the law or other answers rather than return the pre-written answer.
"""

import contextlib
import gzip
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import update

from src.reasoning.model_client import MockModelClient, ModelClient
from src.reasoning.reasoning_engine import GroundedReasoningEngine
from src.storage.db_client import DatabaseClient
from src.storage.models import KnowledgeObject

from evals.scorers import (
    nonexistent_provisions,
    score_cited_subset_retrieved,
    score_provision_recall,
    score_refusal,
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GOLDEN_PATH = os.path.join(PROJECT_ROOT, "evals", "golden_corpus.jsonl")
ANSWERS_PATH = os.path.join(PROJECT_ROOT, "evals", "corpus", "answer_kos.jsonl.gz")
BASELINE_PATH = os.path.join(PROJECT_ROOT, "evals", "baselines", "real_corpus_offline.json")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "evals", "reports")
PROVISIONS_PATH = os.path.join(
    PROJECT_ROOT, "deployments", "dpdpa-wiki", "src", "data", "law", "provisions.json"
)

ACT_DOC = "urn:ki:in:dpdp:act:dpdpa-2023"
RULES_DOC = "urn:ki:in:dpdp:rule:dpdp-rules-2025"
ACT_SOURCE = "urn:ki:in:dpdp:source:gazette-dpdpa-2023"
RULES_SOURCE = "urn:ki:in:dpdp:source:gazette-gsr-846e-2025"

# USD per million tokens, list prices when this was written. Override with
# --price-in / --price-out when the provider or the price differs.
PRICES = {
    "gemini-2.5-flash": (0.30, 2.50),
    "gpt-4o-mini": (0.15, 0.60),
    "openai/gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "openai/gpt-4o": (2.50, 10.00),
}
EMBED_PRICES = {"text-embedding-3-small": 0.02, "openai/text-embedding-3-small": 0.02}
UNKNOWN_PRICE = (5.00, 15.00)  # deliberately high, so an unknown model trips the budget early
MAX_OUTPUT_TOKENS = 2048       # the engine's own cap; used to bound a call before it is made
CHARS_PER_TOKEN = 4


# ---------------------------------------------------------------- corpus

def law_objects() -> List[Dict[str, Any]]:
    """One verbatim knowledge object per provision, as build_knowledge_objects.primary_row."""
    with open(PROVISIONS_PATH) as f:
        provisions = json.load(f)["provisions"]
    rows = []
    for p in provisions:
        label, text = p["label"], p["text"]
        act = p["kind"] in ("section", "act-schedule")
        title = ("The Schedule — Penalties (DPDPA 2023)" if label == "ACT-SCHEDULE" else
                 f"Section {label[1:]} — {p['title']}" if act else
                 f"{p['title']} — DPDP Rules 2025" if label.startswith("SCH") else
                 f"Rule {label[1:]} — {p['title']} (DPDP Rules 2025)")
        coordinates = ({"section": "The Schedule (penalties)"} if label == "ACT-SCHEDULE" else
                       {"section": f"Section {label[1:]}"} if act else
                       {"section": f"{label[4:].title()} Schedule"} if label.startswith("SCH") else
                       {"section": f"Rule {label[1:]}"})
        rows.append({
            "urn": p["urn"], "version": 1, "type": "Act" if act else "Rule",
            "title": title,
            "summary": text[:1500] + (" …" if len(text) > 1500 else ""),
            "date": "2023-08-11" if act else (p.get("in_force_from") or "2025-11-13"),
            "confidence_score": 1.0,
            "source_credibility": "primary",
            "interpretation_stance": "verbatim",
            "body": {"full_text": text, "provision": label, "entities": []},
            "business_impact": {},
            "evidence": [{
                "id": f"ev-{label.lower()}-1",
                "source_urn": ACT_SOURCE if act else RULES_SOURCE,
                "coordinates": coordinates,
                "citation_text": text[:300],
            }],
            "linked_objects": [ACT_DOC if act else RULES_DOC],
            "entities": [],
            "relations": [],
        })
    return rows


def answer_objects() -> List[Dict[str, Any]]:
    with gzip.open(ANSWERS_PATH, "rt", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    for row in rows:
        row["date"] = row["legal_time_start"]
        row["relations"] = []  # graph edges are not used by retrieval; skip the edge table
    return rows


class Corpus:
    """The verified corpus in an in-memory DatabaseClient, with a label index per object."""

    def __init__(self):
        # Never mirror to Supabase: without these DatabaseClient does not create a client.
        for key in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY"):
            os.environ.pop(key, None)
        self.db = DatabaseClient("sqlite:///:memory:")
        self.db.supabase = None

        law, answers = law_objects(), answer_objects()
        self.valid_labels = {row["body"]["provision"] for row in law}
        self.labels = {row["urn"]: {row["body"]["provision"]} for row in law}
        self.labels.update({row["urn"]: set(row["body"]["cited"]) for row in answers})
        loaded_at = datetime(2026, 1, 1)
        for row in law + answers:
            self.db.publish_ko(row, system_time=loaded_at)
        self.size = {"law": len(law), "answers": len(answers)}

    def cited_labels(self, urns: List[str]) -> set:
        return set().union(*(self.labels.get(urn, set()) for urn in urns)) if urns else set()

    @contextlib.contextmanager
    def withheld(self, urns: List[str]):
        """Hide objects from retrieval for one case by closing them in system time."""
        if not urns:
            yield
            return
        closed_at = datetime(2026, 1, 2)
        session = self.db.Session()
        try:
            session.execute(update(KnowledgeObject)
                            .where(KnowledgeObject.urn.in_(urns),
                                   KnowledgeObject.system_time_end == None)  # noqa: E711
                            .values(system_time_end=closed_at))
            session.commit()
            yield
        finally:
            session.execute(update(KnowledgeObject)
                            .where(KnowledgeObject.urn.in_(urns),
                                   KnowledgeObject.system_time_end == closed_at)
                            .values(system_time_end=None))
            session.commit()
            session.close()


class RecordingEngine(GroundedReasoningEngine):
    """The deployed engine, unchanged, remembering what it retrieved and how."""

    def _query_pinecone_vectors(self, query: str) -> List[str]:
        urns = super()._query_pinecone_vectors(query)
        self.last_path = "pinecone" if urns else "keyword"
        return urns

    def retrieve_context(self, query: str) -> List[Dict]:
        self.last_path = "keyword"
        self.last_retrieved = super().retrieve_context(query)
        return self.last_retrieved


# ---------------------------------------------------------------- cost

class BudgetExceeded(RuntimeError):
    pass


def model_name(client: ModelClient) -> str:
    if client.gpt_oss_enabled:
        return f"gpt-oss:{client.gpt_oss_model}"
    if client.gemini_key:
        return "gemini-2.5-flash"
    return client.oai_chat_model or "unknown"


def embed_model_name(client: ModelClient) -> str:
    return "text-embedding-004" if client.gemini_key else (client.oai_embed_model or "unknown")


class MeteredModelClient:
    """Wraps the live client: estimates the cost of every call and refuses one that would
    take the run over budget. Tokens are estimated as characters / 4 (the client does not
    return usage); a malformed-JSON retry inside generate_json is not counted."""

    def __init__(self, client: ModelClient, budget_usd: float,
                 price_in: Optional[float] = None, price_out: Optional[float] = None):
        self.client = client
        self.budget = budget_usd
        self.model = model_name(client)
        local = client.gpt_oss_enabled
        known = PRICES.get(self.model, (0.0, 0.0) if local else UNKNOWN_PRICE)
        self.price_in = known[0] if price_in is None else price_in
        self.price_out = known[1] if price_out is None else price_out
        self.price_known = local or self.model in PRICES or None not in (price_in, price_out)
        self.embed_model = embed_model_name(client)
        self.price_embed = EMBED_PRICES.get(self.embed_model, 0.0)
        self.spent = 0.0
        self.tokens_in = self.tokens_out = self.tokens_embed = 0
        self.calls = 0

    def _charge(self, usd: float, what: str) -> None:
        if self.spent + usd > self.budget:
            raise BudgetExceeded(
                f"{what} would cost up to ${usd:.4f}; ${self.spent:.4f} of the "
                f"${self.budget:.2f} budget is spent. Raise --max-cost-usd to continue.")

    def generate_json(self, prompt: str) -> Dict:
        tokens_in = len(prompt) // CHARS_PER_TOKEN
        worst = (tokens_in * self.price_in + MAX_OUTPUT_TOKENS * self.price_out) / 1e6
        self._charge(worst, f"A {tokens_in:,}-token prompt")
        response = self.client.generate_json(prompt)
        tokens_out = len(json.dumps(response)) // CHARS_PER_TOKEN
        self.tokens_in += tokens_in
        self.tokens_out += tokens_out
        self.calls += 1
        self.spent += (tokens_in * self.price_in + tokens_out * self.price_out) / 1e6
        return response

    def embed(self, text: str) -> list:
        tokens = len(text) // CHARS_PER_TOKEN
        self._charge(tokens * self.price_embed / 1e6, "An embedding")
        self.tokens_embed += tokens
        self.spent += tokens * self.price_embed / 1e6
        return self.client.embed(text)

    def summary(self) -> Dict[str, Any]:
        return {
            "model": self.model, "embed_model": self.embed_model,
            "price_per_mtok": {"in": self.price_in, "out": self.price_out, "embed": self.price_embed},
            "price_known": self.price_known,
            "calls": self.calls, "tokens_in": self.tokens_in, "tokens_out": self.tokens_out,
            "tokens_embed": self.tokens_embed, "usd": round(self.spent, 6),
            "basis": "estimated: characters / 4, list prices",
        }


# ---------------------------------------------------------------- run

def load_golden(path: str) -> List[Dict[str, Any]]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def score_case(case: Dict, response: Dict, retrieved: List[str], corpus: Corpus) -> Dict:
    cited = response.get("cited_urns", [])
    cited_labels = corpus.cited_labels(cited)
    grounded = bool(response.get("grounded"))
    expect_sufficient = bool(case["expect_sufficient"])
    missing_law = nonexistent_provisions(cited_labels, response.get("answer", ""), corpus.valid_labels)
    recall = score_provision_recall(cited_labels, case.get("expect_provisions", []))
    scores = {
        "cited_subset_retrieved": score_cited_subset_retrieved(cited, retrieved),
        "no_nonexistent_provision": not missing_law,
        "refusal_correct": score_refusal(grounded, expect_sufficient),
        "provision_recall": recall,
    }
    passed = (scores["cited_subset_retrieved"] and scores["no_nonexistent_provision"]
              and scores["refusal_correct"] and (recall is None or recall == 1.0))
    retrieved_labels = corpus.cited_labels(retrieved)
    expected = set(case.get("expect_provisions", []))
    return {
        "case_id": case["id"], "kind": case["kind"], "passed": passed, "scores": scores,
        "details": {
            "grounded": grounded,
            "expect_sufficient": expect_sufficient,
            "cited_urns": cited,
            "cited_labels": sorted(cited_labels),
            "expect_provisions": sorted(expected),
            "nonexistent_provisions": missing_law,
            "retrieved_count": len(retrieved),
            "expected_in_retrieved": sorted(expected & retrieved_labels),
        },
    }


def summarise(results: List[Dict]) -> Dict[str, Any]:
    def share(values):
        values = list(values)
        return round(sum(values) / len(values), 4) if values else None

    answers = [r for r in results if r["kind"] == "answer"]
    refusals = [r for r in results if r["kind"] != "answer"]
    return {
        "runs": len(results),
        "passed": sum(r["passed"] for r in results),
        "cited_subset_retrieved": share(r["scores"]["cited_subset_retrieved"] for r in results),
        "no_nonexistent_provision": share(r["scores"]["no_nonexistent_provision"] for r in results),
        "provision_recall_mean": share(r["scores"]["provision_recall"] for r in answers),
        "provision_recall_full": share(r["scores"]["provision_recall"] == 1.0 for r in answers),
        "answered_when_supported": share(r["details"]["grounded"] for r in answers),
        "refused_when_unsupported": share(not r["details"]["grounded"] for r in refusals),
        "retrieved_count_mean": share(r["details"]["retrieved_count"] for r in results),
        "expected_in_retrieved": share(
            len(r["details"]["expected_in_retrieved"]) / len(r["details"]["expect_provisions"])
            for r in answers),
    }


# Hard invariants: any shortfall fails the run. The rest are quality numbers, held to
# the committed baseline so they can only go up.
INVARIANTS = ("cited_subset_retrieved", "no_nonexistent_provision")
RATCHETED = ("provision_recall_mean", "provision_recall_full",
             "answered_when_supported", "refused_when_unsupported")


def check_gates(summary: Dict, baseline: Optional[Dict]) -> List[str]:
    failures = [f"{k} is {summary[k]:.1%}, must be 100%" for k in INVARIANTS if summary[k] != 1.0]
    for k in RATCHETED if baseline else ():
        if summary[k] is not None and baseline.get(k) is not None and summary[k] < baseline[k]:
            failures.append(f"{k} fell to {summary[k]:.1%} from the baseline {baseline[k]:.1%}")
    return failures


def run_real_corpus_suite(
    golden_path: str = GOLDEN_PATH,
    runs_per_case: int = 1,
    live: bool = False,
    holdout: bool = True,
    limit: Optional[int] = None,
    max_cost_usd: float = 1.0,
    price_in: Optional[float] = None,
    price_out: Optional[float] = None,
    baseline_path: Optional[str] = None,
    write_baseline: bool = False,
) -> int:
    """Run the golden set over the real corpus. Returns the process exit code."""
    cases = load_golden(golden_path)[:limit] if limit else load_golden(golden_path)

    if live:
        client = ModelClient()
        if not client.is_configured:
            print("[real-corpus] --live needs GPT_OSS_*, GEMINI_API_KEY, OPENAI_API_KEY or "
                  "OPENROUTER_API_KEY. Nothing was run.")
            return 2
        meter = MeteredModelClient(client, max_cost_usd, price_in, price_out)
        model_client = meter
    else:
        os.environ["OFFLINE_MODE"] = "1"  # the engine then never calls Pinecone
        meter, model_client = None, MockModelClient()

    t0 = time.perf_counter()
    corpus = Corpus()
    engine = RecordingEngine(db_client=corpus.db, model_client=model_client)
    load_s = time.perf_counter() - t0

    mode = f"LIVE ({meter.model})" if live else "OFFLINE (mock model, no network)"
    print("\n=======================================================")
    print(f" Real-corpus eval — {len(cases)} cases × {runs_per_case}")
    print(f" Corpus: {corpus.size['law']} provisions + {corpus.size['answers']} answer objects "
          f"(in-memory SQLite, loaded in {load_s:.1f}s)")
    print(f" Mode:   {mode} · own answer {'held out' if holdout else 'kept in corpus'}")
    if meter:
        known = "" if meter.price_known else "  (model not in the price table: using a high default)"
        print(f" Price:  ${meter.price_in}/M in, ${meter.price_out}/M out{known}")
        print(f" Budget: ${max_cost_usd:.2f} (--max-cost-usd)")
    print("=======================================================\n")

    results, stopped = [], None
    for case in cases:
        hidden = list(case.get("withheld_urns", []))
        if holdout and case.get("answer_urn"):
            hidden.append(case["answer_urn"])
        for run in range(runs_per_case):
            with corpus.withheld(hidden):
                started = time.perf_counter()
                engine.last_retrieved, engine.last_path = [], "none"  # a guardrail refusal retrieves nothing
                try:
                    response = engine.query(case["input"])
                except BudgetExceeded as exc:
                    stopped = str(exc)
                    break
                retrieved = [ko["urn"] for ko in engine.last_retrieved]
                # What a live call would send, so an offline run still shows the bill.
                prompt_chars = len(engine.construct_grounded_prompt(
                    case["input"], engine.last_retrieved)) if retrieved else 0
            result = score_case(case, response, retrieved, corpus)
            result["run_index"] = run + 1
            result["duration_ms"] = round((time.perf_counter() - started) * 1000, 1)
            result["details"]["retrieval_path"] = engine.last_path
            result["details"]["prompt_tokens_est"] = prompt_chars // CHARS_PER_TOKEN
            results.append(result)
        if stopped:
            break
        last = results[-1]
        recall = last["scores"]["provision_recall"]
        cost = f" · ${meter.spent:.4f}" if meter else ""
        print(f"{'✅' if last['passed'] else '❌'} {case['id']:20} {case['kind']:16} "
              f"{'answered' if last['details']['grounded'] else 'refused':8} "
              f"recall {'—' if recall is None else f'{recall:.2f}'} "
              f"· retrieved {last['details']['retrieved_count']:3}{cost} | {case['input'][:50]}")

    if not results:
        print(f"\n[real-corpus] Stopped before the first case: {stopped}")
        return 3

    summary = summarise(results)
    prompt_tokens = [r["details"]["prompt_tokens_est"] for r in results]
    summary["prompt_tokens_est_mean"] = round(sum(prompt_tokens) / len(prompt_tokens))
    baseline = None
    if baseline_path and os.path.exists(baseline_path):
        with open(baseline_path) as f:
            stored = json.load(f)
        if stored.get("holdout") == holdout and not limit:
            baseline = stored["summary"]
    failures = check_gates(summary, baseline)
    if stopped:
        failures.append(f"stopped by the cost guard: {stopped}")

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "live" if live else "offline",
        "holdout": holdout,
        "golden": os.path.relpath(golden_path, PROJECT_ROOT),
        "corpus": corpus.size,
        "runs_per_case": runs_per_case,
        "summary": summary,
        "cost": meter.summary() if meter else {"usd": 0.0, "basis": "mock model, no network"},
        "gate_failures": failures,
        "results": results,
    }
    os.makedirs(REPORTS_DIR, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"real_corpus_{report['mode']}_{stamp}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    pct = lambda v: "—" if v is None else f"{v:.1%}"  # noqa: E731
    print("\n=======================================================")
    print(" REAL-CORPUS SUMMARY")
    print("=======================================================")
    print(f" Cases passed (all checks, full recall): {summary['passed']}/{summary['runs']}")
    print(f" cited ⊆ retrieved:            {pct(summary['cited_subset_retrieved'])}")
    print(f" no nonexistent provision:     {pct(summary['no_nonexistent_provision'])}")
    print(f" provision recall (mean):      {pct(summary['provision_recall_mean'])}")
    print(f" provision recall (full):      {pct(summary['provision_recall_full'])}")
    print(f" answered when supported:      {pct(summary['answered_when_supported'])}")
    print(f" refused when unsupported:     {pct(summary['refused_when_unsupported'])}")
    print(f" expected law in retrieval:    {pct(summary['expected_in_retrieved'])}")
    print(f" objects retrieved (mean):     {summary['retrieved_count_mean']:.0f}")
    print(f" prompt size (mean, est.):     {summary['prompt_tokens_est_mean']:,} tokens")
    if meter:
        c = meter.summary()
        print(f" Cost: ${c['usd']:.4f} — {c['calls']} model calls, {c['tokens_in']:,} in / "
              f"{c['tokens_out']:,} out tokens, {c['tokens_embed']:,} embedding tokens "
              f"({c['basis']})")
    else:
        print(" Cost: $0.00 (mock model, no network)")
    print("-------------------------------------------------------")
    for failure in failures:
        print(f" GATE FAILED: {failure}")
    if not failures:
        print(" Gates: invariants hold" + (", no metric below baseline" if baseline else ""))
    print(f" Report: {os.path.relpath(report_path, PROJECT_ROOT)}\n")

    if write_baseline:
        if live:
            print("[real-corpus] Not writing a baseline from a live run: the gate is offline.")
        elif failures and any(k in f for f in failures for k in INVARIANTS):
            print("[real-corpus] Not writing a baseline while an invariant fails.")
        else:
            os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
            with open(BASELINE_PATH, "w") as f:
                json.dump({"golden": report["golden"], "holdout": holdout,
                           "summary": summary}, f, indent=2)
                f.write("\n")
            print(f"[real-corpus] Baseline written: {os.path.relpath(BASELINE_PATH, PROJECT_ROOT)}")
            return 0

    return 1 if failures else 0
