"""Validate competitor Knowledge Cards. These are not Knowledge Objects."""

from __future__ import annotations

import json
import os

from jsonschema import ValidationError, validate

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "knowledge_card_schema.json")


def get_knowledge_card_schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def validate_knowledge_card(card: dict) -> None:
    """Raise ValidationError if the card is not a valid unpublished competitor card."""
    if card.get("publication_eligible") is True:
        raise ValidationError("competitor Knowledge Cards cannot be publication_eligible")
    if card.get("source_class") != "COMPETITOR":
        raise ValidationError("Knowledge Cards from this pipeline must be COMPETITOR")
    validate(instance=card, schema=get_knowledge_card_schema())
