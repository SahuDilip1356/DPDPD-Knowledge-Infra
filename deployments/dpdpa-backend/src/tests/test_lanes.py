"""Two lanes (decided 2026-10-03): only official law feeds the knowledge store; market data stays out of git.

Evals: specs/official-sources/evals.md, E1.1-E1.6.
"""

import copy
import gzip
import json
import os
import subprocess
import sys

import pytest

from src.schemas.corpus_contract import (
    GAZETTE_SOURCES, PROVISIONS_PATH, check_corpus, check_object, load_law, sha256,
)

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(BACKEND_ROOT, "..", ".."))
SNAPSHOT = os.path.join(REPO_ROOT, "evals", "corpus", "answer_kos.jsonl.gz")
MARKET_LANE = "staging/competitive_intel/market-map"


def git(*args):
    return subprocess.run(["git", "-C", REPO_ROOT, *args], capture_output=True, text=True)


needs_git = pytest.mark.skipif(git("rev-parse", "--git-dir").returncode != 0, reason="not a git checkout")
needs_law = pytest.mark.skipif(
    not (os.path.exists(PROVISIONS_PATH) and os.path.exists(SNAPSHOT)),
    reason="the law file and the eval snapshot ship outside this package")


# E1.1
@needs_git
@pytest.mark.parametrize("path", [
    f"{MARKET_LANE}/saralprivacy-dpdpa-data.zip",
    f"{MARKET_LANE}/a-file-that-does-not-exist-yet.csv",
    "staging/competitive_intel/content-research/notes.md",
])
def test_market_lane_is_ignored(path):
    assert git("check-ignore", "-q", path).returncode == 0, f"{path} is not ignored by git"


# E1.2
@needs_git
def test_nothing_under_staging_is_tracked():
    assert git("ls-files", "staging").stdout.strip() == ""


@pytest.fixture(scope="module")
def law():
    return load_law()


@pytest.fixture(scope="module")
def snapshot():
    with gzip.open(SNAPSHOT, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def conforming(snapshot, law):
    return next(row for row in snapshot if not check_object(row, law))


def market_item():
    return {
        "id": "ev-market",
        "source_urn": "urn:ki:in:dpdp:source:competitor-blog",
        "source_name": "A competitor blog",
        "source_tier": "secondary",
        "citation_text": "Penalties up to Rs 500 crore apply to every small business, always.",
        "coordinates": {"url": "https://competitor.example/blog"},
        "chunk_sha256": sha256("anything"),
        "verification_status": "verified",
    }


# E1.3
@needs_law
def test_eval_snapshot_cites_only_law_lane_sources(snapshot):
    sources = {e.get("source_urn") for row in snapshot for e in row.get("evidence") or []}
    assert sources and sources <= set(GAZETTE_SOURCES), sources - set(GAZETTE_SOURCES)


# E1.4
@needs_law
def test_an_unregistered_source_breaks_the_contract(snapshot, law):
    row = copy.deepcopy(conforming(snapshot, law))
    row["evidence"].append(market_item())
    problems = check_object(row, law)
    assert any("cites an unregistered source" in p and "competitor-blog" in p for p in problems), problems


# E1.6
@needs_law
def test_no_staged_answer_cites_an_unregistered_source(snapshot, law):
    failures = check_corpus(snapshot, law)
    hits = [p for problems in failures.values() for p in problems if "unregistered source" in p]
    assert hits == []


# E1.5
@needs_law
def test_push_refuses_a_batch_with_an_unregistered_source(snapshot, law, tmp_path, monkeypatch):
    sys.path.insert(0, os.path.join(REPO_ROOT, "src", "competitive_intel"))
    try:
        bko = pytest.importorskip("build_knowledge_objects", reason="the builder's own dependencies are not installed")
    finally:
        sys.path.pop(0)
    row = copy.deepcopy(conforming(snapshot, law))
    row["evidence"].append(market_item())
    staged = tmp_path / "answer_kos.jsonl"
    staged.write_text(json.dumps(row) + "\n")
    monkeypatch.setattr(bko, "PRIMARY_FILE", str(tmp_path / "none.jsonl"))
    monkeypatch.setattr(bko, "ANSWERS_FILE", str(staged))
    monkeypatch.setattr(bko, "published_law", lambda: law)  # the site's law file, not staging
    with pytest.raises(SystemExit) as refused:
        bko.push(dry_run=True)
    assert "refused" in str(refused.value) and "unregistered source" in str(refused.value)
