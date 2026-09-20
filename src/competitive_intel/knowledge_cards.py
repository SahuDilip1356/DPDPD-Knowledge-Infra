"""Build unpublished Knowledge Cards from competitor page text."""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

from src.competitive_intel.classify_dpdpa_com import (
    authority_level_for,
    classify_dpdpa_com,
    normalize_url,
)
from src.schemas.validate_knowledge_card import validate_knowledge_card

SECTION_TOPICS = {
    1: "Short title and commencement",
    2: "Definitions",
    3: "Application",
    4: "Grounds for processing",
    5: "Notice",
    6: "Consent",
    7: "Legitimate uses",
    8: "Data Fiduciary obligations",
    9: "Children and persons with disability",
    10: "Significant Data Fiduciary",
    11: "Right to access",
    12: "Right to correction and erasure",
    13: "Right of grievance redressal",
    14: "Right to nominate",
    15: "Duties of Data Principal",
    16: "Processing outside India",
    17: "Exemptions",
    18: "Data Protection Board",
    33: "Penalties",
}

RULE_TOPICS = {
    7: "Personal data breach",
    10: "Verifiable consent of parent",
    13: "Significant Data Fiduciary obligations",
    14: "Rights of Data Principals",
    15: "Transfer outside India",
}

CLAIM_HINTS = re.compile(
    r"\b(shall|must|penalty|penalties|crore|consent|notice|breach|"
    r"fiduciary|legitimate use|data principal|section|rule)\b",
    re.I,
)
STAT_RE = re.compile(
    r"(₹\s?[\d,]+(?:\s*(?:crore|lakh))?|"
    r"\b\d{1,3}\s*crore\b|"
    r"\b72[\s-]*hours?\b|"
    r"\b18[\s-]*months?\b|"
    r"\bMay\s+2027\b|"
    r"\b125\+?\b)",
    re.I,
)
SECTION_RE = re.compile(r"\b(?:section|sec\.?)\s*([0-9]{1,2})\b", re.I)
RULE_RE = re.compile(r"\brule\s*([0-9]{1,2})\b", re.I)
SENTENCE_RE = re.compile(r"[^.!?\n]{20,220}[.!?]")

PRIMARY_SOURCE_HINTS = (
    ("gazette", "Gazette of India"),
    ("egazette", "eGazette"),
    ("meity", "MeitY"),
    ("india code", "India Code"),
    ("puttaswamy", "K.S. Puttaswamy"),
    ("dpbi", "Data Protection Board of India"),
)

TOOL_HINTS = (
    ("privacy notice generator", "Privacy Notice Generator"),
    ("legitimate interest", "Legitimate Interest Assessment"),
    ("consent manager", "Consent Manager"),
    ("cmp", "Consent Management Platform"),
    ("quiz", "DPDPA Quiz"),
)


def _clean_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def is_unusable_page(title: str, markdown: str) -> str | None:
    """Return a skip reason, or None if the page can become a card."""
    title_l = (title or "").lower()
    md = markdown or ""
    if "one moment" in title_l or "one moment, please" in md.lower()[:200]:
        return "cloudflare_interstitial"
    if "page not found" in title_l:
        return "not_found"
    if "www.prashantmali.com" in title_l.lower() or "prashantmali" in (title or ""):
        return "junk_link"
    if len(_clean_space(md)) < 80:
        return "too_thin"
    return None


def _unique_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def extract_sections(text: str, url: str = "") -> list[str]:
    found = [int(n) for n in SECTION_RE.findall(text or "") if 1 <= int(n) <= 44]
    path_match = re.search(r"/section(\d+)\.html", url or "", re.I)
    if path_match:
        found.insert(0, int(path_match.group(1)))
    return [f"Section {n}" for n in _unique_keep_order([str(n) for n in found])]


def extract_rules(text: str, url: str = "") -> list[str]:
    found = [int(n) for n in RULE_RE.findall(text or "") if 1 <= int(n) <= 23]
    path_match = re.search(r"/rule(\d+)\.html", url or "", re.I)
    if path_match:
        found.insert(0, int(path_match.group(1)))
    return [f"Rule {n}" for n in _unique_keep_order([str(n) for n in found])]


def infer_topic(title: str, url: str, content_type: str, sections: list[str]) -> str:
    path = normalize_url(url)
    if content_type == "FAQ":
        return "FAQ universe"
    if content_type == "TEMPLATE":
        cleaned = re.sub(r"\s*template\s*$", "", title, flags=re.I).strip()
        return cleaned or "Template catalogue"
    if content_type == "COURSE":
        return title.split("|")[0].strip() or "Course"
    if content_type == "CASE LAW":
        return title.split("|")[0].strip() or "Case law"
    if content_type == "TOOL":
        return title.split("|")[0].strip() or "Interactive tool"
    if content_type == "COMMERCIAL":
        return "Site marketing"
    if sections:
        number = int(sections[0].split()[1])
        mapped = SECTION_TOPICS.get(number)
        if mapped:
            return mapped
    if content_type == "LAW / RULES":
        rule_match = re.search(r"/rule(\d+)\.html", path, re.I)
        if rule_match:
            number = int(rule_match.group(1))
            return RULE_TOPICS.get(number, f"Rule {number}")
    cleaned = re.sub(r"\s+WITH INTERPRETATION.*$", "", title, flags=re.I)
    cleaned = re.sub(r"\s*\|\s*DPDPA\.com.*$", "", cleaned, flags=re.I)
    cleaned = _clean_space(cleaned)
    if cleaned:
        return cleaned[:80]
    return os.path.basename(path).replace(".html", "").replace("_", " ")


def infer_subtopics(title: str, markdown: str, content_type: str) -> list[str]:
    blob = f"{title}\n{markdown[:4000]}".lower()
    catalog = [
        ("consent", "consent"),
        ("withdraw", "withdrawal"),
        ("notice", "notice"),
        ("legitimate use", "legitimate use"),
        ("child", "children"),
        ("breach", "breach"),
        ("erasure", "erasure"),
        ("nominate", "nomination"),
        ("cross-border", "cross-border transfer"),
        ("transfer", "cross-border transfer"),
        ("significant data fiduciary", "SDF"),
        ("dpi a", "DPIA"),
        ("dpia", "DPIA"),
        ("consent manager", "consent manager"),
        ("whatsapp", "WhatsApp"),
        ("ai ", "AI"),
        ("penalty", "penalties"),
        ("retention", "retention"),
        ("vendor", "vendor / processor"),
        ("employee", "employee data"),
        ("cookie", "cookies"),
    ]
    found = [label for needle, label in catalog if needle in blob]
    if content_type == "TEMPLATE" and "policy" in blob:
        found.append("policy catalogue")
    return _unique_keep_order(found)[:8]


def infer_audience(content_type: str, markdown: str) -> list[str]:
    blob = (markdown or "").lower()
    audience: list[str] = []
    if content_type in {"COURSE", "FAQ"} or "interview" in blob:
        audience.append("student")
    if content_type in {"TEMPLATE", "TOOL", "LAW / RULES", "BLOG", "INTERPRETATION"}:
        audience.append("business")
    if content_type in {"INTERPRETATION", "LAW / RULES", "CASE LAW", "BLOG", "COURSE"}:
        audience.append("privacy professional")
    if "data principal" in blob and content_type == "FAQ":
        audience.append("data principal")
    if not audience:
        audience.append("business")
    return _unique_keep_order(audience)


def extract_statistics(text: str) -> list[str]:
    return _unique_keep_order(m.group(0).strip() for m in STAT_RE.finditer(text or ""))[:8]


def extract_primary_sources(text: str) -> list[str]:
    blob = (text or "").lower()
    return [label for needle, label in PRIMARY_SOURCE_HINTS if needle in blob]


def extract_tools_mentioned(text: str) -> list[str]:
    blob = (text or "").lower()
    return [label for needle, label in TOOL_HINTS if needle in blob]


def extract_claims(markdown: str) -> list[dict[str, str]]:
    claims: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in SENTENCE_RE.findall(markdown or ""):
        sentence = _clean_space(raw)
        if len(sentence) < 24 or not CLAIM_HINTS.search(sentence):
            continue
        if sentence.lower() in seen:
            continue
        if sentence.lower().startswith(("click ", "subscribe", "copyright")):
            continue
        if not sentence[0].isupper() and sentence[0] not in {'"', "'"}:
            continue
        if re.search(r"free .*template|\|\s*dpdpa", sentence, re.I):
            continue
        seen.add(sentence.lower())
        claim_type = "OPINION"
        if STAT_RE.search(sentence):
            claim_type = "STATISTIC"
        elif re.search(r"\b(shall|must|penalty|section|rule)\b", sentence, re.I):
            claim_type = "LEGAL"
        claims.append({"text": sentence[:220], "claim_type": claim_type})
        if len(claims) >= 8:
            break
    return claims


def extract_examples(markdown: str) -> list[str]:
    examples: list[str] = []
    for raw in SENTENCE_RE.findall(markdown or ""):
        sentence = _clean_space(raw)
        if re.search(r"\b(for example|e\.g\.|such as)\b", sentence, re.I):
            examples.append(sentence[:180])
        if len(examples) >= 3:
            break
    return examples


def card_id_for(url: str) -> str:
    digest = hashlib.sha256(normalize_url(url).encode("utf-8")).hexdigest()
    return f"KC-DPDPA-COM-{int(digest[:8], 16) % 1_000_000:06d}"


def build_card(url: str, title: str, markdown: str) -> dict[str, Any]:
    """Turn one competitor page into an unpublished Knowledge Card."""
    if not url:
        raise ValueError("url is required")
    skip = is_unusable_page(title, markdown)
    if skip:
        raise ValueError(skip)

    normalized = normalize_url(url)
    content_type = classify_dpdpa_com(normalized, title)
    combined = f"{title}\n{markdown}"
    sections = extract_sections(combined, normalized)
    rules = extract_rules(combined, normalized)
    topic = infer_topic(title or "Untitled page", normalized, content_type, sections)
    notes = []
    if re.search(r"/chapter\d+\.html$", normalized):
        notes.append("Thin chapter hub.")
    if "faq-comprehensive_1" in normalized:
        notes.append(
            "Duplicate FAQ hub. Same HTML as dpdpa-faq-comprehensive.html. "
            "Canonical points at dpdpa-faq.html. robots.txt Disallowed; fetched on request."
        )
    if content_type in {"TEMPLATE", "COURSE", "TOOL"}:
        notes.append("Tier B product intelligence. Do not reproduce the offering.")
    if "controller" in (markdown or "").lower():
        notes.append("Page uses Controller language. Verify against Data Fiduciary.")

    card = {
        "card_id": card_id_for(normalized),
        "source": "DPDPA.com",
        "source_class": "COMPETITOR",
        "source_url": normalized,
        "content_type": content_type,
        "title": _clean_space(title)[:240] or topic,
        "topic": topic,
        "subtopics": infer_subtopics(title, markdown, content_type),
        "dpdpa_sections": sections[:12],
        "dpdp_rules": rules[:12],
        "audience": infer_audience(content_type, markdown),
        "claims": extract_claims(markdown),
        "statistics": extract_statistics(combined),
        "examples": extract_examples(markdown),
        "tools_mentioned": extract_tools_mentioned(combined),
        "primary_sources_cited": extract_primary_sources(combined),
        "verification_required": True,
        "authority_level": authority_level_for(content_type),
        "publication_eligible": False,
    }
    if notes:
        card["notes"] = " ".join(notes)
    validate_knowledge_card(card)
    return card


def merge_raw_pages(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate by URL, keeping the longest markdown."""
    best: dict[str, dict[str, Any]] = {}
    for page in pages:
        url = page.get("url")
        if not url:
            raise ValueError("each page needs a url")
        try:
            key = normalize_url(str(url))
        except ValueError:
            continue
        current = best.get(key)
        md = page.get("markdown") or ""
        if current is None or len(md) > len(current.get("markdown") or ""):
            best[key] = {
                "url": key,
                "title": page.get("title") or "",
                "markdown": md,
            }
    return list(best.values())


def build_cards(pages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Build validated cards and a skip tally."""
    skipped: dict[str, int] = {}
    cards: list[dict[str, Any]] = []
    for page in merge_raw_pages(pages):
        try:
            cards.append(build_card(page["url"], page["title"], page["markdown"]))
        except ValueError as exc:
            reason = str(exc)
            skipped[reason] = skipped.get(reason, 0) + 1
    cards.sort(key=lambda card: (card["content_type"], card["source_url"]))
    ids = [card["card_id"] for card in cards]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate Knowledge Card ids after extract")
    return cards, skipped


def write_card_export(cards: list[dict[str, Any]], out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    jsonl_path = os.path.join(out_dir, "knowledge_cards.jsonl")
    json_path = os.path.join(out_dir, "knowledge_cards.json")
    summary_path = os.path.join(out_dir, "summary.json")
    with open(jsonl_path, "w", encoding="utf-8") as handle:
        for card in cards:
            handle.write(json.dumps(card, ensure_ascii=True) + "\n")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(cards, handle, indent=2, ensure_ascii=True)
        handle.write("\n")
    counts: dict[str, int] = {}
    for card in cards:
        counts[card["content_type"]] = counts.get(card["content_type"], 0) + 1
        if card["publication_eligible"] is not False:
            raise ValueError("refusing to export a publication-eligible competitor card")
    summary = {
        "source": "DPDPA.com",
        "source_class": "COMPETITOR",
        "card_count": len(cards),
        "publication_eligible": False,
        "by_content_type": counts,
        "cards_with_claims": sum(1 for card in cards if card["claims"]),
        "cards_citing_primary": sum(1 for card in cards if card["primary_sources_cited"]),
    }
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
