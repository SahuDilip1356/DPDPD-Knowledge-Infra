# Question map (Setu training guide, step 1)

Builds the DPDPA question bank, labelled for training-example drafting: our own written
questions (`written_questions.py`, every one kept) plus market questions up to the target.
`coverage_check.py` counts the bank per provision, lane, reader and kind, and lists every
missed target. The output
is market-lane data, so all three outputs (`<name>.jsonl`, `<name>_summary.json`,
`<name>_review.csv`) are written only directly inside gitignored `staging/question-map/`.
`--name` takes a plain file name only. Writing goes through `scripts/safe_output.py`,
which walks to the folder without following symlinks, writes each file to a new temp file,
and renames it into place, so a symlink or hard link planted at an output name is replaced,
never written through.

```bash
python3 scripts/question_map/build_question_map.py \
  --graph "<main checkout>/staging/competitive_intel/questions/unified_questions.jsonl" \
  --street "<JV Creatives>/Research/Content-Intelligence/clusters/20261002-001__DPDPA-Train-Classes/classified-street.csv"
python3 scripts/question_map/coverage_check.py --law "<main checkout>/staging/law-import" --map staging/question-map/question_map.jsonl
SETU_LAW_DIR="<main checkout>/staging/law-import" python3 -m unittest scripts/question_map/test_build_question_map.py scripts/question_map/test_coverage.py scripts/test_safe_output.py -v
```

The law-tied coverage tests read `SETU_LAW_DIR` (default `staging/law-import`, which is
gitignored), so they run locally only; CI skips them.

Kept from each source: the question wording only. Dropped: answers, variants, competitor
names and URLs. Street searches graded `throw_out`, `exam_noise` or `seed_drift` are left out.

## Labels (drafts, `label_source: rule`, `review: pending`)

| Label | Values |
|---|---|
| kind | who, why, how, what, when, where |
| reader | business, learner, public |
| lane | law_answers, law_silent, needs_lawyer, comparison, out_of_scope |

`when` was added to the original five (who, why, how, what, where) because start dates
are among the most-asked things. Dilip approved all six kinds on 2026-11-27.

Selection: every kept street question first, then at least 15 graph questions per topic,
then the rest by demand (sites asking it, plus 3 × street hits, plus 2 if SaralPrivacy
asks it).
