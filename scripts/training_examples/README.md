# Training examples (Setu training guide, step 2)

Each training example is a question, the exact provisions, and a cited answer in
SaralPrivacy's voice. Batches live in gitignored `staging/training-examples/` until
Dilip approves them.

```bash
L="<main checkout>/staging/law-import"
python3 scripts/training_examples/check_examples.py --law "$L" staging/training-examples/batch01.jsonl
python3 scripts/training_examples/make_review_sheet.py --law "$L" staging/training-examples/batch01.jsonl
python3 -m unittest scripts/training_examples/test_check_examples.py -v
```

The checker fails an example when:
- a quote is not one unbroken run of at least 6 words, in the same case, from the cited
  provision (whitespace is ignored; "…" is not allowed);
- the answer refers to a section, rule or schedule it does not cite, in any form ("s. 9",
  "Sections 8 and 9", "Rules 3 to 16", "Fourth Schedule"), or to a sub-section the cited
  text does not have;
- the answer states a rupee amount (₹, Rs, INR or bare) or a time limit that no quote
  contains, or a claim states an amount its own quote does not contain;
- a cited provision is not in force on the check date (`--as-of`, or today) and the answer
  does not give every pending start date. A claim that relies only on a part already in
  force names it with `applies_from`;
- the answer uses a capitalised name the Act and Rules never use, or a known wrong name
  such as "Data Protection Act" or "Commissioner";
- a label is outside the approved sets, a law-answers or comparison example has no quote,
  or a refusal example has no plain refusal phrase, or states a duty with no quote.

`applies_from` is accepted only when the quote sits inside the sub-section that date
covers in the law file's in-force list. A claim on a range ("section 6(1)-(8)") cannot use
it, and goes to a person.

## What it cannot catch (left to the legal read and Dilip)

- whether a plain-English sentence means what the law means;
- an amount or limit that is quoted correctly but described as being for the wrong duty
  (a ₹250 crore quote presented as the fine for not reporting a breach);
- whether a start date sits next to the duty it belongs to, not just somewhere in the answer;
- clause letters are checked only for presence in the whole provision ("8(1)(a)" passes if
  "(a)" appears anywhere in section 8);
- references written in words ("section nine") and lowercase invented phrases.

It can also fail correct text, such as "Unique Identification Authority". Those false
fails are safe; reword or add the name to the allowlist.
