"""
Builds the ground truth the Source Truth agent verifies against: the DPDPA 2023 text
as published by MeitY, split into sections 1-44.

Competitor pages are never ground truth. Only this file is.

Writes  staging/competitive_intel/ground_truth/act_sections.json
        staging/competitive_intel/ground_truth/dpdpa_2023.pdf  (the source, hashed)

Usage:  python3 src/competitive_intel/ground_truth.py
"""
import hashlib
import json
import os
import re

import requests
from pypdf import PdfReader

from fetch import REPO_ROOT

ACT_PDF_URL = "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf"
OUT_DIR = os.path.join(REPO_ROOT, "staging/competitive_intel/ground_truth")
MAX_SECTION = 44

# Marginal headings as printed in the gazette, in section order. They are not trusted as
# typed: verify_titles() proves each one appears in the PDF's own text, in ascending order,
# on every build. (An earlier hand-typed table was shifted by one through Chapter V.)
SECTION_TITLES = [
    "Short title and commencement", "Definitions", "Application of Act",
    "Grounds for processing personal data", "Notice", "Consent", "Certain legitimate uses",
    "General obligations of Data Fiduciary", "Processing of personal data of children",
    "Additional obligations of Significant Data Fiduciary",
    "Right to access information about personal data",
    "Right to correction and erasure of personal data", "Right of grievance redressal",
    "Right to nominate", "Duties of Data Principal", "Processing of personal data outside India",
    "Exemptions", "Establishment of Board",
    "Composition and qualifications for appointment of Chairperson and Members",
    "Salary, allowances payable to and term of office",
    "Disqualifications for appointment and continuation as Chairperson and Members of Board",
    "Resignation by Members and filling of vacancy", "Proceedings of Board",
    "Officers and employees of Board", "Members and officers to be public servants",
    "Powers of Chairperson", "Powers and functions of Board", "Procedure to be followed by Board",
    "Appeal to Appellate Tribunal", "Orders passed by Appellate Tribunal to be executable as decree",
    "Alternate dispute resolution", "Voluntary undertaking", "Penalties",
    "Crediting sums realised by way of penalties to Consolidated Fund of India",
    "Protection of action taken in good faith", "Power to call for information",
    "Power of Central Government to issue directions", "Consistency with other laws",
    "Bar of jurisdiction", "Power to make rules", "Laying of rules and certain notifications",
    "Power to amend Schedule", "Power to remove difficulties", "Amendments to certain Acts",
]


def verify_titles(text: str):
    """Fail the build unless every heading is printed in the gazette, in section order."""
    flat, position = re.sub(r"\s+", " ", text), -1
    for number, title in enumerate(SECTION_TITLES, 1):
        found = flat.find(title + ".", position + 1)
        if found < 0:
            raise SystemExit(f"Heading for section {number} not found in order in the gazette: {title!r}")
        position = found



def download() -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    pdf_path = os.path.join(OUT_DIR, "dpdpa_2023.pdf")
    if not os.path.exists(pdf_path):
        # meity.gov.in rejects non-browser agents with 403.
        browser = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
        resp = requests.get(ACT_PDF_URL, headers={"User-Agent": browser}, timeout=90)
        resp.raise_for_status()
        with open(pdf_path, "wb") as f:
            f.write(resp.content)
    return pdf_path


RUNNING_HEAD = re.compile(
    r"^\s*(\d+\s+THE GAZETTE OF INDIA EXTRAORDINARY\s*\[P\s?ART II\S*|SEC\.\s*1\]\s*THE GAZETTE OF INDIA EXTRAORDINARY\s+\d+)\s*$"
)
ACT_REF = re.compile(r"\d{1,3} of (?:18|19|20)\d\d\.")


def _is_margin(block: str) -> bool:
    """True when `block` is nothing but marginal notes: section headings and Act references."""
    rest = ACT_REF.sub(" ", block)
    rest = re.sub(r"\s+", " ", rest).strip()
    titles = sorted(SECTION_TITLES, key=len, reverse=True)
    while rest:
        for t in titles:
            if rest.startswith(t + "."):
                rest = rest[len(t) + 1:].lstrip()
                break
        else:
            return False
    return True


def strip_page_furniture(page_text: str, report: list, page_no: int) -> str:
    """Remove what the gazette prints around the Act rather than in it.

    pypdf returns each page with its running head first ("6 THE GAZETTE OF INDIA
    EXTRAORDINARY [PART II—" / "SEC. 1] THE GAZETTE ... 7") and the margin notes
    last: the section headings printed beside the text, split over short lines,
    and references such as "53 of 2005.". Left in, they land mid-sentence in the
    section text. A trailing block is removed only when it is made entirely of
    known headings and Act references, so body text can never be dropped by this.
    """
    lines = page_text.split("\n")
    if lines and RUNNING_HEAD.match(lines[0]):
        lines = lines[1:]
    # Page 1 ends with the gazette masthead (Hindi and English banner, registration
    # number, the Ministry's publication line). It starts at the "EXTRAORDINARY"
    # banner, preceded by its Hindi word; nothing after it is part of the Act.
    for i, line in enumerate(lines):
        if line.strip() == "EXTRAORDINARY":
            cut = i - 1 if i > 0 and len(lines[i - 1].strip()) < 15 and " " not in lines[i - 1].strip() else i
            report.append((page_no, "gazette masthead: " + " ".join(l.strip() for l in lines[cut:])[:80] + "…"))
            lines = lines[:cut]
            break
    best = 0
    for k in range(1, min(40, len(lines)) + 1):
        tail = lines[-k:]
        if any(len(l.strip()) > 40 for l in tail):
            break
        if _is_margin(" ".join(tail)):
            best = k
    if best:
        report.append((page_no, " ".join(l.strip() for l in lines[-best:])))
        lines = lines[:-best]
    return "\n".join(lines)


def clean_hyphens(text: str) -> str:
    """The gazette's PDF text layer splits hyphenated words: "seventy -two", "sub -section".

    Left alone, a claim quoting "seventy-two hours" can't be matched against the Act or Rules.
    A spaced dash used as punctuation (" - ") has whitespace on both sides and is untouched.
    """
    return re.sub(r"(\w) -(\w)", r"\1-\2", text)


def split_sections(text: str) -> dict:
    """Cut the Act at each '<n>. ' that starts a line, keeping numbering in order."""
    starts = {}
    expected = 1
    for match in re.finditer(r"^\s*(\d{1,2})\.\s", text, re.M):
        number = int(match.group(1))
        if number == expected and number <= MAX_SECTION:
            starts[number] = match.start()
            expected += 1

    sections = {}
    ordered = sorted(starts.items())
    for index, (number, start) in enumerate(ordered):
        end = ordered[index + 1][1] if index + 1 < len(ordered) else len(text)
        body = re.sub(r"\s+", " ", text[start:end]).strip()
        sections[number] = {
            "section": number,
            "title": SECTION_TITLES[number - 1],
            "text": body,
            "word_count": len(body.split()),
        }
    return sections


def extract_schedule(sections: dict) -> dict:
    """The penalty Schedule is a 3-column table the PDF text layer emits column by column
    (all descriptions, then serial numbers, then amounts), glued onto the end of section 44.
    Rebuild it row by row, and cut section 44 back to its own text. Fails unless exactly
    seven descriptions pair with seven amounts."""
    text = sections[MAX_SECTION]["text"]
    start = text.find("Breach of provisions of this Act or rules made thereunder (2)")
    penalty_at = text.find("Penalty (3)")
    end = text.find("THE SCHEDULE")
    if min(start, penalty_at, end) < 0:
        raise SystemExit("Act Schedule table not found where expected at the end of section 44")

    described = text[start:text.find("Sl. No.", start)]
    described = described.replace("Breach of provisions of this Act or rules made thereunder (2)", "")
    rows = [r.strip() for r in re.split(r"(?=Breach )", described) if r.strip()]
    amounts = [a.strip() for a in re.split(r"(?<=\.)\s+(?=May extend|Up to)",
                                           text[penalty_at + len("Penalty (3)"):end]) if a.strip()]
    if len(rows) != 7 or len(amounts) != 7:
        raise SystemExit(f"Act Schedule rebuild failed: {len(rows)} descriptions vs {len(amounts)} amounts")

    table = [{"serial": n, "breach": row.rstrip("."), "penalty": amount.rstrip(".")}
             for n, (row, amount) in enumerate(zip(rows, amounts), 1)]
    body = "THE SCHEDULE [See section 33(1)] " + " ".join(
        f"{r['serial']}. {r['breach']} — {r['penalty']}." for r in table)

    sections[MAX_SECTION]["text"] = text[:start].strip()
    sections[MAX_SECTION]["word_count"] = len(sections[MAX_SECTION]["text"].split())
    return {"title": "The Schedule — penalties", "text": body, "rows": table,
            "word_count": len(body.split())}


def main():
    pdf_path = download()
    reader = PdfReader(pdf_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    # Headings are proven against the raw text (they are printed as margin notes),
    # then the running heads and margin notes are removed from the body.
    verify_titles(clean_hyphens("\n".join(pages)))
    removed = []
    text = clean_hyphens("\n".join(strip_page_furniture(t, removed, i + 1) for i, t in enumerate(pages)))
    for page_no, block in removed:
        print(f"  page {page_no}: removed margin notes {block!r}")

    sections = split_sections(text)
    schedule = extract_schedule(sections)
    missing = [n for n in range(1, MAX_SECTION + 1) if n not in sections]
    thin = [n for n, s in sections.items() if s["word_count"] < 20]

    payload = {
        "source": "Ministry of Electronics and Information Technology (MeitY)",
        "source_url": ACT_PDF_URL,
        "document": "The Digital Personal Data Protection Act, 2023 (No. 22 of 2023)",
        "pdf_sha256": hashlib.sha256(open(pdf_path, "rb").read()).hexdigest(),
        "trust_layer": 1,
        "sections": {str(n): s for n, s in sorted(sections.items())},
        "schedule": schedule,
    }
    with open(os.path.join(OUT_DIR, "act_sections.json"), "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"{len(sections)}/{MAX_SECTION} sections, {sum(s['word_count'] for s in sections.values()):,} words")
    if missing:
        print("MISSING:", missing)
    if thin:
        print("SUSPICIOUSLY SHORT:", thin)


if __name__ == "__main__":
    main()
