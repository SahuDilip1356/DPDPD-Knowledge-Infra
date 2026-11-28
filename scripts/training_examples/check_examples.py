"""Checker for Setu training examples (training guide step 2), structured answers (option C).

Each example carries an `answer_template`: plain prose with typed slots in braces. A
figure, date, amount or reference can enter the answer only through a slot. The checker
validates every slot against the law, renders the template, and requires `answer` to be
exactly that rendering. The prose between the slots may not hold a digit, a unit word, a
reference word or a number word at all. The approved checks are E1-E15 in
EVALS-structured-answers.md; each check below names the eval it implements.

Slots:
  {ref:act-s8}  {ref:act-s8#6}  {ref:rules-r8,rules-sch3}  ->  (Section 8)  (Section 8(6))  (Rule 8, Third Schedule)
  {name:act-s3}                                            ->  Section 3
  {period:rules-r7|72 hours}  {amount:act-schedule|₹250 crore}  {count:rules-sch3|2 crore}
  {date:act-s8}  {date:act-s6#9}  {date:act-s8,rules-r7}   ->  the start date from the in-force table
                                                              (several ids must share one date)
  {notification:gsr-843e-2025}  {notified:gsr-843e-2025}   ->  G.S.R. 843(E)  13 November 2025

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

# ---------------------------------------------------------------- prose word lists (E5-E7)


def _plurals(word):
    out = {word}
    if re.search(r"(?:s|x|z|ch|sh)$", word):
        out.add(word + "es")
    elif re.search(r"[^aeiou]y$", word):
        out.add(word[:-1] + "ies")
    else:
        out.add(word + "s")
    return out


_UNIT_BASES = {
    "time": ("minute hour hr day week fortnight month year yr decade annum quarter "
             "hourly daily weekly fortnightly monthly quarterly yearly annual annually"),
    "money or count": ("rupee rs inr paisa paise crore cr lakh lac laakh karod karor arab kharab "
                       "thousand hazaar hazar million mn billion bn trillion grand dollar usd euro "
                       "pound percent percentage"),
    "reference": ("section subsection rule subrule clause subclause schedule article regulation "
                  "chapter paragraph para item entry"),
}
# Hinglish unit words take no English plurals; they are listed in their own forms.
_HINGLISH_UNITS = ("ghanta ghante ghanton din dino dinon hafta hafte hafton saptah mahina mahine "
                   "mahino mahinon saal saalon varsh varshon baras barason rupaye rupaiye rupaiya "
                   "rupiya rupaya")
UNIT_WORDS = {}   # word -> its group
for _group, _words in _UNIT_BASES.items():
    for _w in _words.split():
        for _f in _plurals(_w):
            UNIT_WORDS[_f] = _group
for _w in _HINGLISH_UNITS.split():
    UNIT_WORDS[_w] = "time" if not _w.startswith("rup") else "money or count"
UNIT_WORDS.pop("rules")      # "the Rules" names the DPDP Rules; the singular stays banned
for _w in "cl cls sec secs sch subsec subcl ss art arts reg regs sched twelvemonth twelvemonths".split():
    UNIT_WORDS[_w] = "time" if _w.startswith("twelve") else "reference"
PER_CENT = re.compile(r"\bper[\s-]*cents?\b", re.I)
PART_REF = re.compile(r"\b[Pp](?i:arts?)[\s-]+(?:\(\s*\w+\s*\)|(?:[A-Z]|[IVXLCDM]+|one)(?![A-Za-z'’]))")
# A part marker such as (q), (zz) or (xiv) in prose names a clause outside any slot.
PART_MARKER = re.compile(r"(?<![A-Za-z])\(\s*(?:[a-z]{1,2}|[ivxlcdm]{1,6}|[IVXLCDM]{1,6})\s*\)"
                         r"|(?<=[A-Za-z])\((?!s\)|es\))\s*\w{1,6}\s*\)")

# E6: real words one letter away from a unit or reference word. Exempt from the fuzzy check.
FUZZY_EXEMPT = {
    "annul", "annuls", "scheduler", "schedulers",
    "cause", "causes", "rules", "ruled", "ruler", "rulers", "scheduled", "particle", "particles",
    "sentry", "sentries", "gentry", "acres", "lacks", "laces", "lances", "crest", "crests",
    "brass", "praise", "hazard", "hazards", "machine", "machines", "minuet", "mines", "salon",
    "yearn", "yearns", "manes", "parka", "dingo", "articled",
}
FUZZY_MIN = 5

ENGLISH_NUMBER_WORDS = (set(WORD_NUM) - {"one"}) | {
    "zero", "nil", "dozen", "dozens", "half", "halves", "twice", "thrice", "couple",
    "hundreds", "thousands", "tens", "millions", "billions",
}
HINGLISH_NUMBER_WORDS = set((
    "ek teen chaar char paanch panch chhe chhah saat aath nau das gyarah barah baarah terah "
    "chaudah pandrah solah satrah atharah unnis bees ikkis baais teis chaubis pachis pachchis "
    "chhabbis sattais atthais untis tees chalis chaalis adtalis pachas pachaas saath sattar assi "
    "nabbe sau dedh dhai sawa paune aadha bahattar").split())
# "do" (two) is left out: it is the English "do" in "do not".
NUMBER_WORDS = ENGLISH_NUMBER_WORDS | HINGLISH_NUMBER_WORDS
_COMPOUND = re.compile(r"(?:" + "|".join(sorted(WORD_NUM, key=len, reverse=True)) + r"){2,}")
MONTH_NAMES = re.compile(r"\b(?i:january|february|march|april|may|june|july|august|september|october|november|december|"
                         r"jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\b")
_MAY_AS_MONTH = re.compile(r"\b(?i:in|of|on|by|until|till|since|from|mid|during|early|late|next|last|this|before|after)"
                           r"[\s-]+may\b")
HIGH_ORDINAL = re.compile(r"\b(?i:fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|\w+teenth|\w+tieth|"
                          r"hundredth|thousandth|(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-?(?:first|second|third))\b")
ROMAN = re.compile(r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})")

_NUMBER_UNIT = re.compile(r"(?:" + "|".join(sorted(WORD_NUM, key=len, reverse=True)) + r")+(?:"
                          + "|".join(sorted(UNIT_WORDS, key=len, reverse=True)) + r")")
PROSE_PUNCT = set(" .,;:'\"?!()-") | set("‘’“”—–")

# ---------------------------------------------------------------- helpers


def squash(text):
    return re.sub(r"\s+", " ", text or "").strip()


KNOWN_NOTIFICATIONS = {}   # id -> {"citation": ..., "date": ISO}


def load_law(law_dir):
    KNOWN_NOTIFICATIONS.clear()
    notes = os.path.join(law_dir, "dpdp-notifications.jsonl")
    if os.path.exists(notes):
        with open(notes) as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    KNOWN_NOTIFICATIONS[r["id"]] = {"citation": r.get("citation"),
                                                    "date": r.get("date") or r.get("published")}
    # The Rules themselves are G.S.R. 846(E) of 13 November 2025 (law-import README, sources table).
    KNOWN_NOTIFICATIONS.setdefault("gsr-846e-2025", {"citation": "G.S.R. 846(E)", "date": "2025-11-13"})
    law = {}
    for name in ("dpdp-act-2023.jsonl", "dpdp-rules-2025.jsonl"):
        with open(os.path.join(law_dir, name)) as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    law[r["id"]] = r
    return law


NUMBER_WORD_SET = set(WORD_NUM) | {"and", "hundred", "thousand", "lakh", "crore"}


def _joins(ch):
    return ch.isalnum() or ch in "-'’"


def _cuts_number_start(q_words, prev):
    """The quote starts inside a number phrase ("fifty crore" out of "two hundred and fifty")."""
    return bool(q_words and q_words[0] in WORD_NUM and prev and prev[0] in NUMBER_WORD_SET)


def _cuts_number_end(q_words, nxt):
    """The quote ends inside a number phrase ("extend to two" out of "two hundred")."""
    return bool(q_words and q_words[-1] in NUMBER_WORD_SET and nxt and nxt[0] in NUMBER_WORD_SET)


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
            if _cuts_number_start(q_words, prev) or _cuts_number_end(q_words, nxt):
                ok = False
        if ok:
            return True
        start = text.find(quote, start + 1)
    return False


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
    """The text of the sub-section (and clause) a label names, e.g. 'section 44(1)'.
    Returns None when the label is a range or cannot be located."""
    m = re.match(r"\s*(?:section|rule)\s+\d+[A-Za-z]?((?:\(\w+\))+)\s*$", label or "", re.I)
    if not m:
        return None
    subs = re.findall(r"\((\w+)\)", m.group(1))
    lines = (record.get("text") or "").split("\n")
    if not subs[0].isdigit() and _segment(lines, "1", "num", skip_first=False) is not None:
        return None               # the text has numbered sub-sections: a clause needs one first
    seg, parent = lines, None
    for depth, sub in enumerate(subs):
        kind = _marker_kind(sub, parent)
        seg = _segment(seg, sub, kind, skip_first=depth > 0)
        if seg is None:
            return None
        parent = kind
    return squash(" ".join(seg))


ROMAN_LOWER = re.compile(r"m{0,3}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})")
_ROMAN_VAL = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}


def _roman_int(r):
    total = 0
    for a, b in zip(r, r[1:] + " "):
        v = _ROMAN_VAL[a]
        total += -v if b != " " and _ROMAN_VAL.get(b, 0) > v else v
    return total


def _int_roman(n):
    out = ""
    for v, r in ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"), (50, "l"),
                 (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")):
        while n >= v:
            out, n = out + r, n - v
    return out


def _marker_kind(marker, parent):
    if marker.isdigit():
        return "num"
    if parent == "letter" and ROMAN_LOWER.fullmatch(marker):
        return "roman"
    return "letter"


def _next_marker(kind, marker):
    if kind == "num":
        return str(int(re.match(r"\d+", marker).group(0)) + 1)
    if kind == "roman":
        return _int_roman(_roman_int(marker) + 1)
    if marker == "z":
        return "za"
    return marker[:-1] + chr(ord(marker[-1]) + 1)


_KIND_RE = {"num": re.compile(r"\d+[A-Z]?"), "letter": re.compile(r"[a-z]{1,2}"), "roman": ROMAN_LOWER}


def _segment(lines, marker, kind, skip_first):
    """Lines of the part `marker` among the siblings of its level. A sibling is the first
    marker of that kind, then each marker that follows on from the last ((a), (b), (c) ...),
    so a sub-clause (i) is never taken for clause (i) or for a part of another level."""
    marks = []
    for i, line in enumerate(lines):
        if skip_first and i == 0:
            continue
        t = re.sub(r"^\s*\d+[A-Za-z]?\.\s*(?:[^(\n]*?—\s*)?", "", line) if i == 0 else line
        mm = re.match(r"\s*\((\w+)\)", t)
        if mm:
            marks.append((i, mm.group(1)))
    siblings, expected = [], None
    for k, (i, mk) in enumerate(marks):
        if not _KIND_RE[kind].fullmatch(mk):
            continue
        follows = mk == expected or (kind == "num" and expected is not None
                                     and int(re.match(r"\d+", mk).group(0)) >= int(expected))
        if expected is None or follows:
            nxt = marks[k + 1][1] if k + 1 < len(marks) else None
            if kind == "letter" and ROMAN_LOWER.fullmatch(mk) and nxt and nxt == _int_roman(_roman_int(mk) + 1):
                continue          # (i) followed by (ii): sub-clauses of the clause before
            siblings.append((i, mk))
            expected = _next_marker(kind, mk)
    for n, (i, mk) in enumerate(siblings):
        if mk == marker:
            stop = siblings[n + 1][0] if n + 1 < len(siblings) else len(lines)
            return lines[i:stop]
    return None


def _human(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B')} {d.year}"


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
    try:
        datetime.date.fromisoformat(text)
    except ValueError:
        sys.exit(f"Refusing: --as-of {text!r} is not a real date (YYYY-MM-DD).")
    return text


# ---------------------------------------------------------------- template parsing (E2)

SLOT_TYPES = {"ref", "name", "period", "amount", "count", "date", "notification", "notified"}
VALUE_SLOTS = {"period", "amount", "count"}
NO_PART_SLOTS = VALUE_SLOTS | {"notification", "notified"}
SLOT = re.compile(r"\{([^{}]*)\}")
ID = r"[a-z][a-z0-9-]*"
PART = r"\w+(?:\(\w+\))*"
TARGET = re.compile(r"(" + ID + r")(?:#(" + PART + r"))?", re.ASCII)
_INDIAN = r"(?:\d{1,3}|\d{1,2}(?:,\d{2})*,\d{3})"            # 250, 10,000, 1,00,000
# re.ASCII: in Python \d also matches Devanagari and other digits, which float() then reads.
PERIOD_VALUE = re.compile(r"(?:[1-9]\d*|[a-z]+(?:-[a-z]+)?) (?:hours?|days?|weeks?|months?|years?)", re.ASCII)
AMOUNT_VALUE = re.compile(r"₹" + _INDIAN + r"(?: (?:crore|lakh))?", re.ASCII)
COUNT_VALUE = re.compile(_INDIAN + r" (?:crore|lakh)", re.ASCII)
_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def number_in_words(n):
    """The house spelling of 0-99: 'seventy-two', 'eighteen'."""
    if n < 20:
        return _ONES[n]
    return _TENS[n // 10] + ("" if n % 10 == 0 else "-" + _ONES[n % 10])


def _canonical_period(value):
    num, unit = value.split(" ")
    if num.isdigit():
        n = int(num)
    else:
        n = words_to_int(num)
        if n is None or n > 99 or number_in_words(n) != num:
            return False
    return (unit.endswith("s")) == (n != 1)


def _part_labels(part):
    """'6(b)(ii)' -> ['6', 'b', 'ii']."""
    if not part:
        return []
    first = re.match(r"\w+", part).group(0)
    return [first] + re.findall(r"\((\w+)\)", part[len(first):])


def parse_template(template):
    """Split a template into prose strings and slot dicts. Returns (pieces, errors)."""
    pieces, errs, pos = [], [], 0
    for m in SLOT.finditer(template):
        pieces.append(template[pos:m.start()])
        pos = m.end()
        body = m.group(1)
        kind, sep, rest = body.partition(":")
        if not sep or kind not in SLOT_TYPES:
            errs.append(f"slot {m.group(0)!r}: unknown slot type {kind!r}")
            continue
        args, bar, value = rest.partition("|")
        if kind in VALUE_SLOTS and not (bar and value):
            errs.append(f"slot {m.group(0)!r}: a {kind} slot needs a value after '|'")
            continue
        if kind not in VALUE_SLOTS and bar:
            errs.append(f"slot {m.group(0)!r}: a {kind} slot takes no typed value")
            continue
        targets = args.split(",") if kind in ("ref", "date") else [args]
        parsed = []
        for t in targets:
            tm = TARGET.fullmatch(t)
            if not tm:
                parsed = None
                break
            parsed.append((tm.group(1), tm.group(2)))
        if not parsed:
            errs.append(f"slot {m.group(0)!r}: malformed target {args!r}")
            continue
        if kind in NO_PART_SLOTS and any(p for _, p in parsed):
            errs.append(f"slot {m.group(0)!r}: a {kind} slot takes no part")
            continue
        pieces.append({"type": kind, "targets": parsed, "value": value if bar else None, "raw": m.group(0)})
    pieces.append(template[pos:])
    for p in pieces:
        if isinstance(p, str) and ("{" in p or "}" in p):
            errs.append("template has an unclosed or stray brace")
            break
    return pieces, errs


def prose_of(pieces):
    """The template with every slot replaced by a space."""
    return "".join(p if isinstance(p, str) else " " for p in pieces)


# ---------------------------------------------------------------- rendering


def _label(law, ident, part, kind):
    rec = law.get(ident)
    if rec is None:
        return None
    if ident == "act-schedule":
        return "The Schedule" if kind == "ref" else "the Schedule"
    text = rec.get("citation") or ident
    return text + "".join(f"({x})" for x in _part_labels(part))


def _date_for(rec, part):
    """(ISO date, None) for a provision or part, or (None, reason)."""
    entries = _in_force_entries(rec)
    if not entries:
        return None, "has no start date in the in-force table"
    if not part:
        dates = {e["from"] for e in entries}
        if len(dates) == 1:
            return dates.pop(), None
        return None, "has more than one start date; name the part, as in {date:id#N}"
    kind = "rule" if rec["id"].startswith("rules-r") else "section"
    num = str(rec.get("number") or "")
    labels = _part_labels(part)
    want = f"{kind} {num}" + "".join(f"({x})" for x in labels)
    listed, whole = [], []
    for e in entries:
        label = squash(e.get("provision")).lower()
        if label == want:
            return e["from"], None
        m = re.match(rf"{kind} {re.escape(num)}\b(.*)$", label)
        if not m:
            continue
        rest = m.group(1).strip()
        if rest.startswith(", except"):
            excluded, mine = rest[len(", except"):].strip(), want[len(kind) + 1:]
            if not (mine.startswith(excluded) or excluded.startswith(mine)):
                whole.append(e["from"])
            continue
        if not rest:
            whole.append(e["from"])
            continue
        for item in rest.split(","):
            subs = re.findall(r"\((\w+)\)", item)
            rng = re.fullmatch(r"\s*\((\d+)\)-\((\d+)\)\s*", item)
            if rng and labels[0].isdigit() and int(rng.group(1)) <= int(labels[0]) <= int(rng.group(2)):
                listed.append(e["from"])
            elif not rng and subs and labels[:len(subs)] == subs:
                listed.append(e["from"])
    found = set(listed) or set(whole)
    if len(found) == 1:
        return found.pop(), None
    return None, f"has no single start date listed for {want}"


def render(pieces, law):
    return render_spans(pieces, law)[0]


def render_spans(pieces, law):
    """The rendered answer and the (start, end) span each slot fills in it."""
    out, spans, pos = [], [], 0
    for p in pieces:
        text = p if isinstance(p, str) else _render_slot(p, law)
        if not isinstance(p, str):
            spans.append((pos, pos + len(text)))
        out.append(text)
        pos += len(text)
    return "".join(out), spans


def _render_slot(p, law):
    t, (ident, part) = p["type"], p["targets"][0]
    if t == "ref":
        labels = [_label(law, i, pt, "ref") for i, pt in p["targets"]]
        return "(" + ", ".join(x or "?" for x in labels) + ")"
    if t == "name":
        return _label(law, ident, part, "name") or "?"
    if t in VALUE_SLOTS:
        return p["value"]
    if t == "date":
        dates = {_date_for(law[i], pt)[0] if i in law else None for i, pt in p["targets"]}
        d = dates.pop() if len(dates) == 1 else None
        return _human(d) if d else "?"
    if t == "notification":
        return (KNOWN_NOTIFICATIONS.get(ident) or {}).get("citation") or "?"
    d = (KNOWN_NOTIFICATIONS.get(ident) or {}).get("date")                 # notified
    return _human(d) if d else "?"


# ---------------------------------------------------------------- whole-render check (E16, E17)

_EDGE = "\"'“”‘’.,;:!?()—–"
NOTE_CITE = re.compile(r"\b(?:G\.S\.R\.|S\.O\.)")
REF_WORDS = {"section", "sections", "rule", "schedule", "schedules"}


def _figure_word(core):
    """True if a rendered word carries a figure, date, unit or reference."""
    if any(unicodedata.category(ch) in ("Nd", "No", "Nl") or ch in "₹$€£§%" for ch in core):
        return True
    if NOTE_CITE.search(core):
        return True
    for w in re.split(r"[-'’]", core.lower()):
        if w in UNIT_WORDS or w in REF_WORDS or w in NUMBER_WORDS:
            return True
        if MONTH_NAMES.fullmatch(w) and w != "may":
            return True
    return False


def check_rendered_spans(text, spans):
    """E17: nothing joins a slot (no letter, digit or hyphen on either side, no two slots
    touching). E16: every letter and digit of a figure-bearing word of the rendered answer
    lies inside a slot's span."""
    errs = []
    for a, b in spans:
        left = text[a - 1] if a > 0 else " "
        right = text[b] if b < len(text) else " "
        if left.isalnum() or left == "-" or right.isalnum() or right == "-":
            errs.append(f"rendered answer has {text[max(0, a - 3):b + 3]!r}: text touches a slot")
            break
    for (a1, b1), (a2, b2) in zip(spans, spans[1:]):
        if not _slots_separated(text[b1:a2]):
            errs.append(f"rendered answer has {text[a1:b2]!r}: two slots touch; only whitespace separates slots")
            break
    owner = {}
    for n, (a, b) in enumerate(spans):
        owner.update({i: n for i in range(a, b)})
    for m in re.finditer(r"\S+", text):
        if not _figure_word(m.group(0).strip(_EDGE)):
            continue
        chars = [i for i in range(m.start(), m.end()) if text[i].isalnum()]
        if any(i not in owner for i in chars):
            errs.append(f"rendered answer has {m.group(0)!r} outside a slot: figures, dates and "
                        "references enter only through a slot")
            break
        if not _in_one_span({owner[i] for i in chars}):
            errs.append(f"rendered answer has {m.group(0)!r} across more than one slot: a figure, date "
                        "or reference must lie inside one slot")
            break
    return errs


def _slots_separated(gap):                                                  # E23
    """Two slots are separate only if whitespace lies between them."""
    return any(ch.isspace() for ch in gap)


def _in_one_span(owners):                                                   # E24
    return len(owners) <= 1


# ---------------------------------------------------------------- prose checks (E3-E7)


def _tokens(prose):
    """Lower-cased words; hyphens split words, a possessive 's is dropped."""
    return [re.sub(r"['’]s$", "", w).lower() for w in re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?", prose)]


def check_digits(prose):                                                    # E3
    for ch in prose:
        if unicodedata.category(ch) in ("Nd", "No", "Nl"):
            return [f"prose has {ch!r}: figures may only enter through a slot"]
    return []


def check_characters(prose):                                                # E4
    for ch in prose:
        if not ((ch.isascii() and ch.isalpha()) or ch in PROSE_PUNCT):
            return [f"prose has {ch!r} (U+{ord(ch):04X}): only letters, spaces and . , ; : ' \" ? ! ( ) - "
                    "‘ ’ “ ” — – are allowed outside slots"]
    return []


def check_unit_words(prose):                                                # E5
    errs = []
    for w in _tokens(prose):
        if w in UNIT_WORDS:
            errs.append(f"prose has {w!r}: a {UNIT_WORDS[w]} word may only enter through a slot")
            break
    joined = [w.replace("-", "").lower() for w in re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)+", prose)]
    for w in joined:
        if w in UNIT_WORDS:
            errs.append(f"prose has {w!r} split by hyphens: a {UNIT_WORDS[w]} word may only enter through a slot")
            break
    for pat, why in ((PER_CENT, "a percentage"), (PART_REF, "a schedule part"), (PART_MARKER, "a part marker")):
        m = pat.search(prose)
        if m:
            errs.append(f"prose has {m.group(0)!r}: {why} may only enter through a slot")
    return errs


def _one_edit(a, b):
    """True if a becomes b by one inserted, deleted or swapped (adjacent) letter."""
    if a == b:
        return False
    la, lb = len(a), len(b)
    if la == lb:
        diff = [i for i in range(la) if a[i] != b[i]]
        return len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]
    if abs(la - lb) != 1:
        return False
    short, long_ = (a, b) if la < lb else (b, a)
    return any(long_[:i] + long_[i + 1:] == short for i in range(len(long_)))


def check_fuzzy_units(prose):                                               # E6
    for w in _tokens(prose):
        if len(w) < FUZZY_MIN or w in UNIT_WORDS or w in FUZZY_EXEMPT:
            continue
        for unit in UNIT_WORDS:
            if _one_edit(w, unit):
                return [f"prose has {w!r}, one letter away from {unit!r}: spell figures through a slot"]
    return []


def _number_after_may(word):                                               # E18
    """'May one', 'may third': a number word or ordinal after May makes it a date."""
    return word in {"first", "second", "third", "one"} or word in NUMBER_WORDS


def check_number_words(prose):                                              # E7
    for w in _tokens(prose) + [w.replace("-", "").lower() for w in re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)+", prose)]:
        if w in NUMBER_WORDS or _COMPOUND.fullmatch(w) or _NUMBER_UNIT.fullmatch(w):
            return [f"prose has {w!r}: number words other than 'one' may only enter through a slot"]
    for m in MONTH_NAMES.finditer(prose):
        if m.group(0).lower() == "may":
            before = prose[:m.start()].rstrip()
            after = re.match(r"[\W_]*(?:the\s+)?(\w+)", prose[m.end():], re.I)
            ordinal = bool(after) and _number_after_may(after.group(1).lower())
            if m.group(0) == "may" and not ordinal and not _MAY_AS_MONTH.search(prose[:m.end()][-20:]):
                continue          # "the Board may ...": the verb
            if m.group(0) == "May" and (not before or before[-1] in ".?!") and not ordinal:
                continue          # "May the Board ...": the verb, at the start of a sentence
        return [f"prose has {m.group(0)!r}: a month name (dates enter only through a slot)"]
    m = HIGH_ORDINAL.search(prose)
    if m:
        return [f"prose has {m.group(0)!r}: an ordinal past third (a date or deadline enters only through a slot)"]
    for m in re.finditer(r"\b[MDCLXVI]{2,}\b", prose):
        if ROMAN.fullmatch(m.group(0)):
            return [f"prose has {m.group(0)!r}: a Roman numeral"]
    return []


SLOT_SUFFIX = re.compile(r"\}\s*\((?!\s*\{)")


def check_slot_suffix(template):                                            # E5
    """A bracket right after a slot reads as a part of it ("Section 2(F)"), whatever its case."""
    m = SLOT_SUFFIX.search(template)
    if m:
        return [f"template has {template[max(0, m.start() - 12):m.end() + 4]!r}: a bracket right after a slot "
                "reads as a part; put the part inside the slot"]
    return []


PROSE_CHECKS = [check_digits, check_characters, check_unit_words, check_fuzzy_units, check_number_words]

# ---------------------------------------------------------------- slot checks (E9-E12)


LAW_IDS_ALL = {f"act-s{n}" for n in range(1, 45)} | {f"rules-r{n}" for n in range(1, 24)}


COMMENCEMENT = re.compile(r"\bRules? (\d+(?:(?:, | and | to )\d+)*),? shall come into force\b")


def _named_in_quotes(quoted):
    """Rules a verified quote of the Rules' commencement rule (Rule 1) brings into force,
    as 'Rules 3, 5 to 16, 22 and 23 shall come into force'. Cross-references in other
    provisions ('under section 8') do not count."""
    ids = set()
    for q in quoted.get("rules-r1", []):
        for m in COMMENCEMENT.finditer(q):
            for a, b in re.findall(r"(\d+)(?: to (\d+))?", m.group(1)):
                ids |= {f"rules-r{n}" for n in range(int(a), int(b or a) + 1)}
    return ids


def check_ref_slots(slots, law, quoted):                                    # E9
    errs = []
    for s in slots:
        if s["type"] not in ("ref", "name", "date"):
            continue
        for ident, part in s["targets"]:
            if ident not in law:
                errs.append(f"slot {s['raw']}: unknown provision {ident!r}")
                continue
            if part:
                rec = law[ident]
                if not re.match(r"(?:act-s|rules-r)\d", ident):
                    errs.append(f"slot {s['raw']}: {rec['citation']} has no numbered parts")
                    continue
                kind = "rule" if ident.startswith("rules-r") else "section"
                label = f"{kind} {rec.get('number')}" + "".join(f"({x})" for x in _part_labels(part))
                if _part_text(rec, label) is None:
                    errs.append(f"slot {s['raw']}: {rec['citation']} has no part {part}")
                    continue
            if s["type"] == "date":
                if ident not in quoted and ident not in _named_in_quotes(quoted):
                    errs.append(f"slot {s['raw']}: {ident} is not cited by a claim or named in a quote")
            elif ident not in quoted:
                errs.append(f"slot {s['raw']}: no claim with a quote cites {ident}")
    return errs


def money(text, rupees):
    """(value, unit) figures in text: with rupees=True only sums of money (₹, Rs, INR, or
    followed by 'rupees'); with rupees=False only counts (crore or lakh with no money word)."""
    out = set()
    for m in AMOUNT.finditer(text):
        v = to_number(m.group(1))
        is_money = (bool(re.match(r"\s*(?:₹|Rs|INR)", m.group(0)))
                    or bool(re.match(r"\s*(?:of\s+)?rupees\b", text[m.end():], re.I))
                    or bool(re.search(r"\brupees\s*$", text[:m.start()], re.I)))
        if v is not None and is_money == rupees:
            out.add((v, m.group(2).lower()))
    if rupees:
        out |= {x for x in amounts(text) if x[1] == "rupees"}
    return out


def _sentences(pieces):
    """Slot lists per sentence (split at a full stop in the prose)."""
    out, cur = [], []
    for p in pieces:
        if isinstance(p, dict):
            cur.append(p)
        else:
            for _ in re.finditer(r"[.?!](?=\s|$)", p):
                out.append(cur)
                cur = []
    out.append(cur)
    return out


def check_figure_slots(slots, law, quoted, pieces=()):                      # E10
    errs = []
    named = {}
    for sent in _sentences(pieces):
        ids = {s["targets"][0][0] for s in sent if s["type"] in ("ref", "name") and len(s["targets"]) == 1}
        for s in sent:
            named[id(s)] = ids
    for s in slots:
        if s["type"] not in VALUE_SLOTS:
            continue
        ident, value = s["targets"][0][0], s["value"]
        if ident not in law:
            errs.append(f"slot {s['raw']}: unknown provision {ident!r}")
            continue
        pattern = {"period": PERIOD_VALUE, "amount": AMOUNT_VALUE, "count": COUNT_VALUE}[s["type"]]
        if not pattern.fullmatch(value) or (s["type"] == "period" and not _canonical_period(value)):
            errs.append(f"slot {s['raw']}: {value!r} is not a {s['type']} in the house form")
            continue
        if ident not in named.get(id(s), {ident}):
            errs.append(f"slot {s['raw']}: no ref or name slot for {ident} in the same sentence")
        quotes = quoted.get(ident, [])
        if s["type"] == "period":
            want = time_limits(value)
            found = set().union(*(time_limits(q) for q in quotes)) if quotes else set()
        else:
            want = money(value, True) if s["type"] == "amount" else money(value, False)
            found = set().union(*(money(q, s["type"] == "amount") for q in quotes)) if quotes else set()
        if not want or not want <= found:
            errs.append(f"slot {s['raw']}: no quote of a claim citing {ident} contains {value}")
    return errs


def _pending(claims, law, as_of, quoted_claims):
    """{(cite, ISO date)} that must be dated: start dates after the check date."""
    need, errs = set(), []
    for i, cl in quoted_claims:
        cite = cl["cite"]
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
                need.add((cite, d))
    return need, errs


def check_date_slots(slots, law, need):                                     # E11
    errs, have = [], set()
    for s in slots:
        if s["type"] != "date":
            continue
        found = {}
        for ident, part in s["targets"]:
            if ident not in law:
                continue                  # reported by check_ref_slots
            d, why = _date_for(law[ident], part)
            if d is None:
                errs.append(f"slot {s['raw']}: {law[ident]['citation']} {why}")
            else:
                found[ident] = d
        if len(set(found.values())) > 1:
            errs.append(f"slot {s['raw']}: these provisions start on different dates; use one slot per date")
            continue
        have |= set(found.items())
    for cite, d in sorted(need - have):
        errs.append(f"{law[cite]['citation']} is not in force until {_human(d)}; "
                    f"the template needs a {{date:{cite}}} slot for it")
    return errs


def check_notification_slots(slots):                                        # E12
    return [f"slot {s['raw']}: unknown notification {s['targets'][0][0]!r}"
            for s in slots if s["type"] in ("notification", "notified")
            and s["targets"][0][0] not in KNOWN_NOTIFICATIONS]


# ---------------------------------------------------------------- claims, labels, lanes (E13)


def check_claims(claims, law):
    """Returns (errors, [(index, claim)] whose quotes are verified)."""
    errs, good = [], []
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
        good.append((i, cl))
        errs += check_claim_text(i, cl, law, quote)
    return errs, good


def _ref_ids(text):
    """(label, id) for each Section, Rule or schedule a free text names."""
    out = []
    for m in re.finditer(r"\b(Section|Rule)s? (\d+[A-Z]?)", text):
        out.append((m.group(0), ("act-s" if m.group(1) == "Section" else "rules-r") + m.group(2).lower()))
    for m in re.finditer(r"\b(First|Second|Third|Fourth|Fifth|Sixth|Seventh) Schedule\b", text):
        n = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh"].index(m.group(1)) + 1
        out.append((m.group(0), f"rules-sch{n}"))
    for m in re.finditer(r"\b[Tt]he Schedule\b", text):
        out.append((m.group(0), "act-schedule"))
    return out


def check_claim_text(i, cl, law, quote):                                    # E19
    """A claim's own text may state only what its quote and its provision support."""
    errs, text, cite = [], cl.get("text", ""), cl["cite"]
    for v, unit in sorted(amounts(text) - amounts(quote)):
        errs.append(f"claim {i}: states {v:g} {unit} but its own quote does not")
    for kind in (True, False):
        for v, unit in sorted(money(text, kind) - money(quote, kind)):
            errs.append(f"claim {i}: states {v:g} {unit} {'rupees' if kind else 'as a count'} but its own quote does not")
    for v, unit in sorted(time_limits(text) - time_limits(quote)):
        errs.append(f"claim {i}: states {v:g} {unit}s but its own quote does not")
    for m in re.finditer(r"\b\d{1,2} (?:" + "|".join(MONTHS) + r") \d{4}\b", text):
        iso = datetime.datetime.strptime(m.group(0), "%d %B %Y").date().isoformat()
        if iso not in _in_force(law[cite]):
            errs.append(f"claim {i}: gives {m.group(0)}, which is not a start date of {law[cite]['citation']}")
    for label, ident in _ref_ids(text):
        if not (ident == cite or cite.startswith(ident + "-")):
            errs.append(f"claim {i}: names {label}, but the claim cites {law[cite]['citation']}")
    return errs + check_claim_leftover(i, text)


CLAIM_FORMS = [AMOUNT, RUPEES, WORD_RUPEES, TIME,
               re.compile(r"\b\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|"
                          r"November|December) \d{4}\b"),
               re.compile(r"\b(?:Section|Rule)s? \d+[A-Z]?(?:\(\w+\))*"),
               re.compile(r"\b(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh) Schedule(?:, Part [AB])?\b|\b[Tt]he Schedule\b")]


def check_claim_leftover(i, text):                                          # E25
    """Fail-closed: after the known forms (checked above against the quote and provision)
    are taken out, nothing figure-, date- or reference-like may be left in claim text."""
    odd = [ch for ch in text if unicodedata.category(ch) in ("Nd", "No", "Nl") and ch not in "0123456789"]
    if odd:
        return [f"claim {i}: prose has {odd[0]!r}: only ASCII digits may state a figure"]
    rest = text
    for pat in CLAIM_FORMS:
        rest = pat.sub(lambda m: " " * len(m.group(0)), rest)
    errs = check_digits(rest) + check_unit_words(rest) + check_number_words(rest)
    if NOTE_CITE.search(rest):
        errs.append("prose has a notification citation")
    return [f"claim {i}: {e}" for e in errs[:1]]


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]
ROW_FIELDS = {"id", "question", "kind", "reader", "lane", "provisions", "answer_template", "answer", "claims",
              "source", "as_of", "drafted_by", "review", "version"}
CLAIM_FIELDS = {"text", "cite", "quote", "applies_from"}


def check_fields(example):                                                  # E20
    """Training rows carry only fields the checker reads or bookkeeping it ignores."""
    errs = [f"row has field {k!r}, which the checker does not check" for k in sorted(set(example) - ROW_FIELDS)]
    for i, cl in enumerate(example.get("claims") or [], 1):
        errs += [f"claim {i} has field {k!r}, which the checker does not check" for k in sorted(set(cl) - CLAIM_FIELDS)]
    return errs


def check_labels(example):
    return [f"label {f}={example.get(f)!r} not in approved set"
            for f, allowed in (("kind", KINDS), ("reader", READERS), ("lane", LANES))
            if example.get(f) not in allowed]


def check_lane(example, answer):
    errs, lane, claims = [], example.get("lane"), example.get("claims") or []
    if lane in QUOTE_REQUIRED_LANES and not claims:
        errs.append(f"{lane} needs at least one quoted claim")
    if lane in REFUSAL_LANES:
        if not REFUSAL.search(answer):
            errs.append("refusal lane must say plainly that the law does not answer or a lawyer is needed")
        if DUTY_WORDS.search(answer) and not claims:
            errs.append("refusal answer states a duty ('must', 'shall' ...) with no quote behind it")
    return errs


def check_names(answer, law):
    law_blob = " ".join(squash(r["text"]) + " " + r.get("title", "") for r in law.values())
    return [f"answer uses {t!r}, which is not in the law text" for t in _invented_terms(answer, law_blob)]


# ---------------------------------------------------------------- the whole check


def check_has_template(template):                                           # E1
    if not isinstance(template, str) or not template.strip():
        return ["example has no answer_template"]
    return []


def check_rendered(answer, rendered):                                       # E1
    if answer != rendered:
        return [f"answer is not the rendered template; expected {rendered!r}"]
    return []


def check(example, law, as_of=None):
    """as_of: the ISO date the answer is read on; defaults to today. The example's own
    `as_of` field is ignored, so an example cannot move its own check date."""
    as_of = valid_date(datetime.date.today().isoformat() if as_of is None else as_of)
    errs = check_fields(example) + check_labels(example)
    claims = example.get("claims") or []
    claim_errs, good = check_claims(claims, law)
    errs += claim_errs
    quoted = {}
    for _, cl in good:
        quoted.setdefault(cl["cite"], []).append(squash(cl["quote"]))

    template = example.get("answer_template")
    answer = example.get("answer", "")
    missing = check_has_template(template)                                   # E1
    if missing:
        return errs + missing + check_lane(example, answer)
    pieces, parse_errs = parse_template(template)                            # E2
    errs += parse_errs
    slots = [p for p in pieces if isinstance(p, dict)]
    prose = prose_of(pieces)
    for fn in PROSE_CHECKS:                                                  # E3-E7
        errs += fn(prose)
    errs += check_slot_suffix(template)
    errs += check_ref_slots(slots, law, quoted)                              # E9
    errs += check_figure_slots(slots, law, quoted, pieces)                   # E10
    need, pend_errs = _pending(claims, law, as_of, good)
    errs += pend_errs
    errs += check_date_slots(slots, law, need)                               # E11
    errs += check_notification_slots(slots)                                  # E12
    rendered, spans = render_spans(pieces, law)
    if not parse_errs:
        errs += check_rendered(answer, rendered)                             # E1
        errs += check_rendered_spans(rendered, spans)                        # E16, E17
    errs += check_lane(example, rendered)                                    # E13
    errs += check_names(prose, law)
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
