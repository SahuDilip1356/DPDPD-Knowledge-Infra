from src.competitive_intel.content_gap import build_content_gaps
from src.competitive_intel.html_to_markdown import html_to_markdown
from src.competitive_intel.legal_review import build_counsel_queue
from src.competitive_intel.primary_facts import is_denial_of
from src.competitive_intel.question_universe import (
    build_question_universe,
    classify_question_gap,
    extract_questions,
    normalize_question,
)
from src.competitive_intel.source_truth import judge_claim
from src.competitive_intel.topic_matrix import build_topic_matrix
import re


def test_extracts_numbered_and_plain_questions():
    text = (
        "1 What is a Data Fiduciary?\n"
        "How can a Data Principal withdraw consent?\n"
        "Not a question at all."
    )
    questions = extract_questions(text)
    assert any("Data Fiduciary" in item for item in questions)
    assert any("withdraw consent" in item for item in questions)


def test_gap_labels_for_questions():
    assert classify_question_gap(True, True) == "both_ask"
    assert classify_question_gap(True, False) == "they_ask_we_dont"
    assert classify_question_gap(False, True) == "we_ask_they_dont"


def test_universe_stays_unpublished_and_merges_surfaces():
    cards = [
        {
            "content_type": "FAQ",
            "title": "FAQ",
            "topic": "FAQ universe",
            "source_url": "https://www.dpdpa.com/dpdpa-faq.html",
            "claims": [
                {"text": "What is a Consent Manager?", "claim_type": "OPINION"}
            ],
        }
    ]
    rows = build_question_universe(cards, raw_dir=None)
    assert rows
    assert all(row["publication_eligible"] is False for row in rows)
    assert any(row["asked_on_saralprivacy"] for row in rows)


def test_briefs_never_cite_competitor():
    cards = [
        {
            "title": "WhatsApp and DPDPA",
            "topic": "WhatsApp",
            "subtopics": ["whatsapp"],
            "source_url": "https://www.dpdpa.com/blogs/whatsapp.html",
        }
    ]
    matrix = build_topic_matrix(cards, saral_blob="consent notice whatsapp recruitment")
    questions = [
        {
            "question_id": "QST-000001",
            "question_text": "Can I keep numbers on WhatsApp?",
            "topic": "WhatsApp",
            "gap": "they_ask_we_dont",
            "competitor_urls": ["https://www.dpdpa.com/blogs/whatsapp.html"],
            "primary_citation": "DPDPA 2023 Section 8",
        }
    ]
    briefs = build_content_gaps(matrix, questions)
    assert briefs
    assert all("DPDPA.com" in brief["never_cite"] for brief in briefs)
    assert all(brief["publication_eligible"] is False for brief in briefs)
    assert any("WhatsApp" in brief["title"] for brief in briefs)


def test_denial_of_legitimate_interest_is_not_incorrect():
    verdict = judge_claim(
        "There is no open-textured legitimate interests balancing clause.",
        "LEGAL",
    )
    assert verdict["verification_status"] != "INCORRECT"
    assert verdict["publication_allowed"] is False


def test_denial_of_rtbf_is_not_contested():
    verdict = judge_claim(
        "DPDPA has no statutory right to be forgotten as such — only erasure under Section 12.",
        "LEGAL",
    )
    assert verdict["verification_status"] != "CONTESTED"


def test_localisation_myth_is_incorrect():
    verdict = judge_claim(
        "You must maintain India-only datacenters for this information.",
        "LEGAL",
    )
    assert verdict["verification_status"] == "INCORRECT"


def test_counsel_queue_excludes_verified_rows():
    claims = [
        {
            "claim_id": "CLM-000001",
            "claim_text": "Needs a lawyer.",
            "verification_status": "NEEDS_REVIEW",
            "confidence": 0.3,
            "verdict_note": "No catalog match.",
            "original_url": "https://www.dpdpa.com/dpdpa-faq.html",
            "counsel_signed": False,
        },
        {
            "claim_id": "CLM-000002",
            "claim_text": "Consent must be free and specific.",
            "verification_status": "VERIFIED_PRIMARY",
            "confidence": 0.9,
            "verdict_note": "Section 6",
            "original_url": "https://www.dpdpa.com/dpdpa-faq.html",
            "counsel_signed": False,
        },
    ]
    queue = build_counsel_queue(claims)
    assert [row["claim_id"] for row in queue] == ["CLM-000001"]
    assert queue[0]["counsel_signed"] is False


def test_html_to_markdown_keeps_headings_and_jsonld():
    html = """
    <html><head><title>x</title>
    <script type="application/ld+json">
    {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":"What is consent?"}]}
    </script></head>
    <body><h1>FAQ</h1><p>A short page about consent under the Act.</p></body></html>
    """
    markdown = html_to_markdown(html)
    assert "# FAQ" in markdown
    assert "What is consent?" in markdown


def test_is_denial_helper():
    pattern = re.compile(r"legitimate interest", re.I)
    text = "There is no legitimate interest ground in the Act."
    match = pattern.search(text)
    assert match is not None
    assert is_denial_of(text, match) is True
    text2 = "Organizations can rely on legitimate interest."
    match2 = pattern.search(text2)
    assert match2 is not None
    assert is_denial_of(text2, match2) is False


def test_normalize_rejects_empty():
    try:
        normalize_question("   ")
    except ValueError as exc:
        assert "required" in str(exc)
    else:
        raise AssertionError("empty question should fail")
