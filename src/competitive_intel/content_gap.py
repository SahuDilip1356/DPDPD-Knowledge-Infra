"""Decide which articles Setu should write. Cite the Act, never DPDPA.com."""

from __future__ import annotations

import json
import os
from typing import Any

from jsonschema import validate

from src.competitive_intel.topic_matrix import CANONICAL_TOPICS

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "schemas", "content_gap_schema.json"
)

CITE_INSTRUCTION = (
    "Write from the Act, Rules, and Gazette. Do not quote or cite DPDPA.com. "
    "If a fact is only on the competitor site, leave it out until counsel finds a primary source."
)

TOPIC_BRIEFS: dict[str, dict[str, Any]] = {
    "Offline to digital": {
        "title": "When a paper register becomes digital personal data",
        "priority": "P0",
        "audience": "kirana, clinic, and CA-firm owners",
        "why_write": (
            "Neither shop has a clear shelf for the offline-to-digital jump. "
            "A clinic photographing a visitor book is the everyday example."
        ),
        "outline": [
            "What Section 3 covers",
            "Paper in a drawer versus a photo on Drive",
            "A clinic and a kirana example",
            "What to do the week you digitise",
        ],
    },
    "AI + DPDPA": {
        "title": "Using AI tools with customer data under the DPDP Act",
        "priority": "P0",
        "audience": "MSME founders and product teams",
        "why_write": (
            "They wrote about AI. We have almost nothing. Customers already paste "
            "client files into chat tools and need an Act-based answer."
        ),
        "outline": [
            "Personal data does not stop being personal inside an AI tool",
            "Purpose, notice, and vendor duties",
            "What a small firm should ban on day one",
        ],
    },
    "Hidden / inferred data": {
        "title": "Scores, guesses, and inferred data under the DPDP Act",
        "priority": "P1",
        "audience": "product and risk teams",
        "why_write": (
            "They talk about hidden or inferred data. We should explain it in "
            "plain words with a Section 2 / Section 4 hook, not their blog."
        ),
        "outline": [
            "What counts as personal data if you only guessed it",
            "Notice and purpose limits",
            "A lending or HR screening example",
        ],
    },
    "Cookies": {
        "title": "Cookies and trackers under the DPDP Act, in plain English",
        "priority": "P1",
        "audience": "website and D2C teams",
        "why_write": (
            "They have cookie copy. India does not copy the EU cookie banner. "
            "Write the Indian rule, not a GDPR transplant."
        ),
        "outline": [
            "When a cookie is personal data",
            "Consent versus a legitimate use",
            "What a small Indian site should actually put on the page",
        ],
    },
    "WhatsApp": {
        "title": "WhatsApp groups, customer lists, and the DPDP Act",
        "priority": "P0",
        "audience": "MSME owners and front-desk staff",
        "why_write": (
            "Both sides mention WhatsApp. We can win by writing the shop-floor version: "
            "broadcast lists, staff phones, and a customer who says stop."
        ),
        "outline": [
            "A broadcast list is still processing",
            "Staff using a personal phone",
            "How to handle 'please delete my number'",
        ],
    },
    "Healthcare": {
        "title": "Clinics, labs, and the DPDP Act",
        "priority": "P1",
        "audience": "clinic and diagnostic-lab owners",
        "why_write": (
            "They have a healthcare blog. We should write the clinic version with "
            "prescription photos, WhatsApp reports, and staff access."
        ),
        "outline": [
            "Patient photos and reports",
            "Notice and legitimate use at the front desk",
            "Vendors who host your records",
        ],
    },
    "EdTech / schools": {
        "title": "Schools, coaching classes, and children's data",
        "priority": "P1",
        "audience": "school and coaching-class owners",
        "why_write": (
            "They cover EdTech. We can be clearer on children under 18, parent consent, "
            "and the no-tracking rule."
        ),
        "outline": [
            "Who is a child under the Act",
            "Verifiable parental consent",
            "What a coaching WhatsApp group may not do",
        ],
    },
    "DPIA": {
        "title": "When a small firm actually needs a DPIA",
        "priority": "P1",
        "audience": "privacy leads and SDF vendors",
        "why_write": (
            "They treat DPIA as a product. We should say who the Act actually asks, "
            "and what an enterprise client will demand from a vendor."
        ),
        "outline": [
            "Section 10 and Significant Data Fiduciaries",
            "Why a small vendor still gets the questionnaire",
            "A short, honest DPIA outline",
        ],
    },
    "Vendor / processor": {
        "title": "Your payroll, cloud, and WhatsApp vendors under Section 8",
        "priority": "P1",
        "audience": "MSME owners buying software",
        "why_write": (
            "They sell processor templates. We should explain the duty in shop language: "
            "you stay responsible when someone else hosts the data."
        ),
        "outline": [
            "Data Fiduciary versus Data Processor",
            "What the contract must make them do",
            "A payroll-vendor example",
        ],
    },
    "SMEs / small business": {
        "title": "DPDP Act for a 10-person Indian business",
        "priority": "P0",
        "audience": "MSME founders",
        "why_write": (
            "We already have a long guide. A short, dated checklist still wins "
            "against their SME blog."
        ),
        "outline": [
            "Does it apply to you",
            "The six-column register",
            "What to finish before May 2027",
        ],
    },
    "Data mapping / inventory": {
        "title": "How to map the personal data you already hold",
        "priority": "P1",
        "audience": "operations and founders",
        "why_write": (
            "We already talk about mapping. They barely do. Keep the lead with a "
            "one-page register people will actually fill."
        ),
        "outline": [
            "What to list",
            "Purpose and lawful ground",
            "Who can see it and who hosts it",
        ],
    },
    "Recruitment": {
        "title": "CVs, candidate WhatsApp chats, and the DPDP Act",
        "priority": "P1",
        "audience": "recruiters and HR teams",
        "why_write": (
            "This is already our advantage. Write the agency version: old CVs, "
            "shared Drive folders, and a candidate who asks to be forgotten."
        ),
        "outline": [
            "A CV is personal data",
            "How long to keep it",
            "What erasure means for a shared folder",
        ],
    },
    "CA firms": {
        "title": "CA firms, client PAN files, and the DPDP Act",
        "priority": "P1",
        "audience": "chartered accountants",
        "why_write": (
            "We already speak to CA firms. They do not. Keep that shelf with a "
            "Tally-backup and staff-laptop example."
        ),
        "outline": [
            "Client files you hold for years",
            "Staff laptops and WhatsApp",
            "What a client erasure request can and cannot force",
        ],
    },
    "Consent Manager": {
        "title": "What a Consent Manager is — and what it is not",
        "priority": "P1",
        "audience": "product and privacy teams",
        "why_write": (
            "Customers keep asking this. Answer from Section 2 and the Rules, "
            "not from a competitor course page."
        ),
        "outline": [
            "The Act's definition",
            "What registration is for",
            "What a small firm does not need to buy on day one",
        ],
    },
    "Training / certification": {
        "title": "What your team must know before May 2027",
        "priority": "P2",
        "audience": "founders briefing staff",
        "why_write": (
            "They sell courses. We should teach the seven words and the front-desk "
            "habit, citing the Act, not a certificate product."
        ),
        "outline": [
            "The seven words",
            "How a rights request arrives on WhatsApp",
            "What not to promise in training",
        ],
    },
}


def _schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def _fallback_citation(topic: str) -> str:
    for spec in CANONICAL_TOPICS:
        if spec["topic"] == topic and spec["primary"]:
            return spec["primary"]
    return "DPDPA 2023 (confirm the exact section before publishing)"


def build_content_gaps(
    matrix: list[dict[str, Any]],
    questions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Turn topic gaps and unanswered questions into article briefs."""
    if not isinstance(matrix, list) or not matrix:
        raise ValueError("topic matrix is required")
    if not isinstance(questions, list):
        raise ValueError("questions must be a list")

    questions_by_topic: dict[str, list[dict[str, Any]]] = {}
    for question in questions:
        questions_by_topic.setdefault(question["topic"], []).append(question)

    matrix_by_topic = {row["topic"]: row for row in matrix}
    briefs: list[dict[str, Any]] = []
    used_topics: set[str] = set()

    for topic, spec in TOPIC_BRIEFS.items():
        row = matrix_by_topic.get(topic)
        gap = row["gap"] if row else "investigate"
        if gap == "none" and topic not in {"SMEs / small business", "Consent Manager"}:
            continue
        related = questions_by_topic.get(topic, [])
        unanswered = [q for q in related if q["gap"] == "they_ask_we_dont"]
        citations = []
        if row and row.get("primary_citation"):
            citations.append(row["primary_citation"])
        if not citations:
            citations.append(_fallback_citation(topic))
        brief = {
            "brief_id": f"GAP-{len(briefs) + 1:03d}",
            "title": spec["title"],
            "priority": spec["priority"],
            "gap_type": gap,
            "why_write": spec["why_write"],
            "audience": spec["audience"],
            "primary_citations": citations,
            "never_cite": ["DPDPA.com"],
            "questions_answered": [q["question_id"] for q in (unanswered or related)[:8]],
            "competitor_covers": bool(row and row.get("dpdpa_com") != "no"),
            "competitor_urls_discovery_only": list((row or {}).get("competitor_urls") or [])[:5],
            "outline": spec["outline"],
            "cite_instruction": CITE_INSTRUCTION,
            "publication_eligible": False,
        }
        briefs.append(brief)
        used_topics.add(topic)

    leftover = [
        q
        for q in questions
        if q["gap"] == "they_ask_we_dont" and q["topic"] not in used_topics
    ]
    leftover_topics: dict[str, list[dict[str, Any]]] = {}
    for question in leftover:
        leftover_topics.setdefault(question["topic"], []).append(question)
    for topic, group in leftover_topics.items():
        row = matrix_by_topic.get(topic)
        citation = (
            (row or {}).get("primary_citation")
            or group[0].get("primary_citation")
            or _fallback_citation(topic)
        )
        briefs.append(
            {
                "brief_id": f"GAP-{len(briefs) + 1:03d}",
                "title": f"{topic}: answer the questions customers already ask",
                "priority": "P2",
                "gap_type": (row or {}).get("gap") or "investigate",
                "why_write": (
                    f"They already list {len(group)} questions on this topic that "
                    "our surfaces do not ask in those words."
                ),
                "audience": "business",
                "primary_citations": [citation],
                "never_cite": ["DPDPA.com"],
                "questions_answered": [q["question_id"] for q in group[:8]],
                "competitor_covers": True,
                "competitor_urls_discovery_only": [
                    url
                    for q in group
                    for url in q.get("competitor_urls") or []
                ][:5],
                "outline": [q["question_text"] for q in group[:5]],
                "cite_instruction": CITE_INSTRUCTION,
                "publication_eligible": False,
            }
        )

    schema = _schema()
    for brief in briefs:
        validate(instance=brief, schema=schema)
        if "DPDPA.com" not in brief["never_cite"]:
            raise ValueError("every brief must refuse a DPDPA.com citation")
    priority_rank = {"P0": 0, "P1": 1, "P2": 2}
    briefs.sort(key=lambda item: (priority_rank[item["priority"]], item["brief_id"]))
    for index, brief in enumerate(briefs, start=1):
        brief["brief_id"] = f"GAP-{index:03d}"
    return briefs


def gap_summary(briefs: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for brief in briefs:
        counts[brief["priority"]] = counts.get(brief["priority"], 0) + 1
    return {
        "count": len(briefs),
        "by_priority": counts,
        "publication_eligible": False,
        "headline": (
            f"{len(briefs)} article briefs ready. "
            f"{counts.get('P0', 0)} write first, {counts.get('P1', 0)} next, "
            f"{counts.get('P2', 0)} later. Every brief cites the Act, not DPDPA.com."
        ),
    }
