from src.competitive_intel.source_truth import judge_claim, register_claims
from src.competitive_intel.topic_matrix import build_topic_matrix, classify_gap


def test_penalty_claim_is_verified_primary():
    verdict = judge_claim(
        "DPDPA penalties can reach ₹250 crore for failure of security safeguards.",
        "LEGAL",
    )
    assert verdict["verification_status"] == "VERIFIED_PRIMARY"
    assert verdict["publication_allowed"] is True
    assert "Schedule" in (verdict["primary_source"] or "")


def test_controller_language_is_contested():
    verdict = judge_claim("The Controller must notify the Board.", "LEGAL")
    assert verdict["verification_status"] == "CONTESTED"
    assert verdict["publication_allowed"] is False


def test_legitimate_interest_is_incorrect():
    verdict = judge_claim("DPDPA allows processing on legitimate interest.", "LEGAL")
    assert verdict["verification_status"] == "INCORRECT"
    assert verdict["publication_allowed"] is False


def test_unknown_opinion_needs_review_or_unsupported():
    verdict = judge_claim("This is the ultimate resource for every business.", "OPINION")
    assert verdict["verification_status"] in {"UNSUPPORTED", "NEEDS_REVIEW"}
    assert verdict["publication_allowed"] is False


def test_register_claims_keeps_source_as_competitor():
    cards = [
        {
            "card_id": "KC-DPDPA-COM-000001",
            "source_url": "https://www.dpdpa.com/dpdpa-faq.html",
            "dpdpa_sections": ["Section 6"],
            "dpdp_rules": [],
            "claims": [
                {"text": "Consent must be free, specific, informed and unambiguous.", "claim_type": "LEGAL"}
            ],
        }
    ]
    rows = register_claims(cards)
    assert len(rows) == 1
    assert rows[0]["found_on"] == "DPDPA.com"
    assert rows[0]["verification_status"] == "VERIFIED_PRIMARY"


def test_gap_labels():
    assert classify_gap("yes", "yes", "yes", True) == "none"
    assert classify_gap("yes", "no", "no", False) == "investigate"
    assert classify_gap("generic", "yes", "yes", True) == "sp_advantage"
    assert classify_gap("no", "yes", "no", True) == "sp_advantage"


def test_topic_matrix_consent_is_covered_both_sides():
    cards = [
        {
            "title": "Consent under DPDPA",
            "topic": "Consent",
            "subtopics": ["consent", "withdrawal"],
            "source_url": "https://www.dpdpa.com/blogs/consentunderdpdpa.html",
        }
    ]
    rows = build_topic_matrix(cards, saral_blob="consent notice children whatsapp recruitment")
    consent = next(row for row in rows if row["topic"] == "Consent")
    assert consent["dpdpa_com"] != "no"
    assert consent["saralprivacy"] == "yes"
    assert consent["publication_eligible"] is False
