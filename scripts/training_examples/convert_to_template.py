"""Convert free-text training answers into structured templates (option C, eval E14).

Each figure, date, amount, reference and notification in `answer` becomes a slot tied to a
cited provision. Optional rewrites (a JSON file of {example id: [[old, new], ...]}) reword
prose that the new checks ban, such as "rule" or "the next day". The output keeps the old
text as `answer_v2` and writes a report of every example whose rendered answer differs from
it, for a legal re-read.

Usage:
  python3 scripts/training_examples/convert_to_template.py --law <law-import dir> \
      [--rewrites rewrites.json] --report diffs.md <in.jsonl> <out.jsonl>
"""

import argparse
import datetime
import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import check_examples as c  # noqa: E402

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
ORD = {"First": 1, "Second": 2, "Third": 3, "Fourth": 4, "Fifth": 5, "Sixth": 6, "Seventh": 7}
TOKEN = re.compile(
    r"(?P<paren>\((?:[^()]|\([^()]*\))*\))"
    r"|(?P<date>\b\d{1,2} (?:" + MONTHS + r") \d{4}\b)"
    r"|(?P<note>\b(?:G\.S\.R\.|S\.O\.) \d+\(E\))"
    r"|(?P<prov>\b(?:Section|Rule) \d+[A-Z]?(?:\(\w+\))*)"
    r"|(?P<sch>\b(?:[Tt]he Schedule|(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh) Schedule(?:, Part [AB])?)\b)"
    r"|(?P<amount>₹\d[\d,]*(?: (?:crore|lakh))?)"
    r"|(?P<count>\b\d[\d,]* (?:crore|lakh)\b)"
    r"|(?P<period>\b(?:\d+|" + c.NUM_WORDS + r") (?:hours?|days?|weeks?|months?|years?)\b)",
    re.I,
)


class Unresolved(Exception):
    pass


def _cites(e):
    return [cl["cite"] for cl in e.get("claims") or []]


def prov_id(text, e):
    m = re.fullmatch(r"(Section|Rule) (\d+[A-Z]?)((?:\(\w+\))*)", text)
    ident = ("act-s" if m.group(1) == "Section" else "rules-r") + m.group(2).lower()
    subs = re.findall(r"\((\w+)\)", m.group(3))
    part = (subs[0] + "".join(f"({s})" for s in subs[1:])) if subs else None
    return ident + (f"#{part}" if part else "")


def sch_id(text, e):
    if text.lower() == "the schedule":
        return "act-schedule"
    m = re.fullmatch(r"(\w+) Schedule(?:, Part ([AB]))?", text)
    base = f"rules-sch{ORD[m.group(1)]}"
    if m.group(2):
        return f"{base}-{m.group(2).lower()}"
    cited = [x for x in _cites(e) if x == base or x.startswith(base + "-")]
    if len(cited) == 1:
        return cited[0]
    if base in LAW:
        return base
    raise Unresolved(f"{text}: cite one part of it")


def note_id(text):
    for k, v in c.KNOWN_NOTIFICATIONS.items():
        if v["citation"] == text:
            return k
    raise Unresolved(f"unknown notification {text}")


def _part_for(rec, iso, quotes):
    """A part of rec that starts on iso: from a plain in-force label, else the first
    sub-section or clause that holds one of the claim quotes."""
    kind = "rule" if rec["id"].startswith("rules-r") else "section"
    for x in c._in_force_entries(rec):
        if x["from"] != iso or "except" in x["provision"]:
            continue
        m = re.search(r"\d+[A-Za-z]?((?:\(\w+\))+)", x["provision"])
        if m:
            subs = re.findall(r"\((\w+)\)", m.group(1))
            return subs[0] + "".join(f"({s})" for s in subs[1:])
    for n in range(1, 31):
        for part in [str(n)] + [f"{n}({x})" for x in "abcdefghijklmnopqrstuvwxyz"]:
            labels = c._part_labels(part)
            text = c._part_text(rec, f"{kind} {rec.get('number')}" + "".join(f"({x})" for x in labels))
            if text and any(q in text for q in quotes) and c._date_for(rec, part)[0] == iso:
                return part
    return None


def date_slot(iso, e, sentence):
    """Every cited provision (or part) that starts on iso; else a notification named in the
    same sentence with that date."""
    ids = []
    for ident in dict.fromkeys(_cites(e)):
        rec = LAW.get(ident)
        if not rec:
            continue
        if c._date_for(rec, None)[0] == iso:
            ids.append(ident)
            continue
        quotes = [c.squash(cl["quote"]) for cl in e.get("claims") or [] if cl["cite"] == ident]
        part = _part_for(rec, iso, quotes)
        if part and c._date_for(rec, part)[0] == iso:
            ids.append(f"{ident}#{part}")
    if ids:
        return "{date:" + ",".join(ids) + "}"
    for m in re.finditer(r"\b(?:G\.S\.R\.|S\.O\.) \d+\(E\)", sentence):
        ident = note_id(m.group(0))
        if c.KNOWN_NOTIFICATIONS[ident]["date"] == iso:
            return "{notified:" + ident + "}"
    raise Unresolved(f"no cited provision starts on {c._human(iso)}")


def figure_slot(kind, value, e):
    measure = c.time_limits if kind == "period" else c.amounts
    want = measure(value)
    for cl in e.get("claims") or []:
        if want and want <= measure(c.squash(cl["quote"])):
            return f"{{{kind}:{cl['cite']}|{value}}}"
    raise Unresolved(f"no claim quotes {value}")


def paren_refs(inner, e):
    """'Rule 8, Third Schedule' -> '{ref:rules-r8,rules-sch3}', or None if not all references."""
    items = [x.strip() for x in inner.split(",")]
    ids = []
    for it in items:
        rng = re.fullmatch(r"Sections (\d+) to (\d+)", it)
        if rng:
            ids += [f"act-s{n}" for n in range(int(rng.group(1)), int(rng.group(2)) + 1)]
        elif re.fullmatch(r"(?:Section|Rule) \d+[A-Z]?(?:\(\w+\))*", it):
            ids.append(prov_id(it, e))
        elif re.fullmatch(r"[Tt]he Schedule|\w+ Schedule", it):
            ids.append(sch_id(it, e))
        elif re.fullmatch(r"Part [AB]", it) and ids and ids[-1].startswith("rules-sch"):
            ids[-1] = re.sub(r"-[ab]$", "", ids[-1]) + "-" + it[-1].lower()
        else:
            return None
    return "{ref:" + ",".join(ids) + "}"


def convert_text(text, e, sentence=""):
    out, pos = [], 0
    for m in TOKEN.finditer(text):
        out.append(text[pos:m.start()])
        pos = m.end()
        g, tok = m.lastgroup, m.group(0)
        if g == "paren":
            ref = paren_refs(tok[1:-1], e)
            if ref is None and re.fullmatch(r"\((?:G\.S\.R\.|S\.O\.) \d+\(E\)\)", tok):
                ref = "({notification:" + note_id(tok[1:-1]) + "})"
            out.append(ref if ref else "(" + convert_text(tok[1:-1], e, sentence) + ")")
        elif g == "date":
            out.append(date_slot(_iso(tok), e, sentence))
        elif g == "note":
            out.append("{notification:" + note_id(tok) + "}")
        elif g == "prov":
            out.append("{name:" + prov_id(tok, e) + "}")
        elif g == "sch":
            out.append("{name:" + sch_id(tok, e) + "}")
        else:
            out.append(figure_slot(g, tok, e))
    out.append(text[pos:])
    return "".join(out)


def convert(e):
    """Template for one example, converted a sentence at a time so a date can be matched
    to a notification named in its own sentence."""
    text = e["answer"]
    parts = re.split(r"(?<=[.;:])(?<!G\.S\.R\.)(?<!S\.O\.)(\s+)", text)
    return "".join(p if p.isspace() else convert_text(p, e, p) for p in parts)


LAW = {}


def _iso(human):
    return datetime.datetime.strptime(human, "%d %B %Y").date().isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True)
    ap.add_argument("--rewrites")
    ap.add_argument("--report", required=True)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("src")
    ap.add_argument("out")
    a = ap.parse_args()
    LAW.update(c.load_law(a.law))
    rewrites = json.load(open(a.rewrites)) if a.rewrites else {}
    rows, report, problems = [], [], 0
    for line in open(a.src):
        if not line.strip():
            continue
        e = json.loads(line)
        original = e.get("answer_v2", e["answer"])
        e["answer"] = original
        for old, new in rewrites.get(e["id"], []):
            if old not in e["answer"]:
                sys.exit(f"{e['id']}: rewrite text not found: {old!r}")
            e["answer"] = e["answer"].replace(old, new)
        try:
            tpl = convert(e)
        except Unresolved as err:
            print(f"UNRESOLVED {e['id']}: {err}")
            problems += 1
            tpl = None
        if tpl is not None:
            e["answer_template"] = tpl
            e["answer"] = c.render(c.parse_template(tpl)[0], LAW)
            e["answer_v2"] = original
            errs = c.check(e, LAW, a.as_of)
            if errs:
                problems += 1
                print(f"FAIL {e['id']}: " + "; ".join(errs))
            if e["answer"] != original:
                diff = [w for w in difflib.ndiff(original.split(" "), e["answer"].split(" ")) if w[0] in "+-"]
                report.append(f"### {e['id']}\n\n- v2: {original}\n- v3: {e['answer']}\n- changed words: "
                              + " ".join(f"`{w}`" for w in diff) + "\n")
        rows.append(e)
    with open(a.out, "w") as f:
        for e in rows:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    with open(a.report, "w") as f:
        f.write(f"# Option C conversion: answers that changed ({len(report)} of {len(rows)})\n\n"
                "Each rendered answer below differs from its legally reviewed v2 text. "
                "Read the changed words for meaning.\n\n" + "\n".join(report))
    print(f"{len(rows)} examples, {len(report)} changed, {problems} with problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
