"""Stamp competitor claims with Source Truth verdicts."""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

from jsonschema import validate

from src.competitive_intel.knowledge_cards import extract_rules, extract_sections
from src.competitive_intel.primary_facts import (
    INCORRECT_OR_CONTESTED,
    PRIMARY_FACTS,
    first_section,
)

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "schemas", "claim_registry_schema.json"
)


def _schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def claim_id_for(url: str, text: str) -> str:
    digest = hashlib.sha256(f"{url}\n{text}".encode("utf-8")).hexdigest()
    return f"CLM-{int(digest[:8], 16) % 1_000_000:06d}"


def judge_claim(
    text: str,
    claim_type: str,
    sections: list[str] | None = None,
    rules: list[str] | None = None,
) -> dict[str, Any]:
    """Return verdict fields for one claim. Conservative: prefer NEEDS_REVIEW."""
    if not text or len(text.strip()) < 8:
        raise ValueError("claim text is required")
    blob = text.strip()

    for pattern, status, section, note in INCORRECT_OR_CONTESTED:
        if pattern.search(blob):
            return {
                "verification_status": status,
                "confidence": 0.85 if status == "INCORRECT" else 0.7,
                "primary_source": None,
                "dpdpa_section": section or first_section(sections),
                "dpdp_rule": first_section(rules),
                "verdict_note": note,
                "publication_allowed": False,
            }

    for fact in PRIMARY_FACTS:
        if fact.pattern.search(blob):
            allowed = fact.verdict == "VERIFIED_PRIMARY"
            return {
                "verification_status": fact.verdict,
                "confidence": 0.9 if allowed else 0.65,
                "primary_source": fact.primary_source,
                "dpdpa_section": fact.dpdpa_section or first_section(sections),
                "dpdp_rule": fact.dpdp_rule or first_section(rules),
                "verdict_note": fact.note,
                "publication_allowed": allowed,
            }

    if claim_type == "STATISTIC":
        return {
            "verification_status": "NEEDS_REVIEW",
            "confidence": 0.35,
            "primary_source": None,
            "dpdpa_section": first_section(sections),
            "dpdp_rule": first_section(rules),
            "verdict_note": "Numeric claim without a matching Schedule or Rule fact.",
            "publication_allowed": False,
        }

    if sections or rules:
        return {
            "verification_status": "SUPPORTED_INTERPRETATION",
            "confidence": 0.45,
            "primary_source": None,
            "dpdpa_section": first_section(sections),
            "dpdp_rule": first_section(rules),
            "verdict_note": "Mentions a section or rule, but the sentence is still competitor commentary.",
            "publication_allowed": False,
        }

    if claim_type == "OPINION" or re.search(r"\b(we believe|ultimate|comprehensive guide)\b", blob, re.I):
        return {
            "verification_status": "UNSUPPORTED",
            "confidence": 0.4,
            "primary_source": None,
            "dpdpa_section": first_section(sections),
            "dpdp_rule": first_section(rules),
            "verdict_note": "Opinion or marketing language. Not a primary source.",
            "publication_allowed": False,
        }

    return {
        "verification_status": "NEEDS_REVIEW",
        "confidence": 0.3,
        "primary_source": None,
        "dpdpa_section": first_section(sections),
        "dpdp_rule": first_section(rules),
        "verdict_note": "No catalog match. A reviewer must check the Act or Gazette.",
        "publication_allowed": False,
    }


def register_claims(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten card claims into a claims registry."""
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for card in cards:
        url = card.get("source_url")
        if not url:
            raise ValueError("card source_url is required")
        for claim in card.get("claims") or []:
            text = (claim.get("text") or "").strip()
            if not text:
                continue
            row_id = claim_id_for(url, text)
            if row_id in seen:
                continue
            seen.add(row_id)
            judged = judge_claim(
                text,
                claim.get("claim_type") or "OPINION",
                extract_sections(text),
                extract_rules(text),
            )
            row = {
                "claim_id": row_id,
                "claim_text": text[:400],
                "found_on": "DPDPA.com",
                "card_id": card.get("card_id"),
                "original_url": url,
                "claim_type": claim.get("claim_type") or "OPINION",
                "dpdpa_section": judged["dpdpa_section"],
                "dpdp_rule": judged["dpdp_rule"],
                "primary_source": judged["primary_source"],
                "verification_status": judged["verification_status"],
                "confidence": judged["confidence"],
                "verdict_note": judged["verdict_note"],
                "publication_allowed": bool(judged["publication_allowed"]),
                "used_by_saralprivacy": False,
            }
            validate(instance=row, schema=_schema())
            rows.append(row)
    rows.sort(key=lambda item: (item["verification_status"], item["claim_id"]))
    return rows
