import os
import json
import sys
from jsonschema import validate, ValidationError

# Load schema relative to this script
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "knowledge_object_schema.json")

def get_schema():
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)

def validate_ko(ko_data: dict) -> None:
    """
    Validates a Knowledge Object dictionary against the constitutional JSON schema.
    Raises ValidationError if invalid.
    """
    schema = get_schema()
    validate(instance=ko_data, schema=schema)

def validate_ko_file(filepath: str) -> bool:
    """
    Loads and validates a KO JSON file. Returns True if valid, prints error and returns False if invalid.
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return False
        
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        validate_ko(data)
        print(f"Success: {filepath} conforms to the Knowledge Constitution.")
        return True
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON syntax in {filepath}: {e}", file=sys.stderr)
        return False
    except ValidationError as e:
        print(f"Validation Failure in {filepath}:", file=sys.stderr)
        print(f"  Field: {' -> '.join(map(str, e.absolute_path)) or 'root'}", file=sys.stderr)
        print(f"  Message: {e.message}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_schema.py <path_to_ko.json>")
        sys.exit(1)
        
    target_path = sys.argv[1]
    success = validate_ko_file(target_path)
    sys.exit(0 if success else 1)
