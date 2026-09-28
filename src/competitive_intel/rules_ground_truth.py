"""
Builds the DPDP Rules, 2025 ground truth from the Gazette of India, with the corrigendum applied.

Sources (both Layer 1, both in staging/competitive_intel/ground_truth/):
  G.S.R. 846(E), 13 Nov 2025  — the Rules as notified (bilingual; English half is used)
  G.S.R. 892(E), 10 Dec 2025  — corrigendum to G.S.R. 846(E)

Each corrigendum entry names a gazette page and line. Gazette page numbers match PDF page
numbers, so every correction is applied only on its own page and must match exactly once —
a correction that fails to land stops the build rather than being silently skipped.

A plain-English guide (including SaralPrivacy's own) is interpretation, not ground truth.

Writes  staging/competitive_intel/ground_truth/rules_sections.json

Usage:  python3 src/competitive_intel/rules_ground_truth.py
"""
import hashlib
import json
import os
import re

from pypdf import PdfReader

from fetch import REPO_ROOT
from ground_truth import clean_hyphens

GT_DIR = os.path.join(REPO_ROOT, "staging/competitive_intel/ground_truth")
RULES_PDF = os.path.join(GT_DIR, "dpdp_rules_2025_gsr846.pdf")
CORRIGENDUM_PDF = os.path.join(GT_DIR, "dpdp_rules_2025_corrigendum_gsr892.pdf")
MAX_RULE = 23

# G.S.R. 892(E): (page, wrong, right). Page is the gazette page = PDF page number.
CORRIGENDUM = [
    (24, "after the date of publication of this Gazette. (4)",
         "after the date of publication in the Official Gazette. (4)"),
    (24, "after the date of publication of this Gazette. 2. Definitions",
         "after the date of publication in the Official Gazette. 2. Definitions"),
    (29, "Ministries or Department of", "Ministries or Departments of"),
    (32, "may be given in such. (2)", "may be given in such order. (2)"),
    (34, "(c) everybody corporate", "(c) every body corporate"),
    (34, "(18 or 2013)", "(18 of 2013)"),
    # p38 lines 1-15: two clauses were both printed "(a)"; relabel the run to (a)-(g),
    # and the first definition ends with ";" not ".".
    (38, "(35 of 2019). (a)", "(35 of 2019); (b)"),
    (38, "(b) “clinical establishment", "(c) “clinical establishment"),
    (38, "(c) “educational institution", "(d) “educational institution"),
    (38, "(d) “healthcare professional", "(e) “healthcare professional"),
    (38, "(e) “health services", "(f) “health services"),
    (38, "(f) “mental health establishment", "(g) “mental health establishment"),
]

def sha256(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _apply(text: str, wrong: str, right: str) -> tuple:
    """Replace `wrong` with `right`, keeping the page's own whitespace around unchanged tokens.

    PDF extraction breaks lines and doubles spaces unpredictably, so tokens are matched across
    any whitespace. The line breaks between unchanged context tokens are preserved: collapsing
    them would detach headings like "2. Definitions" from the start of their line.
    """
    wrong_tokens, right_tokens = wrong.split(), right.split()
    pattern = "".join(
        re.escape(token) + (r"(\s+)" if i < len(wrong_tokens) - 1 else "")
        for i, token in enumerate(wrong_tokens))
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        return text, len(matches)

    gaps = list(matches[0].groups())
    prefix = 0
    while prefix < min(len(wrong_tokens), len(right_tokens)) and \
            wrong_tokens[prefix] == right_tokens[prefix]:
        prefix += 1
    suffix = 0
    while suffix < min(len(wrong_tokens), len(right_tokens)) - prefix and \
            wrong_tokens[-1 - suffix] == right_tokens[-1 - suffix]:
        suffix += 1

    out = []
    for j, token in enumerate(right_tokens):
        out.append(token)
        if j == len(right_tokens) - 1:
            break
        from_end = len(right_tokens) - 2 - j          # gap index counted from the end
        if j < prefix and j < len(gaps):
            out.append(gaps[j])
        elif from_end < suffix and from_end < len(gaps):
            out.append(gaps[len(gaps) - 1 - from_end])
        else:
            out.append(" ")
    start, end = matches[0].span()
    return text[:start] + "".join(out) + text[end:], 1


def corrected_pages() -> list:
    """English pages of G.S.R. 846(E) with every G.S.R. 892(E) correction applied."""
    reader = PdfReader(RULES_PDF)
    pages = [page.extract_text() or "" for page in reader.pages]
    for page_no, wrong, right in CORRIGENDUM:
        pages[page_no - 1], hits = _apply(pages[page_no - 1], wrong, right)
        if hits != 1:
            raise SystemExit(f"Corrigendum did not land on p{page_no}: {wrong!r} found {hits}x")
    return pages


def english_text(pages: list) -> str:
    full = "\n".join(pages)
    start = full.find("MINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY \nNOTIFICATION")
    if start < 0:
        start = full.find("MINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY")
    body = full[start:]
    # Strip running heads so they don't bleed into rule text.
    body = re.sub(r"\n\s*\d+\s+THE GAZETTE OF INDIA : EXTRAORDINARY\s+\[PART II—SEC\. 3\(i\)\]\s*", "\n", body)
    body = re.sub(r"\n\s*\[PART II—SEC\. 3\(i\)\]\s+THE GAZETTE OF INDIA : EXTRAORDINARY\s+\d+\s*", "\n", body)
    # The Hindi running heads sit on English pages too: "[भाग II—खण्ड 3(i)]" and
    # "भारत का राजपत्र : असाधारण <page>".
    body = re.sub(r"\[[\u0900-\u097f][^\]]{0,40}\]", " ", body)
    body = re.sub(r"[\u0900-\u097f][\u0900-\u097f\s:]*\d{0,3}", " ", body)
    return clean_hyphens(body)


def split_rules(body: str) -> tuple:
    """Find rules 1-23 in order, reading each title from the gazette text itself.

    Titles are never hardcoded: the notified Rules renumbered the draft (e.g. Rule 10 is
    children's consent, Rule 13 is Significant Data Fiduciary), and the gazette prints some
    headings without a space ("17.Appointment") or wraps them across lines.
    """
    starts, position = {}, 0
    for number in range(1, MAX_RULE + 1):
        match = re.compile(rf"(?m)^\s*{number}\.\s*[A-Z]").search(body, position)
        if not match:
            break
        starts[number] = match.start()
        position = match.end()

    schedule_at = body.find("FIRST SCHEDULE", starts.get(MAX_RULE, 0))
    rules, ordered = {}, sorted(starts.items())
    for index, (number, start) in enumerate(ordered):
        if index + 1 < len(ordered):
            end = ordered[index + 1][1]
        else:
            end = schedule_at if schedule_at > start else len(body)
        text = re.sub(r"\s+", " ", body[start:end]).strip()
        heading = re.split(r"\s*[—–]", text[len(str(number)) + 1:], maxsplit=1)[0]
        title = re.sub(r"\s+", " ", heading).strip(" .")
        rules[number] = {"rule": number, "title": title,
                         "text": text, "word_count": len(text.split())}

    schedules = {}
    if schedule_at > 0:
        tail = body[schedule_at:]
        names = ["FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH"]
        marks = [(n, tail.find(f"{n} SCHEDULE")) for n in names]
        marks = [(n, i) for n, i in marks if i >= 0]
        for index, (name, start) in enumerate(marks):
            end = marks[index + 1][1] if index + 1 < len(marks) else len(tail)
            text = re.sub(r"\s+", " ", tail[start:end]).strip()
            text = re.split(r"\[F\. No\.", text)[0].strip()
            schedules[name.title()] = {"schedule": name.title(), "text": text,
                                       "word_count": len(text.split())}
    return rules, schedules


def main():
    for path in (RULES_PDF, CORRIGENDUM_PDF):
        if not os.path.exists(path):
            raise SystemExit(f"Missing source PDF: {path}")

    rules, schedules = split_rules(english_text(corrected_pages()))

    # The commencement table below is read from Rule 1; prove Rule 1 still says it.
    rule1 = rules[1]["text"]
    for phrase in ("Rules 1, 2 and 17 to 21 shall come into force on the date of their publication",
                   "Rule 4 shall come into force one year after the date of publication",
                   "Rules 3, 5 to 16, 22 and 23 shall come into force eighteen months after"):
        if phrase not in rule1:
            raise SystemExit(f"Rule 1 no longer says: {phrase!r} — recheck the commencement table")
    missing = [n for n in range(1, MAX_RULE + 1) if n not in rules]
    thin = [n for n, r in rules.items() if r["word_count"] < 25]

    payload = {
        "document": "Digital Personal Data Protection Rules, 2025",
        "notification": "G.S.R. 846(E), Gazette of India, Extraordinary, 13 November 2025",
        "corrigendum": "G.S.R. 892(E), 10 December 2025 — applied",
        "source": "Ministry of Electronics and Information Technology (MeitY)",
        "rules_pdf_sha256": sha256(RULES_PDF),
        # Byte-identical to the copy MeitY publishes (verified 2026-09-27 by SHA-256 match).
        "rules_pdf_url": "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
        "corrigendum_pdf_sha256": sha256(CORRIGENDUM_PDF),
        "corrections_applied": len(CORRIGENDUM),
        "trust_layer": 1,
        # Rule 1(2)-(4): staggered commencement from the 13 Nov 2025 publication date.
        "commencement": {
            "in_force_from_2025-11-13": [1, 2, 17, 18, 19, 20, 21],
            "in_force_from_2026-11-13": [4],
            "in_force_from_2027-05-13": [3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 22, 23],
        },
        "rules": {str(n): r for n, r in sorted(rules.items())},
        "schedules": schedules,
    }
    with open(os.path.join(GT_DIR, "rules_sections.json"), "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    words = sum(r["word_count"] for r in rules.values())
    print(f"{len(rules)}/{MAX_RULE} rules ({words:,} words), {len(schedules)} schedules, "
          f"{len(CORRIGENDUM)} corrections applied")
    if missing:
        print("MISSING:", missing)
    if thin:
        print("SUSPICIOUSLY SHORT:", thin)


if __name__ == "__main__":
    main()
