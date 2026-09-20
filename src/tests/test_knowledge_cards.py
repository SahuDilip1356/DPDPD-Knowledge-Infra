from jsonschema import ValidationError
import pytest

from src.competitive_intel.classify_dpdpa_com import (
    authority_level_for,
    classify_dpdpa_com,
    normalize_url,
)
from src.competitive_intel.knowledge_cards import (
    build_card,
    build_cards,
    card_id_for,
    extract_sections,
    is_unusable_page,
)
from src.schemas.validate_knowledge_card import validate_knowledge_card


def test_normalize_collapses_apex_and_index():
    assert normalize_url("https://dpdpa.com/tools/legitimate-interest-tool/index.html") == (
        "https://www.dpdpa.com/tools/legitimate-interest-tool"
    )


def test_classify_trays():
    assert classify_dpdpa_com("https://www.dpdpa.com/dpdpa2023/chapter-2/section6.html") == (
        "INTERPRETATION"
    )
    assert classify_dpdpa_com("https://www.dpdpa.com/dpdparules/rule14.html") == "LAW / RULES"
    assert classify_dpdpa_com("https://www.dpdpa.com/dpdpa-faq.html") == "FAQ"
    assert classify_dpdpa_com("https://www.dpdpa.com/blogs/consentunderdpdpa.html") == "BLOG"
    assert classify_dpdpa_com("https://www.dpdpa.com/templates/consentformfordataprocessingtemplate.html") == (
        "TEMPLATE"
    )
    assert classify_dpdpa_com("https://www.dpdpa.com/dpdpacases/case1/case-d.html") == "CASE LAW"
    assert classify_dpdpa_com("https://www.dpdpa.com/dpdpa-module-2.html") == "COURSE"
    assert classify_dpdpa_com("https://www.dpdpa.com/ccl.html") == "COURSE"
    assert classify_dpdpa_com("https://www.dpdpa.com/dpdpa-faq-comprehensive.html") == "FAQ"
    assert classify_dpdpa_com("https://www.dpdpa.com/dpdpa-faq-comprehensive_1.html") == "FAQ"
    assert classify_dpdpa_com("https://www.dpdpa.com/tools/privacy-notice-generator.html") == "TOOL"
    assert classify_dpdpa_com("https://www.dpdpa.com/") == "COMMERCIAL"


def test_competitor_authority_never_primary():
    assert authority_level_for("INTERPRETATION") == "L4"
    assert authority_level_for("BLOG") == "L5"
    assert authority_level_for("COMMERCIAL") == "L6"


def test_skip_cloudflare_and_404():
    assert is_unusable_page("One moment, please…", "x" * 200) == "cloudflare_interstitial"
    assert is_unusable_page("Page Not Found", "The page you requested" + "x" * 80) == "not_found"


def test_section_from_url_and_text():
    sections = extract_sections(
        "See section 6 and Section 7 of the Act.",
        "https://www.dpdpa.com/dpdpa2023/chapter-2/section6.html",
    )
    assert sections[0] == "Section 6"
    assert "Section 7" in sections


def test_card_is_unpublished_competitor_record():
    card = build_card(
        "https://www.dpdpa.com/dpdpa2023/chapter-2/section6.html",
        "DPDPA SECTION 6 WITH INTERPRETATION",
        (
            "Section 6 says consent shall be free, specific, informed and unambiguous. "
            "Penalties can reach 250 crore under the Act. "
            "For example, a website must show a notice before collecting data. "
            "MeitY published related rules in the Gazette."
        ),
    )
    validate_knowledge_card(card)
    assert card["publication_eligible"] is False
    assert card["verification_required"] is True
    assert card["source_class"] == "COMPETITOR"
    assert card["content_type"] == "INTERPRETATION"
    assert card["topic"] == "Consent"
    faq = build_card(
        "https://www.dpdpa.com/dpdpa-faq.html",
        "125+ DPDPA FAQ",
        "What is consent? A Data Fiduciary shall obtain consent before processing personal data. "
        "This FAQ page lists more than one hundred questions for businesses.",
    )
    assert faq["topic"] == "FAQ universe"
    assert "Section 6" in card["dpdpa_sections"]
    assert card["claims"]
    assert "MeitY" in card["primary_sources_cited"]


def test_duplicate_faq_copy_is_flagged():
    card = build_card(
        "https://www.dpdpa.com/dpdpa-faq-comprehensive_1.html",
        "DPDPA FAQ copy",
        "What is consent? A Data Fiduciary shall obtain consent before processing personal data. "
        "This FAQ hub lists categories and points at the main FAQ.",
    )
    assert card["content_type"] == "FAQ"
    assert card["publication_eligible"] is False
    assert "Duplicate FAQ hub" in (card.get("notes") or "")


def test_validator_rejects_publication():
    card = build_card(
        "https://www.dpdpa.com/dpdpa-faq.html",
        "125+ DPDPA FAQ",
        "What is consent? A Data Fiduciary shall obtain consent before processing personal data. "
        "This FAQ page lists more than one hundred questions for businesses.",
    )
    card["publication_eligible"] = True
    with pytest.raises(ValidationError):
        validate_knowledge_card(card)


def test_merge_keeps_longest_markdown():
    pages = [
        {
            "url": "https://dpdpa.com/blogs/consentunderdpdpa.html",
            "title": "Consent",
            "markdown": "short consent text " + "x" * 80,
        },
        {
            "url": "https://www.dpdpa.com/blogs/consentunderdpdpa.html",
            "title": "Consent under DPDPA",
            "markdown": "Consent shall be informed. " * 20,
        },
    ]
    cards, skipped = build_cards(pages)
    assert skipped == {}
    assert len(cards) == 1
    assert cards[0]["source_url"] == "https://www.dpdpa.com/blogs/consentunderdpdpa.html"
    assert cards[0]["card_id"] == card_id_for(cards[0]["source_url"])
