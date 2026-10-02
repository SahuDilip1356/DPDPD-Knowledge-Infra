"""Corpus contract: shape, and every gazette quote checked against the gazette text."""

import copy
import os
import subprocess
import sys

import pytest

from src.schemas.corpus_contract import (
    ACT_SOURCE, PROVISIONS_PATH, RULES_SOURCE, check_corpus, check_object, load_law, report, sha256,
)

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(BACKEND_ROOT, "..", ".."))

pytestmark = pytest.mark.skipif(
    not os.path.exists(PROVISIONS_PATH), reason="the law file ships with the site, outside this package")


@pytest.fixture(scope="module")
def law():
    return load_law()


def quote(law, label, start, length=120):
    return law[label]["text"][start:start + length].strip()


def evidence(law, label, text, n=1):
    act = label.startswith("S")
    return {
        "id": f"ev-{label.lower()}-{n}",
        "source_urn": ACT_SOURCE if act else RULES_SOURCE,
        "source_name": "Gazette of India",
        "source_tier": "primary",
        "coordinates": {"section": f"Section {label[1:]}"} if act else {"rule": f"Rule {label[1:]}"},
        "citation_text": text,
        "chunk_sha256": sha256(law[label]["text"]),
        "verification_status": "verified",
    }


@pytest.fixture
def answer(law):
    return {
        "urn": "urn:ki:in:dpdp:qa:who-must-be-told-of-a-breach-0a1b2c3d",
        "version": 1,
        "type": "Answer",
        "title": "Who must be told of a personal data breach?",
        "summary": "The Data Fiduciary tells the Board and each affected Data Principal (Section 8(6)).",
        "confidence_score": 0.9,
        "source_credibility": "primary-derived",
        "interpretation_stance": "plain-language synthesis of primary law",
        "legal_time_start": "2025-11-13",
        "body": {"cited": ["S8", "R7"], "provisions": ["S8", "R7"], "review_status": "pending",
                 "rules_in_force_from": {"R7": law["R7"]["in_force_from"]}},
        "business_impact": {"impact_summary": "A breach must be reported.", "action_required": "Prepare a breach process."},
        "evidence": [evidence(law, "S8", quote(law, "S8", 40)), evidence(law, "R7", quote(law, "R7", 60), 2)],
        "linked_objects": ["urn:ki:in:dpdp:act:2023:sec:8"],
        "entities": ["Data Fiduciary", "personal data breach"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:2023:sec:8", "edge_type": "Interprets"}],
    }


@pytest.fixture
def verbatim(law):
    text = law["S6"]["text"]
    return {
        "urn": law["S6"]["urn"], "version": 2, "type": "Act",
        "title": "Section 6 — Consent", "summary": text[:1500],
        "confidence_score": 1.0, "source_credibility": "primary", "interpretation_stance": "verbatim",
        "legal_time_start": "2023-08-11T00:00:00+00:00",
        "body": {"full_text": text, "provision": "S6"},
        "business_impact": {},
        "evidence": [evidence(law, "S6", text[:300])],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"], "entities": [],
        "relations": [{"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Depends On"}],
    }


def test_a_verified_answer_and_a_verbatim_provision_conform(law, answer, verbatim):
    assert check_object(answer, law) == []
    assert check_object(verbatim, law) == []


def test_database_columns_beyond_the_contract_are_allowed(law, verbatim):
    verbatim.update(system_time_start="2026-09-29T10:00:00+00:00", system_time_end=None, forum_published=None)
    assert check_object(verbatim, law) == []


def test_a_quote_the_gazette_does_not_contain_is_caught(law, answer):
    # What the page-furniture bug produced: a margin note read as part of the sentence.
    answer["evidence"][0]["citation_text"] += " Processing of personal data of children."
    assert check_object(answer, law) == ["evidence: ev-s8-1 quote is not in the gazette text of S8"]


def test_a_quote_may_elide_but_each_piece_must_be_verbatim(law, answer):
    answer["evidence"][0]["citation_text"] = f"{quote(law, 'S8', 0, 60)} … {quote(law, 'S8', 400, 60)}"
    assert check_object(answer, law) == []
    answer["evidence"][0]["citation_text"] = f"{quote(law, 'S8', 0, 60)} … the Board may waive this duty"
    assert len(check_object(answer, law)) == 1


def test_a_hash_of_superseded_text_is_caught(law, answer):
    answer["evidence"][1]["chunk_sha256"] = sha256(law["R7"]["text"] + " old running head")
    assert check_object(answer, law) == ["evidence: ev-r7-2 hash is not the current gazette text of R7"]


def test_an_answer_must_quote_every_provision_it_cites(law, answer):
    answer["body"]["cited"].append("S10")
    assert check_object(answer, law) == ["answer: cites S10 without a quote from it"]
    answer["body"]["cited"][-1] = "S99"
    assert check_object(answer, law) == ["answer: cites S99, which is not a provision"]


def test_a_wrong_commencement_date_is_caught(law, answer):
    answer["body"]["rules_in_force_from"]["R7"] = "2025-11-13"
    assert check_object(answer, law) == [
        f"answer: says R7 is in force from 2025-11-13; the Rules say {law['R7']['in_force_from']}"]


def test_a_verbatim_object_must_carry_the_gazette_text_unchanged(law, verbatim):
    verbatim["body"]["full_text"] = verbatim["body"]["full_text"].replace("free, specific", "specific")
    assert check_object(verbatim, law) == ["verbatim: full_text is not the gazette text of S6"]


def test_a_hand_written_seed_object_is_rejected(law):
    seed = {
        "urn": "urn:ki:in:dpdp:penalty:breach-notification", "version": 1, "type": "Penalty",
        "title": "Penalty: Failure to Notify Data Breach",
        "summary": "Failure to notify a breach attracts a penalty of up to Rs 200 crore.",
        "confidence_score": 1.0, "legal_time_start": "2023-08-11",
        "source_credibility": None, "interpretation_stance": None, "body": {},
        "business_impact": {"impact_summary": "High.", "action_required": "Prepare."},
        "evidence": [{"id": "ev-1", "source_urn": ACT_SOURCE, "source_name": "Gazette", "source_tier": "primary",
                      "citation_text": "Schedule item 3", "coordinates": {"page": 20}, "verification_status": "verified"}],
        "linked_objects": [], "entities": ["Penalty"], "relations": [],
    }
    problems = check_object(seed, law)
    assert any(p.startswith("shape: type") for p in problems)
    assert any("chunk_sha256" in p for p in problems)
    assert any(p.startswith("evidence: ev-1 names no provision") for p in problems)


def test_the_report_counts_objects_and_groups_violations(law, answer):
    stale = copy.deepcopy(answer)
    stale["urn"] += "-b"
    for item in stale["evidence"]:
        item["chunk_sha256"] = "0" * 64
    failures = check_corpus([answer, stale], law)
    assert list(failures) == [f"{stale['urn']} v1"]
    text = report(failures, 2)
    assert text.startswith("1/2 objects conform")
    assert "    2  evidence: <item> hash is not the current gazette text of <provision>" in text


@pytest.mark.parametrize("script", [
    os.path.join(BACKEND_ROOT, "scripts", "seed_full_knowledge_base.py"),
    os.path.join(BACKEND_ROOT, "scripts", "seed_supabase.py"),
    os.path.join(REPO_ROOT, "seed_knowledge_base.py"),
])
def test_the_retired_seeders_write_nothing(script):
    source = open(script).read()
    assert source.rstrip().endswith('if __name__ == "__main__":\n    sys.exit(RETIRED)')
    compile(source, script, "exec")


def test_a_retired_seeder_exits_before_connecting():
    script = os.path.join(BACKEND_ROOT, "scripts", "seed_supabase.py")
    env = {**os.environ, "SUPABASE_URL": "http://127.0.0.1:9", "SUPABASE_SERVICE_KEY": "unused"}
    done = subprocess.run([sys.executable, script], capture_output=True, text=True, env=env, timeout=60)
    assert done.returncode == 1
    assert "retired" in done.stderr
    assert "Connecting" not in done.stdout
