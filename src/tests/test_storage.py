import os
import shutil
import pytest
from datetime import datetime
from src.storage.git_ledger import GitLedger
from src.storage.db_client import DatabaseClient

TEMP_LEDGER_DIR = os.path.abspath("src/tests/temp_ledger")

# Base mock KO
def get_mock_ko(version: int, date: str) -> dict:
    return {
        "urn": "urn:ki:in:dpdp:rule:notice-test",
        "type": "rule", # Added required schema field
        "title": f"Notice Rules - Version {version}",
        "source": {
            "name": "DPDP Rules Gazette",
            "layer": 1,
            "url": "https://egazette.gov.in/rules.pdf",
            "hash": "c" * 64
        },
        "date": date,
        "version": version,
        "summary": f"This is mock version {version} of the notice rules obligation.",
        "entities": ["Rule", "Consent", "Organization"],
        "evidence": [
          {
            "source_urn": "urn:ki:in:dpdp:source:gazette",
            "citation_text": "Page 1, Rule 1",
            "coordinates": {
              "page": 1,
              "section": "1",
              "hash": "d" * 64
            }
          }
        ],
        "business_impact": {
          "impact_summary": f"Mock business impact for version {version}.",
          "affected_actors": ["Data Fiduciary"],
          "action_required": "Do the mock action."
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
            "version": version,
            "system_time": "2026-07-23T21:05:00Z",
            "commit_message": f"commit version {version}",
            "author_id": "test_agent"
          }
        ]
    }

@pytest.fixture
def clean_ledger():
    if os.path.exists(TEMP_LEDGER_DIR):
        shutil.rmtree(TEMP_LEDGER_DIR)
    yield GitLedger(TEMP_LEDGER_DIR)
    if os.path.exists(TEMP_LEDGER_DIR):
        shutil.rmtree(TEMP_LEDGER_DIR)

def test_git_ledger_write_and_read(clean_ledger):
    ko = get_mock_ko(1, "2026-07-23")
    filepath = clean_ledger.write_ko(ko)
    
    # 1. Verify file was physically written
    assert os.path.exists(filepath)
    # Corrected notice-test folder (hyphen matched)
    assert filepath.endswith("objects/in/dpdp/rule/notice-test/v1.json")
    
    # 2. Verify reading works
    read_data = clean_ledger.read_ko(ko["urn"], version=1)
    assert read_data["title"] == "Notice Rules - Version 1"
    assert read_data["version"] == 1

def test_db_client_bi_temporal_supersession():
    db = DatabaseClient("sqlite:///:memory:")
    
    # Timeline offsets
    t1 = datetime(2026, 1, 1, 12, 0, 0)
    t2 = datetime(2026, 1, 2, 12, 0, 0)
    
    # 1. Publish Version 1 (Valid legally from Jan 1, 2026) at transaction time t1
    ko_v1 = get_mock_ko(1, "2026-01-01")
    db.publish_ko(ko_v1, system_time=t1)
    
    # Query at t1 should return version 1
    res = db.get_ko_at_time("urn:ki:in:dpdp:rule:notice-test", system_time=t1, legal_time=datetime(2026, 1, 1, 13, 0))
    assert res is not None
    assert res.version == 1
    assert res.title == "Notice Rules - Version 1"
    
    # 2. Publish Version 2 (Valid legally from Jan 2, 2026) at transaction time t2
    ko_v2 = get_mock_ko(2, "2026-01-02")
    db.publish_ko(ko_v2, system_time=t2)
    
    # Query at t2 (system time) for legal date Jan 2 should return version 2
    res_latest = db.get_ko_at_time("urn:ki:in:dpdp:rule:notice-test", system_time=t2, legal_time=datetime(2026, 1, 2, 13, 0))
    assert res_latest is not None
    assert res_latest.version == 2
    assert res_latest.title == "Notice Rules - Version 2"
    
    # Query historically at t1 (system time) for legal date Jan 1 should still return version 1
    res_hist = db.get_ko_at_time("urn:ki:in:dpdp:rule:notice-test", system_time=t1, legal_time=datetime(2026, 1, 1, 13, 0))
    assert res_hist is not None
    assert res_hist.version == 1
    assert res_hist.title == "Notice Rules - Version 1"

def test_db_client_relations():
    db = DatabaseClient("sqlite:///:memory:")
    ko = get_mock_ko(1, "2026-07-23")
    db.publish_ko(ko)
    
    edges = db.get_relations(ko["urn"], version=1)
    assert len(edges) == 1
    assert edges[0].target_urn == "urn:ki:in:dpdp:act:sec-6"
    assert edges[0].edge_type == "Implements"
