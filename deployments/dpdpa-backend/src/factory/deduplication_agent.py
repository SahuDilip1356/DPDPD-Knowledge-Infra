"""
Deduplication Agent — Vocabulary Alignment Sub-Department

Purpose:
    Detect and resolve duplicate or near-duplicate Knowledge Objects
    in the system. Uses fingerprinting, title similarity, and evidence
    overlap to identify candidates for merging.

KPIs:
    - Duplicates detected
    - Merge operations completed
    - False positive rate (flagged but not merged)
"""

import hashlib
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class DeduplicationAgent:
    """
    Identifies duplicate and near-duplicate Knowledge Objects using
    multi-signal fingerprinting: title similarity, evidence hash overlap,
    and entity intersection. Proposes merge candidates with confidence scores.
    """

    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initializes the Deduplication Agent.
        
        Args:
            similarity_threshold: Minimum similarity score to flag as duplicate (0.0 to 1.0).
        """
        self.similarity_threshold = similarity_threshold
        self._merge_candidates: List[Dict] = []
        self._audit_log: List[Dict] = []

    def _normalize_text(self, text: str) -> str:
        """
        Normalizes text for comparison: lowercase, strip punctuation,
        collapse whitespace.
        """
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def _compute_shingles(self, text: str, k: int = 3) -> set:
        """
        Generates k-word shingles (overlapping word n-grams) from text.
        Used for Jaccard similarity calculation.
        """
        words = self._normalize_text(text).split()
        if len(words) < k:
            return {" ".join(words)}
        return {" ".join(words[i:i+k]) for i in range(len(words) - k + 1)}

    def compute_title_similarity(self, title_a: str, title_b: str) -> float:
        """
        Computes Jaccard similarity between two titles using word shingles.
        
        Returns:
            Similarity score between 0.0 and 1.0.
        """
        shingles_a = self._compute_shingles(title_a, k=2)
        shingles_b = self._compute_shingles(title_b, k=2)

        if not shingles_a or not shingles_b:
            return 0.0

        intersection = len(shingles_a & shingles_b)
        union = len(shingles_a | shingles_b)

        return intersection / union if union > 0 else 0.0

    def compute_evidence_overlap(self, ko_a: dict, ko_b: dict) -> float:
        """
        Computes the ratio of shared evidence hashes between two KOs.
        Shared evidence strongly indicates duplicate content.
        
        Returns:
            Overlap ratio between 0.0 and 1.0.
        """
        hashes_a = set()
        for ev in ko_a.get("evidence", []):
            coords = ev.get("coordinates", {})
            h = coords.get("hash", "")
            if h:
                hashes_a.add(h)

        hashes_b = set()
        for ev in ko_b.get("evidence", []):
            coords = ev.get("coordinates", {})
            h = coords.get("hash", "")
            if h:
                hashes_b.add(h)

        if not hashes_a or not hashes_b:
            return 0.0

        intersection = len(hashes_a & hashes_b)
        union = len(hashes_a | hashes_b)

        return intersection / union if union > 0 else 0.0

    def compute_entity_overlap(self, ko_a: dict, ko_b: dict) -> float:
        """
        Computes the ratio of shared entity types between two KOs.
        
        Returns:
            Overlap ratio between 0.0 and 1.0.
        """
        entities_a = set(ko_a.get("entities", []))
        entities_b = set(ko_b.get("entities", []))

        if not entities_a or not entities_b:
            return 0.0

        intersection = len(entities_a & entities_b)
        union = len(entities_a | entities_b)

        return intersection / union if union > 0 else 0.0

    def compute_composite_similarity(self, ko_a: dict, ko_b: dict) -> Dict:
        """
        Computes a weighted composite similarity score across multiple signals.
        
        Weights:
            - Title similarity: 0.35
            - Evidence hash overlap: 0.40
            - Entity overlap: 0.25
        
        Returns:
            Dict with individual scores and composite score.
        """
        title_sim = self.compute_title_similarity(
            ko_a.get("title", ""),
            ko_b.get("title", "")
        )
        evidence_sim = self.compute_evidence_overlap(ko_a, ko_b)
        entity_sim = self.compute_entity_overlap(ko_a, ko_b)

        composite = (
            title_sim * 0.35 +
            evidence_sim * 0.40 +
            entity_sim * 0.25
        )

        return {
            "title_similarity": round(title_sim, 4),
            "evidence_overlap": round(evidence_sim, 4),
            "entity_overlap": round(entity_sim, 4),
            "composite_score": round(composite, 4)
        }

    def find_duplicates(self, ko_list: List[dict]) -> List[Dict]:
        """
        Scans all pairwise combinations of Knowledge Objects and identifies
        potential duplicates above the similarity threshold.
        
        Returns:
            List of merge candidate dictionaries with similarity details.
        """
        candidates = []
        seen_pairs = set()

        for i, ko_a in enumerate(ko_list):
            for j, ko_b in enumerate(ko_list):
                if i >= j:
                    continue

                urn_a = ko_a.get("urn", f"unknown-{i}")
                urn_b = ko_b.get("urn", f"unknown-{j}")

                # Skip if already compared
                pair_key = tuple(sorted([urn_a, urn_b]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                scores = self.compute_composite_similarity(ko_a, ko_b)

                if scores["composite_score"] >= self.similarity_threshold:
                    candidates.append({
                        "ko_a_urn": urn_a,
                        "ko_b_urn": urn_b,
                        "ko_a_title": ko_a.get("title", ""),
                        "ko_b_title": ko_b.get("title", ""),
                        **scores,
                        "recommendation": self._recommend_action(scores, ko_a, ko_b)
                    })

        self._merge_candidates = candidates

        self._audit_log.append({
            "event": "duplicate_scan",
            "ko_count": len(ko_list),
            "pairs_compared": len(seen_pairs),
            "duplicates_found": len(candidates),
            "threshold": self.similarity_threshold,
            "timestamp": datetime.utcnow().isoformat()
        })

        return candidates

    def _recommend_action(
        self, scores: Dict, ko_a: dict, ko_b: dict
    ) -> str:
        """
        Recommends an action based on similarity scores:
        - 'MERGE': Very high confidence of duplicate
        - 'REVIEW': Moderate confidence, needs human review
        - 'LINK': Not a duplicate but related, create a relationship
        """
        composite = scores["composite_score"]

        if composite >= 0.85:
            return "MERGE"
        elif composite >= 0.70:
            return "REVIEW"
        else:
            return "LINK"

    def propose_merge(self, ko_a: dict, ko_b: dict) -> dict:
        """
        Proposes a merged Knowledge Object from two duplicate KOs.
        The KO with the higher confidence score is treated as primary.
        Evidence and relations are unioned, version is incremented.
        
        Returns:
            The proposed merged KO dictionary.
        """
        # Primary is the one with higher confidence
        if ko_a.get("confidence_score", 0) >= ko_b.get("confidence_score", 0):
            primary, secondary = ko_a, ko_b
        else:
            primary, secondary = ko_b, ko_a

        merged = dict(primary)

        # Union evidence chains (deduplicate by hash)
        existing_hashes = set()
        merged_evidence = []
        for ev in primary.get("evidence", []) + secondary.get("evidence", []):
            ev_hash = ev.get("coordinates", {}).get("hash", "")
            if ev_hash and ev_hash not in existing_hashes:
                existing_hashes.add(ev_hash)
                merged_evidence.append(ev)
            elif not ev_hash:
                merged_evidence.append(ev)
        merged["evidence"] = merged_evidence

        # Union entities (deduplicate)
        merged["entities"] = sorted(set(
            primary.get("entities", []) + secondary.get("entities", [])
        ))

        # Union relations (deduplicate by target + type)
        existing_rels = set()
        merged_relations = []
        for rel in primary.get("relations", []) + secondary.get("relations", []):
            rel_key = (rel.get("target_urn", ""), rel.get("edge_type", ""))
            if rel_key not in existing_rels:
                existing_rels.add(rel_key)
                merged_relations.append(rel)
        merged["relations"] = merged_relations

        # Union linked objects
        merged["linked_objects"] = sorted(set(
            primary.get("linked_objects", []) + secondary.get("linked_objects", [])
        ))

        # Update version
        merged["version"] = max(
            primary.get("version", 1),
            secondary.get("version", 1)
        ) + 1

        # Add merge audit to history
        merge_entry = {
            "version": merged["version"],
            "system_time": datetime.utcnow().isoformat(),
            "commit_message": f"Merged from {secondary.get('urn', 'unknown')} into {primary.get('urn', 'unknown')}",
            "author_id": "deduplication_agent"
        }
        history = list(primary.get("history", []))
        history.append(merge_entry)
        merged["history"] = history

        self._audit_log.append({
            "event": "merge_proposed",
            "primary_urn": primary.get("urn"),
            "secondary_urn": secondary.get("urn"),
            "merged_version": merged["version"],
            "timestamp": datetime.utcnow().isoformat()
        })

        return merged

    def get_merge_candidates(self) -> List[Dict]:
        """
        Returns the current list of merge candidates from the last scan.
        """
        return list(self._merge_candidates)

    def get_audit_log(self) -> List[Dict]:
        """
        Returns the audit trail of all deduplication operations.
        """
        return list(self._audit_log)
