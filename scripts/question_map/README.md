# Question map (Setu training guide, step 1)

Builds about 1,000 DPDPA questions, labelled for training-example drafting. The output
is market-lane data, so it is written only to gitignored `staging/question-map/`; the
script refuses any other path.

```bash
python3 scripts/question_map/build_question_map.py \
  --graph "<main checkout>/staging/competitive_intel/questions/unified_questions.jsonl" \
  --street "<JV Creatives>/Research/Content-Intelligence/clusters/20261002-001__DPDPA-Train-Classes/classified-street.csv"
python3 -m unittest scripts/question_map/test_build_question_map.py -v
```

Kept from each source: the question wording only. Dropped: answers, variants, competitor
names and URLs. Street searches graded `throw_out`, `exam_noise` or `seed_drift` are left out.

## Labels (drafts, `label_source: rule`, `review: pending`)

| Label | Values |
|---|---|
| kind | who, why, how, what, when, where |
| reader | business, learner, public |
| lane | law_answers, law_silent, needs_lawyer, comparison, out_of_scope |

`when` is not in the original five (who, why, how, what, where). It was added because
start dates are one of the most-asked things, and Dilip approves it or folds it into
`what`.

Selection: every kept street question first, then at least 15 graph questions per topic,
then the rest by demand (sites asking it, plus 3 × street hits, plus 2 if SaralPrivacy
asks it).
