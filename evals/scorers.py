"""
Evaluation Scorers — Phase 3 & Phase 5 of AI Evals & Reliability Playbook

Five ways to turn quality into a number, prioritizing free/deterministic checks first:
1. sufficient_match: Boolean comparison of groundedness / refusal intent.
2. citation_recall: Checks whether all expected statutory URNs were cited.
3. no_fabrication: Verifies that cited URNs are a strict subset of retrieved context.
4. trajectory_match: Grades the path (retrieval / tool calls) against expected steps.
"""

from typing import Dict, List, Optional, Set, Any

def score_sufficient_match(actual_sufficient: bool, expect_sufficient: bool) -> bool:
    """Boolean exact match on evidence sufficiency / refusal."""
    return bool(actual_sufficient) == bool(expect_sufficient)


def score_citation_recall(cited_urns: List[str], expect_urns: List[str]) -> bool:
    """Checks whether every expected URN is present in the cited URNs."""
    if not expect_urns:
        # If no URN was expected (e.g. negative cases), pass if no URN was cited
        return len(cited_urns) == 0
    
    cited_set = set(cited_urns)
    expected_set = set(expect_urns)
    return expected_set.issubset(cited_set)


def score_no_fabrication(cited_urns: List[str], retrieved_urns: List[str]) -> bool:
    """Verifies that no cited URN was fabricated (must be a subset of retrieved)."""
    if not cited_urns:
        return True
    cited_set = set(cited_urns)
    retrieved_set = set(retrieved_urns)
    return cited_set.issubset(retrieved_set)


def score_trajectory_match(
    actual_spans_or_tools: List[str],
    expected_tools: List[str],
    acceptable_substitutes: Optional[Dict[str, List[str]]] = None
) -> bool:
    """
    Trajectory check: did the agent take the right path?
    Negative tests expect empty list [].
    Supports alias mapping / acceptable substitute tools.
    """
    if not expected_tools:
        # Negative test case: expecting no retrieval or external tool calls
        return "retrieve_context" not in actual_spans_or_tools

    substitutes = acceptable_substitutes or {}
    
    for exp in expected_tools:
        valid_options = {exp}
        if exp in substitutes:
            valid_options.update(substitutes[exp])
        
        # Check if at least one valid option was executed
        if not any(opt in actual_spans_or_tools for opt in valid_options):
            return False

    return True


def evaluate_case(
    case: Dict[str, Any],
    run_output: Dict[str, Any],
    retrieved_urns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Runs all free, deterministic scorers against a single run output.
    """
    actual_sufficient = bool(run_output.get("grounded", False))
    expect_sufficient = bool(case.get("expect_sufficient", True))

    cited_urns = run_output.get("cited_urns", [])
    expect_urns = case.get("expect_urns", [])

    retrieved = retrieved_urns or run_output.get("retrieved_urns", cited_urns)

    # Extract executed spans / tools from trace if present
    trace_spans = []
    if "trace" in run_output and "spans" in run_output["trace"]:
        trace_spans = [s["name"] for s in run_output["trace"]["spans"]]
        # Map retrieval span to tool concept
        if "retrieval" in trace_spans:
            trace_spans.append("retrieve_context")

    expected_tools = case.get("expected_tools", [])

    sufficient_match = score_sufficient_match(actual_sufficient, expect_sufficient)
    citation_recall = score_citation_recall(cited_urns, expect_urns)
    no_fab = score_no_fabrication(cited_urns, retrieved)
    trajectory = score_trajectory_match(trace_spans, expected_tools)

    passed_all = sufficient_match and citation_recall and no_fab and trajectory

    return {
        "case_id": case.get("id"),
        "passed": passed_all,
        "scores": {
            "sufficient_match": sufficient_match,
            "citation_recall": citation_recall,
            "no_fabrication": no_fab,
            "trajectory_match": trajectory
        },
        "details": {
            "actual_sufficient": actual_sufficient,
            "expect_sufficient": expect_sufficient,
            "cited_urns": cited_urns,
            "expect_urns": expect_urns,
            "executed_spans": trace_spans,
            "expected_tools": expected_tools,
            "severity": case.get("severity", 3)
        }
    }
