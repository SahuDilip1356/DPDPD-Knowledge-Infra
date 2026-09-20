"""Collect the questions customers actually ask. Do not copy competitor answers."""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

from jsonschema import validate

from src.competitive_intel.knowledge_cards import extract_rules, extract_sections
from src.competitive_intel.topic_matrix import CANONICAL_TOPICS, REPO_ROOT

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "schemas", "question_universe_schema.json"
)

QUESTION_RE = re.compile(
    r"((?:What|How|When|Who|Do|Does|Can|Is|Are|Why|Which|Where|Should|Must|"
    r"If)\b[^?\n]{8,160}\?)",
    re.I,
)
NUMBERED_Q_RE = re.compile(
    r"(?:^|\n)\s*\d+\s+((?:What|How|When|Who|Do|Does|Can|Is|Are|Why|Which|"
    r"Where|Should|Must|If)[^?\n]{6,180}\?)",
    re.I,
)
JS_FAQ_RE = re.compile(r'q:\s*"([^"]+\?)"', re.I)
MD_H_RE = re.compile(r"^#{2,3}\s+(.+\?)\s*$", re.M)

MSME_CUSTOMER_QUESTIONS: tuple[tuple[str, str, str], ...] = (
    (
        "Does the DPDP Act apply to my small shop, clinic, or CA firm?",
        "SMEs / small business",
        "DPDPA 2023 Section 3",
    ),
    (
        "Can I keep customer numbers in a WhatsApp group?",
        "WhatsApp",
        "DPDPA 2023 Section 4 / Section 8",
    ),
    (
        "What do I do if a customer asks me to delete their data?",
        "Erasure / RTBF framing",
        "DPDPA 2023 Section 12",
    ),
    (
        "How long may I keep a customer's data?",
        "Retention",
        "DPDPA 2023 Section 8(7)",
    ),
    (
        "Do I need consent if a walk-in customer gives me a number for delivery?",
        "Legitimate uses",
        "DPDPA 2023 Section 7",
    ),
    (
        "What must my notice say before I ask for consent?",
        "Notice",
        "DPDPA 2023 Section 5",
    ),
    (
        "Does a paper visitor register become covered once I photograph it?",
        "Offline to digital",
        "DPDPA 2023 Section 3",
    ),
    (
        "Do I need a Data Protection Officer?",
        "Significant Data Fiduciary",
        "DPDPA 2023 Section 10",
    ),
    (
        "What is the penalty if I fail to keep data safe?",
        "Penalties",
        "DPDPA 2023 Section 33 and Schedule",
    ),
    (
        "Can I send personal data outside India?",
        "Cross-border transfer",
        "DPDPA 2023 Section 16",
    ),
)


def _schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def question_id_for(text: str) -> str:
    digest = hashlib.sha256(normalize_question(text).encode("utf-8")).hexdigest()
    return f"QST-{int(digest[:8], 16) % 1_000_000:06d}"


def normalize_question(text: str) -> str:
    if not text or not text.strip():
        raise ValueError("question text is required")
    cleaned = re.sub(r"\s+", " ", text).strip()
    cleaned = re.sub(r"^[\"'`]+|[\"'`]+$", "", cleaned)
    return cleaned


def infer_topic(text: str) -> str:
    blob = text.lower()
    if "consent manager" in blob:
        return "Consent Manager"
    for spec in CANONICAL_TOPICS:
        if any(needle in blob for needle in spec["needles"]):
            return spec["topic"]
    if "data fiduciary" in blob or "processor" in blob:
        return "Data Fiduciary obligations"
    if "personal data" in blob or "dpdpa" in blob or "dpdp" in blob:
        return "Definitions"
    return "General"


def infer_citation(text: str, topic: str) -> str | None:
    sections = extract_sections(text)
    if sections:
        return f"DPDPA 2023 {sections[0]}"
    for spec in CANONICAL_TOPICS:
        if spec["topic"] == topic and spec["primary"]:
            return spec["primary"]
    return None


def infer_audience(text: str, source: str) -> list[str]:
    blob = f"{text} {source}".lower()
    audience: list[str] = []
    if "interview" in blob or "student" in blob or "exam" in blob:
        audience.append("student")
    if "msme" in blob or "small" in blob or "kirana" in blob or "whatsapp" in blob:
        audience.append("business")
    if "principal" in blob or "my data" in blob or "customer asks" in blob:
        audience.append("data principal")
    if "professional" in blob or "dpo" in blob or "sdf" in blob:
        audience.append("privacy professional")
    if not audience:
        audience.append("business")
    return audience


def extract_questions(text: str) -> list[str]:
    if not text:
        return []
    found: list[str] = []
    for pattern in (NUMBERED_Q_RE, QUESTION_RE, MD_H_RE, JS_FAQ_RE):
        found.extend(pattern.findall(text))
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in found:
        question = normalize_question(raw)
        if question.endswith("??"):
            continue
        if len(question) < 12 or len(question) > 180:
            continue
        key = question.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(question)
    return cleaned


def _load_text(path: str) -> str:
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def load_saralprivacy_questions(root: str = REPO_ROOT) -> list[tuple[str, str]]:
    """Return (question, surface) from SaralPrivacy pages we already wrote."""
    rows: list[tuple[str, str]] = []
    home = _load_text(
        os.path.join(root, "deployments", "dpdpa-wiki", "src", "data", "homeContent.js")
    )
    for question in extract_questions(home):
        rows.append((question, "homepage FAQ"))
    guide = _load_text(
        os.path.join(
            root,
            "deployments",
            "dpdpa-wiki",
            "src",
            "content",
            "guides",
            "dpdp-act-explained-indian-msmes.md",
        )
    )
    for question in extract_questions(guide):
        rows.append((question, "MSME guide"))
    for question, _topic, _cite in MSME_CUSTOMER_QUESTIONS:
        rows.append((question, "MSME customer language"))
    return rows


def load_raw_competitor_questions(raw_dir: str) -> list[tuple[str, str]]:
    """Read gitignored crawl bodies for FAQ-style questions only."""
    if not os.path.isdir(raw_dir):
        return []
    rows: list[tuple[str, str]] = []
    for name in sorted(os.listdir(raw_dir)):
        if not name.endswith(".jsonl"):
            continue
        path = os.path.join(raw_dir, name)
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                page = json.loads(line)
                url = str(page.get("url") or "")
                if not url:
                    continue
                path_l = url.lower()
                useful = (
                    "faq" in path_l
                    or "interview-questions" in path_l
                    or page.get("dataset") == "remaining_sitemap"
                )
                if not useful:
                    continue
                markdown = page.get("markdown") or ""
                for question in extract_questions(markdown):
                    rows.append((question, url))
    return rows


def classify_question_gap(they: bool, we: bool) -> str:
    if they and we:
        return "both_ask"
    if they and not we:
        return "they_ask_we_dont"
    if we and not they:
        return "we_ask_they_dont"
    return "customer_gap"


def build_question_universe(
    cards: list[dict[str, Any]],
    raw_dir: str | None = None,
    root: str = REPO_ROOT,
) -> list[dict[str, Any]]:
    """Merge competitor discovery questions with SaralPrivacy customer questions."""
    if not isinstance(cards, list):
        raise ValueError("cards must be a list")

    buckets: dict[str, dict[str, Any]] = {}

    def add(question: str, *, competitor_url: str | None, surface: str | None) -> None:
        text = normalize_question(question)
        key = text.lower()
        topic = infer_topic(text)
        citation = infer_citation(text, topic)
        sections = extract_sections(text)
        rules = extract_rules(text)
        row = buckets.get(key)
        if row is None:
            row = {
                "question_id": question_id_for(text),
                "question_text": text,
                "audience": infer_audience(text, f"{competitor_url or ''} {surface or ''}"),
                "topic": topic,
                "dpdpa_section": sections[0] if sections else None,
                "dpdp_rule": rules[0] if rules else None,
                "asked_on_competitor": False,
                "competitor_urls": [],
                "asked_on_saralprivacy": False,
                "saralprivacy_surfaces": [],
                "primary_citation": citation,
                "gap": "customer_gap",
                "publication_eligible": False,
            }
            buckets[key] = row
        if competitor_url:
            row["asked_on_competitor"] = True
            if competitor_url not in row["competitor_urls"]:
                row["competitor_urls"].append(competitor_url)
        if surface:
            row["asked_on_saralprivacy"] = True
            if surface not in row["saralprivacy_surfaces"]:
                row["saralprivacy_surfaces"].append(surface)
        row["gap"] = classify_question_gap(
            row["asked_on_competitor"], row["asked_on_saralprivacy"]
        )
        if citation and not row["primary_citation"]:
            row["primary_citation"] = citation

    for card in cards:
        url = card.get("source_url") or ""
        blob = "\n".join(
            [
                card.get("title") or "",
                card.get("topic") or "",
                *(c.get("text") or "" for c in card.get("claims") or []),
            ]
        )
        if card.get("content_type") in {"FAQ", "COURSE"} or "faq" in url.lower():
            for question in extract_questions(blob):
                add(question, competitor_url=url, surface=None)

    if raw_dir:
        for question, url in load_raw_competitor_questions(raw_dir):
            add(question, competitor_url=url, surface=None)

    for question, surface in load_saralprivacy_questions(root):
        add(question, competitor_url=None, surface=surface)

    schema = _schema()
    rows = list(buckets.values())
    for row in rows:
        validate(instance=row, schema=schema)
        if row["publication_eligible"] is not False:
            raise ValueError("question universe rows stay unpublished")
    rows.sort(key=lambda item: (item["gap"], item["topic"], item["question_id"]))
    return rows


def question_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["gap"]] = counts.get(row["gap"], 0) + 1
    return {
        "count": len(rows),
        "by_gap": counts,
        "they_ask_we_dont": counts.get("they_ask_we_dont", 0),
        "publication_eligible": False,
        "headline": (
            f"{len(rows)} customer questions collected. "
            f"{counts.get('they_ask_we_dont', 0)} they ask and we do not, "
            f"{counts.get('we_ask_they_dont', 0)} we ask and they do not, "
            f"{counts.get('both_ask', 0)} both already ask."
        ),
    }
