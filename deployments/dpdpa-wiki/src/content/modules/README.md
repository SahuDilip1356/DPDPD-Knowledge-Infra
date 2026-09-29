# Course modules — authoring format

One Markdown file per module, `NN-slug.md`, in this folder. The front-matter is the
Module record from `specs/dpdpa-wiki-reimagine/spec.md`; the body is the lessons.
`scripts/check-citations.mjs` runs before every build and fails it if any lesson or quiz
item cites a provision outside the module's `provisions` list.

```
---
slug: what-is-dpdpa                 # fixed slugs, in order: what-is-dpdpa, core-rules,
order: 1                            #   peoples-rights, special-cases, enforcement, in-your-business
title: What is the DPDPA?
summary: One or two sentences shown on /learn and at the top of the module.
minutes: 12                         # honest reading time
provisions: [S1, S2, S3, S44, R1, R2]   # every label the module may cite
next: core-rules                    # null on module 6
handoff_label: Check your readiness on SaralPrivacy   # module 6 only
handoff_url: https://saralprivacy.com/assessment      # module 6 only
quiz:
  - q: "Who does the Act apply to?"
    a: "Only companies with more than 250 employees"
    b: "Anyone processing digital personal data in India, and some processing outside it"
    c: "Only government departments"
    d: "Only companies that sell online"
    answer: b
    cites: S3
  - q: "..."
    a: "..."
    b: "..."
    c: "..."
    d: "..."
    answer: a
    cites: S2, R2
---

Intro paragraph(s) before the first heading: what this module is for, in two sentences.

## First lesson heading

Plain English for a business owner. Cite the law inline as "Section 3(1)", "Rule 7(2)",
"the First Schedule", "the Schedule to the Act". Every citation is turned into a link to
the provision page at build time and checked against `provisions`.

## Second lesson heading

…
```

Rules for authors:

- Plain English for a first-time reader. Say "Data Principal" and "Data Fiduciary"
  (the Act's terms), never "data subject" or "controller".
- Every legal statement rests on a cited provision. If you cannot cite it, do not say it.
- Quote the gazette only in short fragments; the provision page has the full text.
- Rules that are not yet in force: say so once per lesson where it matters ("Rule 7
  applies from 13 May 2027"). Dates: Rules 1, 2, 17–21 from 13 November 2025; Rule 4
  from 13 November 2026; Rules 3, 5–16, 22, 23 from 13 May 2027. Schedules follow the
  rule that invokes them.
- No penalties outside the Schedule's seven rows. No "₹250 crore for everything".
- 5 to 8 quiz items, four options each, exactly one correct, each item cites a label
  in `provisions`. Distractors must be plausible and wrong, not silly.
- 4 to 7 lessons of 150 to 350 words each. `minutes` is words ÷ 200, rounded up.
- Source material: the verified provision text in `src/data/law/provisions.json` and the
  answer knowledge objects in `staging/competitive_intel/knowledge_objects/answer_kos.jsonl`
  (each carries verbatim evidence and the labels it cites). Competitor pages are never a
  source.
