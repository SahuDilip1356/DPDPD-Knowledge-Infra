"""
Test Suite — Sprint 6: API Gateway & Grounded Reasoning Engine

Tests the GroundedReasoningEngine and FastAPI endpoints (health, query, object lookup, diff).
"""

import os
import sys

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Use a file-based SQLite database for tests to share data across FastAPI routing threads safely
TEST_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_api.db"))
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.api.api_service import app, db_client, reasoning_engine
reasoning_engine.model_client = None
db_client.supabase = None
if reasoning_engine.db_client:
    reasoning_engine.db_client.supabase = None
from src.tests.test_reasoning_pipeline import make_ko


client = TestClient(app)


# ─── Setup Test Data ─────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def cleanup_db_file():
    yield
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass


@pytest.fixture(autouse=True)
def setup_test_db():
    """
    Cleans database tables and populates them with sample KOs before each test.
    """
    session = db_client.Session()
    try:
        from src.storage.models import Base
        # Recreate tables in sqlite memory db
        Base.metadata.drop_all(db_client.engine)
        Base.metadata.create_all(db_client.engine)
        
        # Populate with mock objects
        ko1 = make_ko(
            urn="urn:ki:in:dpdp:act:dpdpa-2023",
            title="Digital Personal Data Protection Act 2023",
            entities=["Act", "Consent", "Purpose"],
            summary="This Act governs the processing of digital personal data in India.",
            confidence=0.95
        )
        ko2 = make_ko(
            urn="urn:ki:in:dpdp:rule:consent-notice",
            title="Consent Notice Rules 2024",
            entities=["Rule", "Consent"],
            summary="Notice of consent must list all data items collected.",
            confidence=0.85
        )
        # Establish relationship
        ko2["relations"] = [
            {"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}
        ]
        
        db_client.publish_ko(ko1, system_time=datetime.utcnow() - timedelta(hours=2))
        db_client.publish_ko(ko2, system_time=datetime.utcnow() - timedelta(hours=1))
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════════════════
# REASONING ENGINE TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestGroundedReasoningEngine:

    def test_retrieve_context_match(self):
        """Should find relevant KO by keyword match in query."""
        results = reasoning_engine.retrieve_context("Notice rules")
        assert len(results) >= 1
        assert any("consent-notice" in r["urn"] for r in results)

    def test_retrieve_context_no_match(self):
        """Should return empty list for unrelated terms."""
        results = reasoning_engine.retrieve_context("Quantum Cryptography")
        assert len(results) == 0

    def test_query_grounded_response(self):
        """Should return cited and grounded answer for valid query."""
        res = reasoning_engine.query("Notice requirements")
        assert res["grounded"] is True
        assert "consent-notice" in res["answer"]
        assert len(res["citations"]) > 0
        assert res["citations"][0]["urn"] == "urn:ki:in:dpdp:rule:consent-notice"

    def test_query_ungrounded_fallback(self):
        """Should fall back with warning message for unresolvable query."""
        res = reasoning_engine.query("Nuclear energy regulations")
        assert res["grounded"] is False
        assert "INSUFFICIENT_EVIDENCE" in res["answer"]
        assert len(res["citations"]) == 0


# ═══════════════════════════════════════════════════════════════════════════
# API GATEWAY ENDPOINT TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestApiGateway:

    def test_health_endpoint(self):
        """GET /health should return 200 and state HEALTHY."""
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "HEALTHY"

    def test_query_endpoint_grounded(self):
        """POST /knowledge/query should return grounded response with citations."""
        res = client.post("/knowledge/query", json={"query": "consent notice"})
        assert res.status_code == 200
        data = res.json()
        assert data["grounded"] is True
        assert len(data["citations"]) > 0

    def test_query_endpoint_ungrounded(self):
        """POST /knowledge/query should return ungrounded result for random search."""
        res = client.post("/knowledge/query", json={"query": "artificial general intelligence"})
        assert res.status_code == 200
        data = res.json()
        assert data["grounded"] is False
        assert "INSUFFICIENT_EVIDENCE" in data["answer"]

    def test_get_object_latest(self):
        """GET /knowledge/objects/{urn} should fetch correct KO model."""
        res = client.get("/knowledge/objects/urn:ki:in:dpdp:rule:consent-notice")
        assert res.status_code == 200
        data = res.json()
        assert data["urn"] == "urn:ki:in:dpdp:rule:consent-notice"
        assert len(data["relations"]) == 1
        assert data["relations"][0]["target_urn"] == "urn:ki:in:dpdp:act:dpdpa-2023"

    def test_get_object_not_found(self):
        """GET /knowledge/objects/{urn} should return 404 for unknown URN."""
        res = client.get("/knowledge/objects/urn:ki:in:dpdp:act:missing")
        assert res.status_code == 404

    def test_get_graph_diff(self):
        """GET /knowledge/graph/diff should list updates since timestamp."""
        # Query changes since 1.5 hours ago (should find consent-notice only)
        since = (datetime.utcnow() - timedelta(minutes=90)).isoformat()
        res = client.get(f"/knowledge/graph/diff?since_timestamp={since}")
        assert res.status_code == 200
        data = res.json()
        assert data["updates_count"] == 1
        assert data["updates"][0]["urn"] == "urn:ki:in:dpdp:rule:consent-notice"
