"""
Test Suite — Groundedness Flag & Structured Output Verification (E1 & E2)

Verifies:
1. Natural-language refusal correctly marks grounded: False.
2. Literal token presence in a grounded answer does NOT cause false-negative refusal.
3. Malformed JSON fails closed with grounded: False and raw output preserved.
4. Fabricated citations are stripped and confined to retrieved URNs.
5. Input guardrails immediately refuse out-of-scope queries.
"""

import pytest
from src.reasoning.reasoning_engine import GroundedReasoningEngine
from src.reasoning.model_client import MockModelClient
from src.tests.test_reasoning_pipeline import make_ko

@pytest.fixture
def mock_db_with_kos():
    class DummyDB:
        def __init__(self):
            self.supabase = None
            self.sample_ko = make_ko(
                urn="urn:ki:in:dpdp:act:dpdpa-2023",
                title="Digital Personal Data Protection Act 2023",
                entities=["Act", "Penalty"],
                summary="Section 33 sets penalties up to 250 crore for failure to take security safeguards.",
                confidence=0.95
            )
            
        def retrieve_context(self, query):
            return [self.sample_ko]
    return DummyDB()


def test_natural_language_refusal(mock_db_with_kos):
    """Model declines in natural language -> grounded: False."""
    client = MockModelClient({
        "User Query:": {
            "answer": "I don't have sufficient evidence in the regulatory corpus to answer this query.",
            "cited_urns": [],
            "sufficient_evidence": False
        }
    })
    engine = GroundedReasoningEngine(model_client=client)
    # Bypass retrieval to test prompt & answer resolution
    engine.retrieve_context = lambda q: [mock_db_with_kos.sample_ko]
    
    res = engine.query("What is the penalty for breach?")
    assert res["grounded"] is False
    assert len(res["citations"]) == 0
    assert "don't have sufficient evidence" in res["answer"]


def test_literal_token_in_grounded_answer(mock_db_with_kos):
    """Model mentions INSUFFICIENT_EVIDENCE in prose, but answer is valid and cited -> grounded: True."""
    client = MockModelClient({
        "User Query:": {
            "answer": "Although the user asked if there is INSUFFICIENT_EVIDENCE, Section 33 explicitly prescribes penalties. [urn:ki:in:dpdp:act:dpdpa-2023 (Page 1, Section 33, Hash: aaaaaaaa)]",
            "cited_urns": ["urn:ki:in:dpdp:act:dpdpa-2023"],
            "sufficient_evidence": True
        }
    })
    engine = GroundedReasoningEngine(model_client=client)
    engine.retrieve_context = lambda q: [mock_db_with_kos.sample_ko]
    
    res = engine.query("Is there insufficient evidence on penalties?")
    assert res["grounded"] is True
    assert len(res["citations"]) == 1
    assert res["citations"][0]["urn"] == "urn:ki:in:dpdp:act:dpdpa-2023"


def test_malformed_json_fallback(mock_db_with_kos):
    """Malformed JSON fails closed with grounded: False and raw output preserved."""
    class BrokenJsonClient(MockModelClient):
        def generate_json(self, prompt: str):
            return {
                "answer": "NOT VALID JSON OBJECT FROM MODEL",
                "cited_urns": [],
                "sufficient_evidence": False,
                "error": "MALFORMED_JSON",
                "raw_output": "NOT VALID JSON OBJECT FROM MODEL"
            }

    engine = GroundedReasoningEngine(model_client=BrokenJsonClient())
    engine.retrieve_context = lambda q: [mock_db_with_kos.sample_ko]
    
    res = engine.query("Any query")
    assert res["grounded"] is False
    assert len(res["citations"]) == 0
    assert "raw_output" in res


def test_fabricated_citation_confinement(mock_db_with_kos):
    """Model claims a hallucinated URN not in retrieved context -> stripped from citations."""
    client = MockModelClient({
        "User Query:": {
            "answer": "Section 33 specifies breach penalties. [urn:ki:in:dpdp:act:dpdpa-2023] and [urn:ki:in:dpdp:hallucinated:fake-act]",
            "cited_urns": ["urn:ki:in:dpdp:act:dpdpa-2023", "urn:ki:in:dpdp:hallucinated:fake-act"],
            "sufficient_evidence": True
        }
    })
    engine = GroundedReasoningEngine(model_client=client)
    engine.retrieve_context = lambda q: [mock_db_with_kos.sample_ko]
    
    res = engine.query("What are the penalties?")
    assert res["grounded"] is True
    assert res["cited_urns"] == ["urn:ki:in:dpdp:act:dpdpa-2023"]
    assert len(res["citations"]) == 1
    assert res["citations"][0]["urn"] == "urn:ki:in:dpdp:act:dpdpa-2023"


def test_input_guardrail_fast_refusal():
    """Out-of-scope query refused immediately by pre-flight guardrail without calling model."""
    client = MockModelClient()
    engine = GroundedReasoningEngine(model_client=client)
    
    res = engine.query("What is my current account balance?")
    assert res["grounded"] is False
    assert "REFUSAL" in res["answer"]
    assert len(client.call_history) == 0  # LLM never touched!
    assert "trace" in res
    assert res["trace"]["spans"][0]["name"] == "guardrail_input"
