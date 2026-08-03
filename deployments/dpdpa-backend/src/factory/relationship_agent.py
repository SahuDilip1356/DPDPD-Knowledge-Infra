"""
Relationship Engineering Agent — Department 5: Link Creation

Purpose:
    Create typed, directed edges between Knowledge Objects.
    Everything connects. This agent analyzes Knowledge Objects and
    proposes relationships based on content overlap, legal references,
    and structural dependencies.

KPIs:
    - Edges created
    - Orphan nodes eliminated
    - Cross-layer links established
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# Pattern matchers for legal reference extraction
SECTION_PATTERN = re.compile(
    r"(?:Section|Sec\.|§)\s*(\d+[A-Za-z]?(?:\(\d+\))?)",
    re.IGNORECASE
)
RULE_PATTERN = re.compile(
    r"(?:Rule|R\.)\s*(\d+[A-Za-z]?(?:\(\d+\))?)",
    re.IGNORECASE
)
ACT_PATTERN = re.compile(
    r"(?:the\s+)?([A-Z][A-Za-z\s]+?(?:Act|Bill|Code|Ordinance)),?\s*(\d{4})?",
    re.IGNORECASE
)


class RelationshipAgent:
    """
    Analyzes Knowledge Objects and proposes typed, directed relationships
    between them. Detects legal cross-references, structural dependencies,
    and semantic overlaps to build the knowledge graph's edge layer.
    """

    def __init__(self):
        """
        Initializes the Relationship Engineering Agent.
        """
        # Registry of proposed edges awaiting confirmation
        self._proposed_edges: List[Dict] = []
        # Registry of confirmed edges
        self._confirmed_edges: List[Dict] = []
        # Audit log
        self._audit_log: List[Dict] = []

    def extract_legal_references(self, text: str) -> List[Dict]:
        """
        Extracts legal references (section numbers, rule numbers, act names)
        from a text block.
        
        Returns:
            List of reference dictionaries with type and identifier.
        """
        references = []

        for match in SECTION_PATTERN.finditer(text):
            references.append({
                "type": "section",
                "identifier": f"Section {match.group(1)}",
                "raw_match": match.group(0)
            })

        for match in RULE_PATTERN.finditer(text):
            references.append({
                "type": "rule",
                "identifier": f"Rule {match.group(1)}",
                "raw_match": match.group(0)
            })

        for match in ACT_PATTERN.finditer(text):
            act_name = match.group(1).strip()
            year = match.group(2) if match.group(2) else ""
            full_name = f"{act_name} {year}".strip() if year else act_name
            references.append({
                "type": "act",
                "identifier": full_name,
                "raw_match": match.group(0)
            })

        return references

    def detect_amendment_relationship(
        self, source_ko: dict, target_ko: dict
    ) -> Optional[Dict]:
        """
        Detects if the source KO amends or supersedes the target KO.
        Checks for title patterns like 'Amendment to...' and matching entities.
        
        Returns:
            A proposed edge dict or None.
        """
        source_title = source_ko.get("title", "").lower()
        target_title = target_ko.get("title", "").lower()

        # Check for amendment keywords in the source
        amendment_keywords = ["amendment", "amends", "amended", "modification"]
        is_amendment = any(kw in source_title for kw in amendment_keywords)

        if is_amendment:
            # Check if the target is referenced by the source
            source_summary = source_ko.get("summary", "").lower()
            target_words = set(target_title.split())
            overlap = sum(1 for w in target_words if w in source_summary and len(w) > 3)

            if overlap >= 2:
                return {
                    "source_urn": source_ko["urn"],
                    "target_urn": target_ko["urn"],
                    "edge_type": "Amends",
                    "confidence": min(0.5 + (overlap * 0.1), 1.0),
                    "evidence": f"Amendment keyword in title, {overlap} term overlaps"
                }

        return None

    def detect_dependency_relationship(
        self, source_ko: dict, target_ko: dict
    ) -> Optional[Dict]:
        """
        Detects if the source KO depends on the target KO through
        explicit legal references in the source's evidence chain.
        
        Returns:
            A proposed edge dict or None.
        """
        source_text = source_ko.get("summary", "")
        for ev in source_ko.get("evidence", []):
            source_text += " " + ev.get("citation_text", "")

        target_urn = target_ko.get("urn", "")
        target_title = target_ko.get("title", "")

        # Direct URN reference
        if target_urn in source_text:
            return {
                "source_urn": source_ko["urn"],
                "target_urn": target_ko["urn"],
                "edge_type": "Depends On",
                "confidence": 0.95,
                "evidence": "Direct URN reference in source evidence"
            }

        # Title reference check
        if len(target_title) > 5 and target_title.lower() in source_text.lower():
            return {
                "source_urn": source_ko["urn"],
                "target_urn": target_ko["urn"],
                "edge_type": "References",
                "confidence": 0.75,
                "evidence": f"Title '{target_title}' found in source text"
            }

        return None

    def detect_entity_overlap(
        self, source_ko: dict, target_ko: dict
    ) -> Optional[Dict]:
        """
        Detects shared entity references between two KOs.
        High overlap suggests a 'Supports' or 'References' relationship.
        
        Returns:
            A proposed edge dict or None if overlap is below threshold.
        """
        source_entities = set(source_ko.get("entities", []))
        target_entities = set(target_ko.get("entities", []))

        if not source_entities or not target_entities:
            return None

        overlap = source_entities & target_entities
        overlap_ratio = len(overlap) / min(len(source_entities), len(target_entities))

        if overlap_ratio >= 0.5 and len(overlap) >= 2:
            return {
                "source_urn": source_ko["urn"],
                "target_urn": target_ko["urn"],
                "edge_type": "Supports",
                "confidence": round(overlap_ratio, 2),
                "evidence": f"Entity overlap: {sorted(overlap)}"
            }

        return None

    def analyze_pair(
        self, source_ko: dict, target_ko: dict
    ) -> List[Dict]:
        """
        Runs all relationship detectors on a pair of Knowledge Objects.
        
        Returns:
            List of proposed edge dictionaries.
        """
        if source_ko.get("urn") == target_ko.get("urn"):
            return []

        proposed = []

        # Run detection strategies
        amendment = self.detect_amendment_relationship(source_ko, target_ko)
        if amendment:
            proposed.append(amendment)

        dependency = self.detect_dependency_relationship(source_ko, target_ko)
        if dependency:
            proposed.append(dependency)

        overlap = self.detect_entity_overlap(source_ko, target_ko)
        if overlap:
            proposed.append(overlap)

        return proposed

    def propose_edges(self, ko_list: List[dict]) -> List[Dict]:
        """
        Analyzes all pairwise combinations of Knowledge Objects and
        proposes edges between them.
        
        Returns:
            List of all proposed edges with confidence scores.
        """
        all_proposals = []

        for i, source in enumerate(ko_list):
            for j, target in enumerate(ko_list):
                if i == j:
                    continue
                proposals = self.analyze_pair(source, target)
                all_proposals.extend(proposals)

        # Deduplicate: keep the highest confidence for each (source, target, edge_type)
        seen = {}
        for edge in all_proposals:
            key = (edge["source_urn"], edge["target_urn"], edge["edge_type"])
            if key not in seen or edge["confidence"] > seen[key]["confidence"]:
                seen[key] = edge

        self._proposed_edges = list(seen.values())

        self._audit_log.append({
            "event": "edges_proposed",
            "ko_count": len(ko_list),
            "edges_proposed": len(self._proposed_edges),
            "timestamp": datetime.utcnow().isoformat()
        })

        return self._proposed_edges

    def confirm_edges(self, min_confidence: float = 0.6) -> List[Dict]:
        """
        Confirms proposed edges above a confidence threshold.
        
        Returns:
            List of confirmed edges ready for graph storage.
        """
        confirmed = [
            edge for edge in self._proposed_edges
            if edge.get("confidence", 0) >= min_confidence
        ]

        self._confirmed_edges.extend(confirmed)
        self._proposed_edges = [
            edge for edge in self._proposed_edges
            if edge.get("confidence", 0) < min_confidence
        ]

        self._audit_log.append({
            "event": "edges_confirmed",
            "confirmed_count": len(confirmed),
            "remaining_proposals": len(self._proposed_edges),
            "threshold": min_confidence,
            "timestamp": datetime.utcnow().isoformat()
        })

        return confirmed

    def detect_orphans(self, ko_list: List[dict]) -> List[str]:
        """
        Identifies Knowledge Objects that have zero inbound or outbound
        edges in the confirmed edge set. Orphan nodes indicate missing context.
        
        Returns:
            List of URNs of orphan KOs.
        """
        connected_urns = set()
        for edge in self._confirmed_edges:
            connected_urns.add(edge["source_urn"])
            connected_urns.add(edge["target_urn"])

        all_urns = {ko["urn"] for ko in ko_list}
        orphans = sorted(all_urns - connected_urns)

        return orphans

    def get_audit_log(self) -> List[Dict]:
        """
        Returns the audit trail of all relationship operations.
        """
        return list(self._audit_log)
