"""Ranked keyword fallback: relevance order, top-k cap and relevance floor."""

import json
import os
from datetime import datetime
from types import SimpleNamespace

import pytest

from src.reasoning.keyword_ranker import TOP_K, rank_by_relevance, tokenize
from src.reasoning.reasoning_engine import GroundedReasoningEngine
from src.storage.db_client import DatabaseClient
from src.tests.test_reasoning_pipeline import make_ko


def _doc(urn, title, summary="", entities=None):
    return {"urn": urn, "title": title, "summary": summary, "entities": entities or []}


# Ten objects about personal data, one of them about breach notification.
CORPUS = [
    _doc(f"urn:ki:test:generic-{i}", f"Personal data topic {i}",
         "Personal data under the Act must be processed lawfully.")
    for i in range(9)
] + [
    _doc("urn:ki:test:breach", "Breach notification",
         "A personal data breach must be reported to the Board within 72 hours."),
]


# ─── Ranker ─────────────────────────────────────────────────────────────────

def test_tokenize_drops_stopwords_and_folds_plurals():
    assert tokenize("What are the penalties for the notices?") == ["penalty", "notice"]


def test_most_relevant_object_ranks_first():
    ranked = rank_by_relevance("When must a personal data breach be reported?", CORPUS)
    assert ranked[0]["urn"] == "urn:ki:test:breach"


def test_results_are_capped_at_top_k():
    ranked = rank_by_relevance("personal data", CORPUS)
    assert len(ranked) == TOP_K


def test_stopword_only_query_retrieves_nothing():
    assert rank_by_relevance("what is the", CORPUS) == []


def test_floor_drops_objects_that_miss_the_key_term():
    # "encryption" appears nowhere, so matching only "personal data" is not enough.
    assert rank_by_relevance("encryption of personal data", CORPUS, min_coverage=0.5) == []
    assert rank_by_relevance("encryption of personal data", CORPUS, min_coverage=0.0)


def test_unrelated_query_retrieves_nothing():
    assert rank_by_relevance("sourdough bread recipe", CORPUS) == []


# ─── Engine fallback branches ───────────────────────────────────────────────

def _kos():
    return [
        make_ko(urn=d["urn"], title=d["title"], summary=d["summary"], entities=["Data"])
        for d in CORPUS
    ]


def test_sqlite_fallback_is_ranked_and_capped(monkeypatch):
    for key in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY"):
        monkeypatch.delenv(key, raising=False)
    db = DatabaseClient("sqlite:///:memory:")
    db.supabase = None
    for ko in _kos():
        db.publish_ko(ko, system_time=datetime(2026, 1, 1))
    engine = GroundedReasoningEngine(db_client=db)

    results = engine.retrieve_context("How fast must a data breach be reported?")
    assert 1 <= len(results) <= TOP_K
    assert results[0]["urn"] == "urn:ki:test:breach"
    assert engine.retrieve_context("what is the") == []


class _FakeSupabaseQuery:
    def __init__(self, rows):
        self.rows = rows

    def table(self, _name):
        return self

    def select(self, *_args):
        return self

    def is_(self, *_args):
        return self

    def execute(self):
        return SimpleNamespace(data=self.rows)


def test_supabase_fallback_is_ranked_and_capped():
    rows = [
        {**ko, "legal_time_start": "2024-01-15T00:00:00", "confidence_score": ko["confidence_score"]}
        for ko in _kos()
    ]
    engine = GroundedReasoningEngine(db_client=SimpleNamespace(supabase=_FakeSupabaseQuery(rows)))

    results = engine.retrieve_context("personal data")
    assert len(results) == TOP_K
    breach = engine.retrieve_context("breach reported to the Board")
    assert breach[0]["urn"] == "urn:ki:test:breach"
    assert breach[0]["date"] == "2024-01-15"
    assert engine.retrieve_context("sourdough bread recipe") == []


def test_git_ledger_fallback_is_ranked_and_capped(tmp_path):
    objects = tmp_path / "objects"
    objects.mkdir()
    for i, ko in enumerate(_kos()):
        (objects / f"{i}.json").write_text(json.dumps(ko))
    engine = GroundedReasoningEngine(git_ledger=SimpleNamespace(base_dir=str(tmp_path)))

    assert len(engine.retrieve_context("personal data")) == TOP_K
    assert engine.retrieve_context("breach")[0]["urn"] == "urn:ki:test:breach"
    assert engine.retrieve_context("what is the") == []
