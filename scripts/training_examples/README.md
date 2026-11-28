# Training examples (Setu training guide, step 2)

Each training example is a question, the exact provisions, and a cited answer in
SaralPrivacy's voice. Batches live in gitignored `staging/training-examples/` until
Dilip approves them. Review sheets are written through `scripts/safe_output.py`, which
never writes through a symlink or hard link planted at the sheet's name.

```bash
L="<main checkout>/staging/law-import"
python3 scripts/training_examples/check_examples.py --law "$L" staging/training-examples/batch01.jsonl
python3 scripts/training_examples/make_review_sheet.py --law "$L" staging/training-examples/batch01.jsonl
SETU_LAW_DIR="$L" python3 -m unittest scripts/training_examples/test_check_examples.py scripts/training_examples/test_convert_to_template.py -v
SETU_LAW_DIR="$L" python3 scripts/training_examples/mutation_run.py
```

## Structured answers (option C)

Every example carries an `answer_template`: prose with typed slots. A figure, date,
amount, reference or notification can enter the answer only through a slot, and
`answer` must be exactly the rendered template. The approved checks are E1 to E15 in
[EVALS-structured-answers.md](EVALS-structured-answers.md).

| Slot | Renders | Checked against |
|---|---|---|
| `{ref:act-s8}`, `{ref:act-s8#6}`, `{ref:rules-r8,rules-sch3}` | (Section 8), (Section 8(6)), (Rule 8, Third Schedule) | the id exists, the part exists in its text, a claim with a verified quote cites it |
| `{name:act-s3}` | Section 3 | same as `ref` |
| `{period:rules-r7\|72 hours}` | 72 hours | a quote of a claim citing that id holds the same period |
| `{amount:act-schedule\|₹250 crore}` | ₹250 crore | a quote of a claim citing that id holds the same amount |
| `{count:rules-sch3\|2 crore}` | 2 crore | same as `amount` |
| `{date:act-s8}`, `{date:act-s6#9}`, `{date:act-s8,rules-r7}` | 13 May 2027 | nothing typed: the in-force table gives the date |
| `{notification:gsr-843e-2025}` | G.S.R. 843(E) | a known notification |
| `{notified:gsr-843e-2025}` | 13 November 2025 | nothing typed: the notification record gives the date |

The prose between the slots may not contain:
- a digit in any script;
- a character other than ASCII letters, spaces and `. , ; : ' " ? ! ( ) -` plus ‘ ’ “ ” — –;
- a unit or reference word, in English or Hinglish (hour, crore, lakh, Section, rule, schedule,
  clause, Part A, per cent, ghante, saal and the rest), or a word one inserted, deleted or
  swapped letter away from one ("hourss", "yeras", "secton");
- a number word other than "one", in English or Hinglish, or a Roman numeral;
- a month name in any case or short form, or an ordinal past "third";
- a part marker such as "(q)", or "cl", "sec", "sch", "Part-A".

"the Rules" is allowed; the singular "rule" is not. A figure slot must share its sentence
with a ref or name slot for the same provision; an amount must come from a quote that names
rupees, a count from one that does not. A date slot's provision must be cited by a claim or
brought into force by a quoted part of Rule 1. A cited provision that is not in force
on the check date needs a `date` slot for it, or for the part a claim relies on
(`applies_from`). The check date is `--as-of` or today; an example cannot set its own.

The checks then run again on the rendered answer: every digit, number word, unit word,
month, reference and notification must lie inside a slot's span, and no letter, digit,
hyphen or other slot may touch a slot ("Rule 7A", "l72 hours" and "72 hours72 hours"
fail). Only whitespace separates two slots, and each figure-bearing word must lie inside
one slot. Claim text may state only figures its own quote holds, dates its own provision
starts on, and references to its own provision; after those forms are taken out, any digit,
unit or reference word, number word, month or notification left fails. Slot values, slot
targets and claim text take ASCII digits only. A row may carry only fields the checker
reads, so the old free-text `answer_v2` lives in its own file.

The claim checks are unchanged. A quote is one unbroken run of at least 6 words, in the
same case, from the cited provision, starting and ending on whole words, and never cutting
a number phrase. Labels must come from the approved sets, law-answers and comparison
examples need a quote, and refusal lanes need a plain refusal phrase. Capitalised names the
Act and Rules never use fail.

`mutation_run.py` switches off each check in turn and fails if the tests still pass. The
tests that read the real law run only when `SETU_LAW_DIR` (default `staging/law-import`)
exists, so CI, which has no law-import folder, skips them; run them locally.

## Converting free-text answers

`convert_to_template.py` turns a v2 batch into templates and writes three files into
gitignored `staging/training-examples/` through `scripts/safe_output.py`:
`<name>.jsonl` (the training rows), `<name>_v2_answers.jsonl` (the reviewed v2 answers by
id, never read for training) and `<name>_c_changes.md` (every answer whose rendering
differs from v2, whose claim text was changed, or whose date or figure was attributed
across sentences: "check attribution"). Rewordings go in a JSON file: `{id: [[old, new]]}`
changes the answer and `{"<id>#claimN": [[old, new]]}` changes claim N's text.

```bash
python3 scripts/training_examples/convert_to_template.py --law "$L" --as-of 2026-11-27 \
  --rewrites staging/training-examples/c_rewrites.json --name batch01 staging/training-examples/batch01.jsonl
```

## What it cannot catch (left to the legal read and Dilip)

- whether a plain-English sentence means what the law means;
- an amount or limit that is quoted correctly but described as being for the wrong duty;
- whether a date slot sits next to the duty it belongs to;
- which row of the Schedule a figure comes from (the Schedule is one provision);
- a misspelled unit word under five letters ("dayz") or with a replaced letter ("hoyrs");
- a number with no unit and no slot ("within fourty-eight");
- lowercase invented phrases ("data breach inquiry report").

It can also fail correct text, such as "Unique Identification Authority". Those false
fails are safe; reword, or add the name to the allowlist.
