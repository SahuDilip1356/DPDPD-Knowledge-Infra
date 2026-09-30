"""
Comprehensive Eval Runner — AI Evals & Reliability Playbook

Features:
1. Multi-run spread evaluation (Phase 1): Runs each case N times (default: 3x) to measure stability.
2. Free, deterministic scorers first (Phase 3): sufficient_match, citation_recall, no_fabrication.
3. Trajectory evaluation (Phase 5): Verifies path against expected tool sequence.
4. LLM-as-a-judge (Phase 6): Optional structured rubric evaluation.
5. Error analysis & clustering (Phase 7): Clusters failures and generates FAILURE_CATALOG.md.
6. Persistent reports: Outputs structured JSON report to evals/reports/.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# Evaluate the backend that is deployed (deployments/dpdpa-backend), not the
# older copy under the repository root's src/, which has drifted from it.
# `src.*` must resolve to the canonical tree, so it goes first on sys.path;
# the repository root follows so `evals.*` still imports.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "deployments", "dpdpa-backend")
for path in (PROJECT_ROOT, BACKEND_ROOT):
    if path in sys.path:
        sys.path.remove(path)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, BACKEND_ROOT)

from src.reasoning.reasoning_engine import GroundedReasoningEngine
from src.reasoning.model_client import ModelClient, MockModelClient
from evals.scorers import evaluate_case
from evals.error_analysis import ErrorAnalyzer
from evals.judge import RubricJudge

REPORTS_DIR = os.path.join(PROJECT_ROOT, "evals", "reports")
DATASET_PATH = os.path.join(PROJECT_ROOT, "evals", "dataset.jsonl")

def load_dataset(dataset_path: str = DATASET_PATH) -> List[Dict[str, Any]]:
    cases = []
    with open(dataset_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


from src.storage.db_client import DatabaseClient
from src.tests.test_reasoning_pipeline import make_ko

def build_eval_db_client():
    db = DatabaseClient("sqlite:///:memory:")
    db.supabase = None

    ko_act = make_ko(
        urn="urn:ki:in:dpdp:act:dpdpa-2023",
        title="Digital Personal Data Protection Act 2023",
        entities=["Act", "Penalty", "Penalties", "Consent", "Notice", "Children", "Child", "DPO", "Grievance", "Duties", "Cross-Border", "Transfer", "Legitimate", "Erasure", "Board", "DPBI"],
        summary="Digital Personal Data Protection Act 2023. Section 33 & Schedule prescribe penalties up to 250 crore for breach safeguards failure, and 200 crore for failure to notify Board, and 10,000 for frivolous grievance. Section 5 covers consent notice. Section 7 covers legitimate uses. Section 8 covers erasure. Section 9 restricts child data tracking. Section 10 mandates DPO for SDF. Section 13 covers grievance redressal. Section 15 covers duties. Section 16 governs cross-border transfers.",
        confidence=1.0,
        evidence=[{
            "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023",
            "citation_text": "Digital Personal Data Protection Act 2023 statutory core provisions.",
            "coordinates": {"page": 1, "section": "Section 33", "hash": "da8cf9105432a9e8751db432ef5012a4b8cd9a77efca1357db5c6c99ef412e87"}
        }],
        business_impact={
            "impact_summary": "Statutory compliance obligations across enterprises in India.",
            "action_required": "Implement reasonable security safeguards and consent management mechanisms."
        }
    )
    db.publish_ko(ko_act)
    return db


def run_eval_suite(
    dataset_path: str = DATASET_PATH,
    runs_per_case: int = 3,
    offline: bool = False,
    limit: Optional[int] = None,
    use_judge: bool = False
) -> Dict[str, Any]:
    """
    Executes evaluation across all cases in the dataset with multi-run spread measurement.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    cases = load_dataset(dataset_path)
    if limit:
        cases = cases[:limit]

    db_client = build_eval_db_client()

    # Initialize reasoning engine
    if offline:
        os.environ["OFFLINE_MODE"] = "1"
        client = MockModelClient()
        engine = GroundedReasoningEngine(db_client=db_client, model_client=client)
    else:
        client = ModelClient()
        if not client.gemini_key and not client.openai_key:
            print("[EvalRunner] No API keys found in environment. Switching to offline mock runner.")
            os.environ["OFFLINE_MODE"] = "1"
            client = MockModelClient()
        engine = GroundedReasoningEngine(db_client=db_client, model_client=client)

    # Initialize judge if requested
    judge = RubricJudge(model_client=client) if use_judge else None

    # Track results
    case_summaries = []
    all_individual_runs = []
    latencies = []

    print(f"\n=======================================================")
    print(f" AI Evals & Reliability Suite — Running {len(cases)} Cases ({runs_per_case}x each)")
    print(f" Mode: {'OFFLINE (MOCK)' if isinstance(client, MockModelClient) else 'LIVE (MODEL)'}")
    print(f"=======================================================\n")

    for case in cases:
        case_id = case.get("id")
        query = case.get("input")
        category = case.get("category", "General")
        severity = case.get("severity", 3)
        
        run_results_for_case = []
        
        for run_idx in range(runs_per_case):
            t0 = time.perf_counter()
            response = engine.query(query)
            t1 = time.perf_counter()
            duration_ms = round((t1 - t0) * 1000, 2)
            latencies.append(duration_ms)

            eval_res = evaluate_case(case, response)
            eval_res["duration_ms"] = duration_ms
            eval_res["run_index"] = run_idx + 1

            if judge:
                judge_score = judge.grade(query, response.get("answer", ""))
                eval_res["judge"] = judge_score

            run_results_for_case.append(eval_res)
            all_individual_runs.append(eval_res)

        passes = sum(1 for r in run_results_for_case if r["passed"])
        
        # Stability classification (Phase 1 Spread):
        if passes == runs_per_case:
            stability = "STABLE_PASS"
            badge = "✅"
        elif passes == 0:
            stability = "CONSISTENT_FAIL"
            badge = "❌"
        else:
            stability = "VARIANCE_DETECTED"
            badge = "⚠️"

        case_summaries.append({
            "case_id": case_id,
            "category": category,
            "severity": severity,
            "input": query,
            "passes": passes,
            "total_runs": runs_per_case,
            "stability": stability,
            "sample_scores": run_results_for_case[0]["scores"]
        })

        print(f"{badge} [{case_id}] {stability:18} ({passes}/{runs_per_case}) | Sev {severity} | {category:20} | {query[:45]}...")

    # Aggregate metric scores
    total_evals = len(all_individual_runs)
    metric_passes = {
        "sufficient_match": sum(1 for r in all_individual_runs if r["scores"]["sufficient_match"]),
        "citation_recall": sum(1 for r in all_individual_runs if r["scores"]["citation_recall"]),
        "no_fabrication": sum(1 for r in all_individual_runs if r["scores"]["no_fabrication"]),
        "trajectory_match": sum(1 for r in all_individual_runs if r["scores"]["trajectory_match"])
    }

    mean_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
    sorted_lat = sorted(latencies)
    p95_latency = sorted_lat[int(len(sorted_lat) * 0.95)] if sorted_lat else 0.0

    # Phase 7: Error Analysis & Clustering
    analysis = ErrorAnalyzer.analyze_failures(all_individual_runs)
    ErrorAnalyzer.generate_catalog_markdown(analysis)

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_cases": len(cases),
        "runs_per_case": runs_per_case,
        "total_runs": total_evals,
        "total_passed": sum(1 for r in all_individual_runs if r["passed"]),
        "pass_rate_pct": round((sum(1 for r in all_individual_runs if r["passed"]) / total_evals) * 100, 1) if total_evals else 0.0,
        "metrics": {
            k: {
                "passed": v,
                "total": total_evals,
                "pct": round((v / total_evals) * 100, 1)
            }
            for k, v in metric_passes.items()
        },
        "latency": {
            "mean_ms": mean_latency,
            "p95_ms": p95_latency
        },
        "error_clusters": analysis["clusters"],
        "cases": case_summaries
    }

    # Save report
    report_filename = f"eval_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    report_filepath = os.path.join(REPORTS_DIR, report_filename)
    with open(report_filepath, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary table
    print(f"\n=======================================================")
    print(f" EVALUATION SUMMARY REPORT")
    print(f"=======================================================")
    print(f" Total Executed Runs: {total_evals}")
    print(f" Overall Pass Rate:   {report['pass_rate_pct']}%")
    print(f" Latency:             Mean: {mean_latency}ms | P95: {p95_latency}ms")
    print(f"-------------------------------------------------------")
    print(f" Scorer Breakdown (Free/Deterministic):")
    for k, v in report["metrics"].items():
        print(f"   - {k:18}: {v['passed']:2}/{v['total']:2} ({v['pct']}%)")
    print(f"-------------------------------------------------------")
    print(f" Failure Clusters Identified: {analysis['cluster_count']}")
    for c in analysis["clusters"]:
        print(f"   - {c['name']:25}: {c['count']} failures")
    print(f"-------------------------------------------------------")
    print(f" Report saved: {report_filepath}")
    print(f" Failure catalog updated: evals/FAILURE_CATALOG.md\n")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AI Evals & Reliability Suite")
    parser.add_argument("--dataset", type=str, default=DATASET_PATH, help="Path to dataset.jsonl")
    parser.add_argument("--runs", type=int, default=3, help="Number of runs per case (spread measurement)")
    parser.add_argument("--offline", action="store_true", help="Run with deterministic offline mock client")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of test cases")
    parser.add_argument("--judge", action="store_true", help="Include LLM-as-a-judge rubric evaluation")
    args = parser.parse_args()

    run_eval_suite(
        dataset_path=args.dataset,
        runs_per_case=args.runs,
        offline=args.offline,
        limit=args.limit,
        use_judge=args.judge
    )
