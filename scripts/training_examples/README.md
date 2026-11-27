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
- the answer names a section or rule it does not cite, or a rupee amount that no quote
  contains;
- the answer uses a capitalised legal-looking term that the Act and Rules never use;
- it cites a provision that is not in force on the example's `as_of` date, and the answer
  does not give the start date;
- a label is outside the approved sets, a law-answers example has no quote, or a refusal
  example does not say plainly that the law is silent or a lawyer is needed.

The checker cannot tell whether a plain-English sentence means what the law means. That
needs a separate legal read and Dilip's approval.
