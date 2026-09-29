"""
Deterministic request and response guardrails for the live reasoning path.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple


REFUSAL_PATTERNS = [
    (
        re.compile(
            r"\b(account\s*balance|my\s*balance|bank\s*balance|compliance\s*score|audit\s*status)\b",
            re.I,
        ),
        "The service cannot access private account, financial, or audit data.",
    ),
    (
        re.compile(
            r"\b(company\s*revenue|annual\s*revenue|financial\s*statement|how\s*much\s*revenue|balance\s*sheet)\b",
            re.I,
        ),
        "The service does not have access to private financial or accounting data.",
    ),
    (
        re.compile(r"\b(gdpr|article\s*17|ccpa|foreign\s*privacy\s*law)\b", re.I),
        "Out of corpus: this service currently answers from the Indian DPDPA knowledge core.",
    ),
    (
        re.compile(r"\b(weather\s+on\s+mars|mars\s+weather)\b", re.I),
        "Out of scope: the query is outside the regulatory domain.",
    ),
    (
        re.compile(
            r"\b(speeding|delhi\s*highways?|traffic\s*(violation|ticket|fine|penalty)|motor\s*vehicles?)\b",
            re.I,
        ),
        "Out of scope: traffic violations are outside the DPDPA domain.",
    ),
    (
        re.compile(
            r"\b(ignore\s+(all\s+)?previous\s+instructions|system\s+prompt|reveal\s+(your\s+)?prompt)\b",
            re.I,
        ),
        "Security refusal: prompt extraction or instruction override is not allowed.",
    ),
]

CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
INDIAN_PAN_REGEX = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
URN_REGEX = re.compile(r"urn:ki:[a-zA-Z0-9_:\-]+")


class InputGuardrail:
    """Fast pre-flight checks that do not invoke a model."""

    @staticmethod
    def inspect(query: str) -> Tuple[bool, Optional[str]]:
        if not query or not query.strip():
            return False, "Empty query provided."

        query_clean = query.strip()
        for pattern, reason in REFUSAL_PATTERNS:
            if pattern.search(query_clean):
                return False, reason

        return True, None


class OutputGuardrail:
    """Validate the structured response and confine citations to retrieval."""

    @staticmethod
    def inspect(
        parsed_response: Dict[str, Any], retrieved_urns: Set[str]
    ) -> Tuple[bool, Dict[str, Any], List[str]]:
        violations: List[str] = []
        sanitized = dict(parsed_response) if isinstance(parsed_response, dict) else {}

        if "answer" not in sanitized or not isinstance(sanitized["answer"], str):
            violations.append("MISSING_OR_INVALID_ANSWER_FIELD")
            sanitized["answer"] = str(sanitized.get("answer", ""))

        if not isinstance(sanitized.get("sufficient_evidence"), bool):
            violations.append("MISSING_OR_INVALID_SUFFICIENT_EVIDENCE_FLAG")
            sanitized["sufficient_evidence"] = False

        raw_claimed = sanitized.get("cited_urns", [])
        if not isinstance(raw_claimed, list) or not all(
            isinstance(urn, str) for urn in raw_claimed
        ):
            violations.append("INVALID_CITED_URNS_TYPE")
            raw_claimed = []

        answer_urns = set(URN_REGEX.findall(sanitized["answer"]))
        claimed_urns = set(raw_claimed) | answer_urns
        fabricated = claimed_urns - retrieved_urns
        valid_cited = claimed_urns & retrieved_urns

        if fabricated:
            violations.append(f"FABRICATED_CITATIONS: {sorted(fabricated)}")
            sanitized["answer"] = (
                "INSUFFICIENT_EVIDENCE: The generated answer contained a citation "
                "that was not present in the retrieved knowledge context."
            )
            sanitized["cited_urns"] = []
            sanitized["sufficient_evidence"] = False
        else:
            sanitized["cited_urns"] = sorted(valid_cited)

        if sanitized["sufficient_evidence"] and not sanitized["cited_urns"]:
            violations.append("SUFFICIENT_ANSWER_WITHOUT_CITATION")
            sanitized["sufficient_evidence"] = False

        answer_text = sanitized["answer"]
        if CREDIT_CARD_REGEX.search(answer_text):
            violations.append("PII_CREDIT_CARD_DETECTED")
            answer_text = CREDIT_CARD_REGEX.sub("[REDACTED_CC]", answer_text)
        if INDIAN_PAN_REGEX.search(answer_text):
            violations.append("PII_PAN_DETECTED")
            answer_text = INDIAN_PAN_REGEX.sub("[REDACTED_PAN]", answer_text)
        sanitized["answer"] = answer_text

        return len(violations) == 0, sanitized, violations
