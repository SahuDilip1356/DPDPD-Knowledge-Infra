import pytest
from jsonschema import ValidationError
from src.schemas.validate_schema import validate_ko

# Helper to construct a valid base dictionary
def get_valid_ko() -> dict:
    return {
        "urn": "urn:ki:in:dpdp:norm:notice-requirement",
        "title": "Consent Notice Requirement",
        "source": {
            "name": "DPDP Rules 2026 Gazette",
            "layer": 1,
            "url": "https://egazette.gov.in/rules.pdf",
            "hash": "a" * 64
        },
        "date": "2026-07-23",
        "version": 1,
        "summary": "This object mandates that notice must be provided in multiple languages before consent.",
        "entities": ["Rule", "Consent", "Organization"],
        "evidence": [
          {
            "source_urn": "urn:ki:in:dpdp:source:gazette-rules",
            "citation_text": "Page 4, Rule 3(2)",
            "coordinates": {
              "page": 4,
              "section": "3(2)",
              "hash": "b" * 64
            }
          }
        ],
        "business_impact": {
          "impact_summary": "Notice prompts must be updated on mobile and web forms.",
          "affected_actors": ["Data Fiduciary"],
          "action_required": "Deploy updated notice checkbox prompts."
        },
        "confidence_score": 1.0,
        "relations": [
          {
            "target_urn": "urn:ki:in:dpdp:act:sec-6",
            "edge_type": "Implements"
          }
        ],
        "linked_objects": ["urn:ki:in:dpdp:act:sec-6"],
        "history": [
          {
            "version": 1,
            "system_time": "2026-07-23T21:05:00Z",
            "commit_message": "initial commit",
            "author_id": "publishing_agent"
          }
        ]
    }

def test_valid_ko_passes():
    ko = get_valid_ko()
    # Should not raise any exceptions
    validate_ko(ko)

def test_missing_required_field_fails():
    ko = get_valid_ko()
    del ko["evidence"]
    with pytest.raises(ValidationError) as exc_info:
        validate_ko(ko)
    assert "'evidence' is a required property" in str(exc_info.value)

def test_invalid_urn_format_fails():
    ko = get_valid_ko()
    ko["urn"] = "invalid-urn-without-prefix"
    with pytest.raises(ValidationError):
        validate_ko(ko)

def test_invalid_source_layer_fails():
    ko = get_valid_ko()
    ko["source"]["layer"] = 9 # Layer can only be 1 to 8
    with pytest.raises(ValidationError):
        validate_ko(ko)

def test_invalid_entity_type_fails():
    ko = get_valid_ko()
    ko["entities"].append("NonConstitutionalNoun")
    with pytest.raises(ValidationError):
        validate_ko(ko)

def test_invalid_relation_verb_fails():
    ko = get_valid_ko()
    ko["relations"][0]["edge_type"] = "NonConstitutionalVerb"
    with pytest.raises(ValidationError):
        validate_ko(ko)
