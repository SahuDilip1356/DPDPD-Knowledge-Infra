"""
Factory Orchestrator — The Research Factory Pipeline Controller

Purpose:
    Orchestrates the complete data flow through all 8 permanent departments
    of the Research Factory. Manages the daily processing cycle from
    ingestion through publishing.

    Pipeline Flow:
    1. Research (Scout) → 2. Verification (Citation) → 3. Knowledge Eng (Parsing)
    → 4. Ontology → 5. Relationship Eng → 6. Reasoning → 7. Business Translation
    → 8. Publishing
"""

from typing import Dict, List, Optional
from datetime import datetime

from src.factory.scout_agent import ScoutAgent
from src.factory.parsing_agent import ParsingAgent
from src.factory.citation_agent import CitationAgent
from src.factory.ontology_agent import OntologyAgent
from src.factory.relationship_agent import RelationshipAgent
from src.factory.deduplication_agent import DeduplicationAgent
from src.factory.reasoning_agent import ReasoningAgent
from src.factory.business_translation_agent import BusinessTranslationAgent
from src.factory.publishing_agent import PublishingAgent
from src.reasoning.model_client import ModelClient


class FactoryOrchestrator:
    """
    The master conductor of the Research Factory.
    Coordinates the sequential execution of all 8 departments
    and produces a comprehensive pipeline execution report.
    """

    def __init__(self, git_ledger=None, db_client=None, model_client=None):
        """
        Initializes all department agents and wires them together.

        Args:
            git_ledger: Optional GitLedger for file-based persistence.
            db_client: Optional DatabaseClient for indexed storage.
            model_client: Optional ModelClient for visual document OCR.
        """
        self.model_client = model_client or ModelClient()

        # Department 1: Research (Scout & Collection)
        self.scout = ScoutAgent()
        # Department 2: Verification (Citation & Evidence)
        self.citation = CitationAgent()
        # Department 3: Knowledge Engineering (Parsing & Extraction)
        self.parser = ParsingAgent(model_client=self.model_client)
        # Department 4: Ontology (Vocabulary Governance)
        self.ontology = OntologyAgent()
        # Department 5: Relationship Engineering (Link Creation)
        self.relationships = RelationshipAgent()
        # Sub-department: Deduplication
        self.deduplication = DeduplicationAgent()
        # Department 6: Reasoning (Insight Generation)
        self.reasoning = ReasoningAgent()
        # Department 7: Business Translation (Legal-to-Business)
        self.business_translation = BusinessTranslationAgent()
        # Department 8: Publishing (Commit & Distribute)
        self.publishing = PublishingAgent(
            git_ledger=git_ledger,
            db_client=db_client
        )

        # Pipeline execution log
        self._pipeline_log: List[Dict] = []

    def process_evidence_packet(
        self,
        source_urn: str,
        source_layer: int,
        parsed_pages: List[Dict]
    ) -> Dict:
        """
        Runs Departments 2-3: Citation agent builds evidence packets
        from parsed document pages.

        Returns:
            Evidence packet dictionary.
        """
        return self.citation.generate_evidence_packet(
            source_urn=source_urn,
            source_layer=source_layer,
            parsed_pages=parsed_pages
        )

    def normalize_knowledge_objects(
        self, ko_list: List[dict]
    ) -> List[dict]:
        """
        Runs Department 4: Ontology normalization across all KOs.
        Resolves synonyms and validates entity/edge vocabulary.

        Returns:
            List of ontology-normalized KOs.
        """
        normalized = []
        for ko in ko_list:
            nko = self.ontology.normalize_ko(ko)
            normalized.append(nko)
        return normalized

    def build_relationships(
        self, ko_list: List[dict], min_confidence: float = 0.5
    ) -> Dict:
        """
        Runs Department 5: Relationship Engineering.
        Proposes and confirms edges between KOs.

        Returns:
            Dict with confirmed edges, orphans, and proposals.
        """
        proposals = self.relationships.propose_edges(ko_list)
        confirmed = self.relationships.confirm_edges(min_confidence=min_confidence)
        orphans = self.relationships.detect_orphans(ko_list)

        return {
            "proposals_total": len(proposals),
            "confirmed_edges": confirmed,
            "confirmed_count": len(confirmed),
            "orphan_urns": orphans,
            "orphan_count": len(orphans),
        }

    def deduplicate(
        self, ko_list: List[dict]
    ) -> Dict:
        """
        Runs Deduplication sub-department.
        Scans for duplicate KOs and proposes merges.

        Returns:
            Dict with duplicate candidates and merge recommendations.
        """
        candidates = self.deduplication.find_duplicates(ko_list)

        return {
            "duplicates_found": len(candidates),
            "candidates": candidates,
        }

    def generate_insights(
        self, ko_list: List[dict], expected_entities: List[str] = None
    ) -> Dict:
        """
        Runs Department 6: Reasoning Agent.
        Generates insights including conflicts, gaps, and emerging patterns.

        Returns:
            Insight report dictionary.
        """
        return self.reasoning.synthesize(ko_list, expected_entities or [])

    def translate_to_business(self, ko_list: List[dict]) -> Dict:
        """
        Runs Department 7: Business Translation.
        Converts legal obligations into business action items.

        Returns:
            Business translation report.
        """
        return self.business_translation.translate_batch(ko_list)

    def publish_knowledge(self, ko_list: List[dict]) -> Dict:
        """
        Runs Department 8: Publishing Agent.
        Validates and commits KOs to permanent storage.

        Returns:
            Publish report.
        """
        return self.publishing.publish_batch(ko_list)

    def run_pipeline(
        self,
        ko_list: List[dict],
        expected_entities: List[str] = None,
        edge_confidence: float = 0.5,
        skip_publish: bool = False
    ) -> Dict:
        """
        Executes the complete Research Factory pipeline:

        Dept 4 (Ontology) → Dept 5 (Relationships) → Dedup →
        Dept 6 (Reasoning) → Dept 7 (Business Translation) →
        Dept 8 (Publishing)

        Note: Departments 1-3 (Scout, Citation, Parsing) run upstream
        and feed KOs into this pipeline.

        Args:
            ko_list: List of draft Knowledge Objects to process.
            expected_entities: List of entity types expected for gap analysis.
            edge_confidence: Minimum confidence for confirming edges.
            skip_publish: If True, skips the publishing step (for dry runs).

        Returns:
            Comprehensive pipeline execution report.
        """
        pipeline_start = datetime.utcnow()
        stages = {}

        # ─── Stage 1: Ontology Normalization (Dept 4) ───────────────────
        stage_start = datetime.utcnow()
        normalized_kos = self.normalize_knowledge_objects(ko_list)
        # Strip internal ontology flags for downstream processing
        clean_kos = []
        for nko in normalized_kos:
            clean = {k: v for k, v in nko.items() if not k.startswith("_")}
            clean_kos.append(clean)
        stages["ontology"] = {
            "status": "COMPLETE",
            "kos_processed": len(clean_kos),
            "duration_ms": (datetime.utcnow() - stage_start).total_seconds() * 1000
        }

        # ─── Stage 2: Relationship Engineering (Dept 5) ─────────────────
        stage_start = datetime.utcnow()
        rel_report = self.build_relationships(clean_kos, edge_confidence)
        stages["relationships"] = {
            "status": "COMPLETE",
            **rel_report,
            "duration_ms": (datetime.utcnow() - stage_start).total_seconds() * 1000
        }

        # ─── Stage 3: Deduplication ─────────────────────────────────────
        stage_start = datetime.utcnow()
        dedup_report = self.deduplicate(clean_kos)
        stages["deduplication"] = {
            "status": "COMPLETE",
            **dedup_report,
            "duration_ms": (datetime.utcnow() - stage_start).total_seconds() * 1000
        }

        # ─── Stage 4: Reasoning (Dept 6) ────────────────────────────────
        stage_start = datetime.utcnow()
        insight_report = self.generate_insights(clean_kos, expected_entities)
        stages["reasoning"] = {
            "status": "COMPLETE",
            "total_insights": insight_report["total_insights"],
            "severity_breakdown": insight_report["severity_breakdown"],
            "duration_ms": (datetime.utcnow() - stage_start).total_seconds() * 1000
        }

        # ─── Stage 5: Business Translation (Dept 7) ────────────────────
        stage_start = datetime.utcnow()
        business_report = self.translate_to_business(clean_kos)
        stages["business_translation"] = {
            "status": "COMPLETE",
            "total_actions": business_report["total_actions"],
            "by_role": business_report["by_role"],
            "duration_ms": (datetime.utcnow() - stage_start).total_seconds() * 1000
        }

        # ─── Stage 6: Publishing (Dept 8) ──────────────────────────────
        if not skip_publish:
            stage_start = datetime.utcnow()
            publish_report = self.publish_knowledge(clean_kos)
            stages["publishing"] = {
                "status": "COMPLETE",
                "published": publish_report["published_count"],
                "rejected": publish_report["rejected_count"],
                "failed": publish_report.get("failed_count", 0),
                "duration_ms": (datetime.utcnow() - stage_start).total_seconds() * 1000
            }
        else:
            stages["publishing"] = {"status": "SKIPPED"}

        # ─── Pipeline Summary ──────────────────────────────────────────
        pipeline_end = datetime.utcnow()
        total_duration = (pipeline_end - pipeline_start).total_seconds() * 1000

        report = {
            "pipeline_id": f"pipeline-{pipeline_start.strftime('%Y%m%d-%H%M%S')}",
            "started_at": pipeline_start.isoformat(),
            "completed_at": pipeline_end.isoformat(),
            "total_duration_ms": total_duration,
            "ko_count": len(ko_list),
            "stages": stages,
            "insights": insight_report,
            "business_actions": business_report,
        }

        self._pipeline_log.append(report)

        # Write to ingestion_audit.log
        try:
            import json
            import os
            log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "staging", "ingestion_audit.log"))
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            log_entry = {
                "timestamp": pipeline_start.isoformat() + "Z",
                "pipeline_id": report["pipeline_id"],
                "ko_count": report["ko_count"],
                "published_count": report["stages"]["publishing"].get("published", 0) if "publishing" in report["stages"] else 0,
                "rejected_count": report["stages"]["publishing"].get("rejected", 0) if "publishing" in report["stages"] else 0,
                "duration_ms": total_duration,
                "status": "SUCCESS" if report["stages"]["publishing"].get("status") == "COMPLETE" else "FAILED"
            }
            with open(log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as le:
            print(f"[!] Warning: Failed to write ingestion audit log: {le}")

        return report

    def get_pipeline_log(self) -> List[Dict]:
        """Returns the log of all pipeline executions."""
        return list(self._pipeline_log)
