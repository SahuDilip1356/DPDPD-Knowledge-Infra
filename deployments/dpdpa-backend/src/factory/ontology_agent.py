"""
Ontology Agent — Department 4: Vocabulary Governance

Purpose:
    Maintain the canonical vocabulary registry for the Knowledge Infrastructure.
    Never allow duplicate concepts. Normalize entity references across all
    Knowledge Objects to ensure consistent terminology.

KPIs:
    - Canonical terms registered
    - Duplicates prevented
    - Synonym mappings resolved
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# ─── Canonical Entity Types (from Knowledge Constitution) ───────────────────
CANONICAL_ENTITIES = [
    "Act", "Rule", "Notification", "Circular", "Case", "Judgement",
    "Opinion", "Organization", "Person", "Template", "Risk", "Control",
    "Purpose", "Consent", "Legal Basis", "Penalty", "Data Category",
    "Industry", "Business Process", "Software", "Vendor", "Country", "Authority"
]

# ─── Canonical Edge Types ───────────────────────────────────────────────────
CANONICAL_EDGES = [
    "Amends", "Supersedes", "Interprets", "Depends On", "Overrides",
    "Conflicts With", "Supports", "Implements", "References", "Requires",
    "Applies To", "Violates", "Explains", "Replaces"
]


class OntologyAgent:
    """
    Maintains the controlled vocabulary of the knowledge graph.
    Prevents concept drift by ensuring every term used in Knowledge Objects
    maps to a canonical concept. Manages synonym resolution and term validation.
    """

    def __init__(self):
        """
        Initializes the Ontology Agent with the canonical term registries.
        """
        # Canonical term registry: normalized_key -> canonical_form
        self._entity_registry: Dict[str, str] = {}
        # Synonym map: alternate_form -> canonical_form
        self._synonym_map: Dict[str, str] = {}
        # Audit log of all normalization events
        self._audit_log: List[Dict] = []

        # Bootstrap with constitutional entity types
        for entity in CANONICAL_ENTITIES:
            self._register_canonical(entity, "entity")
        for edge in CANONICAL_EDGES:
            self._register_canonical(edge, "edge")

    def _normalize_key(self, term: str) -> str:
        """
        Generates a normalized lookup key: lowercase, stripped, collapsed whitespace.
        """
        return re.sub(r"\s+", " ", term.strip().lower())

    def _register_canonical(self, term: str, category: str) -> None:
        """
        Registers a term as canonical in the registry.
        """
        key = self._normalize_key(term)
        self._entity_registry[key] = {
            "canonical_form": term,
            "category": category,
            "registered_at": datetime.utcnow().isoformat()
        }

    def resolve_entity(self, raw_term: str) -> Optional[str]:
        """
        Resolves a raw entity term to its canonical form.
        
        Resolution order:
        1. Direct match in canonical registry
        2. Match via synonym map
        3. None (unrecognized term)
        
        Returns:
            The canonical form if found, None otherwise.
        """
        key = self._normalize_key(raw_term)

        # Direct canonical match
        if key in self._entity_registry:
            return self._entity_registry[key]["canonical_form"]

        # Synonym resolution
        if key in self._synonym_map:
            canonical_key = self._synonym_map[key]
            return self._entity_registry[canonical_key]["canonical_form"]

        return None

    def resolve_edge_type(self, raw_edge: str) -> Optional[str]:
        """
        Resolves a raw edge type string to its canonical form.
        """
        return self.resolve_entity(raw_edge)

    def register_synonym(self, synonym: str, canonical_term: str) -> bool:
        """
        Maps a synonym to an existing canonical term.
        
        Returns:
            True if the synonym was registered, False if the canonical term
            does not exist in the registry.
        """
        canonical_key = self._normalize_key(canonical_term)
        if canonical_key not in self._entity_registry:
            return False

        synonym_key = self._normalize_key(synonym)
        
        # Prevent self-referential synonyms
        if synonym_key == canonical_key:
            return True

        self._synonym_map[synonym_key] = canonical_key
        self._audit_log.append({
            "event": "synonym_registered",
            "synonym": synonym,
            "canonical": canonical_term,
            "timestamp": datetime.utcnow().isoformat()
        })
        return True

    def validate_ko_entities(self, ko_data: dict) -> Tuple[List[str], List[str]]:
        """
        Validates all entity references in a Knowledge Object against
        the canonical registry.

        Returns:
            Tuple of (valid_entities, invalid_entities)
        """
        valid = []
        invalid = []

        for entity in ko_data.get("entities", []):
            resolved = self.resolve_entity(entity)
            if resolved:
                valid.append(resolved)
            else:
                invalid.append(entity)

        return valid, invalid

    def validate_ko_relations(self, ko_data: dict) -> Tuple[List[Dict], List[Dict]]:
        """
        Validates all relationship edge types in a Knowledge Object.
        
        Returns:
            Tuple of (valid_relations, invalid_relations)
        """
        valid = []
        invalid = []

        for rel in ko_data.get("relations", []):
            edge_type = rel.get("edge_type", "")
            resolved = self.resolve_edge_type(edge_type)
            if resolved:
                valid.append({**rel, "edge_type": resolved})
            else:
                invalid.append(rel)

        return valid, invalid

    def normalize_ko(self, ko_data: dict) -> dict:
        """
        Normalizes all entity references and edge types in a Knowledge Object
        to their canonical forms. Unresolvable terms are preserved but flagged.
        
        Returns:
            The normalized KO data with a '_ontology_flags' metadata key.
        """
        normalized = dict(ko_data)
        flags = {
            "unresolved_entities": [],
            "unresolved_edges": [],
            "normalizations_applied": 0
        }

        # Normalize entities
        normalized_entities = []
        for entity in ko_data.get("entities", []):
            resolved = self.resolve_entity(entity)
            if resolved:
                normalized_entities.append(resolved)
                if resolved != entity:
                    flags["normalizations_applied"] += 1
            else:
                normalized_entities.append(entity)
                flags["unresolved_entities"].append(entity)
        normalized["entities"] = normalized_entities

        # Normalize relation edge types
        normalized_relations = []
        for rel in ko_data.get("relations", []):
            edge_type = rel.get("edge_type", "")
            resolved = self.resolve_edge_type(edge_type)
            if resolved:
                new_rel = {**rel, "edge_type": resolved}
                normalized_relations.append(new_rel)
                if resolved != edge_type:
                    flags["normalizations_applied"] += 1
            else:
                normalized_relations.append(rel)
                flags["unresolved_edges"].append(edge_type)
        normalized["relations"] = normalized_relations

        # Attach ontology metadata
        normalized["_ontology_flags"] = flags

        self._audit_log.append({
            "event": "ko_normalized",
            "urn": ko_data.get("urn", "unknown"),
            "normalizations": flags["normalizations_applied"],
            "unresolved": len(flags["unresolved_entities"]) + len(flags["unresolved_edges"]),
            "timestamp": datetime.utcnow().isoformat()
        })

        return normalized

    def get_vocabulary(self) -> Dict[str, List[str]]:
        """
        Returns the full canonical vocabulary grouped by category.
        """
        vocab: Dict[str, List[str]] = {}
        for key, entry in self._entity_registry.items():
            category = entry["category"]
            if category not in vocab:
                vocab[category] = []
            vocab[category].append(entry["canonical_form"])
        return vocab

    def get_synonyms(self) -> Dict[str, str]:
        """
        Returns the full synonym mapping: synonym -> canonical_form.
        """
        result = {}
        for synonym_key, canonical_key in self._synonym_map.items():
            canonical_form = self._entity_registry[canonical_key]["canonical_form"]
            result[synonym_key] = canonical_form
        return result

    def get_audit_log(self) -> List[Dict]:
        """
        Returns the audit trail of all ontology operations.
        """
        return list(self._audit_log)
