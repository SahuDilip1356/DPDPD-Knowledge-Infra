"""
Business Translation Agent — Department 7: Legal-to-Business Conversion

Purpose:
    Convert complex legal language into concrete business actions.
    "What changes for businesses? Which controls must update?"
    Maps legal obligations to affected business roles, processes,
    and compliance controls.

KPIs:
    - Actionability score: High-quality compliance instructions
    - Control linkage precision: Accurate mapping to templates/SOPs
    - Coverage: All legal obligations mapped to business functions
"""

import re
from typing import Dict, List, Optional
from datetime import datetime


# ─── Business Role Taxonomy ─────────────────────────────────────────────────
BUSINESS_ROLES = [
    "Data Protection Officer",
    "Chief Privacy Officer",
    "IT Security Lead",
    "Legal Counsel",
    "Compliance Manager",
    "HR Director",
    "Product Manager",
    "Engineering Lead",
    "Marketing Director",
    "Vendor Management Lead",
    "Board of Directors",
    "CEO / Managing Director",
]

# ─── Compliance Action Categories ───────────────────────────────────────────
ACTION_CATEGORIES = [
    "POLICY_UPDATE",        # Update internal policies or SOPs
    "PROCESS_CHANGE",       # Change business process or workflow
    "TECHNICAL_CONTROL",    # Implement or modify technical safeguards
    "TRAINING_REQUIRED",    # Staff training or awareness
    "DOCUMENTATION",        # Create or update documentation
    "VENDOR_REVIEW",        # Review third-party contracts or vendors
    "RISK_ASSESSMENT",      # Conduct risk assessment or DPIA
    "NOTIFICATION",         # Send notifications to data principals
    "CONSENT_REVIEW",       # Review consent mechanisms
    "DATA_MAPPING",         # Update data flow maps or inventories
]

# ─── Keyword to Action Category Mapping ─────────────────────────────────────
OBLIGATION_KEYWORDS = {
    "consent": {"category": "CONSENT_REVIEW", "roles": ["Data Protection Officer", "Product Manager"]},
    "notice": {"category": "NOTIFICATION", "roles": ["Legal Counsel", "Data Protection Officer"]},
    "notify": {"category": "NOTIFICATION", "roles": ["Data Protection Officer", "Compliance Manager"]},
    "breach": {"category": "NOTIFICATION", "roles": ["IT Security Lead", "Data Protection Officer", "CEO / Managing Director"]},
    "security": {"category": "TECHNICAL_CONTROL", "roles": ["IT Security Lead", "Engineering Lead"]},
    "safeguard": {"category": "TECHNICAL_CONTROL", "roles": ["IT Security Lead", "Engineering Lead"]},
    "encrypt": {"category": "TECHNICAL_CONTROL", "roles": ["IT Security Lead", "Engineering Lead"]},
    "training": {"category": "TRAINING_REQUIRED", "roles": ["HR Director", "Compliance Manager"]},
    "awareness": {"category": "TRAINING_REQUIRED", "roles": ["HR Director", "Compliance Manager"]},
    "policy": {"category": "POLICY_UPDATE", "roles": ["Legal Counsel", "Compliance Manager"]},
    "procedure": {"category": "PROCESS_CHANGE", "roles": ["Compliance Manager"]},
    "process": {"category": "PROCESS_CHANGE", "roles": ["Compliance Manager", "Product Manager"]},
    "vendor": {"category": "VENDOR_REVIEW", "roles": ["Vendor Management Lead", "Legal Counsel"]},
    "processor": {"category": "VENDOR_REVIEW", "roles": ["Vendor Management Lead", "Data Protection Officer"]},
    "third party": {"category": "VENDOR_REVIEW", "roles": ["Vendor Management Lead"]},
    "risk": {"category": "RISK_ASSESSMENT", "roles": ["Data Protection Officer", "Compliance Manager"]},
    "impact assessment": {"category": "RISK_ASSESSMENT", "roles": ["Data Protection Officer"]},
    "dpia": {"category": "RISK_ASSESSMENT", "roles": ["Data Protection Officer"]},
    "record": {"category": "DOCUMENTATION", "roles": ["Compliance Manager"]},
    "document": {"category": "DOCUMENTATION", "roles": ["Compliance Manager", "Legal Counsel"]},
    "retain": {"category": "DATA_MAPPING", "roles": ["Data Protection Officer", "IT Security Lead"]},
    "delete": {"category": "DATA_MAPPING", "roles": ["IT Security Lead", "Data Protection Officer"]},
    "erase": {"category": "DATA_MAPPING", "roles": ["IT Security Lead", "Data Protection Officer"]},
    "transfer": {"category": "DATA_MAPPING", "roles": ["Data Protection Officer", "Legal Counsel"]},
    "penalty": {"category": "RISK_ASSESSMENT", "roles": ["Legal Counsel", "CEO / Managing Director", "Board of Directors"]},
    "fine": {"category": "RISK_ASSESSMENT", "roles": ["Legal Counsel", "CEO / Managing Director"]},
}


class BusinessTranslationAgent:
    """
    Translates legal obligations from Knowledge Objects into concrete
    business actions, assigns responsible roles, and generates
    compliance action items with priority and deadline guidance.
    """

    def __init__(self):
        """
        Initializes the Business Translation Agent.
        """
        self._action_items: List[Dict] = []
        self._audit_log: List[Dict] = []

    def extract_obligations(self, ko_data: dict) -> List[Dict]:
        """
        Extracts obligation signals from a Knowledge Object's summary,
        evidence, and business_impact fields by scanning for regulatory
        action keywords.

        Returns:
            List of detected obligation dictionaries.
        """
        # Combine all text sources for scanning
        text_sources = [
            ko_data.get("summary", ""),
            ko_data.get("business_impact", {}).get("impact_summary", ""),
            ko_data.get("business_impact", {}).get("action_required", ""),
        ]
        for ev in ko_data.get("evidence", []):
            text_sources.append(ev.get("citation_text", ""))

        full_text = " ".join(text_sources).lower()

        obligations = []
        seen_categories = set()

        for keyword, mapping in OBLIGATION_KEYWORDS.items():
            if keyword in full_text and mapping["category"] not in seen_categories:
                seen_categories.add(mapping["category"])
                obligations.append({
                    "trigger_keyword": keyword,
                    "category": mapping["category"],
                    "affected_roles": mapping["roles"],
                    "source_urn": ko_data.get("urn", "unknown"),
                })

        return obligations

    def assess_priority(self, ko_data: dict, obligation: Dict) -> str:
        """
        Assesses priority level of an obligation based on:
        - Source layer (Layer 1-3 = CRITICAL, 4-5 = HIGH, 6-8 = MEDIUM)
        - Confidence score
        - Penalty-related keywords

        Returns:
            Priority level: "CRITICAL", "HIGH", "MEDIUM", or "LOW"
        """
        layer = ko_data.get("source", {}).get("layer", 8)
        confidence = ko_data.get("confidence_score", 0.5)
        category = obligation.get("category", "")

        # Penalty or breach = always HIGH+
        if category in ("RISK_ASSESSMENT",) and obligation.get("trigger_keyword") in ("penalty", "fine", "breach"):
            return "CRITICAL"

        # Layer-based priority
        if layer <= 3:
            base = "CRITICAL" if confidence >= 0.8 else "HIGH"
        elif layer <= 5:
            base = "HIGH" if confidence >= 0.7 else "MEDIUM"
        else:
            base = "MEDIUM" if confidence >= 0.6 else "LOW"

        return base

    def generate_action_items(self, ko_data: dict) -> List[Dict]:
        """
        Generates concrete business action items from a Knowledge Object.
        Each action item includes the obligation, responsible roles,
        priority, and recommended deadline category.

        Returns:
            List of action item dictionaries.
        """
        obligations = self.extract_obligations(ko_data)
        action_items = []

        for obligation in obligations:
            priority = self.assess_priority(ko_data, obligation)

            action_item = {
                "urn": ko_data.get("urn", "unknown"),
                "ko_title": ko_data.get("title", ""),
                "obligation_category": obligation["category"],
                "trigger": obligation["trigger_keyword"],
                "priority": priority,
                "affected_roles": obligation["affected_roles"],
                "action_description": self._generate_action_description(
                    obligation, ko_data
                ),
                "deadline_category": self._recommend_deadline(priority),
                "status": "OPEN",
                "created_at": datetime.utcnow().isoformat()
            }
            action_items.append(action_item)

        self._action_items.extend(action_items)

        self._audit_log.append({
            "event": "actions_generated",
            "urn": ko_data.get("urn"),
            "obligations_found": len(obligations),
            "actions_created": len(action_items),
            "timestamp": datetime.utcnow().isoformat()
        })

        return action_items

    def _generate_action_description(
        self, obligation: Dict, ko_data: dict
    ) -> str:
        """
        Generates a human-readable action description from the obligation.
        """
        category = obligation["category"]
        title = ko_data.get("title", "the regulation")
        keyword = obligation["trigger_keyword"]

        descriptions = {
            "CONSENT_REVIEW": f"Review and update consent mechanisms in response to '{title}'. Ensure consent collection aligns with '{keyword}' requirements.",
            "NOTIFICATION": f"Prepare and send required notifications as mandated by '{title}'. Review '{keyword}' obligations for compliance.",
            "TECHNICAL_CONTROL": f"Implement or update technical safeguards required by '{title}'. Address '{keyword}' requirements in security architecture.",
            "TRAINING_REQUIRED": f"Conduct staff training on obligations introduced by '{title}'. Focus on '{keyword}' awareness and compliance procedures.",
            "POLICY_UPDATE": f"Update internal policies and SOPs to reflect changes in '{title}'. Address '{keyword}' requirements.",
            "PROCESS_CHANGE": f"Review and modify business processes to comply with '{title}'. Incorporate '{keyword}' requirements into workflows.",
            "VENDOR_REVIEW": f"Review third-party contracts and vendor arrangements in light of '{title}'. Ensure '{keyword}' compliance across supply chain.",
            "RISK_ASSESSMENT": f"Conduct risk assessment or DPIA as required by '{title}'. Evaluate '{keyword}' implications on data processing activities.",
            "DOCUMENTATION": f"Create or update compliance documentation as required by '{title}'. Ensure '{keyword}' records are maintained.",
            "DATA_MAPPING": f"Update data flow maps and inventories to reflect '{title}' requirements. Address '{keyword}' obligations in data lifecycle.",
        }

        return descriptions.get(category, f"Address '{keyword}' obligations from '{title}'.")

    def _recommend_deadline(self, priority: str) -> str:
        """
        Recommends a deadline category based on priority.
        """
        deadlines = {
            "CRITICAL": "IMMEDIATE (within 7 days)",
            "HIGH": "SHORT_TERM (within 30 days)",
            "MEDIUM": "MEDIUM_TERM (within 90 days)",
            "LOW": "LONG_TERM (within 180 days)",
        }
        return deadlines.get(priority, "MEDIUM_TERM (within 90 days)")

    def translate_batch(self, ko_list: List[dict]) -> Dict:
        """
        Processes a batch of Knowledge Objects and generates a consolidated
        business translation report.

        Returns:
            A structured report with all action items grouped by priority.
        """
        all_actions = []
        for ko in ko_list:
            actions = self.generate_action_items(ko)
            all_actions.extend(actions)

        # Group by priority
        by_priority = {}
        for action in all_actions:
            p = action["priority"]
            if p not in by_priority:
                by_priority[p] = []
            by_priority[p].append(action)

        # Group by role
        by_role: Dict[str, List[Dict]] = {}
        for action in all_actions:
            for role in action["affected_roles"]:
                if role not in by_role:
                    by_role[role] = []
                by_role[role].append(action)

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "ko_count": len(ko_list),
            "total_actions": len(all_actions),
            "by_priority": by_priority,
            "by_role": {role: len(items) for role, items in by_role.items()},
            "actions": all_actions,
        }

        self._audit_log.append({
            "event": "batch_translation",
            "ko_count": len(ko_list),
            "total_actions": len(all_actions),
            "timestamp": datetime.utcnow().isoformat()
        })

        return report

    def get_action_items(self) -> List[Dict]:
        """Returns all action items generated so far."""
        return list(self._action_items)

    def get_audit_log(self) -> List[Dict]:
        """Returns the audit trail of all translation operations."""
        return list(self._audit_log)
