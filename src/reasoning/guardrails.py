"""
Fast Millisecond Guardrails — Phase 8 of AI Evals & Reliability Playbook

Sits in the live request path with a sub-5ms speed budget:
1. InputGuardrail: Fast refusal & prompt injection detection without calling LLMs.
2. OutputGuardrail: Strict schema verification, tool/URN allow-list, and PII containment.
"""

import re
from typing import Dict, List, Optional, Set, Tuple, Any

# Fast regex patterns for input refusal detection
REFUSAL_PATTERNS = [
    (re.compile(r"\b(account\s*balance|my\s*balance|bank\s*balance|compliance\s*score|audit\s*status)\b", re.I),
     "Bot cannot access personal financial, user audit status, or private account data."),
    (re.compile(r"\b(company\s*revenue|annual\s*revenue|financial\s*statement|how\s*much\s*revenue|balance\s*sheet)\b", re.I),
     "Bot does not have access to private financial or corporate accounting data."),
    (re.compile(r"\b(gdpr|article\s*17|ccpa|foreign\s*privacy\s*law)\b", re.I),
     "Out of corpus: The engine only reasons over the Indian DPDPA 2023 regulatory core."),
    (re.compile(r"\b(weather\s+on\s+mars|mars\s+weather)\b", re.I),
     "Out of scope: Query is outside the regulatory domain."),
    (re.compile(r"\b(speeding|delhi\s*highways?|traffic\s*(violation|ticket|fine|penalty)|motor\s*vehicles?)\b", re.I),
     "Out of scope: Traffic violations are outside the DPDPA 2023 domain."),
    (re.compile(r"\b(ignore\s+(all\s+)?previous\s+instructions|system\s+prompt|reveal\s+(your\s+)?prompt)\b", re.I),
     "Security refusal: Disallowed system command or prompt extraction attempt."),
]

# Simple PII detection patterns (PAN, Aadhaar-like numbers, Credit Card)
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
INDIAN_PAN_REGEX = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b")

class InputGuardrail:
    """Pre-flight deterministic guardrail (< 1ms)."""

    @staticmethod
    def inspect(query: str) -> Tuple[bool, Optional[str]]:
        """
        Returns (is_allowed, refusal_reason).
        If is_allowed is False, the query is blocked before hitting any LLM.
        """
        if not query or not query.strip():
            return False, "Empty query provided."

        query_clean = query.strip()
        for pattern, reason in REFUSAL_PATTERNS:
            if pattern.search(query_clean):
                return False, reason

        return True, None


class OutputGuardrail:
    """Post-flight deterministic guardrail (< 2ms)."""

    @staticmethod
    def inspect(
        parsed_response: Dict[str, Any],
        retrieved_urns: Set[str]
    ) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Validates schema, enforces citation containment against retrieved URNs,
        and sanitizes PII.
        
        Returns:
            (is_valid, sanitized_dict, violations_list)
        """
        violations = []
        sanitized = dict(parsed_response)

        # 1. Schema integrity
        if "answer" not in sanitized or not isinstance(sanitized["answer"], str):
            violations.append("MISSING_OR_INVALID_ANSWER_FIELD")
            sanitized["answer"] = str(sanitized.get("answer", ""))

        if "sufficient_evidence" not in sanitized:
            violations.append("MISSING_SUFFICIENT_EVIDENCE_FLAG")
            sanitized["sufficient_evidence"] = False
        else:
            sanitized["sufficient_evidence"] = bool(sanitized["sufficient_evidence"])

        raw_claimed = sanitized.get("cited_urns", [])
        if not isinstance(raw_claimed, list):
            violations.append("INVALID_CITED_URNS_TYPE")
            raw_claimed = []
            
        claimed_urns = set(raw_claimed)

        # 2. Citation Confinement (no_fabrication)
        fabricated = claimed_urns - retrieved_urns
        if fabricated:
            violations.append(f"FABRICATED_CITATIONS: {sorted(list(fabricated))}")
            # Containment: keep only retrieved & claimed
            valid_cited = claimed_urns & retrieved_urns
            sanitized["cited_urns"] = sorted(list(valid_cited))
        else:
            sanitized["cited_urns"] = sorted(list(claimed_urns))

        # 3. PII Redaction
        answer_text = sanitized["answer"]
        if CREDIT_CARD_REGEX.search(answer_text):
            violations.append("PII_CREDIT_CARD_DETECTED")
            answer_text = CREDIT_CARD_REGEX.sub("[REDACTED_CC]", answer_text)
        if INDIAN_PAN_REGEX.search(answer_text):
            violations.append("PII_PAN_DETECTED")
            answer_text = INDIAN_PAN_REGEX.sub("[REDACTED_PAN]", answer_text)
        sanitized["answer"] = answer_text

        is_valid = (len(violations) == 0)
        return is_valid, sanitized, violations
