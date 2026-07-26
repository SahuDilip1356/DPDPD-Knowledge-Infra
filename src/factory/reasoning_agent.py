"""
Reasoning Agent — Department 6: Insight Generation

Purpose:
    Evaluate the combined meaning of Knowledge Graph changes.
    Detect conflicting opinions, legal splits, and compliance gaps.
    Generate semantic INSIGHTS — not summaries.

KPIs:
    - Conflict detection rate = 100% (zero missed contradictions)
    - Argument soundness (trust-score-weighted reasoning paths)
    - Insight quality (actionable conclusions, not paraphrases)
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime


# ─── Insight Types ──────────────────────────────────────────────────────────
INSIGHT_TYPES = [
    "CONFLICT",          # Two KOs contradict each other
    "GAP",               # Expected coverage area has no KO
    "SUPERSESSION",      # A newer KO has replaced an older one
    "EMERGING_PATTERN",  # Multiple KOs point to a convergent trend
    "COMPLIANCE_RISK",   # A change creates new compliance obligations
    "SPLIT_OPINION",     # Expert opinions diverge on interpretation
]


class ReasoningAgent:
    """
    Analyzes the Knowledge Graph to produce semantic insights.
    Does NOT summarize — it reasons over relationships, conflicts,
    and patterns to generate actionable intelligence.
    """

    def __init__(self):
        """
        Initializes the Reasoning Agent.
        """
        self._insights: List[Dict] = []
        self._audit_log: List[Dict] = []

    def detect_conflicts(self, ko_list: List[dict]) -> List[Dict]:
        """
        Scans Knowledge Objects for explicit conflict edges ('Conflicts With',
        'Overrides') and semantic contradictions in business impact directives.

        Returns:
            List of conflict insight dictionaries.
        """
        conflicts = []

        # 1. Explicit conflict edges
        for ko in ko_list:
            for rel in ko.get("relations", []):
                if rel.get("edge_type") in ("Conflicts With", "Overrides"):
                    conflicts.append({
                        "type": "CONFLICT",
                        "severity": "HIGH",
                        "source_urn": ko["urn"],
                        "target_urn": rel["target_urn"],
                        "edge_type": rel["edge_type"],
                        "description": (
                            f"KO '{ko.get('title', ko['urn'])}' explicitly "
                            f"{rel['edge_type'].lower()} "
                            f"KO '{rel['target_urn']}'"
                        ),
                        "timestamp": datetime.utcnow().isoformat()
                    })

        # 2. Semantic contradiction detection via opposing business impacts
        ko_by_urn = {ko["urn"]: ko for ko in ko_list}
        for i, ko_a in enumerate(ko_list):
            for j, ko_b in enumerate(ko_list):
                if i >= j:
                    continue

                contradiction = self._detect_impact_contradiction(ko_a, ko_b)
                if contradiction:
                    conflicts.append(contradiction)

        self._audit_log.append({
            "event": "conflict_scan",
            "ko_count": len(ko_list),
            "conflicts_found": len(conflicts),
            "timestamp": datetime.utcnow().isoformat()
        })

        return conflicts

    def _detect_impact_contradiction(
        self, ko_a: dict, ko_b: dict
    ) -> Optional[Dict]:
        """
        Detects contradictions in business impact directives between two KOs
        that share common entities but prescribe opposing actions.
        """
        entities_a = set(ko_a.get("entities", []))
        entities_b = set(ko_b.get("entities", []))
        shared = entities_a & entities_b

        if len(shared) < 2:
            return None

        impact_a = ko_a.get("business_impact", {}).get("action_required", "").lower()
        impact_b = ko_b.get("business_impact", {}).get("action_required", "").lower()

        if not impact_a or not impact_b:
            return None

        # Detect opposing action keywords
        opposing_pairs = [
            ({"allow", "permit", "enable"}, {"prohibit", "deny", "restrict", "ban"}),
            ({"mandatory", "required", "must"}, {"optional", "voluntary", "may"}),
            ({"retain", "store", "keep"}, {"delete", "erase", "destroy"}),
        ]

        for set_a, set_b in opposing_pairs:
            a_has_first = any(w in impact_a for w in set_a)
            a_has_second = any(w in impact_a for w in set_b)
            b_has_first = any(w in impact_b for w in set_a)
            b_has_second = any(w in impact_b for w in set_b)

            if (a_has_first and b_has_second) or (a_has_second and b_has_first):
                return {
                    "type": "CONFLICT",
                    "severity": "MEDIUM",
                    "source_urn": ko_a["urn"],
                    "target_urn": ko_b["urn"],
                    "edge_type": "Semantic Contradiction",
                    "shared_entities": sorted(shared),
                    "description": (
                        f"Opposing business actions detected: "
                        f"'{ko_a.get('title', '')}' vs '{ko_b.get('title', '')}' "
                        f"on shared entities {sorted(shared)}"
                    ),
                    "timestamp": datetime.utcnow().isoformat()
                }

        return None

    def detect_supersessions(self, ko_list: List[dict]) -> List[Dict]:
        """
        Identifies Knowledge Objects that have been superseded by newer versions
        or explicitly replaced via 'Supersedes' / 'Replaces' edges.

        Returns:
            List of supersession insight dictionaries.
        """
        supersessions = []

        for ko in ko_list:
            for rel in ko.get("relations", []):
                if rel.get("edge_type") in ("Supersedes", "Replaces"):
                    supersessions.append({
                        "type": "SUPERSESSION",
                        "severity": "INFO",
                        "active_urn": ko["urn"],
                        "superseded_urn": rel["target_urn"],
                        "description": (
                            f"'{ko.get('title', ko['urn'])}' has "
                            f"{rel['edge_type'].lower()} "
                            f"'{rel['target_urn']}'"
                        ),
                        "timestamp": datetime.utcnow().isoformat()
                    })

        return supersessions

    def detect_coverage_gaps(
        self, ko_list: List[dict], expected_entities: List[str]
    ) -> List[Dict]:
        """
        Identifies entity types from the expected vocabulary that have
        zero representation in the current Knowledge Object corpus.

        Returns:
            List of gap insight dictionaries.
        """
        covered = set()
        for ko in ko_list:
            covered.update(ko.get("entities", []))

        gaps = []
        for entity in expected_entities:
            if entity not in covered:
                gaps.append({
                    "type": "GAP",
                    "severity": "MEDIUM",
                    "missing_entity": entity,
                    "description": (
                        f"No Knowledge Object covers entity type '{entity}'. "
                        f"This represents a coverage gap in the knowledge graph."
                    ),
                    "timestamp": datetime.utcnow().isoformat()
                })

        self._audit_log.append({
            "event": "gap_analysis",
            "expected_count": len(expected_entities),
            "covered_count": len(covered),
            "gaps_found": len(gaps),
            "timestamp": datetime.utcnow().isoformat()
        })

        return gaps

    def detect_emerging_patterns(self, ko_list: List[dict]) -> List[Dict]:
        """
        Analyzes entity frequency and co-occurrence to identify emerging
        regulatory patterns (e.g., sudden spike in 'Consent' + 'Penalty' KOs).

        Returns:
            List of pattern insight dictionaries.
        """
        # Count entity frequencies
        entity_freq: Dict[str, int] = {}
        for ko in ko_list:
            for entity in ko.get("entities", []):
                entity_freq[entity] = entity_freq.get(entity, 0) + 1

        # Count entity co-occurrences
        cooccurrence: Dict[Tuple[str, str], int] = {}
        for ko in ko_list:
            entities = sorted(set(ko.get("entities", [])))
            for i, e1 in enumerate(entities):
                for e2 in entities[i+1:]:
                    pair = (e1, e2)
                    cooccurrence[pair] = cooccurrence.get(pair, 0) + 1

        patterns = []

        # Flag high-frequency co-occurrences (appearing in >40% of KOs)
        threshold = max(2, len(ko_list) * 0.4)
        for pair, count in cooccurrence.items():
            if count >= threshold:
                patterns.append({
                    "type": "EMERGING_PATTERN",
                    "severity": "INFO",
                    "entities": list(pair),
                    "frequency": count,
                    "ko_coverage": round(count / len(ko_list), 2) if ko_list else 0,
                    "description": (
                        f"Entities '{pair[0]}' and '{pair[1]}' co-occur in "
                        f"{count}/{len(ko_list)} KOs ({round(count/len(ko_list)*100 if ko_list else 0)}% coverage). "
                        f"This suggests an emerging regulatory pattern."
                    ),
                    "timestamp": datetime.utcnow().isoformat()
                })

        return patterns

    def detect_split_opinions(self, ko_list: List[dict]) -> List[Dict]:
        """
        Scans for objects of type 'Opinion' and checks if multiple independent
        commentaries voice diverging stances on the same Core Law URN.
        """
        opinions = [ko for ko in ko_list if ko.get("type") == "Opinion"]
        if len(opinions) < 2:
            return []

        # Map target URN -> list of opinions referencing it
        references: Dict[str, List[dict]] = {}
        for op in opinions:
            for rel in op.get("relations", []):
                target = rel.get("target_urn")
                if target:
                    references.setdefault(target, []).append(op)

        split_insights = []
        for target_urn, ops in references.items():
            if len(ops) >= 2:
                # Check for different stances
                stances = {op.get("interpretation_stance") for op in ops if op.get("interpretation_stance")}
                if len(stances) >= 2:
                    authors = [op.get("authority", "unknown") for op in ops]
                    split_insights.append({
                        "type": "SPLIT_OPINION",
                        "severity": "MEDIUM",
                        "target_urn": target_urn,
                        "description": (
                            f"Diverging legal/industry interpretations detected for Core URN '{target_urn}'. "
                            f"Commentaries by {', '.join(authors)} express split opinions: "
                            f"{', '.join(stances)}."
                        ),
                        "timestamp": datetime.utcnow().isoformat()
                    })

        return split_insights

    def synthesize(self, ko_list: List[dict], expected_entities: List[str] = None) -> Dict:
        """
        Runs the full reasoning pipeline across all detectors and produces
        a comprehensive insight report.

        Returns:
            A structured insight report with all findings.
        """
        if expected_entities is None:
            expected_entities = []

        conflicts = self.detect_conflicts(ko_list)
        supersessions = self.detect_supersessions(ko_list)
        gaps = self.detect_coverage_gaps(ko_list, expected_entities)
        patterns = self.detect_emerging_patterns(ko_list)
        split_opinions = self.detect_split_opinions(ko_list)

        all_insights = conflicts + supersessions + gaps + patterns + split_opinions
        self._insights = all_insights

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "ko_count": len(ko_list),
            "total_insights": len(all_insights),
            "summary": {
                "conflicts": len(conflicts),
                "supersessions": len(supersessions),
                "coverage_gaps": len(gaps),
                "emerging_patterns": len(patterns),
                "split_opinions": len(split_opinions)
            },
            "insights": all_insights,
            "severity_breakdown": {
                "HIGH": sum(1 for i in all_insights if i.get("severity") == "HIGH"),
                "MEDIUM": sum(1 for i in all_insights if i.get("severity") == "MEDIUM"),
                "INFO": sum(1 for i in all_insights if i.get("severity") == "INFO"),
            }
        }

        self._audit_log.append({
            "event": "synthesis_complete",
            "ko_count": len(ko_list),
            "total_insights": len(all_insights),
            "timestamp": datetime.utcnow().isoformat()
        })

        return report

    def get_insights(self) -> List[Dict]:
        """Returns all insights from the last synthesis run."""
        return list(self._insights)

    def get_audit_log(self) -> List[Dict]:
        """Returns the audit trail of all reasoning operations."""
        return list(self._audit_log)
