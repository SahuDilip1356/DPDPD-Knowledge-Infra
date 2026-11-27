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

The checker cannot tell whether a plain-English sentence means what the law means. That
needs a separate legal read and Dilip's approval.
