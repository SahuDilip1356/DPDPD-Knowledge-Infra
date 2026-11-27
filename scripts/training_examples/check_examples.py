"""Quote checker for Setu training examples (training guide step 2).

Every example must pass before Dilip sees it. The checker fails an example when:
- a claim cites an unknown provision, or its quote is not one unbroken run of at least 6
  words, in the same case, from that provision (whitespace ignored, no elision);
- the answer refers to a section, rule or schedule it does not cite (long and short forms,
  plurals, ranges), or to a sub-section or clause the cited text does not have;
- the answer states a rupee amount or a time limit that no quote contains, or a claim
  states an amount its own quote does not contain;
- a cited provision is not yet in force on the check date and the answer does not give
  every pending start date (a claim may name the part it relies on with `applies_from`);
- the answer uses a name the law does not use, or a known wrong name;
- a label is outside the approved sets, a law-answers or comparison example has no quote,
  or a refusal example has no plain refusal phrase or states a duty without a quote.

The check date is `--as-of` or today. An example cannot set its own.

Usage:
  python3 scripts/training_examples/check_examples.py --law <law-import dir> [--as-of YYYY-MM-DD] <examples.jsonl>
"""

import argparse
import ast
import datetime
import json
import os
import re
import sys
import unicodedata

KINDS = {"who", "why", "how", "what", "when", "where"}
READERS = {"business", "learner", "public"}
LANES = {"law_answers", "law_silent", "needs_lawyer", "comparison", "out_of_scope"}
REFUSAL_LANES = {"law_silent", "needs_lawyer", "out_of_scope"}
QUOTE_REQUIRED_LANES = {"law_answers", "comparison"}
MIN_QUOTE_WORDS = 6

ELISION = re.compile(r"…|\.\.\.|\[\s*\.\.\.\s*\]")

NUM = r"\d+[A-Za-z]?(?: ?\(\d+[A-Za-z]?\))*(?: ?\([a-z]{1,4}\))*"
REF = re.compile(
    r"(?<![\w.-])(?P<kind>sections?|ss?\.|secs?\.?|rules?|r\.)\s*"
    r"(?P<list>" + NUM + r"(?:\s*(?:,|and|or|to|-|–)\s*" + NUM + r")*)",
    re.I,
)
ORDINAL = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7}
SCHEDULE_REF = re.compile(r"\b(First|Second|Third|Fourth|Fifth|Sixth|Seventh) Schedule\b|\b(?:the|The) Schedule\b")

WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000,
}
_W = "|".join(sorted(WORD_NUM, key=len, reverse=True))
NUM_WORDS = r"(?:" + _W + r")(?:(?:[\s-]+|\s+and\s+)(?:" + _W + r"))*"
NUMBER = r"(?:\d[\d,]*(?:\.\d+)?|" + NUM_WORDS + r")"
TIME_NUMBER = r"(?:\d[\d,]*|" + NUM_WORDS + r"|an?)"
AMOUNT = re.compile(r"(?:₹|\bRs\.?|\bINR)?\s*\b(" + NUMBER + r")\s*(crore|lakh)\b", re.I)
RUPEES = re.compile(r"(?:₹|\bRs\.?\s?|\bINR\s?)(\d[\d,]*)(?![\d,]*\s*(?:crore|lakh))", re.I)
WORD_RUPEES = re.compile(r"\b(" + NUM_WORDS + r")\s+rupees\b", re.I)
TIME = re.compile(r"(?<![\w-])(" + TIME_NUMBER + r")[\s-]+(hours?|days?|weeks?|months?|years?)\b(?!-old)", re.I)

REFUSAL = re.compile(
    r"\b((the )?(DPDP )?(Act|Rules)( and( the)? Rules)? (does|do) not|there is (none|no)|"
    r"(ask|speak to|check with|consult|with) a lawyer|a (question|matter) for a lawyer|"
    r"needs? a lawyer|legal advice|a lawyer (needs|can|should)|I cannot answer|no one can tell you)",
    re.I,
)
DUTY_WORDS = re.compile(r"\b(must|shall|have to|has to|need to|needs to|required to)\b", re.I)

CAP_RUN = re.compile(r"\b(?:[A-Z][a-z]+|[A-Z]{2,})(?:\s+(?:of|and|for|to)?\s*(?:[A-Z][a-z]+|[A-Z]{2,}))+\b")
LEADING = {"The", "A", "An", "This", "That", "These", "Your", "Our", "If", "In", "Under", "For",
           "When", "Yes", "No", "So", "But", "And", "Each", "Every", "Any", "From", "Until", "Once",
           "Tell", "Ask", "Check", "Give", "Keep", "Get", "Send", "Use", "Note", "Then", "Only",
           "Before", "After", "Both", "Also", "Most", "Some", "Today", "Even", "Among", "Not",
           "Delete", "Appeal", "Medical", "Such", "It", "Its", "What", "Whether", "Students"}
ALLOWED_NAMES = {
    "SaralPrivacy", "Setu", "India", "Indian", "RBI", "SEBI", "IRDAI", "Aadhaar", "MeitY",
    "CERT-In", "GDPR", "WhatsApp", "UPSC", "DPDP Act", "DPDP Rules", "DPDPA", "Gazette",
    "Data Protection Board", "Data Protection Board of India", "Board", "Act", "Rules", "Pune",
    "Eighth Schedule",
}
KNOWN_WRONG_TERMS = {
    "Data Protection Act", "Data Protection Rules", "Personal Data Protection Act",
    "Personal Data Protection Bill", "Data Protection Authority", "Data Protection Commissioner",
    "Indian Data Protection Rules", "Data Personal Breach Inquiry",
}
KNOWN_WRONG_WORDS = re.compile(r"\b(Commissioner|Ombudsman|Authority|Regulator)\b")

# ---- Fail-closed residual check ----
# Only these exact house forms may carry a number, a currency or a reference. Each is
# validated by the checks above, then removed; anything numeric or reference-like left over
# fails, whatever its wording.
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE = re.compile(r"\b\d{1,2} (?:" + MONTHS + r") \d{4}\b")
NOTIFICATION = re.compile(r"\b(?:G\.S\.R\.|S\.O\.) \d+\(E\)")


def _iso(human):
    try:
        return datetime.datetime.strptime(human, "%d %B %Y").date().isoformat()
    except ValueError:
        return None


CANON = [
    DATE,                                                                     # 13 May 2027
    NOTIFICATION,                                                             # G.S.R. 843(E)
    re.compile(r"\b(?:Section|Rule)s? \d+[A-Z]?(?:\(\d+[A-Za-z]?\))*(?:\([a-z]{1,4}\))?"
               r"(?:(?:, | and | to )\d+[A-Z]?(?:\(\d+[A-Za-z]?\))*)*(?![\w(])"),  # Section 8(6), Sections 11 to 14
    re.compile(r"\b[Tt]he Schedule\b|\b(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh) Schedule"
               r"(?:, Part [AB])?\b|\bEighth Schedule to the Constitution\b"),
    re.compile(r"₹\d{1,3}(?:,\d{2,3})*(?!,?\d)(?: (?:crore|lakh)\b(?!s))?"),       # ₹250 crore, ₹10,000
    re.compile(r"\b(?:\d+|" + NUM_WORDS + r") (?:hours?|days?|weeks?|months?|years?)\b", re.I),  # 72 hours
]
COUNT = re.compile(r"\b(\d+) (?:crore|lakh) (?!rupees)[a-z]+")                     # 2 crore registered users
RESIDUAL_BAD = [
    (re.compile(r"[₹$€£§]|\bRs\b\.?|\bINR\b|\bUSD\b|\brupees?\b|\bcrores\b|\blakhs\b|\b(?:m|b|tr)illions?\b", re.I),
     "a currency or amount not in the house form ₹N crore"),
    (re.compile(r"\bu/s\b|(?<![\w.])(?:ss?|r|secs?|art)\.?\s*\d|\b(?:section|rule)s?\s+\d|\bread with\b|\bthrough\s+\d", re.I),
     "a reference not in the house form (Section N) or (Rule N)"),
    (re.compile(r"\bschedules?\b", re.I), "a schedule not named in the house form"),
    (re.compile(r"\b(?:fortnight|hrs?|mins?|minutes?|working days?|business days?)\b", re.I),
     "a time limit not in the house form N hours/days/months/years"),
    (re.compile(r"\b(?:" + NUM_WORDS + r")\b(?:\W+\w+){0,3}?\W+(?:hours?|days?|weeks?|months?|years?)\b", re.I),
     "a time limit not in the house form"),
    (re.compile(r"%|\bper ?cent\b|\bpercent\b", re.I), "a percentage"),
    (re.compile(r"\b(?:dozens?|couple|half|quarters?|score|trillions?|crore|lakh)\b", re.I),
     "an amount or count word outside the house forms"),
    (re.compile(r"\b(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|"
                r"\w+teenth|\w+tieth)\s+(?:hours?|days?|weeks?|months?|years?)\b", re.I),
     "a deadline written as an ordinal"),
    (re.compile(r"\b(?:" + "|".join(w for w in sorted(WORD_NUM, key=len, reverse=True) if w != "one") + r")\b", re.I),
     "a number word outside the house forms (only 'one' is allowed in prose)"),
    (re.compile(r"\d"), "a number outside the house forms (dates, citations, ₹ amounts, time limits)"),
]


ROMAN = re.compile(r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})")


def _residual(answer, quote_values):
    errs = []
    for ch in answer:
        if unicodedata.category(ch).startswith("N") and not ("0" <= ch <= "9"):
            errs.append(f"answer has {ch!r}: a non-ASCII digit or numeral")
            break
    text = answer
    for pat in CANON:
        text = pat.sub(" ", text)
    for m in COUNT.finditer(text):
        if float(m.group(1)) in quote_values:
            text = text.replace(m.group(0), " ")
    for m in re.finditer(r"\b[MDCLXVI]{2,}\b", text):
        if ROMAN.fullmatch(m.group(0)):
            errs.append(f"answer has {m.group(0)!r}: a Roman numeral")
            break
    for pat, why in RESIDUAL_BAD:
        m = pat.search(text)
        if m:
            errs.append(f"answer has {m.group(0)!r}: {why}")
    return errs


def _quote_values(quotes):
    vals = set()
    for q in quotes:
        for m in re.finditer(r"\d[\d,]*", q):
            vals.add(float(m.group(0).replace(",", "")))
        for m in re.finditer(NUM_WORDS, q, re.I):
            v = to_number(m.group(0))
            if v is not None:
                vals.add(v)
    return vals


NUMBER_WORD_SET = set(WORD_NUM) | {"and", "hundred", "thousand", "lakh", "crore"}


def _joins(ch):
    return ch.isalnum() or ch in "-'’"


def _on_word_boundaries(quote, text):
    """True if some occurrence starts and ends on whole words and does not cut a number
    phrase ("two hours" out of "seventy-two hours", "fifty crore" out of "two hundred and fifty")."""
    start = text.find(quote)
    while start != -1:
        end = start + len(quote)
        before = text[start - 1] if start else " "
        after = text[end] if end < len(text) else " "
        ok = not _joins(before) and not _joins(after)
        if ok:
            q_words = re.findall(r"[A-Za-z]+", quote.lower())
            prev = re.findall(r"[A-Za-z]+", text[:start].lower())[-1:]
            nxt = re.findall(r"[A-Za-z]+", text[end:].lower())[:1]
            if q_words and q_words[0] in WORD_NUM and prev and prev[0] in NUMBER_WORD_SET:
                ok = False
            if q_words and q_words[-1] in NUMBER_WORD_SET and nxt and nxt[0] in NUMBER_WORD_SET:
                ok = False
        if ok:
            return True
        start = text.find(quote, start + 1)
    return False


def squash(text):
    return re.sub(r"\s+", " ", text or "").strip()


KNOWN_NOTIFICATIONS = {}   # citation -> date, loaded from dpdp-notifications.jsonl


def load_law(law_dir):
    KNOWN_NOTIFICATIONS.clear()
    notes = os.path.join(law_dir, "dpdp-notifications.jsonl")
    if os.path.exists(notes):
        with open(notes) as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    KNOWN_NOTIFICATIONS[r.get("citation")] = r.get("date") or r.get("published")
        # The Rules themselves are G.S.R. 846(E) of 13 November 2025 (law-import README, sources table).
        KNOWN_NOTIFICATIONS.setdefault("G.S.R. 846(E)", "2025-11-13")
    law = {}
    for name in ("dpdp-act-2023.jsonl", "dpdp-rules-2025.jsonl"):
        with open(os.path.join(law_dir, name)) as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    law[r["id"]] = r
    return law


def words_to_int(text):
    total, current = 0, 0
    for w in re.split(r"[\s-]+", text.lower().replace(",", "")):
        if not w or w == "and":
            continue
        if w.isdigit():
            current += int(w)
        elif w == "hundred":
            current = max(current, 1) * 100
        elif w == "thousand":
            total += max(current, 1) * 1000
            current = 0
        elif w in WORD_NUM:
            current += WORD_NUM[w]
        else:
            return None
    return total + current


def to_number(token):
    token = token.strip()
    if token.lower() in ("a", "an"):
        return 1.0
    if re.fullmatch(r"\d[\d,]*(?:\.\d+)?", token):
        return float(token.replace(",", ""))
    v = words_to_int(token)
    return float(v) if v is not None else None


def amounts(text):
    """(value, unit) pairs: crore and lakh kept as units, plain rupees as 'rupees'."""
    out = set()
    for m in AMOUNT.finditer(text):
        v = to_number(m.group(1))
        if v is not None:
            out.add((v, m.group(2).lower()))
    for m in RUPEES.finditer(text):
        out.add((float(m.group(1).replace(",", "")), "rupees"))
    for m in WORD_RUPEES.finditer(text):
        if re.search(r"(crore|lakh)\s+rupees$", m.group(0), re.I):
            continue
        v = to_number(m.group(1))
        if v is not None:
            out.add((v, "rupees"))
    return out


def time_limits(text):
    out = set()
    for m in TIME.finditer(text):
        v = to_number(m.group(1))
        if v is not None:
            out.add((v, m.group(2).lower().rstrip("s")))
    return out


def _in_force_entries(record):
    v = record.get("in_force") or []
    if isinstance(v, str):
        try:
            v = ast.literal_eval(v)
        except (ValueError, SyntaxError):
            return []
    return [x for x in v if isinstance(x, dict) and x.get("from")]


def _in_force(record):
    return [x["from"] for x in _in_force_entries(record)]


def _part_text(record, label):
    """The text of the sub-section (and clause) an in-force label names, e.g. 'section 44(1)'.
    Returns None when the label is a range or cannot be located: such claims go to a person."""
    m = re.match(r"\s*(?:section|rule)\s+\d+[A-Za-z]?((?:\(\w+\))+)\s*$", label or "", re.I)
    if not m:
        return None
    subs = re.findall(r"\((\w+)\)", m.group(1))
    lines = (record.get("text") or "").split("\n")

    def segment(lines, marker, numeric):
        start = None
        for i, line in enumerate(lines):
            t = re.sub(r"^\s*\d+[A-Za-z]?\.\s*", "", line) if start is None else line
            if t.lstrip().startswith(f"({marker})"):
                start = i
                break
        if start is None:
            return None
        out = [lines[start]]
        stop = r"^\s*\(\d+\)" if numeric else r"^\s*\((?:[a-z]{1,4}|\d+)\)"
        for line in lines[start + 1:]:
            if re.match(stop, line):
                break
            out.append(line)
        return out

    seg = lines
    for k, sub in enumerate(subs):
        seg = segment(seg, sub, sub.isdigit())
        if seg is None:
            return None
    return squash(" ".join(seg))


def _human(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B')} {d.year}"


def _expand(listing):
    """'3, 5 to 16 and 22' -> ['3', '5', ..., '16', '22'] (sub-parts kept on singles)."""
    out = []
    for p in re.split(r"\s*(?:,|\band\b|\bor\b)\s*", listing):
        rng = re.split(r"\s*(?:\bto\b|-|–)\s*", p)
        if len(rng) == 2 and rng[0].isdigit() and rng[1].isdigit():
            out += [str(i) for i in range(int(rng[0]), int(rng[1]) + 1)]
        elif p:
            out.append(p)
    return out


def _check_refs(answer, cites, law):
    errs = []
    by_kind = {"section": {}, "rule": {}}
    for c in cites:
        if c not in law:
            continue
        num = str(law[c].get("number") or "")
        if c.startswith("act-s") and num:
            by_kind["section"][num] = law[c]
        elif c.startswith("rules-r") and num:
            by_kind["rule"][num] = law[c]
    for m in REF.finditer(answer):
        kind = "rule" if m.group("kind").lower().startswith("r") else "section"
        for item in _expand(m.group("list")):
            base = re.match(r"\d+[A-Za-z]?", item).group(0)
            if base.isdigit() and int(base) >= 1000:
                continue  # a year, as in "Rules 2025"
            rec = by_kind[kind].get(base)
            if rec is None:
                errs.append(f"answer refers to {kind} {item} without citing it")
                continue
            subs = "".join(re.findall(r"\([0-9A-Za-z]+\)", item[len(base):]))
            if subs and _part_text(rec, f"{kind} {base}{subs}") is None:
                errs.append(f"answer refers to {kind} {base}{subs}, but {rec['citation']} has no such part")
    for m in SCHEDULE_REF.finditer(answer):
        if m.group(1):
            n = ORDINAL[m.group(1).lower()]
            if not any(c.startswith(f"rules-sch{n}") for c in cites):
                errs.append(f"answer refers to the {m.group(1)} Schedule without citing it")
        elif not any(c.startswith("act-sch") for c in cites):
            errs.append("answer refers to the Schedule without citing it")
    return errs


def _invented_terms(answer, law_blob):
    found = []
    for m in CAP_RUN.finditer(answer):
        words = m.group(0).split()
        while words and words[0] in LEADING:
            words = words[1:]
        if len(words) < 2:
            continue
        term = " ".join(words)
        if term in KNOWN_WRONG_TERMS:
            found.append(term)
            continue
        singular = re.sub(r"ies$", "y", term) if term.endswith("ies") else re.sub(r"s$", "", term)
        if term in ALLOWED_NAMES or term in law_blob or singular in law_blob:
            continue
        segments = [s for s in re.split(r"\s+(?:and|of|for|to)\s+", term) if s]
        if len(segments) > 1 and all(s in ALLOWED_NAMES or s in law_blob for s in segments):
            continue
        found.append(term)
    for m in KNOWN_WRONG_WORDS.finditer(answer):
        found.append(m.group(1))
    return found


def valid_date(text):
    """Return text if it is a real YYYY-MM-DD date; otherwise refuse. A malformed date
    would compare wrongly as a string and silently switch the start-date check off."""
    if not isinstance(text, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        sys.exit(f"Refusing: --as-of must be YYYY-MM-DD, got {text!r}.")
    datetime.date.fromisoformat(text)
    return text


def check(example, law, as_of=None):
    """as_of: the ISO date the answer is read on; defaults to today. The example's own
    `as_of` field is ignored, so an example cannot move its own check date."""
    as_of = valid_date(datetime.date.today().isoformat() if as_of is None else as_of)
    errs = []
    for field, allowed in (("kind", KINDS), ("reader", READERS), ("lane", LANES)):
        if example.get(field) not in allowed:
            errs.append(f"label {field}={example.get(field)!r} not in approved set")

    claims = example.get("claims") or []
    cites = [cl.get("cite") for cl in claims]
    quotes = []
    for i, cl in enumerate(claims, 1):
        cite, quote = cl.get("cite"), squash(cl.get("quote"))
        if cite not in law:
            errs.append(f"claim {i}: unknown provision {cite!r}")
            continue
        if ELISION.search(quote):
            errs.append(f"claim {i}: quote uses elision")
            continue
        if len(quote.split()) < MIN_QUOTE_WORDS:
            errs.append(f"claim {i}: quote shorter than {MIN_QUOTE_WORDS} words")
            continue
        if quote not in squash(law[cite]["text"]):
            errs.append(f"claim {i}: quote not found in {law[cite]['citation']}")
            continue
        if not _on_word_boundaries(quote, squash(law[cite]["text"])):
            errs.append(f"claim {i}: quote starts or ends mid-word in {law[cite]['citation']}")
            continue
        quotes.append(quote)
        for v, unit in sorted(amounts(cl.get("text", "")) - amounts(quote)):
            errs.append(f"claim {i}: states {v:g} {unit} but its own quote does not")

    lane = example.get("lane")
    answer = example.get("answer", "")
    if lane in QUOTE_REQUIRED_LANES and not claims:
        errs.append(f"{lane} needs at least one quoted claim")
    if lane in REFUSAL_LANES:
        if not REFUSAL.search(answer):
            errs.append("refusal lane must say plainly that the law does not answer or a lawyer is needed")
        if DUTY_WORDS.search(answer) and not claims:
            errs.append("refusal answer states a duty ('must', 'shall' ...) with no quote behind it")

    errs += _check_refs(answer, cites, law)

    quote_amounts, claim_amounts, quote_times = set(), set(), set()
    for q in quotes:
        quote_amounts |= amounts(q)
        quote_times |= time_limits(q)
    for cl in claims:
        claim_amounts |= amounts(cl.get("text", ""))
    for v, unit in sorted(amounts(answer)):
        if (v, unit) not in quote_amounts or (v, unit) not in claim_amounts:
            errs.append(f"answer states {v:g} {unit} but no claim quotes it")
    for v, unit in sorted(time_limits(answer)):
        if (v, unit) not in quote_times:
            errs.append(f"answer states {v:g} {unit}{'s' if v != 1 else ''} but no quote contains it")

    # A duty that has not started yet must be dated, or readers act on it too early.
    pending = {}
    for i, cl in enumerate(claims, 1):
        cite = cl.get("cite")
        if cite not in law:
            continue
        dates = _in_force(law[cite])
        if cl.get("applies_from"):
            # The date must belong to the very part of the provision the quote comes from.
            labels = [x.get("provision") for x in _in_force_entries(law[cite]) if x.get("from") == cl["applies_from"]]
            parts = [_part_text(law[cite], lb) for lb in labels]
            if not any(p and squash(cl.get("quote")) in p for p in parts):
                errs.append(f"claim {i}: applies_from {cl['applies_from']} does not cover the part of "
                            f"{law[cite]['citation']} the quote is from")
                continue
            dates = [cl["applies_from"]]
        for d in dates:
            if d > as_of:
                pending.setdefault(d, law[cite]["citation"])
    for d, citation in sorted(pending.items()):
        if _human(d) not in answer:
            errs.append(f"{citation} is not in force until {_human(d)}; the answer must say so")

    for m in NOTIFICATION.finditer(answer):
        if m.group(0) not in KNOWN_NOTIFICATIONS:
            errs.append(f"answer names {m.group(0)}, which is not a known notification")
    # A date must be a real start date somewhere in the Act or Rules, or a known gazette date.
    # (Which duty it belongs to is left to the legal read; the pending-date check above makes
    # sure each cited provision's own start date is present.)
    allowed_dates = {d for r in law.values() for d in _in_force(r)}
    allowed_dates |= {d for d in KNOWN_NOTIFICATIONS.values() if d}
    for m in DATE.finditer(answer):
        iso = _iso(m.group(0))
        if iso not in allowed_dates:
            errs.append(f"answer gives {m.group(0)}, which is not a start date of a cited provision or a known gazette date")

    errs += _residual(answer, _quote_values(quotes))

    law_blob = " ".join(squash(r["text"]) + " " + r.get("title", "") for r in law.values())
    for term in _invented_terms(answer, law_blob):
        errs.append(f"answer uses {term!r}, which is not in the law text")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True, help="folder holding dpdp-act-2023.jsonl and dpdp-rules-2025.jsonl")
    ap.add_argument("--as-of", default=None, help="ISO date the answers are read on (default today)")
    ap.add_argument("examples")
    a = ap.parse_args()
    if a.as_of is not None:
        valid_date(a.as_of)
    law = load_law(a.law)
    bad = 0
    with open(a.examples) as f:
        for line in f:
            if not line.strip():
                continue
            e = json.loads(line)
            errs = check(e, law, a.as_of)
            if errs:
                bad += 1
                print(f"FAIL {e.get('id')}: " + "; ".join(errs))
    print(f"{bad} failing")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
