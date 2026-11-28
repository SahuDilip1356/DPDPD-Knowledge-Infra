# Evals for structured answers (option C)

Status: approved by Dilip on 2026-11-28 ("Start build"). Built on `feat/training-examples`; see Build notes.
Risk tier: High (training data for a model that answers law questions).

## The idea

Today an answer is free text, and the checker has to find every way a number can be
spelled. Three review rounds showed that list never ends.

With option C, each example carries an `answer_template`. The template is plain prose
with typed slots in braces. A figure, a date, an amount or a reference can only enter
through a slot. The checker validates every slot against the law, then renders the
template into `answer`. The prose between slots may not contain a digit, a unit word or a
reference word at all, so there is nothing to spell.

```
"answer_template": "Tell the Board within {period:rules-r7|72 hours} of becoming aware of the breach {ref:rules-r7}."
"answer":          "Tell the Board within 72 hours of becoming aware of the breach (Rule 7)."
```

The closing layer is the unit and reference words. A number means nothing legally
without one ("hours", "crore", "Section"), and units are a short, closed list. Number
spellings are not.

## Slots

| Slot | Renders | Checked against |
|---|---|---|
| `{ref:act-s8}`, `{ref:act-s8#6}`, `{ref:rules-r8,rules-sch3}` | (Section 8), (Section 8(6)), (Rule 8, Third Schedule) | The id exists; the part exists in that provision's text; a claim with a quote cites it |
| `{name:act-s3}` | Section 3 | Same as `ref` |
| `{period:rules-r7\|72 hours}` | 72 hours | The value parses as a number and a unit; that period appears in a quote of a claim citing that id |
| `{amount:act-schedule\|₹250 crore}` | ₹250 crore | The value parses; that amount appears in a quote of a claim citing that id |
| `{count:rules-sch3\|2 crore}` | 2 crore | Same as `amount` |
| `{date:act-s8}`, `{date:act-s6#9}`, `{date:act-s8,rules-r7}` | 13 May 2027 | Nothing typed: the date comes from the in-force table; several ids must share one date |
| `{notification:gsr-846e-2025}` | G.S.R. 846(E) | The id is a known notification |
| `{notified:gsr-846e-2025}` | 13 November 2025 | Nothing typed: the date comes from the notification record |

## Pass/fail checks

Each line below becomes at least one test. "Fail" means the checker reports the example
as failing and names the reason.

**Format**
- E1. An example without `answer_template`, or whose `answer` is not exactly the
  rendered template, fails.
- E2. An unknown slot type, a malformed slot or an unclosed brace fails.

**Prose (the template with every slot removed)**
- E3. Any digit fails, including full-width and other Unicode digits.
- E4. Any character outside letters, spaces and `. , ; : ' " ? ! ( ) -` plus ‘ ’ “ ” — –
  fails. That covers ₹, $, %, §, zero-width characters and Devanagari.
- E5. Any unit or reference word fails, in English or Hinglish:
  - time: minute, hour, hr, day, week, fortnight, month, year, yr, decade, annum, quarter;
    ghanta, ghante, ghanton, din, dino, hafta, hafte, hafton, saptah, mahina, mahine,
    saal, varsh, baras
  - money and counts: rupee, Rs, INR, paisa, paise, crore, cr, lakh, lac, laakh, karod,
    karor, arab, kharab, thousand, hazaar, million, mn, billion, bn, trillion, grand,
    dollar, USD, euro, pound, percent, per cent
  - references: section, sub-section, rule (singular), sub-rule, clause, sub-clause,
    schedule, article, regulation, chapter, paragraph, para, item, entry, and "Part"
    followed by a letter or numeral
  - every plural and case form of the above.
  The peer's round-3 inputs all become tests that must fail: "do hafte", "das hours",
  "chaubis ghanton", "das rupaiye", "pandrah laakh", "fourty-eight hours",
  "sevnty-two hours", "seventytwo hours", "within X days", "Section X", "one lac",
  "one cr", "one bn", "one arab", "one grand", "section one", "sub-rule (ix) of Rule 7",
  "clause (z) of Rule 7".
- E6. A word of five or more letters that is one inserted, deleted or swapped letter away
  from a unit or reference word fails ("hourss", "yeras", "secton"). A short list of real
  words is exempt, such as "cause" next to "clause".
- E7. English and Hinglish number words fail, except "one" (as in "one of the duties").
- E8. A few fixed names pass: "the DPDP Act", "the DPDP Rules", "the Act", "the Rules",
  "the Act and Rules", "the Data Protection Board". Nothing with a number is on that
  list.

**Slots**
- E9. A `ref` or `name` slot fails if the id is unknown, the part is not in that
  provision's text, or no claim with a quote cites that id.
- E10. A `period`, `amount` or `count` slot fails if the value does not parse, or if no
  quote of a claim citing that id contains the same figure ("seventy-two hours" in the
  quote matches 72 hours).
- E11. If a cited provision is not in force on the check date, the template must carry a
  `date` slot for it (or for the part a claim relies on), or the example fails.
- E12. An unknown notification id fails.

**Kept from today's checker, unchanged**
- E13. Quotes are verbatim, at least six words, on word boundaries; labels come from the
  approved sets; refusal lanes use a plain refusal phrase; invented names fail.

**Batches and tests**
- E14. Batches 01 and 02 are converted and report 0 failing. Where a rendered answer
  differs from its legally reviewed v2 text, the difference is listed for a legal
  re-read. Expected differences are small, such as "the same day" becoming a date slot.
- E15. Mutation run: switching off any single check makes at least one test fail. No
  surviving mutants.

## What this does not close

- A misspelled unit word under five letters, such as "dayz", or one with a replaced letter,
  such as "hoyrs" (see Build notes). Fuzzy matching on short
  words would flag ordinary words ("days" is one letter from "dais" and "dads").
- A number with no unit and no slot, such as "within fourty-eight". It has no legal
  meaning on its own, and a legal reviewer still reads every answer.
- Whether the model trains on the template (it would then emit slots and the API would
  render them) or on the rendered text. Both fields are stored. This is decided at step
  3 of the training guide, not here.

## Build notes (2026-11-28)

Choices made while building and in review rounds 1 to 3. Dilip accepted them on 2026-11-28:

- **One date slot can name several provisions** (`{date:act-s8,rules-r7}`) when they start
  on the same date. Most answers say "From 13 May 2027" once for several duties. The slot
  fails if the dates differ.
- **A date slot's provision must be cited by a claim, or brought into force by a quoted part
  of Rule 1** ("Rules 3, 5 to 16, 22 and 23 shall come into force" lets an answer date Rule
  3). Round 1 showed that with no such tie, a refusal answer could give any provision's
  date; round 2 showed that cross-references ("under section 14 of the TRAI Act") must not
  count.
- **Ordinals up to "third" are allowed; "fourth" and later, and month names in any case or
  short form ("november", "Nov"), are not.** "a first description" passes. "the fourteenth
  of May" and "in January" fail, because a date needs no unit word. "May" passes only as the
  verb: at the start of a sentence and not followed by "first", "second" or "third", or as
  lowercase "may" not after a word like "in" or "since".
- **A figure must sit in the same sentence as a ref or name slot naming only its provision**, and
  an `amount` must come from a quote that names rupees, a `count` from one that does not.
  Period values use the house spelling (72 hours, seventy-two hours, one year).
- **A part marker in prose fails** ("(q)", "(zz)", "Act(q)"), as do "cl", "sec", "sch" and
  "Part-A". "(EU)" and "person(s)" pass. Parts are found by the structure of the text, so (i)
  under clause (b) is never taken for clause (i), and a clause cannot skip a numbered
  sub-section ("Rule 7(a)" fails; it is 7(1)(a)).
- **E6 covers inserted, deleted and swapped letters, not replaced ones.** A replaced letter
  turns unit words into common words ("years" into "hears"). "hoyrs" is not caught.

Known gaps, left to the legal read:
- The Schedule is one provision, so a figure is tied to the Schedule but not to its row:
  "{amount:act-schedule|₹200 crore}" for the safeguards breach passes, though that row says
  ₹250 crore. Fixing it needs row-level parts for the Schedule.
- Tense ("already applies now, since 13 May 2027") and vague periods ("overnight", "a score
  of fines").
- The banned words also fail ordinary English: "add a clause to the contract", "as a rule",
  "annual report", "half of the data", "the two of them".

E14: the converter ties each date and figure to the provision its own sentence names. Where
a date such as an opening "From 13 May 2027" covers provisions named only in later
sentences, it is given to them and the example is flagged "check attribution". It also
flags a sentence that names a provision which does not start on the date it gives. 47 of
the 100 carry a flag. Every changed or flagged answer is in
`staging/training-examples/batch01_c_changes.md` and `batch02_c_changes.md`.

## Whole-render check (approved by Dilip on 2026-11-28)

Asked for by Dilip on 2026-11-28 ("Setu: whole-render check") after the PR #17 review at
40313e1. Today the checker reads the prose with each slot blanked to a space, so text glued
to a slot is never seen as part of the figure or reference. These pass today against the
real law, and must fail:

| Template | Renders |
|---|---|
| `under {name:rules-r7}A` | under Rule 7A |
| `under {name:rules-r7}-A` | under Rule 7-A |
| `within l{period:rules-r7\|72 hours}` | within l72 hours |
| `within O{period:rules-r7\|72 hours}` | within O72 hours |
| `{period:rules-r7\|72 hours}{period:rules-r7\|72 hours}` | 72 hours72 hours |

The fix is to render the whole answer, with every slot filled from the law data, and scan
the rendered text instead of the blanked prose.

**Pass/fail checks**
- E16. On the rendered answer, every digit, number word, currency sign, unit word, month
  name, reference ("Section 8", "Rule 7(2)(b)", a schedule name) and notification citation
  must lie wholly inside the rendered span of one slot. Anything found outside a slot fails.
  The five templates above fail.
- E17. A slot's rendered span must have a word boundary on both sides: no letter, digit or
  hyphen may touch it, and two slots may not touch each other. A bracket right after a slot
  still fails (today's rule, kept).
- E18. "May" or "may" followed by a number word or an ordinal ("May one", "may third") is a
  date with no slot, and fails wherever it appears.
- E19. Claim text (`claims[].text`) is checked too. It may state a period, amount or count
  only if its own quote holds the same figure, a date only if it is a start date of its own
  provision, and a reference only to its own provision. "Report within 48 hours under
  Section 9." with a Rule 7 quote fails on both the figure and the reference.
- E20. Training rows carry no unchecked text. The converter no longer writes `answer_v2`
  into a batch. The v2 answers go to a separate `batchNN_v2_answers.jsonl` that the training
  step never reads. A test fails if any batch row has a field outside the checked set (id,
  question, kind, reader, lane, provisions, answer_template, answer, claims and the
  bookkeeping fields source, as_of, drafted_by, review, version).
- E21. Mutation run: switching off the whole-render boundary check, or the claim-text check,
  makes at least one test fail. Both join `mutation_run.py`.
- E22. Batches 01 and 02 are re-run under the new rules. Any example that now fails is
  listed by id and reason before anything is changed, and fixes go through the rewrites file
  and the legal re-read list.

E1 to E15 stay as they are and must stay green.

**Build result (2026-11-28).** The five templates above fail. 79 tests pass and the mutation
run kills 55 of 55. E22: three examples failed on claim text and were fixed through the
rewrites file, each listed in the changes report. In Q-00071 claim 2 named Rule 4 while
citing Rule 1. In Q-00010 claim 3 stated a period only claim 4's quote holds. In Q-00509
claim 2 named the Second Schedule while citing Rule 16. Batches 01 and 02 then report 0
failing.

**Not part of the evals (done in the same change):** rewrite the PR #17 body for the
structured checker; write the converter's outputs through `scripts/safe_output.py`; remove
three unused names. PR #17 will be squash-merged, because nine earlier commits carry a home
path.
