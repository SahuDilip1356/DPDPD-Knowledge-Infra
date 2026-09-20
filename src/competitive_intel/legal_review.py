"""Package claims a human lawyer must still sign. This is not counsel sign-off."""

from __future__ import annotations

from typing import Any


COUNSEL_STATUSES = frozenset({"NEEDS_REVIEW", "CONTESTED", "INCORRECT"})

LOOK_FOR = {
    "INCORRECT": "Check whether the sentence states Indian law or a GDPR transplant.",
    "CONTESTED": "Check the Act wording. The machine saw a foreign label.",
    "NEEDS_REVIEW": "No catalog match. Read the sentence against the Act or Gazette.",
}


def build_counsel_queue(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the rows a lawyer should stamp. Nothing here is COUNSEL_SIGNED."""
    if not isinstance(claims, list):
        raise ValueError("claims must be a list")
    queue: list[dict[str, Any]] = []
    for claim in claims:
        status = claim.get("verification_status")
        if status not in COUNSEL_STATUSES:
            continue
        if claim.get("counsel_signed") is True:
            continue
        queue.append(
            {
                "claim_id": claim["claim_id"],
                "claim_text": claim["claim_text"],
                "verification_status": status,
                "confidence": claim.get("confidence"),
                "verdict_note": claim.get("verdict_note"),
                "dpdpa_section": claim.get("dpdpa_section"),
                "dpdp_rule": claim.get("dpdp_rule"),
                "original_url": claim.get("original_url"),
                "card_id": claim.get("card_id"),
                "look_for": LOOK_FOR[status],
                "counsel_signed": False,
                "publication_allowed": False,
            }
        )
    queue.sort(key=lambda item: (item["verification_status"], item["claim_id"]))
    return queue


def counsel_summary(queue: list[dict[str, Any]], claims: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    for row in queue:
        by_status[row["verification_status"]] = by_status.get(row["verification_status"], 0) + 1
    signed = sum(1 for claim in claims if claim.get("counsel_signed") is True)
    return {
        "queue_count": len(queue),
        "by_status": by_status,
        "counsel_signed": signed,
        "machine_only": True,
        "publication_eligible": False,
        "headline": (
            f"{len(queue)} claims still need a human lawyer. "
            "The machine rechecked the easy myths. It did not sign as counsel."
        ),
    }


def render_counsel_markdown(queue: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    """A short worksheet a lawyer can print. Not legal advice."""
    lines = [
        "# Counsel review worksheet",
        "",
        summary["headline"],
        "",
        "This list is a factory queue. It is **not** a legal opinion and not a sign-off.",
        "Do not publish any row until counsel_signed is true and the Act citation is attached.",
        "",
        f"Rows: {summary['queue_count']}. Signed: {summary['counsel_signed']}.",
        "",
        "| ID | Stamp | Claim | What to check | Section |",
        "|---|---|---|---|---|",
    ]
    for row in queue:
        claim = row["claim_text"].replace("|", "/").replace("\n", " ")
        if len(claim) > 140:
            claim = claim[:137] + "..."
        note = (row.get("look_for") or "").replace("|", "/")
        section = row.get("dpdpa_section") or row.get("dpdp_rule") or "—"
        lines.append(
            f"| {row['claim_id']} | {row['verification_status']} | {claim} | {note} | {section} |"
        )
    lines.append("")
    return "\n".join(lines)
