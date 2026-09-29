"""Tests for the real-corpus eval. Run: python -m pytest -q evals/test_real_corpus.py"""

import json
import re
import socket

import pytest

import evals.runner  # noqa: F401  puts the deployed backend first on sys.path
from evals import real_corpus
from evals.scorers import nonexistent_provisions, provision_mentions
from src.reasoning.model_client import ModelClient

VALID = ({f"S{n}" for n in range(1, 45)} | {f"R{n}" for n in range(1, 24)} | {"ACT-SCHEDULE"}
         | {f"SCH-{o}" for o in "FIRST SECOND THIRD FOURTH FIFTH SIXTH SEVENTH".split()})


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    """No network, no Pinecone, and reports go to a temporary directory."""
    def refuse(self, address):
        raise RuntimeError(f"network call during an eval test: {address}")
    monkeypatch.setattr(socket.socket, "connect", refuse)
    for key in ("PINECONE_API_KEY", "OFFLINE_MODE"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(real_corpus, "REPORTS_DIR", str(tmp_path))
    return tmp_path


def report(tmp_path):
    [path] = tmp_path.glob("real_corpus_*.json")
    return json.loads(path.read_text())


@pytest.mark.parametrize("text, labels", [
    ("Under Section 33(2) and the Schedule", ["S33"]),
    ("Sections 6 and 7 apply; see Rule 7(1)(a).", ["S6", "S7", "R7"]),
    ("the DPDP Rules 2025 and the Rules, 2025", []),
    ("Section 43A of the Information Technology Act, omitted by Section 44", ["S44"]),
    ("section 8 of the Act and Rule 3 of the DPDP Rules", ["S8", "R3"]),
    ("[urn:x (Page 1, Section Section 33, Hash: aa)] and Section None", ["S33"]),
    ("the Seventh Schedule and the Eighth Schedule", ["SCH-SEVENTH", "SCH-EIGHTH"]),
])
def test_provision_mentions(text, labels):
    assert [m["label"] for m in provision_mentions(text)] == labels


def test_nonexistent_provisions():
    assert nonexistent_provisions({"S33"}, "Section 45, Rule 24 and the Eighth Schedule", VALID) == [
        "R24", "S45", "SCH-EIGHTH"]
    assert nonexistent_provisions({"S33", "R7"}, "Section 33(2) and Rule 7", VALID) == []


def test_golden_labels_exist():
    for case in real_corpus.load_golden(real_corpus.GOLDEN_PATH):
        assert set(case.get("expect_provisions", [])) <= VALID, case["id"]
        assert case["expect_sufficient"] == (case["kind"] == "answer"), case["id"]


def test_offline_run_holds_invariants_without_network(isolated):
    assert real_corpus.run_real_corpus_suite(limit=4) == 0
    summary = report(isolated)["summary"]
    assert summary["cited_subset_retrieved"] == 1.0
    assert summary["no_nonexistent_provision"] == 1.0


class FakeLive(ModelClient):
    """Poses as a configured Gemini client; answers with a provision that does not exist."""
    calls = 0

    def __init__(self):
        super().__init__()
        self.gpt_oss_enabled, self.gemini_key = False, "fake"

    def generate_json(self, prompt):
        FakeLive.calls += 1
        urn = re.search(r"URN: (\S+)", prompt).group(1)
        return {"answer": f"Section 99 applies [{urn}].", "cited_urns": [urn],
                "sufficient_evidence": True}


def test_cost_guard_stops_before_the_call(monkeypatch):
    monkeypatch.setattr(real_corpus, "ModelClient", FakeLive)
    FakeLive.calls = 0
    assert real_corpus.run_real_corpus_suite(live=True, limit=1, max_cost_usd=0.001) == 3
    assert FakeLive.calls == 0


def test_live_run_reports_cost_and_catches_invented_law(monkeypatch, isolated):
    monkeypatch.setattr(real_corpus, "ModelClient", FakeLive)
    assert real_corpus.run_real_corpus_suite(live=True, limit=1, max_cost_usd=5.0) == 1
    result = report(isolated)
    assert result["cost"]["usd"] > 0 and result["cost"]["calls"] == 1
    assert result["results"][0]["details"]["nonexistent_provisions"] == ["S99"]
