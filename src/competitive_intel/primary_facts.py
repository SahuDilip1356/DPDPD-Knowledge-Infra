"""Official-fact patterns for Source Truth. Cite the Act, not DPDPA.com."""

from __future__ import annotations

import re
from typing import NamedTuple


class PrimaryFact(NamedTuple):
    fact_id: str
    pattern: re.Pattern[str]
    primary_source: str
    dpdpa_section: str | None
    dpdp_rule: str | None
    verdict: str
    note: str


PRIMARY_FACTS: tuple[PrimaryFact, ...] = (
    PrimaryFact(
        "penalty-250-crore-security",
        re.compile(r"(250\s*crore|two hundred and fifty crore).{0,80}(safeguard|security|breach)|"
                   r"(safeguard|security).{0,80}(250\s*crore|two hundred and fifty crore)", re.I),
        "DPDPA 2023 Schedule, Item 1 (Section 8(5) / Section 33)",
        "Section 33",
        None,
        "VERIFIED_PRIMARY",
        "The Schedule caps failure of reasonable security safeguards at ₹250 crore.",
    ),
    PrimaryFact(
        "penalty-250-crore-generic",
        re.compile(r"(penalt\w+|fine|reach).{0,40}(₹\s*)?250\s*crore|(₹\s*)?250\s*crore.{0,40}(penalt|fine|act)", re.I),
        "DPDPA 2023 Schedule (maximum listed penalty is ₹250 crore)",
        "Section 33",
        None,
        "VERIFIED_PRIMARY",
        "₹250 crore is the highest Schedule amount, not a single fine for every breach.",
    ),
    PrimaryFact(
        "penalty-200-crore-breach-notify",
        re.compile(r"(200\s*crore).{0,60}(notif|intim|breach)|(breach).{0,60}(200\s*crore)", re.I),
        "DPDPA 2023 Schedule, Item 2 (Section 8(6) / Section 33)",
        "Section 33",
        None,
        "VERIFIED_PRIMARY",
        "Failure to intimate a personal data breach is scheduled up to ₹200 crore.",
    ),
    PrimaryFact(
        "penalty-200-crore-children",
        re.compile(r"(200\s*crore).{0,60}(child|parent)|(child|section 9).{0,60}(200\s*crore)", re.I),
        "DPDPA 2023 Schedule, Item 3 (Section 9 / Section 33)",
        "Section 9",
        None,
        "VERIFIED_PRIMARY",
        "Breach of children's-data duties is scheduled up to ₹200 crore.",
    ),
    PrimaryFact(
        "penalty-150-crore-sdf",
        re.compile(r"(150\s*crore).{0,50}(sdf|significant)|(significant data fiduciary).{0,50}(150\s*crore)", re.I),
        "DPDPA 2023 Schedule, Item 4 (Section 10 / Section 33)",
        "Section 10",
        None,
        "VERIFIED_PRIMARY",
        "Breach of SDF duties is scheduled up to ₹150 crore.",
    ),
    PrimaryFact(
        "consent-quality",
        re.compile(r"consent.{0,80}(free|specific|informed|unconditional|unambiguous)|"
                   r"(free,\s*specific|informed and unambiguous)", re.I),
        "DPDPA 2023 Section 6",
        "Section 6",
        None,
        "VERIFIED_PRIMARY",
        "Section 6 states the quality tests for consent.",
    ),
    PrimaryFact(
        "notice-before-consent",
        re.compile(r"notice.{0,60}(before|prior).{0,40}consent|consent.{0,40}notice", re.I),
        "DPDPA 2023 Section 5",
        "Section 5",
        None,
        "SUPPORTED_INTERPRETATION",
        "Section 5 requires notice; pair the claim with the statutory text before publishing.",
    ),
    PrimaryFact(
        "legitimate-uses",
        re.compile(r"legitimate uses?", re.I),
        "DPDPA 2023 Section 7",
        "Section 7",
        None,
        "VERIFIED_PRIMARY",
        "The Act uses 'certain legitimate uses', not GDPR 'legitimate interest'.",
    ),
    PrimaryFact(
        "children-parental-consent",
        re.compile(r"(verifiable consent|parental consent|parent or lawful guardian).{0,40}(child|children)|"
                   r"child(ren)?.{0,40}(parent|guardian|verifiable consent)", re.I),
        "DPDPA 2023 Section 9; DPDP Rules 2025 Rule 5",
        "Section 9",
        "Rule 5",
        "VERIFIED_PRIMARY",
        "Children's data needs verifiable consent of a parent or lawful guardian.",
    ),
    PrimaryFact(
        "no-child-tracking",
        re.compile(r"(track|behavioural|behavioral|targeted advertis).{0,40}child|"
                   r"child.{0,40}(track|behavioural|targeted)", re.I),
        "DPDPA 2023 Section 9",
        "Section 9",
        None,
        "VERIFIED_PRIMARY",
        "Section 9 restricts tracking, behavioural monitoring, and targeted advertising directed at children.",
    ),
    PrimaryFact(
        "data-fiduciary-definition",
        re.compile(r"data fiduciary.{0,80}(purpose|means of processing|determines)", re.I),
        "DPDPA 2023 Section 2",
        "Section 2",
        None,
        "VERIFIED_PRIMARY",
        "A Data Fiduciary determines the purpose and means of processing.",
    ),
    PrimaryFact(
        "puttaswamy",
        re.compile(r"puttaswamy", re.I),
        "Justice K.S. Puttaswamy v. Union of India (2017)",
        None,
        None,
        "VERIFIED_PRIMARY",
        "Puttaswamy is a Supreme Court judgement, not a DPDPA.com original.",
    ),
    PrimaryFact(
        "sdf-dpo-dpia",
        re.compile(r"significant data fiduciary.{0,80}(dpo|data protection officer|dpia|audit)|"
                   r"(dpo|dpia).{0,80}significant data fiduciary", re.I),
        "DPDPA 2023 Section 10",
        "Section 10",
        None,
        "VERIFIED_PRIMARY",
        "SDFs have extra duties including DPO, DPIA, and audit.",
    ),
    PrimaryFact(
        "rules-2025-gazette",
        re.compile(r"(dpdp rules 2025|13\s*november\s*2025|november 13,?\s*2025)", re.I),
        "Gazette of India — DPDP Rules 2025 (MeitY)",
        None,
        None,
        "SUPPORTED_INTERPRETATION",
        "Confirm the exact Gazette citation before treating dates as operational law.",
    ),
    PrimaryFact(
        "consent-withdrawal",
        re.compile(r"(withdraw(al)? of consent|consent.{0,30}withdraw|withdraw.{0,20}consent)", re.I),
        "DPDPA 2023 Section 6",
        "Section 6",
        None,
        "VERIFIED_PRIMARY",
        "Section 6 lets a Data Principal withdraw consent as easily as it was given.",
    ),
    PrimaryFact(
        "erasure-correction",
        re.compile(r"(right to.{0,20}(correct|eras|complet)|correct.{0,20}inaccurate|eras\w+.{0,20}personal data)", re.I),
        "DPDPA 2023 Section 12",
        "Section 12",
        None,
        "VERIFIED_PRIMARY",
        "Section 12 is correction, completion, updating, and erasure — not a GDPR right to be forgotten.",
    ),
    PrimaryFact(
        "access-summary",
        re.compile(r"(right to access|summary of.{0,30}personal data|access request)", re.I),
        "DPDPA 2023 Section 11",
        "Section 11",
        None,
        "VERIFIED_PRIMARY",
        "Section 11 is the right to a summary of personal data and of sharing.",
    ),
    PrimaryFact(
        "grievance-first",
        re.compile(r"(grievance redressal|complain.{0,30}(board|fiduciary)|internal complaint)", re.I),
        "DPDPA 2023 Section 13",
        "Section 13",
        None,
        "VERIFIED_PRIMARY",
        "Section 13 requires a readily available grievance mechanism before the Board.",
    ),
    PrimaryFact(
        "nominate",
        re.compile(r"(right to nominate|nominee).{0,40}(death|incapacit|behalf)", re.I),
        "DPDPA 2023 Section 14",
        "Section 14",
        None,
        "VERIFIED_PRIMARY",
        "Section 14 is the right to nominate someone to exercise rights on death or incapacity.",
    ),
    PrimaryFact(
        "transfer-not-localisation",
        re.compile(r"(transfer.{0,40}outside india|section 16|restricted countr)", re.I),
        "DPDPA 2023 Section 16",
        "Section 16",
        None,
        "VERIFIED_PRIMARY",
        "Section 16 is a Government blacklist of countries, not a data-localisation mandate.",
    ),
)

INCORRECT_OR_CONTESTED: tuple[tuple[re.Pattern[str], str, str | None, str], ...] = (
    (
        re.compile(r"\bcontroller\b", re.I),
        "CONTESTED",
        None,
        "DPDPA uses Data Fiduciary, not GDPR Controller. Do not publish this wording as Indian law.",
    ),
    (
        re.compile(r"legitimate interest", re.I),
        "INCORRECT",
        "Section 7",
        "DPDPA does not create a GDPR-style legitimate-interest ground. The Act says legitimate uses.",
    ),
    (
        re.compile(r"(india.?eu|eu.?india).{0,40}adequac|adequacy.{0,40}(india|dpdpa)", re.I),
        "UNSUPPORTED",
        None,
        "EU adequacy is a European Commission decision, not a DPDPA fact. Treat as market commentary.",
    ),
    (
        re.compile(r"right to be forgotten", re.I),
        "CONTESTED",
        "Section 12",
        "DPDPA does not name a GDPR-style right to be forgotten. Closest duty is correction/erasure under Section 12.",
    ),
    (
        re.compile(
            r"(india-only datacent|data locali[sz]ation|"
            r"must.{0,30}(store|keep|maintain|host).{0,40}(only in india|india only))",
            re.I,
        ),
        "INCORRECT",
        "Section 16",
        "DPDPA does not require India-only data centres. Section 16 lets the Government restrict transfer to named countries.",
    ),
    (
        re.compile(
            r"(january\s*3,?\s*2025|3\s*january\s*2025).{0,50}(rule|notif)|"
            r"(dpdp rules|rules 2025).{0,50}(january\s*3|3\s*january)",
            re.I,
        ),
        "CONTESTED",
        None,
        "Confirm the Gazette date. SaralPrivacy primary notes use 13 November 2025, not 3 January 2025.",
    ),
)


DENIAL_RE = re.compile(
    r"\b(no|not|never|does not|do not|doesn't|don't|has no|have no|"
    r"there is no|without a|is not|are not|no such)\b",
    re.I,
)


def is_denial_of(text: str, match: re.Match[str]) -> bool:
    """True when the sentence is rejecting the matched myth, not asserting it."""
    if not text:
        raise ValueError("text is required")
    window = text[max(0, match.start() - 90) : match.end() + 40]
    return bool(DENIAL_RE.search(window))


def first_section(values: list[str] | None) -> str | None:
    if not values:
        return None
    return values[0]
