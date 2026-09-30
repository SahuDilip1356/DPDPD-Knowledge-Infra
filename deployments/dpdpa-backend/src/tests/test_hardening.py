"""Security, rate-limit, readiness, and provider-routing tests."""

from fastapi.testclient import TestClient

from src.api.api_service import app, db_client, model_client, query_rate_limiter
from src.reasoning.model_client import ModelClient


client = TestClient(app)


def test_admin_routes_fail_closed_without_configuration(monkeypatch):
    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    for path in ("/admin/stats", "/admin/search-audit", "/admin/ingestion-audit"):
        assert client.get(path).status_code == 503


def test_admin_routes_require_correct_key(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "correct-key")
    for path in ("/admin/stats", "/admin/search-audit", "/admin/ingestion-audit"):
        assert client.get(path).status_code == 401
        assert client.get(
            path, headers={"X-Admin-Key": "wrong-key"}
        ).status_code == 401
        assert client.get(
            path, headers={"X-Admin-Key": "correct-key"}
        ).status_code == 200


def test_empty_stats_are_truthful(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "correct-key")

    class EmptyQuery:
        def filter(self, *_args):
            return self

        def all(self):
            return []

    class EmptySession:
        def query(self, *_args):
            return EmptyQuery()

        def close(self):
            pass

    monkeypatch.setattr(db_client, "Session", EmptySession)
    response = client.get(
        "/admin/stats", headers={"X-Admin-Key": "correct-key"}
    )
    assert response.json() == {
        "total_knowledge_objects": 0,
        "core_layer_count": 0,
        "opinion_layer_count": 0,
        "other_layers_count": 0,
    }


def test_query_payload_limit_rejects_before_model():
    response = client.post("/knowledge/query", json={"query": "x" * 4001})
    assert response.status_code == 422


def test_query_rate_limit_returns_retry_after(monkeypatch):
    query_rate_limiter.reset()
    monkeypatch.setenv("QUERY_RATE_LIMIT_PER_MINUTE", "2")
    monkeypatch.setenv("QUERY_RATE_LIMIT_PER_DAY", "100")
    assert client.post("/knowledge/query", json={"query": "one"}).status_code == 200
    assert client.post("/knowledge/query", json={"query": "two"}).status_code == 200
    limited = client.post("/knowledge/query", json={"query": "three"})
    assert limited.status_code == 429
    assert "retry-after" in limited.headers
    query_rate_limiter.reset()


def test_production_readiness_fails_without_model_key(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setattr(model_client, "gemini_key", None)
    monkeypatch.setattr(model_client, "oai_key", None)
    monkeypatch.setattr(model_client, "gpt_oss_enabled", False)
    assert client.get("/health/ready").status_code == 503


def test_gpt_oss_is_preferred_cook(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("GPT_OSS_MODEL", "gpt-oss:20b")
    monkeypatch.setenv("GPT_OSS_BASE_URL", "http://127.0.0.1:11434/v1")
    model = ModelClient()
    assert model.gpt_oss_enabled is True
    assert model.is_configured is True
    monkeypatch.setattr(model, "_generate_gpt_oss", lambda _prompt: "oss-cooked")
    assert model.generate("prompt") == "oss-cooked"


def test_openrouter_is_used_for_generation_and_vision(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GPT_OSS_BASE_URL", raising=False)
    monkeypatch.delenv("GPT_OSS_MODEL", raising=False)
    monkeypatch.delenv("GPT_OSS_API_KEY", raising=False)
    monkeypatch.delenv("REASONING_PROVIDER", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "router-key")
    model = ModelClient()
    assert model.oai_provider == "OpenRouter"
    assert model.is_configured is True

    monkeypatch.setattr(model, "_generate_openai", lambda _prompt: "generated")
    monkeypatch.setattr(
        model,
        "_generate_vision_openai",
        lambda _prompt, _mime, _bytes: "vision",
    )
    assert model.generate("prompt") == "generated"
    assert model.generate_vision("prompt", "image/png", b"bytes") == "vision"
