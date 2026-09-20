"""Compare DPDPA.com coverage with SaralPrivacy's existing corpus."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from jsonschema import validate

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "schemas", "topic_matrix_schema.json"
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CANONICAL_TOPICS: tuple[dict[str, Any], ...] = (
    {"topic_id": "TOP-001", "topic": "Consent", "needles": ("consent",), "primary": "DPDPA 2023 Section 6", "sp_strong": True},
    {"topic_id": "TOP-002", "topic": "Notice", "needles": ("notice",), "primary": "DPDPA 2023 Section 5", "sp_strong": True},
    {"topic_id": "TOP-003", "topic": "Children", "needles": ("child", "parental", "under 18"), "primary": "DPDPA 2023 Section 9", "sp_strong": True},
    {"topic_id": "TOP-004", "topic": "Legitimate uses", "needles": ("legitimate use", "legitimate uses"), "primary": "DPDPA 2023 Section 7", "sp_strong": True},
    {"topic_id": "TOP-005", "topic": "Data Fiduciary obligations", "needles": ("data fiduciary", "security safeguard"), "primary": "DPDPA 2023 Section 8", "sp_strong": True},
    {"topic_id": "TOP-006", "topic": "Data mapping / inventory", "needles": ("data mapping", "inventory", "data map"), "primary": "DPDPA 2023 Section 4 / Section 8", "sp_strong": True},
    {"topic_id": "TOP-007", "topic": "DPIA", "needles": ("dpia", "privacy impact"), "primary": "DPDPA 2023 Section 10", "sp_strong": False},
    {"topic_id": "TOP-008", "topic": "Significant Data Fiduciary", "needles": ("significant data fiduciary", " sdf"), "primary": "DPDPA 2023 Section 10", "sp_strong": True},
    {"topic_id": "TOP-009", "topic": "Consent Manager", "needles": ("consent manager",), "primary": "DPDPA 2023 Section 2; Rules on registration", "sp_strong": True},
    {"topic_id": "TOP-010", "topic": "Breach response", "needles": ("breach", "72-hour", "72 hour"), "primary": "DPDPA 2023 Section 8(6); Rules on intimation", "sp_strong": True},
    {"topic_id": "TOP-011", "topic": "Penalties", "needles": ("penalty", "crore", "fine"), "primary": "DPDPA 2023 Section 33 and Schedule", "sp_strong": True},
    {"topic_id": "TOP-012", "topic": "Cross-border transfer", "needles": ("cross-border", "outside india", "transfer"), "primary": "DPDPA 2023 Section 16", "sp_strong": True},
    {"topic_id": "TOP-013", "topic": "AI + DPDPA", "needles": ("generative ai", "chatgpt", "machine learning", "ai and", "ai &", "on ai"), "primary": None, "sp_strong": False},
    {"topic_id": "TOP-014", "topic": "WhatsApp", "needles": ("whatsapp",), "primary": None, "sp_strong": True},
    {"topic_id": "TOP-015", "topic": "Recruitment", "needles": ("recruitment", "candidate", "cv "), "primary": None, "sp_strong": True},
    {"topic_id": "TOP-016", "topic": "CA firms", "needles": ("ca firm", "chartered accountant"), "primary": None, "sp_strong": True},
    {"topic_id": "TOP-017", "topic": "Hidden / inferred data", "needles": ("inference data", "attention and inference", "inferred", "hidden data"), "primary": None, "sp_strong": True},
    {"topic_id": "TOP-018", "topic": "Offline to digital", "needles": ("offline", "paper to", "digitised", "digitized"), "primary": "DPDPA 2023 Section 3 (digital personal data)", "sp_strong": True},
    {"topic_id": "TOP-019", "topic": "Healthcare", "needles": ("hospital", "healthcare", "clinic"), "primary": None, "sp_strong": True},
    {"topic_id": "TOP-020", "topic": "EdTech / schools", "needles": ("ed-tech", "edtech", "school", "student data", "coaching"), "primary": None, "sp_strong": True},
    {"topic_id": "TOP-021", "topic": "HR / employee data", "needles": ("employee data", "hr department", "employment"), "primary": "DPDPA 2023 Section 7 (employment as legitimate use)", "sp_strong": True},
    {"topic_id": "TOP-022", "topic": "Retention", "needles": ("retention",), "primary": "DPDPA 2023 Section 8(7)", "sp_strong": True},
    {"topic_id": "TOP-023", "topic": "Vendor / processor", "needles": ("vendor", "processor", "data processing agreement"), "primary": "DPDPA 2023 Section 8", "sp_strong": False},
    {"topic_id": "TOP-024", "topic": "Cookies", "needles": ("cookie",), "primary": None, "sp_strong": False},
    {"topic_id": "TOP-025", "topic": "Erasure / RTBF framing", "needles": ("right to be forgotten", "erasure"), "primary": "DPDPA 2023 Section 12", "sp_strong": True},
    {"topic_id": "TOP-026", "topic": "Nomination", "needles": ("nominat",), "primary": "DPDPA 2023 Section 14", "sp_strong": True},
    {"topic_id": "TOP-027", "topic": "Data Protection Board", "needles": ("data protection board", "dpbi"), "primary": "DPDPA 2023 Section 18", "sp_strong": True},
    {"topic_id": "TOP-028", "topic": "Templates / policies", "needles": ("template",), "primary": None, "sp_strong": True},
    {"topic_id": "TOP-029", "topic": "Training / certification", "needles": ("certificate course", "module 1", "interview question"), "primary": None, "sp_strong": False},
    {"topic_id": "TOP-030", "topic": "SMEs / small business", "needles": ("sme", "small business", "msme"), "primary": None, "sp_strong": True},
)


def _schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def load_saralprivacy_corpus(root: str = REPO_ROOT) -> str:
    """Read the local SaralPrivacy knowledge surfaces as one search blob."""
    paths = [
        os.path.join(root, "DPDPA_BIBLE.md"),
        os.path.join(root, "deployments", "dpdpa-backend", "DPDPA_BIBLE.md"),
        os.path.join(root, "seed_full_knowledge_base.py"),
        os.path.join(root, "deployments", "dpdpa-wiki", "src", "content", "guides", "dpdp-act-explained-indian-msmes.md"),
        os.path.join(root, "deployments", "dpdpa-wiki", "src", "data", "homeContent.js"),
        os.path.join(root, "KNOWLEDGE_CONSTITUTION.md"),
    ]
    chunks: list[str] = []
    for path in paths:
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as handle:
                chunks.append(handle.read())
    if not chunks:
        raise FileNotFoundError("no SaralPrivacy corpus files found")
    return "\n".join(chunks).lower()


def _hits(blob: str, needles: tuple[str, ...]) -> int:
    return sum(blob.count(needle.lower()) for needle in needles)


def _coverage(count: int, generic_below: int = 3) -> str:
    if count <= 0:
        return "no"
    if count < generic_below:
        return "generic"
    return "yes"


def _card_blob(card: dict[str, Any]) -> str:
    parts = [
        card.get("title") or "",
        card.get("topic") or "",
        " ".join(card.get("subtopics") or []),
        card.get("source_url") or "",
    ]
    return " ".join(parts).lower()


def classify_gap(dpdpa_com: str, saralprivacy: str, primary: str, sp_strong: bool) -> str:
    if dpdpa_com != "no" and saralprivacy == "no":
        return "investigate"
    if dpdpa_com == "no" and saralprivacy != "no":
        return "sp_advantage" if sp_strong else "sp_opportunity"
    if dpdpa_com == "generic" and saralprivacy == "yes" and sp_strong:
        return "sp_advantage"
    if dpdpa_com == "yes" and saralprivacy == "yes" and sp_strong:
        return "differentiate" if primary == "no" else "none"
    if dpdpa_com == "yes" and saralprivacy == "generic":
        return "investigate"
    if dpdpa_com == "yes" and saralprivacy == "yes" and not sp_strong:
        return "differentiate"
    if dpdpa_com == "no" and saralprivacy == "no":
        return "sp_opportunity" if primary == "yes" else "investigate"
    return "none"


def build_topic_matrix(
    cards: list[dict[str, Any]],
    saral_blob: str | None = None,
) -> list[dict[str, Any]]:
    """Build the founder gap table."""
    corpus = saral_blob if saral_blob is not None else load_saralprivacy_corpus()
    rows: list[dict[str, Any]] = []
    for spec in CANONICAL_TOPICS:
        competitor_urls: list[str] = []
        competitor_hits = 0
        for card in cards:
            blob = _card_blob(card)
            score = _hits(blob, spec["needles"])
            if score:
                competitor_hits += score
                url = card.get("source_url")
                if url and url not in competitor_urls:
                    competitor_urls.append(url)
        sp_hits = _hits(corpus, spec["needles"])
        dpdpa_com = _coverage(competitor_hits, generic_below=2)
        # Templates and course pages count as coverage even if few URLs.
        if spec["topic_id"] in {"TOP-028", "TOP-029"} and competitor_urls:
            dpdpa_com = "yes"
        saralprivacy = _coverage(sp_hits, generic_below=2)
        if spec["sp_strong"] and sp_hits:
            saralprivacy = "yes"
        primary = "yes" if spec["primary"] else "no"
        gap = classify_gap(dpdpa_com, saralprivacy, primary, spec["sp_strong"])
        row = {
            "topic_id": spec["topic_id"],
            "topic": spec["topic"],
            "dpdpa_com": dpdpa_com,
            "saralprivacy": saralprivacy,
            "primary_evidence": primary,
            "gap": gap,
            "competitor_urls": competitor_urls[:8],
            "saralprivacy_evidence": (
                [spec["primary"]] if spec["primary"] else []
            )
            + (["SaralPrivacy MSME guide / Bible / seed KOs"] if saralprivacy != "no" else []),
            "primary_citation": spec["primary"],
            "note": f"Competitor hits={competitor_hits} across {len(competitor_urls)} pages; SaralPrivacy hits={sp_hits}.",
            "publication_eligible": False,
        }
        validate(instance=row, schema=_schema())
        rows.append(row)
    return rows


def matrix_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["gap"]] = counts.get(row["gap"], 0) + 1
    covered_both = sum(1 for row in rows if row["dpdpa_com"] != "no" and row["saralprivacy"] != "no")
    competitor_only = sum(1 for row in rows if row["dpdpa_com"] != "no" and row["saralprivacy"] == "no")
    sp_only = sum(1 for row in rows if row["dpdpa_com"] == "no" and row["saralprivacy"] != "no")
    return {
        "topic_count": len(rows),
        "both_cover": covered_both,
        "competitor_only": competitor_only,
        "saralprivacy_only": sp_only,
        "by_gap": counts,
        "publication_eligible": False,
        "headline": (
            f"We compared {len(rows)} concepts: {covered_both} both cover, "
            f"{sum(1 for row in rows if row['gap'] == 'differentiate')} where SaralPrivacy can differentiate, "
            f"{sum(1 for row in rows if row['gap'] in {'investigate', 'sp_opportunity'})} genuine gaps or opportunities, "
            f"{sp_only} already stronger on the SaralPrivacy side."
        ),
    }
