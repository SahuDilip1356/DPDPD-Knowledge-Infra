"""Convert free-text training answers into structured templates (option C, eval E14).

Each figure, date, amount, reference and notification in `answer` becomes a slot tied to a
cited provision. Optional rewrites (a JSON file of {example id: [[old, new], ...]}) reword
prose that the new checks ban, such as "rule" or "the next day".

Writes three files into gitignored staging/training-examples/, through scripts/safe_output.py:
  <name>.jsonl              the training rows, with no unchecked text (E20)
  <name>_v2_answers.jsonl   the legally reviewed v2 answers, by id; never read for training
  <name>_c_changes.md       every answer whose rendering differs from v2 or whose date or
                            figure was attributed across sentences, for a legal re-read
The v2 answer is read from the input row's `answer_v2`, else from <input>_v2_answers.jsonl
next to the input, else from `answer`.

Usage:
  python3 scripts/training_examples/convert_to_template.py --law <law-import dir> \
      [--rewrites rewrites.json] [--as-of YYYY-MM-DD] --name batch01 <in.jsonl>
"""

import argparse
import datetime
import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import check_examples as c  # noqa: E402
import safe_output  # noqa: E402

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_REL = ("staging", "training-examples")

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


FLAGS = []   # attributions for the legal read, reset per example
DATED = {}     # ISO date -> ids named in a sentence that gives that date, set per example
DATE_RE = re.compile(r"\b\d{1,2} (?:" + MONTHS + r") \d{4}\b")


def _local_ids(sentence, e):
    """Base ids of the provisions the sentence itself names."""
    ids = set()
    for m in re.finditer(r"\bSections (\d+) to (\d+)", sentence):
        ids |= {f"act-s{n}" for n in range(int(m.group(1)), int(m.group(2)) + 1)}
    for m in re.finditer(r"\b(?:Section|Rule) \d+[A-Z]?", sentence):
        ids.add(prov_id(m.group(0), e).split("#")[0])
    for m in re.finditer(r"\b(?:[Tt]he Schedule|(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh) Schedule)\b", sentence):
        try:
            ids.add(sch_id(m.group(0), e))
        except Unresolved:
            pass
    return ids


def date_slot(iso, e, sentence):
    """The cited provisions (or parts) named in the same sentence that start on iso. If the
    sentence names none, every cited provision that starts on iso, flagged for the legal read.
    Else a notification named in the sentence with that date."""
    local = _local_ids(sentence, e)
    ids, fallback = [], []
    for ident in dict.fromkeys(_cites(e)):
        rec = LAW.get(ident)
        if not rec:
            continue
        quotes = [c.squash(cl["quote"]) for cl in e.get("claims") or [] if cl["cite"] == ident]
        part = None if c._date_for(rec, None)[0] == iso else _part_for(rec, iso, quotes)
        if c._date_for(rec, part)[0] != iso:
            continue
        (ids if ident in local else fallback).append(ident + (f"#{part}" if part else ""))
    wrong = sorted(x for x in local if x in _cites(e) and not any(i.split("#")[0] == x for i in ids))
    if wrong:
        FLAGS.append(f"sentence gives {c._human(iso)} and names {', '.join(wrong)}, which "
                     f"{'does' if len(wrong) == 1 else 'do'} not start then")
    extra = [x for x in fallback if x.split("#")[0] not in DATED.get(iso, set())]
    if extra:
        ids += extra
        FLAGS.append(f"date {c._human(iso)} also given to {', '.join(extra)}, named in no dated sentence")
    if ids:
        return "{date:" + ",".join(ids) + "}"
    for m in re.finditer(r"\b(?:G\.S\.R\.|S\.O\.) \d+\(E\)", sentence):
        ident = note_id(m.group(0))
        if c.KNOWN_NOTIFICATIONS[ident]["date"] == iso:
            return "{notified:" + ident + "}"
    raise Unresolved(f"no cited provision starts on {c._human(iso)}")


def figure_slot(kind, value, e, sentence):
    """The claim quoting this figure whose provision the sentence names; flagged when only
    another provision quotes it or several do."""
    if kind == "period":
        measure = c.time_limits
    else:
        measure = lambda t: c.money(t, kind == "amount")  # noqa: E731
    want = measure(value)
    cites = list(dict.fromkeys(cl["cite"] for cl in e.get("claims") or []
                               if want and want <= measure(c.squash(cl["quote"]))))
    if not cites:
        raise Unresolved(f"no claim quotes {value}")
    local = [x for x in cites if x in _local_ids(sentence, e)]
    if len(local) == 1:
        return f"{{{kind}:{local[0]}|{value}}}"
    FLAGS.append(f"{value} given to {cites[0]}: quoted by {', '.join(cites)}; its sentence names "
                 + (", ".join(local) if local else "none of them"))
    return f"{{{kind}:{(local or cites)[0]}|{value}}}"


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
            out.append(figure_slot(g, tok, e, sentence))
    out.append(text[pos:])
    return "".join(out)


def convert(e):
    """Template for one example, converted a sentence at a time so a date or figure goes to
    the provision its own sentence names."""
    text = e["answer"]
    parts = re.split(r"(?<=[.?!])(?<!G\.S\.R\.)(?<!S\.O\.)(\s+)", text)
    DATED.clear()
    for p in parts:
        for m in DATE_RE.finditer(p):
            DATED.setdefault(_iso(m.group(0)), set()).update(_local_ids(p, e))
    return "".join(p if p.isspace() else convert_text(p, e, p) for p in parts)


LAW = {}


def _iso(human):
    try:
        return datetime.datetime.strptime(human, "%d %B %Y").date().isoformat()
    except ValueError:
        raise Unresolved(f"{human} is not a real date")                      # E32


def apply_rewrites(e, rewrites):
    """Rewrites keyed by id change the answer; keyed '<id>#claimN' they change claim N's text.
    A rewrite already applied is kept as it is. Returns the claim changes, for the report."""
    targets = [(e["id"], e, "answer")] + [(f"{e['id']}#claim{i}", cl, "text")
                                          for i, cl in enumerate(e.get("claims") or [], 1)]
    changed = []
    for key, obj, field in targets:
        for old, new in rewrites.get(key, []):
            if old not in obj[field]:
                if new not in obj[field]:
                    sys.exit(f"{key}: rewrite text not found: {old!r}")
                # already applied on an earlier run (claims are not restored from v2)
            obj[field] = obj[field].replace(old, new)
            if "#" in key:
                changed.append(f"{key.split('#')[1]} text: {old!r} -> {new!r}")
    return changed


def claim_template(cl):
    """A claim's text as a template whose slots name only the claim's own provision (E35)."""
    return convert({"answer": cl["text"], "claims": [cl]})


def convert_claims(e):
    """Give every claim a text_template, rebuilt from its text on every run so a claim
    rewrite never leaves a stale template. Returns (changes, problems) for the report."""
    changes, problems = [], []
    for i, cl in enumerate(e.get("claims") or [], 1):
        before = cl["text"]
        try:
            cl["text_template"] = claim_template(cl)
        except Unresolved as err:
            problems.append(f"claim{i}: {err}")
            continue
        cl["text"] = c.render(c.parse_template(cl["text_template"])[0], LAW)
        if cl["text"] != before:
            changes.append(f"claim{i} text: {before!r} -> {cl['text']!r}")
    return changes, problems


def split_v2(rows):
    """Training rows without `answer_v2`, and the v2 answers by id."""
    train, v2 = [], []
    for e in rows:
        e = dict(e)
        if "answer_v2" in e:
            v2.append({"id": e["id"], "answer_v2": e.pop("answer_v2")})
        train.append(e)
    return train, v2


def _v2_answers(src):
    path = re.sub(r"\.jsonl$", "", src) + "_v2_answers.jsonl"
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return {r["id"]: r["answer_v2"] for r in (json.loads(x) for x in f if x.strip())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True)
    ap.add_argument("--rewrites")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--name", required=True, help="plain output name, e.g. batch01")
    ap.add_argument("src")
    a = ap.parse_args()
    LAW.update(c.load_law(a.law))
    rewrites = {}
    if a.rewrites:
        with open(a.rewrites) as f:
            rewrites = json.load(f)
    v2_by_id = _v2_answers(a.src)
    rows, report, problems = [], [], 0
    with open(a.src) as f:
        lines = [x for x in f if x.strip()]
    for line in lines:
        e = json.loads(line)
        original = e.get("answer_v2") or v2_by_id.get(e["id"]) or e["answer"]
        e["answer"] = original
        claim_changes = apply_rewrites(e, rewrites)
        rendered_changes, claim_problems = convert_claims(e)
        claim_changes += rendered_changes
        for msg in claim_problems:
            print(f"UNRESOLVED {e['id']} {msg}")
            problems += 1
        FLAGS.clear()
        try:
            tpl = convert(e)
        except Unresolved as err:
            print(f"UNRESOLVED {e['id']}: {err}")
            problems += 1
            tpl = None
        if tpl is not None:
            e["answer_template"] = tpl
            e["answer"] = c.render(c.parse_template(tpl)[0], LAW)
            e.pop("answer_v2", None)
            errs = c.check(e, LAW, a.as_of)
            if errs:
                problems += 1
                print(f"FAIL {e['id']}: " + "; ".join(errs))
            if e["answer"] != original or FLAGS or claim_changes:
                diff = [w for w in difflib.ndiff(original.split(" "), e["answer"].split(" ")) if w[0] in "+-"]
                report.append(f"### {e['id']}\n\n- v2: {original}\n- v3: {e['answer']}\n- changed words: "
                              + " ".join(f"`{w}`" for w in diff) + "\n"
                              + "".join(f"- check attribution: {f}\n" for f in FLAGS)
                              + "".join(f"- {x}\n" for x in claim_changes))
        e["answer_v2"] = original
        rows.append(e)
    train, v2 = split_v2(rows)
    dump = lambda rs: "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs)  # noqa: E731
    head = (f"# Option C conversion: answers that changed ({len(report)} of {len(rows)})\n\n"
            "Each rendered answer below differs from its legally reviewed v2 text, or had a date or "
            "figure attributed across sentences. Read the changed words for meaning.\n\n")
    safe_output.write_files(REPO_ROOT, OUT_REL, {f"{a.name}.jsonl": dump(train),
                                                 f"{a.name}_v2_answers.jsonl": dump(v2),
                                                 f"{a.name}_c_changes.md": head + "\n".join(report)})
    print(f"{len(rows)} examples, {len(report)} changed, {problems} with problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
