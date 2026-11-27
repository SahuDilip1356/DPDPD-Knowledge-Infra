# Training examples (Setu training guide, step 2)

Each training example is a question, the exact provisions, and a cited answer in
SaralPrivacy's voice. Batches live in gitignored `staging/training-examples/` until
Dilip approves them. Review sheets are written through `scripts/safe_output.py`, which
never writes through a symlink or hard link planted at the sheet's name.

```bash
L="<main checkout>/staging/law-import"
python3 scripts/training_examples/check_examples.py --law "$L" staging/training-examples/batch01.jsonl
python3 scripts/training_examples/make_review_sheet.py --law "$L" staging/training-examples/batch01.jsonl
python3 -m unittest scripts/training_examples/test_check_examples.py -v
```

The checker fails closed. An answer may carry a number, an amount, a time limit or a
reference only in these house forms:

| Form | Example | Also checked |
|---|---|---|
| Date | 13 May 2027 | every pending start date of a cited provision must appear |
| Notification | G.S.R. 843(E) | |
| Citation | (Section 8(6)), (Rule 7), (Sections 11 to 14) | each number is cited; each sub-section exists in the cited text |
| Schedule | (The Schedule), Fourth Schedule, Part A | the schedule is cited |
| Amount | ₹250 crore, ₹10,000 | the value and unit are in that claim's own quote |
| Time limit | 72 hours, seventy-two hours, one year | the value and unit are in a quote |

The checker removes those forms after checking them. If anything numeric or reference-like
is left (a digit, a currency sign, "Rs", "crores", "u/s", "§", "s. 8", "schedule" in another
form, "72-hour", "a fortnight", "seven business days"), the example fails, whatever the
wording. The tests list every wording a reviewer has found, and they must keep failing.

It also fails an example when:
- a quote is not one unbroken run of at least 6 words, in the same case, from the cited
  provision, starting and ending on whole words (no "…");
- the answer uses a capitalised name the Act and Rules never use, or a known wrong name;
- the check date is not a real YYYY-MM-DD date (`--as-of`, or today);
- a claim's `applies_from` does not match the sub-section its quote comes from;
- a label is outside the approved sets, a law-answers or comparison example has no quote,
  or a refusal example has no plain refusal phrase, or states a duty with no quote.

## What it cannot catch (left to the legal read and Dilip)

- whether a plain-English sentence means what the law means;
- an amount or limit that is quoted correctly but described as being for the wrong duty
  (a ₹250 crore quote presented as the fine for not reporting a breach);
- whether a start date sits next to the duty it belongs to, not only somewhere in the answer;
- clause letters are checked only for presence in the whole provision ("8(1)(a)" passes if
  "(a)" appears anywhere in section 8);
- references written in words ("section nine") and lowercase invented phrases.

It can also fail correct text, such as "Unique Identification Authority". Those false
fails are safe; reword or add the name to the allowlist.
