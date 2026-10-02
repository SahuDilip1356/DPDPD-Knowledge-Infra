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


# ---------------------------------------------------------------------------
# Real-corpus scorers: citations are scored as provision labels
# (S1–S44, ACT-SCHEDULE, R1–R23, SCH-FIRST … SCH-SEVENTH).
# ---------------------------------------------------------------------------

import re

ORDINALS = ["FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH",
            "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"]

_NUMBER_LIST = r"(\d{1,3}[A-Z]?(?:\([^)\s]{1,6}\))*(?:\s*(?:,|and|or|to|&)\s*\d{1,3}[A-Z]?(?:\([^)\s]{1,6}\))*)*)"
_PROVISION_REF = re.compile(
    r"\b(?P<kind>Sections?|Sec\.|Rules?)\s+" + _NUMBER_LIST + r"(?!\d)", re.I
)
_SCHEDULE_REF = re.compile(r"\b(?P<ord>" + "|".join(ORDINALS) + r")\s+Schedule\b", re.I)
# "Section 43A of the Information Technology Act" names another statute; "section 8 of
# the Act" and "Rule 7 of the DPDP Rules" name this one.
_OTHER_STATUTE = re.compile(
    r"\s+of\s+the\s+(?!(?:DPDP|Digital\s+Personal\s+Data|Act\b|said\s+Act|Rules\b|principal\s+Act))",
    re.I,
)


def provision_mentions(text: str) -> List[Dict[str, Any]]:
    """Every provision the text names, as {"raw", "label"}.

    `label` is the canonical label the mention would have if it existed (S12, R7,
    SCH-EIGHTH); whether it exists is for the caller's provision list to decide.
    References to other statutes are skipped.
    """
    mentions = []
    for match in _PROVISION_REF.finditer(text or ""):
        if _OTHER_STATUTE.match(text, match.end()):
            continue
        prefix = "R" if match.group("kind").lower().startswith("rule") else "S"
        numbers = re.sub(r"\([^)]*\)", "", match.group(2))
        for number in re.findall(r"\d{1,3}[A-Z]?", numbers):
            mentions.append({"raw": match.group(0), "label": f"{prefix}{number.upper()}"})
    for match in _SCHEDULE_REF.finditer(text or ""):
        mentions.append({"raw": match.group(0), "label": f"SCH-{match.group('ord').upper()}"})
    return mentions


def score_cited_subset_retrieved(cited_urns: List[str], retrieved_urns: List[str]) -> bool:
    """Every cited object was actually retrieved for this query."""
    return set(cited_urns) <= set(retrieved_urns)


def score_provision_recall(cited_labels: Set[str], expected: List[str]) -> Optional[float]:
    """Share of the expected provisions the answer cites. None when nothing is expected."""
    if not expected:
        return None
    return len(set(expected) & set(cited_labels)) / len(set(expected))


def nonexistent_provisions(
    cited_labels: Set[str], answer_text: str, valid_labels: Set[str]
) -> List[str]:
    """Provisions cited (by object) or named (in the answer text) that do not exist."""
    named = {m["label"] for m in provision_mentions(answer_text)}
    return sorted((set(cited_labels) | named) - set(valid_labels))


def score_refusal(grounded: bool, expect_sufficient: bool) -> bool:
    """Answers when the corpus supports the question; refuses when it does not."""
    return bool(grounded) == bool(expect_sufficient)
