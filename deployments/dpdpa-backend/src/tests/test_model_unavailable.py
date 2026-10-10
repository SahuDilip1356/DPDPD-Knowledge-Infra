"""A provider outage must surface as ModelUnavailable / HTTP 503, never as a refusal.

On 2026-10-02 the OpenAI account returned 429 credit_balance_exhausted on every call and the
engine answered INSUFFICIENT_EVIDENCE, so the eval scored the outage as correct refusals.
"""

import pytest
import requests
from fastapi.testclient import TestClient

from src.api import api_service
from src.api.api_service import app
from src.reasoning.model_client import ModelClient, ModelUnavailable


class FakeResponse:
    def __init__(self, status, payload=None):
        self.status_code = status
        self._payload = payload or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            err = requests.exceptions.HTTPError(
                f"{self.status_code} Error for url: https://example/v1?key=AIzaSECRETSECRETSECRET123")
            err.response = self
            raise err


@pytest.fixture
def openrouter(monkeypatch):
    for key in ("GPT_OSS_BASE_URL", "GPT_OSS_MODEL", "REASONING_PROVIDER", "GEMINI_API_KEY",
                "GOOGLE_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    return ModelClient()


def test_http_429_raises_model_unavailable_after_one_retry(monkeypatch, openrouter):
    calls = []
    monkeypatch.setattr(requests, "post", lambda *a, **k: calls.append(1) or FakeResponse(429))
    with pytest.raises(ModelUnavailable) as exc:
        openrouter.generate_json("question")
    assert len(calls) == 2
    assert "OpenRouter returned HTTP 429" in str(exc.value)
    assert "AIza" not in str(exc.value) and "key=" not in str(exc.value)


def test_network_error_raises_model_unavailable(monkeypatch, openrouter):
    def down(*_a, **_k):
        raise requests.exceptions.ConnectionError("no route to host")
    monkeypatch.setattr(requests, "post", down)
    with pytest.raises(ModelUnavailable, match="unreachable"):
        openrouter.generate_json("question")


def test_no_provider_configured_raises_model_unavailable(openrouter):
    openrouter.oai_key = None
    with pytest.raises(ModelUnavailable):
        openrouter.generate_json("question")


def test_malformed_answer_still_fails_closed_as_insufficient_evidence(monkeypatch, openrouter):
    payload = {"choices": [{"message": {"content": "not json at all"}}]}
    monkeypatch.setattr(requests, "post", lambda *a, **k: FakeResponse(200, payload))
    result = openrouter.generate_json("question")
    assert result["answer"].startswith("INSUFFICIENT_EVIDENCE")
    assert result["sufficient_evidence"] is False


def test_transient_outage_then_answer_recovers(monkeypatch, openrouter):
    good = {"choices": [{"message": {"content": '{"answer": "ok", "cited_urns": [], "sufficient_evidence": false}'}}]}
    responses = iter([FakeResponse(503), FakeResponse(200, good)])
    monkeypatch.setattr(requests, "post", lambda *a, **k: next(responses))
    assert openrouter.generate_json("question")["answer"] == "ok"


def test_query_endpoint_returns_503_with_retry_after(monkeypatch):
    def outage(_query):
        raise ModelUnavailable("OpenRouter returned HTTP 429")
    monkeypatch.setattr(api_service.reasoning_engine, "query", outage)
    monkeypatch.setattr(api_service, "log_search_query", lambda *a, **k: None)
    response = TestClient(app).post("/knowledge/query", json={"query": "What is a Data Fiduciary?"})
    assert response.status_code == 503
    assert response.headers.get("retry-after") == "60"
    assert "INSUFFICIENT_EVIDENCE" not in response.text
