import os
import json
import re
from src.schemas.validate_schema import validate_ko

class GitLedger:
    def __init__(self, base_dir: str):
        """
        Initializes the Git Ledger client pointed to a local directory structure.
        """
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def parse_urn(self, urn: str) -> dict:
        """
        Parses a URN like urn:ki:in:dpdp:rule:consent-notice to extract metadata parts.
        """
        pattern = r"^urn:ki:([a-z0-9_-]+):([a-z0-9_-]+):([a-z0-9_-]+):([a-z0-9_-]+(?::[a-z0-9_-]+)*)$"
        match = re.match(pattern, urn)
        if not match:
            raise ValueError(f"Invalid URN format for ledger: {urn}")
            
        jurisdiction, domain, type_name, object_id = match.groups()
        return {
            "jurisdiction": jurisdiction,
            "domain": domain,
            "type": type_name,
            "object_id": object_id
        }

    def get_filepath(self, urn: str, version: int) -> str:
        """
        Resolves the absolute file path for a versioned KO JSON.
        Format: objects/{jurisdiction}/{domain}/{type}/{object_id}/v{version}.json
        """
        meta = self.parse_urn(urn)
        # Replace colons in object_id with underscores for safe file system names
        safe_id = meta["object_id"].replace(":", "_")
        
        path = os.path.join(
            self.base_dir,
            "objects",
            meta["jurisdiction"],
            meta["domain"],
            meta["type"],
            safe_id,
            f"v{version}.json"
        )
        return path

    def write_ko(self, ko_data: dict) -> str:
        """
        Validates a Knowledge Object, writes it to its versioned path in the Git Ledger,
        and returns the absolute file path.
        """
        # 1. Enforce validation against schema before write
        validate_ko(ko_data)
        
        urn = ko_data["urn"]
        version = ko_data["version"]
        filepath = self.get_filepath(urn, version)
        
        # Ensure parent folders exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save JSON
        with open(filepath, "w") as f:
            json.dump(ko_data, f, indent=2)
            
        return filepath

    def read_ko(self, urn: str, version: int) -> dict:
        """
        Reads a specific KO version from the Git Ledger.
        """
        filepath = self.get_filepath(urn, version)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Knowledge Object URN '{urn}' version {version} not found in ledger.")
            
        with open(filepath, "r") as f:
            return json.load(f)
