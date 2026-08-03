"""
Test Suite — Sprint 5: Reasoning, Business Translation, Publishing & Orchestrator

Tests Departments 6, 7, 8 and the full Factory Orchestrator pipeline.
"""

import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.factory.reasoning_agent import ReasoningAgent
from src.factory.business_translation_agent import BusinessTranslationAgent
from src.factory.publishing_agent import PublishingAgent
from src.factory.factory_orchestrator import FactoryOrchestrator
from src.storage.git_ledger import GitLedger


# ─── Test Fixtures ──────────────────────────────────────────────────────────

def make_ko(urn, title, entities, relations=None, evidence=None,
            summary="", confidence=0.8, version=1, linked_objects=None,
            business_impact=None, source_layer=1, history=None):
    """Helper to create a valid Knowledge Object for testing."""
    if business_impact is None:
        business_impact = {
            "impact_summary": "Compliance impact requiring review",
            "action_required": "Review and update internal policies"
        }
    if history is None:
        history = [{
            "version": version,
            "system_time": "2024-01-15T00:00:00Z",
            "commit_message": "Initial creation"
        }]
    return {
        "urn": urn,
        "title": title,
        "source": {"name": "Test Source", "layer": source_layer},
        "date": "2024-01-15",
        "version": version,
        "summary": summary or f"Summary for {title}",
        "entities": entities,
        "evidence": evidence if evidence is not None else [
            {
                "source_urn": f"{urn}:source",
                "citation_text": f"Citation from {title}",
                "coordinates": {
                    "page": 1,
                    "section": "Section 1",
                    "hash": "a" * 64
                }
            }
        ],
        "business_impact": business_impact,
        "confidence_score": confidence,
        "relations": relations or [],
        "linked_objects": linked_objects or [],
        "history": history
    }


def make_conflict_pair():
    """Creates a pair of KOs with conflicting business impacts."""
    ko_a = make_ko(
        urn="urn:ki:in:dpdp:rule:consent-mandatory",
        title="Consent Mandate for Data Processing",
        entities=["Rule", "Consent", "Purpose"],
        summary="All data processing requires mandatory explicit consent.",
        business_impact={
            "impact_summary": "Consent collection is mandatory before processing",
            "action_required": "Must obtain consent before any data processing"
        },
        evidence=[{
            "source_urn": "urn:ki:in:dpdp:act:dpdpa:s6",
            "citation_text": "Processing requires mandatory consent",
            "coordinates": {"hash": "b" * 64}
        }]
    )
    ko_b = make_ko(
        urn="urn:ki:in:dpdp:circular:consent-optional",
        title="Circular on Consent Exceptions",
        entities=["Circular", "Consent", "Purpose"],
        summary="Certain processing activities may proceed without consent.",
        business_impact={
            "impact_summary": "Some processing is optional regarding consent",
            "action_required": "Optional consent for legitimate interest processing"
        },
        evidence=[{
            "source_urn": "urn:ki:in:dpdp:act:dpdpa:s7",
            "citation_text": "Processing optional for legitimate interests",
            "coordinates": {"hash": "c" * 64}
        }]
    )
    return ko_a, ko_b


# ═══════════════════════════════════════════════════════════════════════════
# REASONING AGENT TESTS (Department 6)
# ═══════════════════════════════════════════════════════════════════════════

class TestReasoningAgent:

    def test_detect_explicit_conflicts(self):
        """Should detect 'Conflicts With' edge types."""
        agent = ReasoningAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:rule:a",
            title="Rule A",
            entities=["Rule"],
            relations=[
                {"target_urn": "urn:ki:in:dpdp:rule:b", "edge_type": "Conflicts With"}
            ]
        )
        conflicts = agent.detect_conflicts([ko])
        assert len(conflicts) >= 1
        assert conflicts[0]["type"] == "CONFLICT"
        assert conflicts[0]["severity"] == "HIGH"

    def test_detect_semantic_contradiction(self):
        """Should detect opposing business impact keywords."""
        agent = ReasoningAgent()
        ko_a, ko_b = make_conflict_pair()
        conflicts = agent.detect_conflicts([ko_a, ko_b])
        semantic = [c for c in conflicts if c.get("edge_type") == "Semantic Contradiction"]
        assert len(semantic) >= 1

    def test_detect_supersessions(self):
        """Should identify Supersedes/Replaces edges."""
        agent = ReasoningAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:rule:v2",
            title="Updated Rules 2024",
            entities=["Rule"],
            relations=[
                {"target_urn": "urn:ki:in:dpdp:rule:v1", "edge_type": "Supersedes"}
            ]
        )
        supersessions = agent.detect_supersessions([ko])
        assert len(supersessions) == 1
        assert supersessions[0]["type"] == "SUPERSESSION"
        assert supersessions[0]["active_urn"] == "urn:ki:in:dpdp:rule:v2"

    def test_detect_coverage_gaps(self):
        """Should flag entity types with zero coverage."""
        agent = ReasoningAgent()
        ko_list = [
            make_ko(urn="urn:ki:in:dpdp:act:a", title="Act", entities=["Act", "Rule"]),
        ]
        gaps = agent.detect_coverage_gaps(
            ko_list,
            expected_entities=["Act", "Rule", "Penalty", "Template"]
        )
        gap_entities = [g["missing_entity"] for g in gaps]
        assert "Penalty" in gap_entities
        assert "Template" in gap_entities
        assert "Act" not in gap_entities

    def test_detect_emerging_patterns(self):
        """Should flag high-frequency entity co-occurrences."""
        agent = ReasoningAgent()
        ko_list = [
            make_ko(urn=f"urn:ki:in:dpdp:rule:r{i}", title=f"Rule {i}",
                     entities=["Rule", "Consent", "Purpose"])
            for i in range(5)
        ]
        patterns = agent.detect_emerging_patterns(ko_list)
        assert len(patterns) > 0
        # Rule+Consent should be flagged as an emerging pattern
        pair_entities = [tuple(p["entities"]) for p in patterns]
        assert any("Consent" in pair and "Rule" in pair for pair in pair_entities)

    def test_synthesize_report(self):
        """Full synthesis should produce a structured report."""
        agent = ReasoningAgent()
        ko_a, ko_b = make_conflict_pair()
        report = agent.synthesize(
            [ko_a, ko_b],
            expected_entities=["Act", "Rule", "Consent", "Template"]
        )
        assert report["ko_count"] == 2
        assert report["total_insights"] > 0
        assert "summary" in report
        assert "severity_breakdown" in report
        assert len(agent.get_audit_log()) > 0


# ═══════════════════════════════════════════════════════════════════════════
# BUSINESS TRANSLATION AGENT TESTS (Department 7)
# ═══════════════════════════════════════════════════════════════════════════

class TestBusinessTranslationAgent:

    def test_extract_consent_obligation(self):
        """Should extract consent-related obligations."""
        agent = BusinessTranslationAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:rule:consent",
            title="Consent Rules",
            entities=["Rule", "Consent"],
            summary="Organizations must obtain consent before processing personal data.",
            business_impact={
                "impact_summary": "Consent collection is required",
                "action_required": "Update consent mechanisms"
            }
        )
        obligations = agent.extract_obligations(ko)
        categories = [o["category"] for o in obligations]
        assert "CONSENT_REVIEW" in categories

    def test_extract_breach_obligation(self):
        """Should extract breach notification obligations."""
        agent = BusinessTranslationAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:rule:breach",
            title="Breach Notification Rules",
            entities=["Rule"],
            summary="In case of a data breach, the data fiduciary must notify the Board.",
            business_impact={
                "impact_summary": "Breach notification to DPB within 72 hours",
                "action_required": "Establish breach notification process"
            }
        )
        obligations = agent.extract_obligations(ko)
        categories = [o["category"] for o in obligations]
        assert "NOTIFICATION" in categories

    def test_extract_security_obligation(self):
        """Should extract security/technical control obligations."""
        agent = BusinessTranslationAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:rule:security",
            title="Security Safeguard Rules",
            entities=["Rule", "Control"],
            summary="Implement appropriate security safeguards including encryption.",
            business_impact={
                "impact_summary": "Security controls must be updated",
                "action_required": "Implement encryption and security safeguards"
            }
        )
        obligations = agent.extract_obligations(ko)
        categories = [o["category"] for o in obligations]
        assert "TECHNICAL_CONTROL" in categories

    def test_priority_assessment_critical(self):
        """Layer 1 + high confidence + penalty = CRITICAL."""
        agent = BusinessTranslationAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:act:penalty",
            title="Penalty Provisions",
            entities=["Act", "Penalty"],
            confidence=0.9,
            source_layer=1
        )
        obligation = {"category": "RISK_ASSESSMENT", "trigger_keyword": "penalty"}
        priority = agent.assess_priority(ko, obligation)
        assert priority == "CRITICAL"

    def test_priority_assessment_low(self):
        """Layer 8 + low confidence = LOW."""
        agent = BusinessTranslationAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:opinion:advisory",
            title="Advisory Opinion",
            entities=["Opinion"],
            confidence=0.4,
            source_layer=8
        )
        obligation = {"category": "DOCUMENTATION", "trigger_keyword": "document"}
        priority = agent.assess_priority(ko, obligation)
        assert priority == "LOW"

    def test_generate_action_items(self):
        """Should produce action items with roles and deadlines."""
        agent = BusinessTranslationAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:rule:consent-rules",
            title="Consent Collection Rules 2024",
            entities=["Rule", "Consent"],
            summary="Mandatory consent notice must be provided before processing.",
            business_impact={
                "impact_summary": "Consent notice is required",
                "action_required": "Update consent notice procedures"
            }
        )
        actions = agent.generate_action_items(ko)
        assert len(actions) > 0
        for action in actions:
            assert "priority" in action
            assert "affected_roles" in action
            assert "deadline_category" in action
            assert action["status"] == "OPEN"

    def test_translate_batch_report(self):
        """Batch translation should produce a consolidated report."""
        agent = BusinessTranslationAgent()
        ko_list = [
            make_ko(
                urn="urn:ki:in:dpdp:rule:a",
                title="Consent Rules",
                entities=["Rule", "Consent"],
                summary="Consent is mandatory for all processing."
            ),
            make_ko(
                urn="urn:ki:in:dpdp:rule:b",
                title="Security Safeguards",
                entities=["Rule", "Control"],
                summary="Security safeguards and encryption must be implemented."
            ),
        ]
        report = agent.translate_batch(ko_list)
        assert report["ko_count"] == 2
        assert report["total_actions"] > 0
        assert "by_priority" in report
        assert "by_role" in report


# ═══════════════════════════════════════════════════════════════════════════
# PUBLISHING AGENT TESTS (Department 8)
# ═══════════════════════════════════════════════════════════════════════════

class TestPublishingAgent:

    def test_validate_valid_ko(self):
        """A properly formed KO should pass validation."""
        agent = PublishingAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:act:valid-ko",
            title="Valid Act",
            entities=["Act"],
        )
        result = agent.validate_for_publish(ko)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_missing_evidence(self):
        """KO without evidence should fail validation."""
        agent = PublishingAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:act:no-evidence",
            title="No Evidence Act",
            entities=["Act"],
            evidence=[]
        )
        result = agent.validate_for_publish(ko)
        assert result["valid"] is False
        assert any("evidence" in e.lower() for e in result["errors"])

    def test_validate_self_referencing_edge(self):
        """KO with self-referencing edge should fail validation."""
        agent = PublishingAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:act:self-ref",
            title="Self Ref Act",
            entities=["Act"],
            relations=[
                {"target_urn": "urn:ki:in:dpdp:act:self-ref", "edge_type": "Amends"}
            ]
        )
        result = agent.validate_for_publish(ko)
        assert result["valid"] is False
        assert any("self-referencing" in e.lower() for e in result["errors"])

    def test_publish_to_git_ledger(self):
        """Should write KO to Git Ledger on successful publish."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = GitLedger(tmpdir)
            agent = PublishingAgent(git_ledger=ledger)

            ko = make_ko(
                urn="urn:ki:in:dpdp:act:published",
                title="Published Act",
                entities=["Act"],
            )
            receipt = agent.publish(ko)
            assert receipt["status"] == "PUBLISHED"
            assert receipt["ledger_path"] is not None
            assert os.path.exists(receipt["ledger_path"])

    def test_publish_rejected_ko(self):
        """Invalid KO should be rejected with error details."""
        agent = PublishingAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:act:bad",
            title="Bad Act",
            entities=["Act"],
            evidence=[]
        )
        receipt = agent.publish(ko)
        assert receipt["status"] == "REJECTED"
        assert len(receipt["errors"]) > 0

    def test_publish_batch(self):
        """Batch publish should process all KOs and report results."""
        agent = PublishingAgent()
        ko_list = [
            make_ko(
                urn="urn:ki:in:dpdp:act:good",
                title="Good Act",
                entities=["Act"],
            ),
            make_ko(
                urn="urn:ki:in:dpdp:act:bad",
                title="Bad Act",
                entities=["Act"],
                evidence=[]
            ),
        ]
        report = agent.publish_batch(ko_list)
        assert report["total_submitted"] == 2
        assert report["published_count"] == 1
        assert report["rejected_count"] == 1

    def test_audit_log(self):
        """All operations should be recorded in audit log."""
        agent = PublishingAgent()
        ko = make_ko(urn="urn:ki:in:dpdp:act:log-test", title="Log Test", entities=["Act"])
        agent.publish(ko)
        log = agent.get_audit_log()
        assert len(log) >= 1
        events = [e["event"] for e in log]
        assert "ko_published" in events


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY ORCHESTRATOR INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestFactoryOrchestrator:

    def test_full_pipeline_dry_run(self):
        """
        End-to-end dry run: Ontology → Relationships → Dedup →
        Reasoning → Business Translation (publishing skipped).
        """
        orchestrator = FactoryOrchestrator()

        ko_list = [
            make_ko(
                urn="urn:ki:in:dpdp:act:dpdpa-2023",
                title="Digital Personal Data Protection Act 2023",
                entities=["Act", "Consent", "Purpose", "Penalty"],
                summary="The primary legislation governing personal data protection in India.",
                business_impact={
                    "impact_summary": "Comprehensive consent and security obligations",
                    "action_required": "Review all consent and security policies"
                }
            ),
            make_ko(
                urn="urn:ki:in:dpdp:rule:consent-rules",
                title="Consent Rules 2024",
                entities=["Rule", "Consent", "Purpose"],
                summary="Rules implementing consent requirements of the DPDPA.",
                business_impact={
                    "impact_summary": "Consent notice format standardized",
                    "action_required": "Update consent notice procedures"
                }
            ),
            make_ko(
                urn="urn:ki:in:dpdp:circular:breach-notification",
                title="Breach Notification Circular",
                entities=["Circular", "Consent"],
                summary="Circular on breach notification to the Board and data principals.",
                business_impact={
                    "impact_summary": "72-hour breach notification window",
                    "action_required": "Establish breach notification process"
                }
            ),
        ]

        report = orchestrator.run_pipeline(
            ko_list,
            expected_entities=["Act", "Rule", "Consent", "Template", "Penalty"],
            edge_confidence=0.5,
            skip_publish=True
        )

        # Pipeline should complete all stages
        assert report["ko_count"] == 3
        assert report["stages"]["ontology"]["status"] == "COMPLETE"
        assert report["stages"]["relationships"]["status"] == "COMPLETE"
        assert report["stages"]["deduplication"]["status"] == "COMPLETE"
        assert report["stages"]["reasoning"]["status"] == "COMPLETE"
        assert report["stages"]["business_translation"]["status"] == "COMPLETE"
        assert report["stages"]["publishing"]["status"] == "SKIPPED"

        # Should generate insights
        assert report["insights"]["total_insights"] > 0

        # Should generate business actions
        assert report["business_actions"]["total_actions"] > 0

    def test_full_pipeline_with_publish(self):
        """
        End-to-end with publishing to Git Ledger.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = GitLedger(tmpdir)
            orchestrator = FactoryOrchestrator(git_ledger=ledger)

            ko_list = [
                make_ko(
                    urn="urn:ki:in:dpdp:act:published-act",
                    title="Published Act for Pipeline Test",
                    entities=["Act", "Rule"],
                    summary="Act to test end-to-end publishing.",
                    business_impact={
                        "impact_summary": "Policy compliance required",
                        "action_required": "Update policies accordingly"
                    }
                ),
            ]

            report = orchestrator.run_pipeline(
                ko_list,
                skip_publish=False
            )

            assert report["stages"]["publishing"]["status"] == "COMPLETE"
            assert report["stages"]["publishing"]["published"] == 1
            assert report["stages"]["publishing"]["rejected"] == 0

    def test_pipeline_log(self):
        """Pipeline executions should be logged."""
        orchestrator = FactoryOrchestrator()
        ko_list = [
            make_ko(urn="urn:ki:in:dpdp:act:log", title="Log Test", entities=["Act"])
        ]
        orchestrator.run_pipeline(ko_list, skip_publish=True)
        log = orchestrator.get_pipeline_log()
        assert len(log) == 1
        assert "pipeline_id" in log[0]
