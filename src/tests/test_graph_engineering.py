"""
Test Suite — Sprint 4: Graph Engineering & Vocabulary Alignment

Tests the Ontology Agent, Relationship Engineering Agent, and Deduplication Agent.
"""

import pytest
import sys
import os

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.factory.ontology_agent import OntologyAgent, CANONICAL_ENTITIES, CANONICAL_EDGES
from src.factory.relationship_agent import RelationshipAgent
from src.factory.deduplication_agent import DeduplicationAgent


# ─── Test Fixtures ──────────────────────────────────────────────────────────

def make_ko(urn, title, entities, relations=None, evidence=None,
            summary="", confidence=0.8, version=1, linked_objects=None):
    """Helper to create a minimal Knowledge Object for testing."""
    return {
        "urn": urn,
        "title": title,
        "source": {"name": "Test Source", "layer": 1},
        "date": "2024-01-15",
        "version": version,
        "summary": summary or f"Summary for {title}",
        "entities": entities,
        "evidence": evidence or [],
        "business_impact": {
            "impact_summary": "Test impact",
            "action_required": "Test action"
        },
        "confidence_score": confidence,
        "relations": relations or [],
        "linked_objects": linked_objects or [],
        "history": [{
            "version": version,
            "system_time": "2024-01-15T00:00:00Z",
            "commit_message": "Initial creation"
        }]
    }


# ═══════════════════════════════════════════════════════════════════════════
# ONTOLOGY AGENT TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestOntologyAgent:

    def test_canonical_entities_loaded(self):
        """All 23 constitutional entities should be in the registry."""
        agent = OntologyAgent()
        for entity in CANONICAL_ENTITIES:
            resolved = agent.resolve_entity(entity)
            assert resolved == entity, f"Entity '{entity}' not found in registry"

    def test_canonical_edges_loaded(self):
        """All 14 edge types should be in the registry."""
        agent = OntologyAgent()
        for edge in CANONICAL_EDGES:
            resolved = agent.resolve_edge_type(edge)
            assert resolved == edge, f"Edge '{edge}' not found in registry"

    def test_case_insensitive_resolution(self):
        """Entity resolution should be case-insensitive."""
        agent = OntologyAgent()
        assert agent.resolve_entity("act") == "Act"
        assert agent.resolve_entity("ACT") == "Act"
        assert agent.resolve_entity("  act  ") == "Act"
        assert agent.resolve_entity("LEGAL BASIS") == "Legal Basis"

    def test_unknown_entity_returns_none(self):
        """Unregistered terms should return None."""
        agent = OntologyAgent()
        assert agent.resolve_entity("Blockchain") is None
        assert agent.resolve_entity("Random Concept") is None

    def test_synonym_registration(self):
        """Synonyms should resolve to their canonical form."""
        agent = OntologyAgent()
        assert agent.register_synonym("Law", "Act") is True
        assert agent.resolve_entity("Law") == "Act"
        assert agent.resolve_entity("law") == "Act"

    def test_synonym_for_nonexistent_canonical_fails(self):
        """Synonyms for non-existent canonical terms should fail."""
        agent = OntologyAgent()
        assert agent.register_synonym("Widget", "Nonexistent") is False

    def test_validate_ko_entities(self):
        """Validates entity lists in a KO against the canonical registry."""
        agent = OntologyAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:act:test-1",
            title="Test Act",
            entities=["Act", "Rule", "InvalidEntity", "Person"]
        )
        valid, invalid = agent.validate_ko_entities(ko)
        assert "Act" in valid
        assert "Rule" in valid
        assert "Person" in valid
        assert "InvalidEntity" in invalid
        assert len(valid) == 3
        assert len(invalid) == 1

    def test_validate_ko_relations(self):
        """Validates relation edge types against the canonical registry."""
        agent = OntologyAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:act:test-1",
            title="Test Act",
            entities=["Act"],
            relations=[
                {"target_urn": "urn:ki:in:dpdp:rule:test-2", "edge_type": "Amends"},
                {"target_urn": "urn:ki:in:dpdp:rule:test-3", "edge_type": "InvalidEdge"}
            ]
        )
        valid, invalid = agent.validate_ko_relations(ko)
        assert len(valid) == 1
        assert valid[0]["edge_type"] == "Amends"
        assert len(invalid) == 1

    def test_normalize_ko(self):
        """normalize_ko should convert terms to canonical forms and flag issues."""
        agent = OntologyAgent()
        agent.register_synonym("Law", "Act")
        agent.register_synonym("Modifies", "Amends")

        ko = make_ko(
            urn="urn:ki:in:dpdp:act:test-1",
            title="Test",
            entities=["Law", "Rule", "WeirdThing"],
            relations=[
                {"target_urn": "urn:ki:in:dpdp:rule:x", "edge_type": "Modifies"},
                {"target_urn": "urn:ki:in:dpdp:rule:y", "edge_type": "BadEdge"}
            ]
        )

        normalized = agent.normalize_ko(ko)

        assert "Act" in normalized["entities"]  # Law -> Act
        assert "Rule" in normalized["entities"]  # Unchanged
        assert "WeirdThing" in normalized["entities"]  # Preserved (unresolved)

        assert normalized["relations"][0]["edge_type"] == "Amends"  # Modifies -> Amends

        flags = normalized["_ontology_flags"]
        assert "WeirdThing" in flags["unresolved_entities"]
        assert "BadEdge" in flags["unresolved_edges"]
        assert flags["normalizations_applied"] == 2  # Law->Act, Modifies->Amends

    def test_get_vocabulary(self):
        """get_vocabulary should return terms grouped by category."""
        agent = OntologyAgent()
        vocab = agent.get_vocabulary()
        assert "entity" in vocab
        assert "edge" in vocab
        assert "Act" in vocab["entity"]
        assert "Amends" in vocab["edge"]

    def test_audit_log(self):
        """Operations should be recorded in the audit log."""
        agent = OntologyAgent()
        agent.register_synonym("Law", "Act")
        ko = make_ko(
            urn="urn:ki:in:dpdp:act:test-1",
            title="Test", entities=["Act"]
        )
        agent.normalize_ko(ko)

        log = agent.get_audit_log()
        assert len(log) >= 2
        events = [entry["event"] for entry in log]
        assert "synonym_registered" in events
        assert "ko_normalized" in events


# ═══════════════════════════════════════════════════════════════════════════
# RELATIONSHIP ENGINEERING AGENT TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestRelationshipAgent:

    def test_extract_section_references(self):
        """Should extract Section references from legal text."""
        agent = RelationshipAgent()
        refs = agent.extract_legal_references(
            "As per Section 7(1) of the Act, and Section 12 mandates..."
        )
        section_refs = [r for r in refs if r["type"] == "section"]
        assert len(section_refs) >= 2
        identifiers = [r["identifier"] for r in section_refs]
        assert "Section 7(1)" in identifiers
        assert "Section 12" in identifiers

    def test_extract_rule_references(self):
        """Should extract Rule references from legal text."""
        agent = RelationshipAgent()
        refs = agent.extract_legal_references(
            "Rule 4 specifies the format. See also Rule 7A."
        )
        rule_refs = [r for r in refs if r["type"] == "rule"]
        assert len(rule_refs) >= 2

    def test_extract_act_references(self):
        """Should extract Act name references."""
        agent = RelationshipAgent()
        refs = agent.extract_legal_references(
            "Under the Digital Personal Data Protection Act, 2023, the controller must..."
        )
        act_refs = [r for r in refs if r["type"] == "act"]
        assert len(act_refs) >= 1

    def test_amendment_detection(self):
        """Should detect amendment relationships from title keywords."""
        agent = RelationshipAgent()
        source = make_ko(
            urn="urn:ki:in:dpdp:notification:amend-1",
            title="Amendment to Data Protection Rules 2024",
            entities=["Rule", "Notification"],
            summary="This amends the Data Protection Rules concerning consent."
        )
        target = make_ko(
            urn="urn:ki:in:dpdp:rule:data-protection-rules",
            title="Data Protection Rules 2024",
            entities=["Rule"]
        )
        result = agent.detect_amendment_relationship(source, target)
        assert result is not None
        assert result["edge_type"] == "Amends"
        assert result["confidence"] > 0.5

    def test_dependency_detection_by_title(self):
        """Should detect dependency when target title appears in source text."""
        agent = RelationshipAgent()
        source = make_ko(
            urn="urn:ki:in:dpdp:circular:c-1",
            title="Circular on Consent Framework",
            entities=["Circular", "Consent"],
            summary="This circular implements Digital Personal Data Protection Act 2023 consent requirements."
        )
        target = make_ko(
            urn="urn:ki:in:dpdp:act:dpdpa",
            title="Digital Personal Data Protection Act 2023",
            entities=["Act"]
        )
        result = agent.detect_dependency_relationship(source, target)
        assert result is not None
        assert result["edge_type"] == "References"

    def test_entity_overlap_detection(self):
        """Should detect entity overlap above threshold."""
        agent = RelationshipAgent()
        ko_a = make_ko(
            urn="urn:ki:in:dpdp:act:a-1",
            title="KO A",
            entities=["Act", "Rule", "Consent", "Purpose"]
        )
        ko_b = make_ko(
            urn="urn:ki:in:dpdp:rule:b-1",
            title="KO B",
            entities=["Rule", "Consent", "Purpose", "Penalty"]
        )
        result = agent.detect_entity_overlap(ko_a, ko_b)
        assert result is not None
        assert result["edge_type"] == "Supports"
        assert result["confidence"] >= 0.5

    def test_no_self_relationship(self):
        """Should not create edges between a KO and itself."""
        agent = RelationshipAgent()
        ko = make_ko(
            urn="urn:ki:in:dpdp:act:self",
            title="Self Test",
            entities=["Act"]
        )
        edges = agent.analyze_pair(ko, ko)
        assert len(edges) == 0

    def test_propose_edges_across_list(self):
        """propose_edges should analyze all pairs and deduplicate."""
        agent = RelationshipAgent()
        ko_list = [
            make_ko(
                urn="urn:ki:in:dpdp:act:a-1",
                title="Amendment to Consent Rules",
                entities=["Act", "Rule", "Consent"],
                summary="Amends the Consent Rules 2024 framework."
            ),
            make_ko(
                urn="urn:ki:in:dpdp:rule:r-1",
                title="Consent Rules 2024",
                entities=["Rule", "Consent", "Purpose"]
            ),
            make_ko(
                urn="urn:ki:in:dpdp:case:c-1",
                title="Unrelated Case",
                entities=["Case", "Judgement"]
            )
        ]
        proposals = agent.propose_edges(ko_list)
        assert isinstance(proposals, list)
        # Should find at least the entity overlap between first two KOs
        urns_in_edges = {(e["source_urn"], e["target_urn"]) for e in proposals}
        assert len(proposals) > 0

    def test_confirm_edges_with_threshold(self):
        """confirm_edges should filter by confidence threshold."""
        agent = RelationshipAgent()
        agent._proposed_edges = [
            {"source_urn": "a", "target_urn": "b", "edge_type": "Amends", "confidence": 0.9},
            {"source_urn": "c", "target_urn": "d", "edge_type": "Supports", "confidence": 0.4},
        ]
        confirmed = agent.confirm_edges(min_confidence=0.6)
        assert len(confirmed) == 1
        assert confirmed[0]["edge_type"] == "Amends"

    def test_detect_orphans(self):
        """Should identify KOs with zero edges."""
        agent = RelationshipAgent()
        agent._confirmed_edges = [
            {"source_urn": "urn:a", "target_urn": "urn:b", "edge_type": "Amends"}
        ]
        ko_list = [
            make_ko(urn="urn:a", title="A", entities=["Act"]),
            make_ko(urn="urn:b", title="B", entities=["Rule"]),
            make_ko(urn="urn:c", title="C", entities=["Case"]),
        ]
        orphans = agent.detect_orphans(ko_list)
        assert "urn:c" in orphans
        assert "urn:a" not in orphans


# ═══════════════════════════════════════════════════════════════════════════
# DEDUPLICATION AGENT TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestDeduplicationAgent:

    def test_title_similarity_identical(self):
        """Identical titles should have similarity of 1.0."""
        agent = DeduplicationAgent()
        score = agent.compute_title_similarity(
            "Data Protection Act 2023",
            "Data Protection Act 2023"
        )
        assert score == 1.0

    def test_title_similarity_different(self):
        """Completely different titles should have low similarity."""
        agent = DeduplicationAgent()
        score = agent.compute_title_similarity(
            "Data Protection Act 2023",
            "Quantum Computing Standards 2025"
        )
        assert score < 0.3

    def test_title_similarity_partial(self):
        """Partially similar titles should have moderate similarity."""
        agent = DeduplicationAgent()
        score = agent.compute_title_similarity(
            "Digital Personal Data Protection Act 2023",
            "Data Protection Act 2023"
        )
        assert score > 0.3

    def test_evidence_overlap_identical_hashes(self):
        """KOs with identical evidence hashes should have high overlap."""
        agent = DeduplicationAgent()
        evidence = [
            {"source_urn": "s1", "citation_text": "text",
             "coordinates": {"hash": "abc123" + "0" * 58}},
            {"source_urn": "s2", "citation_text": "text2",
             "coordinates": {"hash": "def456" + "0" * 58}},
        ]
        ko_a = make_ko(urn="urn:a", title="A", entities=["Act"], evidence=evidence)
        ko_b = make_ko(urn="urn:b", title="B", entities=["Act"], evidence=evidence)
        score = agent.compute_evidence_overlap(ko_a, ko_b)
        assert score == 1.0

    def test_evidence_overlap_no_hashes(self):
        """KOs with no evidence hashes should return 0.0."""
        agent = DeduplicationAgent()
        ko_a = make_ko(urn="urn:a", title="A", entities=["Act"])
        ko_b = make_ko(urn="urn:b", title="B", entities=["Act"])
        score = agent.compute_evidence_overlap(ko_a, ko_b)
        assert score == 0.0

    def test_composite_similarity(self):
        """Composite score should combine all signals."""
        agent = DeduplicationAgent()
        ko_a = make_ko(
            urn="urn:a",
            title="Data Protection Act 2023",
            entities=["Act", "Rule", "Consent"]
        )
        ko_b = make_ko(
            urn="urn:b",
            title="Data Protection Act 2023",
            entities=["Act", "Rule", "Consent"]
        )
        scores = agent.compute_composite_similarity(ko_a, ko_b)
        assert scores["title_similarity"] == 1.0
        assert scores["entity_overlap"] == 1.0
        assert scores["composite_score"] > 0.5

    def test_find_duplicates_detects_match(self):
        """Should flag near-identical KOs as duplicates."""
        agent = DeduplicationAgent(similarity_threshold=0.5)
        ko_list = [
            make_ko(
                urn="urn:ki:in:dpdp:act:dpdpa-v1",
                title="Data Protection Act 2023",
                entities=["Act", "Rule", "Consent"]
            ),
            make_ko(
                urn="urn:ki:in:dpdp:act:dpdpa-v2",
                title="Data Protection Act 2023",
                entities=["Act", "Rule", "Consent"]
            ),
            make_ko(
                urn="urn:ki:in:dpdp:case:unrelated",
                title="Supreme Court Judgement on Tax",
                entities=["Case", "Judgement"]
            )
        ]
        duplicates = agent.find_duplicates(ko_list)
        assert len(duplicates) >= 1
        # The two DPDPA KOs should be flagged
        dup_urns = [(d["ko_a_urn"], d["ko_b_urn"]) for d in duplicates]
        assert any(
            "dpdpa-v1" in a and "dpdpa-v2" in b
            for a, b in dup_urns
        )

    def test_find_duplicates_no_false_positives(self):
        """Completely different KOs should not be flagged."""
        agent = DeduplicationAgent(similarity_threshold=0.7)
        ko_list = [
            make_ko(
                urn="urn:ki:in:dpdp:act:alpha",
                title="Digital Personal Data Protection Act",
                entities=["Act", "Consent"]
            ),
            make_ko(
                urn="urn:ki:in:dpdp:case:beta",
                title="Supreme Court Tax Ruling 2025",
                entities=["Case", "Judgement"]
            )
        ]
        duplicates = agent.find_duplicates(ko_list)
        assert len(duplicates) == 0

    def test_recommend_merge(self):
        """High-similarity pairs should get MERGE recommendation."""
        agent = DeduplicationAgent()
        scores = {"composite_score": 0.90}
        ko_a = make_ko(urn="a", title="A", entities=[])
        ko_b = make_ko(urn="b", title="B", entities=[])
        action = agent._recommend_action(scores, ko_a, ko_b)
        assert action == "MERGE"

    def test_recommend_review(self):
        """Moderate-similarity pairs should get REVIEW recommendation."""
        agent = DeduplicationAgent()
        scores = {"composite_score": 0.75}
        ko_a = make_ko(urn="a", title="A", entities=[])
        ko_b = make_ko(urn="b", title="B", entities=[])
        action = agent._recommend_action(scores, ko_a, ko_b)
        assert action == "REVIEW"

    def test_propose_merge_unions_evidence(self):
        """Merged KO should union evidence from both sources."""
        agent = DeduplicationAgent()
        ev_a = [
            {"source_urn": "s1", "citation_text": "t1",
             "coordinates": {"hash": "aaa" + "0" * 61}},
        ]
        ev_b = [
            {"source_urn": "s2", "citation_text": "t2",
             "coordinates": {"hash": "bbb" + "0" * 61}},
        ]
        ko_a = make_ko(
            urn="urn:a", title="A", entities=["Act", "Rule"],
            evidence=ev_a, confidence=0.9
        )
        ko_b = make_ko(
            urn="urn:b", title="B", entities=["Rule", "Consent"],
            evidence=ev_b, confidence=0.7
        )
        merged = agent.propose_merge(ko_a, ko_b)

        # Primary should be ko_a (higher confidence)
        assert merged["urn"] == "urn:a"
        # Evidence unioned
        assert len(merged["evidence"]) == 2
        # Entities unioned and sorted
        assert "Act" in merged["entities"]
        assert "Consent" in merged["entities"]
        assert "Rule" in merged["entities"]
        # Version incremented
        assert merged["version"] == 2
        # History has merge entry
        last_history = merged["history"][-1]
        assert "Merged" in last_history["commit_message"]
        assert last_history["author_id"] == "deduplication_agent"

    def test_audit_log(self):
        """Deduplication operations should be recorded."""
        agent = DeduplicationAgent(similarity_threshold=0.5)
        ko_list = [
            make_ko(urn="urn:a", title="Test A", entities=["Act"]),
            make_ko(urn="urn:b", title="Test B", entities=["Rule"]),
        ]
        agent.find_duplicates(ko_list)
        log = agent.get_audit_log()
        assert len(log) >= 1
        assert log[0]["event"] == "duplicate_scan"


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION TEST: Full Pipeline Flow
# ═══════════════════════════════════════════════════════════════════════════

class TestGraphEngineeringIntegration:

    def test_full_pipeline_flow(self):
        """
        End-to-end test: Ontology normalizes KOs -> Relationship Agent proposes
        edges -> Deduplication Agent scans for duplicates.
        """
        # Step 1: Create KOs
        ko_list = [
            make_ko(
                urn="urn:ki:in:dpdp:act:dpdpa-2023",
                title="Digital Personal Data Protection Act 2023",
                entities=["Act", "Consent", "Purpose", "Penalty"],
                summary="The primary legislation governing personal data protection in India."
            ),
            make_ko(
                urn="urn:ki:in:dpdp:rule:consent-rules",
                title="Consent Rules 2024",
                entities=["Rule", "Consent", "Purpose"],
                summary="Rules implementing Digital Personal Data Protection Act 2023 consent requirements."
            ),
            make_ko(
                urn="urn:ki:in:dpdp:circular:dpb-circular-1",
                title="DPB Circular on Consent Framework",
                entities=["Circular", "Consent"],
                summary="Circular implementing the Consent Rules 2024 framework."
            )
        ]

        # Step 2: Ontology normalization
        ontology = OntologyAgent()
        ontology.register_synonym("Law", "Act")

        normalized_kos = [ontology.normalize_ko(ko) for ko in ko_list]
        for nko in normalized_kos:
            valid, invalid = ontology.validate_ko_entities(nko)
            assert len(invalid) == 0, f"Unexpected invalid entities: {invalid}"

        # Step 3: Relationship Engineering
        rel_agent = RelationshipAgent()
        proposals = rel_agent.propose_edges(normalized_kos)
        assert len(proposals) > 0, "Should find at least one relationship"

        confirmed = rel_agent.confirm_edges(min_confidence=0.5)
        assert len(confirmed) > 0, "Should confirm at least one edge"

        orphans = rel_agent.detect_orphans(normalized_kos)
        # All three KOs should be connected via entity overlap
        assert len(orphans) < len(normalized_kos), "Should have fewer orphans than total KOs"

        # Step 4: Deduplication scan (should find NO duplicates here)
        dedup = DeduplicationAgent(similarity_threshold=0.8)
        duplicates = dedup.find_duplicates(normalized_kos)
        assert len(duplicates) == 0, "These distinct KOs should not be flagged as duplicates"

        # Verify audit trails exist
        assert len(ontology.get_audit_log()) > 0
        assert len(rel_agent.get_audit_log()) > 0
        assert len(dedup.get_audit_log()) > 0
