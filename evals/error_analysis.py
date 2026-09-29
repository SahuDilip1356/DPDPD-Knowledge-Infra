"""
Error Analysis & Failure Catalog Generator — Phase 7 of AI Evals & Reliability Playbook

"Nobody ever improved a system by staring at an average number.
The useful question is not why isn't it 100 — it is where does the missing percent live."

The Loop:
1. Run eval
2. Read every individual failure
3. Cluster by shared root cause
4. Name and Count clusters
5. Generate actionable Failure Catalog
6. Turn every fixed bug into a permanent test row in dataset.jsonl
"""

import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Any

FAILURE_CATALOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "FAILURE_CATALOG.md")
)
DATASET_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "dataset.jsonl")
)

class ErrorAnalyzer:
    """
    Analyzes failed test rows and clusters them by specific, actionable root causes.
    """

    @staticmethod
    def diagnose_failure(eval_record: Dict[str, Any]) -> str:
        """Determines the specific failure cluster for a case."""
        scores = eval_record.get("scores", {})
        details = eval_record.get("details", {})
        
        actual_suff = details.get("actual_sufficient", False)
        expect_suff = details.get("expect_sufficient", True)

        if not expect_suff and actual_suff:
            return "out_of_scope_leakage"
        elif expect_suff and not actual_suff:
            return "false_negative_refusal"
        elif not scores.get("citation_recall", True):
            return "missing_statutory_citation"
        elif not scores.get("no_fabrication", True):
            return "fabricated_citation"
        elif not scores.get("trajectory_match", True):
            return "trajectory_violation"
        else:
            return "unclassified_failure"

    @classmethod
    def analyze_failures(cls, eval_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Clusters all failed runs, counts frequencies, and lists member cases.
        """
        clusters = defaultdict(list)
        total_runs = len(eval_results)
        failed_runs = [r for r in eval_results if not r.get("passed", False)]

        for failure in failed_runs:
            cluster_name = cls.diagnose_failure(failure)
            clusters[cluster_name].append(failure)

        # Sort clusters by failure count descending
        sorted_clusters = sorted(
            [{"name": k, "count": len(v), "cases": v} for k, v in clusters.items()],
            key=lambda x: x["count"],
            reverse=True
        )

        return {
            "total_evaluated": total_runs,
            "total_failed": len(failed_runs),
            "pass_rate": round(((total_runs - len(failed_runs)) / total_runs) * 100, 1) if total_runs else 0.0,
            "cluster_count": len(sorted_clusters),
            "clusters": sorted_clusters
        }

    @classmethod
    def generate_catalog_markdown(
        cls,
        analysis: Dict[str, Any],
        output_path: str = FAILURE_CATALOG_PATH
    ) -> str:
        """
        Renders a persistent Markdown Failure Catalog.
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
        lines = [
            "# Failure Mode Catalog — AI Evals & Reliability",
            "",
            f"> **Last Generated:** `{timestamp}`  ",
            f"> **Total Evaluated:** {analysis['total_evaluated']} | **Failed:** {analysis['total_failed']} | **Pass Rate:** {analysis['pass_rate']}%  ",
            f"> **Identified Failure Clusters:** {analysis['cluster_count']}",
            "",
            "## Summary of Failure Clusters",
            "",
            "| Cluster Name | Failures | Severity Impact | Primary Cause | Action Item |",
            "|---|---|---|---|---|"
        ]

        CLUSTER_DESCRIPTIONS = {
            "out_of_scope_leakage": (
                "High (Sev 4-5)",
                "System attempted to answer out-of-corpus / negative query instead of refusing.",
                "Tighten InputGuardrail regex and prompt refusal triggers."
            ),
            "false_negative_refusal": (
                "Medium (Sev 3)",
                "System declared insufficient evidence despite valid statutory context present.",
                "Expand retrieval keyword coverage or relax semantic distance threshold."
            ),
            "missing_statutory_citation": (
                "Medium (Sev 3-4)",
                "Answer was produced without citing all expected statutory URN coordinates.",
                "Enforce inline URN coordinates formatting in system prompt instructions."
            ),
            "fabricated_citation": (
                "Critical (Sev 5)",
                "Model attempted to cite URNs never provided in retrieved context.",
                "OutputGuardrail intersection `retrieved ∩ claimed` successfully caught and stripped."
            ),
            "trajectory_violation": (
                "Low-Medium (Sev 2-3)",
                "Execution path deviated from expected tool/retrieval sequence.",
                "Check routing logic or update acceptable substitutes list."
            ),
            "unclassified_failure": (
                "Investigate",
                "Unusual or multi-factor failure mode.",
                "Perform manual inspection of raw output."
            )
        }

        for c in analysis["clusters"]:
            c_name = c["name"]
            sev, cause, action = CLUSTER_DESCRIPTIONS.get(
                c_name, ("Medium", "General mismatch", "Review failure details")
            )
            lines.append(f"| `{c_name}` | {c['count']} | {sev} | {cause} | {action} |")

        lines.extend([
            "",
            "## Detailed Case Breakdown",
            ""
        ])

        if not analysis["clusters"]:
            lines.append("_No failures recorded in the latest run. System cleared 100% of cases._")
        else:
            for c in analysis["clusters"]:
                lines.append(f"### Cluster: `{c['name']}` ({c['count']} cases)")
                lines.append("")
                for item in c["cases"]:
                    case_id = item.get("case_id")
                    details = item.get("details", {})
                    lines.append(f"- **Case `{case_id}`** (Severity {details.get('severity', 'unknown')}):")
                    lines.append(f"  - Actual Sufficient: `{details.get('actual_sufficient')}` (Expected: `{details.get('expect_sufficient')}`)")
                    lines.append(f"  - Cited URNs: `{details.get('cited_urns')}`")
                    lines.append(f"  - Expected URNs: `{details.get('expect_urns')}`")
                lines.append("")

        lines.extend([
            "---",
            "## Team Handover Policy",
            "",
            "Every fixed failure mode must be added as a permanent row to `evals/dataset.jsonl`.",
            "Never close an issue until the regression case is written and verified in the eval suite."
        ])

        md_content = "\n".join(lines)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(md_content)

        return md_content

    @staticmethod
    def promote_bug_to_permanent_row(
        case_id: str,
        query: str,
        expect_sufficient: bool,
        expect_urns: List[str],
        expect_section: str,
        severity: int,
        note: str,
        dataset_path: str = DATASET_PATH
    ):
        """
        Permanently registers a fixed production bug or missed test case into dataset.jsonl.
        """
        row = {
            "id": case_id,
            "input": query,
            "category": "Regression / Production Bug",
            "severity": severity,
            "expect_sufficient": expect_sufficient,
            "expect_urns": expect_urns,
            "expect_section": expect_section,
            "expected_tools": ["retrieve_context"] if expect_sufficient else [],
            "note": note
        }
        with open(dataset_path, "a") as f:
            f.write(json.dumps(row) + "\n")
        print(f"[ErrorAnalyzer] Successfully added permanent regression case: {case_id}")
