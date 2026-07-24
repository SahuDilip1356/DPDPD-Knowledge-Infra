"""
Publishing Agent — Department 8: Output & Distribution

Purpose:
    Commit validated Knowledge Objects to the Git Ledger,
    update the database index, and generate publish receipts.
    The final gate before knowledge enters the canonical record.

KPIs:
    - Transaction commit rate = 100%
    - Schema validation pass rate = 100% (nothing bypasses validation)
    - Downstream notification latency < 10 seconds
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime

from src.schemas.validate_schema import validate_ko


class PublishingAgent:
    """
    The final gate in the Research Factory pipeline.
    Validates, signs, and commits Knowledge Objects to permanent storage.
    Generates publish receipts and maintains a transaction log.
    """

    def __init__(self, git_ledger=None, db_client=None):
        """
        Initializes the Publishing Agent.

        Args:
            git_ledger: Optional GitLedger instance for file-based persistence.
            db_client: Optional DatabaseClient instance for indexed storage.
        """
        self._git_ledger = git_ledger
        self._db_client = db_client
        self._publish_log: List[Dict] = []
        self._rejected_log: List[Dict] = []
        self._audit_log: List[Dict] = []

    def validate_for_publish(self, ko_data: dict) -> Dict:
        """
        Performs pre-publish validation checks:
        1. JSON Schema compliance
        2. Required field completeness
        3. Evidence chain integrity (at least one evidence item)
        4. Relation validity (no self-referencing edges)

        Returns:
            Validation result dict with 'valid' boolean and 'errors' list.
        """
        errors = []

        # 1. JSON Schema validation
        try:
            validate_ko(ko_data)
        except Exception as e:
            errors.append(f"Schema validation failed: {str(e)}")

        # 2. Evidence chain check
        evidence = ko_data.get("evidence", [])
        if not evidence:
            errors.append("No evidence items found. Every KO must have at least one citation.")

        # 3. Self-referencing edge check
        urn = ko_data.get("urn", "")
        for rel in ko_data.get("relations", []):
            if rel.get("target_urn") == urn:
                errors.append(f"Self-referencing edge detected: {rel.get('edge_type', 'unknown')}")

        # 4. Business impact completeness
        impact = ko_data.get("business_impact", {})
        if not impact.get("impact_summary"):
            errors.append("Missing business_impact.impact_summary")
        if not impact.get("action_required"):
            errors.append("Missing business_impact.action_required")

        # 5. History chain integrity
        history = ko_data.get("history", [])
        if not history:
            errors.append("Empty history chain. At least one history entry is required.")
        else:
            versions_in_history = [h.get("version") for h in history]
            if ko_data.get("version") not in versions_in_history:
                errors.append(
                    f"Current version {ko_data.get('version')} not found in history chain."
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "urn": ko_data.get("urn", "unknown"),
            "version": ko_data.get("version", 0)
        }

    def publish(self, ko_data: dict) -> Dict:
        """
        Publishes a validated Knowledge Object to permanent storage.

        Steps:
        1. Run pre-publish validation
        2. Write to Git Ledger (if configured)
        3. Index in Database (if configured)
        4. Generate publish receipt

        Returns:
            Publish receipt dictionary.
        """
        # Step 1: Validate
        validation = self.validate_for_publish(ko_data)
        if not validation["valid"]:
            receipt = {
                "status": "REJECTED",
                "urn": ko_data.get("urn", "unknown"),
                "version": ko_data.get("version", 0),
                "errors": validation["errors"],
                "timestamp": datetime.utcnow().isoformat()
            }
            self._rejected_log.append(receipt)
            self._audit_log.append({
                "event": "publish_rejected",
                "urn": ko_data.get("urn"),
                "errors": len(validation["errors"]),
                "timestamp": datetime.utcnow().isoformat()
            })
            return receipt

        # Step 2: Write to Git Ledger
        ledger_path = None
        if self._git_ledger:
            try:
                ledger_path = self._git_ledger.write_ko(ko_data)
            except Exception as e:
                return {
                    "status": "FAILED",
                    "urn": ko_data["urn"],
                    "version": ko_data["version"],
                    "error": f"Git Ledger write failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                }

        # Step 3: Index in Database
        db_indexed = False
        if self._db_client:
            try:
                self._db_client.publish_ko(ko_data)
                db_indexed = True
            except Exception as e:
                # Non-fatal: log but don't block the publish
                self._audit_log.append({
                    "event": "db_index_warning",
                    "urn": ko_data["urn"],
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })

        # Step 4: Generate receipt
        receipt = {
            "status": "PUBLISHED",
            "urn": ko_data["urn"],
            "version": ko_data["version"],
            "title": ko_data.get("title", ""),
            "ledger_path": ledger_path,
            "db_indexed": db_indexed,
            "evidence_count": len(ko_data.get("evidence", [])),
            "relation_count": len(ko_data.get("relations", [])),
            "entity_count": len(ko_data.get("entities", [])),
            "timestamp": datetime.utcnow().isoformat()
        }

        self._publish_log.append(receipt)
        self._audit_log.append({
            "event": "ko_published",
            "urn": ko_data["urn"],
            "version": ko_data["version"],
            "timestamp": datetime.utcnow().isoformat()
        })

        return receipt

    def publish_batch(self, ko_list: List[dict]) -> Dict:
        """
        Publishes a batch of Knowledge Objects, collecting results.

        Returns:
            Batch publish report.
        """
        results = {
            "published": [],
            "rejected": [],
            "failed": [],
        }

        for ko in ko_list:
            receipt = self.publish(ko)
            if receipt["status"] == "PUBLISHED":
                results["published"].append(receipt)
            elif receipt["status"] == "REJECTED":
                results["rejected"].append(receipt)
            else:
                results["failed"].append(receipt)

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_submitted": len(ko_list),
            "published_count": len(results["published"]),
            "rejected_count": len(results["rejected"]),
            "failed_count": len(results["failed"]),
            **results
        }

        self._audit_log.append({
            "event": "batch_publish",
            "submitted": len(ko_list),
            "published": len(results["published"]),
            "rejected": len(results["rejected"]),
            "failed": len(results["failed"]),
            "timestamp": datetime.utcnow().isoformat()
        })

        return report

    def get_publish_log(self) -> List[Dict]:
        """Returns the log of all successfully published KOs."""
        return list(self._publish_log)

    def get_rejected_log(self) -> List[Dict]:
        """Returns the log of all rejected KOs."""
        return list(self._rejected_log)

    def get_audit_log(self) -> List[Dict]:
        """Returns the audit trail of all publishing operations."""
        return list(self._audit_log)
