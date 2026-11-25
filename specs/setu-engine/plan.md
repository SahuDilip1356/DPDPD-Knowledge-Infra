# Plan: Setu engine

**Status:** draft
**Spec:** ./spec.md
**Date:** 2026-11-25

Nothing in this plan runs a training job. T10 only writes and dry-runs the job; it runs
for real only after Dilip signs D3 on the decision sheet.

## Architecture

```
clients (wiki Ask, saralprivacy.com, Setu chatbot, third platform)
      │  POST /v1/answer   GET /v1/explainers/{urn}
      ▼
deployments/dpdpa-backend/src/api/            front door: keys, rate limit, shape, redaction
      ▼
deployments/dpdpa-backend/src/reasoning/
   query_rewriter.py   street words → law terms (glossary, no facts)          [new]
   reasoning_engine.py retrieve_context(): dense (Pinecone) + BM25 in parallel,
                       reciprocal-rank fusion, rerank top-20 → top-5,
                       then graph expansion (definitions in s.2, linked rules)
   model_client.py     answer model (provider and model are settings, D1)
   claim_checker.py    quote verbatim, id exists, legal-term lexicon          [new]
   guardrails.py       input guard (existing), output guard calls the checker
      ▼
law lane store (Supabase + Pinecone, read-only)   explainer store [new table]
```

What exists today: `/knowledge/query` (api_service.py:255) runs the engine; retrieval is
Pinecone top-5 with a BM25 fallback only when Pinecone is down (keyword_ranker.py,
TOP_K=5, MIN_COVERAGE=0.2); the eval runner `evals/runner.py --corpus real` reports
recall 0.447 offline (baseline `evals/baselines/real_corpus_offline.json`: 64 cases,
expected-in-retrieved 0.725, mean prompt 2,502 tokens) and 0.71 live after PR #9;
`ModelUnavailable` already maps to 503 (PR #11).

## Decisions

- Keep `/knowledge/query` working; add `/v1/answer` beside it, and move the wiki to it
  behind a flag (T16). Rejected: changing `/knowledge/query` in place, which breaks the
  live site during the switch.
- Fuse dense and BM25 with reciprocal-rank fusion (k=60) instead of tuning score
  weights. RRF needs no score calibration between the two lists.
- Rerank with a hosted cross-encoder over 20 candidates. Rejected: an LLM reranker,
  which adds a model call and a second place to hallucinate.
- The legal-term lexicon is built from the law lane text at index time, not hand
  written, so it follows amendments.
- Readability: Flesch-Kincaid grade via `textstat` (not installed yet; added to
  requirements in T13), with the section 2 defined terms masked before grading.
- Voice tuning, if D3 is yes: LoRA on the reader model's open-weight base, trained on
  Hugging Face Jobs in Dilip's account, adapter stored in a private repo. Details and
  cost in decisions.md D3.

## Tasks

### T1: Fill the decision sheet's legal and price facts
- implements: AC17
- depends_on: none
- files: specs/setu-engine/decisions.md
- risk: tier1
- size: S
- complexity: 4
- verify: test "$(grep -c '^- \[ \] Yes' specs/setu-engine/decisions.md)" -ge 7 && ! grep -n 'TBD' specs/setu-engine/decisions.md
- notes: check from the law lane whether any country is notified under section 16
  before writing D1's residency line (A5). Every price needs its URL and retrieval date.

### T2: Add a reader-model switch to the real-corpus eval and run the bake-off
- implements: AC2, AC6
- depends_on: none
- files: evals/runner.py, evals/real_corpus.py, evals/test_real_corpus.py, evals/reports/
- risk: tier2
- size: S
- complexity: 4
- verify: python3 -m pytest evals/test_real_corpus.py -q
- notes: add `--chat-model` and record the model in the report. The live runs cost cents
  each through OpenRouter (`OPENAI_API_KEY= ... --live --price-in ... --price-out ...`);
  Dilip opts in to each live run. Retrieval stays fixed so A1 can be tested.

### T3: Run dense and BM25 retrieval together and fuse the lists
- implements: AC2
- depends_on: T2
- files: deployments/dpdpa-backend/src/reasoning/reasoning_engine.py, deployments/dpdpa-backend/src/reasoning/keyword_ranker.py, deployments/dpdpa-backend/src/tests/test_hybrid_retrieval.py
- risk: tier2
- size: M
- complexity: 5
- verify: cd deployments/dpdpa-backend && python3 -m pytest src/tests/test_hybrid_retrieval.py src/tests/test_keyword_ranker.py -q && cd ../.. && python3 evals/runner.py --corpus real --offline
- notes: BM25 is fallback-only today (reasoning_engine.py:96). Keep the IDF coverage floor
  on the BM25 side so withheld-support cases still refuse.

### T4: Rerank 20 fused candidates down to 5
- implements: AC2
- depends_on: T3
- files: deployments/dpdpa-backend/src/reasoning/reranker.py, deployments/dpdpa-backend/src/reasoning/reasoning_engine.py, deployments/dpdpa-backend/src/tests/test_reranker.py
- risk: tier2
- size: S
- complexity: 5
- verify: cd deployments/dpdpa-backend && python3 -m pytest src/tests/test_reranker.py -q
- notes: the reranker is a network call; on failure fall back to fused order and log
  `degraded`, never refuse for that reason alone.

### T5: Expand retrieved provisions to their definitions and linked rules
- implements: AC2, AC7
- depends_on: T3
- files: deployments/dpdpa-backend/src/reasoning/graph_expand.py, deployments/dpdpa-backend/src/reasoning/reasoning_engine.py, deployments/dpdpa-backend/src/tests/test_graph_expand.py
- risk: tier2
- size: M
- complexity: 6
- verify: cd deployments/dpdpa-backend && python3 -m pytest src/tests/test_graph_expand.py -q
- notes: hard part is the token budget: expansion may add at most 3 objects and must keep
  the prompt under 4,000 tokens. Carry `in_force_from` from the law files onto each claim.

### T6: Add the street-word rewriter and commit the 101-question street set
- implements: AC3
- depends_on: T3
- files: deployments/dpdpa-backend/src/reasoning/query_rewriter.py, deployments/dpdpa-backend/src/reasoning/street_glossary.json, evals/street_questions.jsonl, deployments/dpdpa-backend/src/tests/test_query_rewriter.py
- risk: tier1
- size: M
- complexity: 6
- verify: cd deployments/dpdpa-backend && python3 -m pytest src/tests/test_query_rewriter.py -q
- notes: the rewriter adds law terms to the query; it never removes words and never adds
  a fact. Each glossary entry maps to a term that occurs in the Act or Rules text (the
  test checks this). Dilip reviews the glossary (Ask first). The 17 unanswered street
  questions are the first test cases.

### T7: Build the clean voice set from the briefings
- implements: AC12
- depends_on: T8
- files: scripts/voice/build_voice_set.py, scripts/voice/test_build_voice_set.py
- risk: tier1
- size: M
- complexity: 6
- verify: python3 -m pytest scripts/voice/test_build_voice_set.py -q
- notes: input is `staging/own/briefings/dpdpa-briefings-v1.zip` in the main checkout
  (gitignored; never commit the data). The script refuses to build while any of the 4
  dates in REVIEW-BEFORE-PUBLISHING.md (2026-05-13, 06-04, 08-31, 09-30) still holds its
  flagged claim. Runs the T8 lexicon over every row. Writes 168 train and 40 held-out rows
  to the gitignored staging folder.

### T8: Check every claim against the law lane before an answer leaves
- implements: AC4, AC5, AC9
- depends_on: none
- files: deployments/dpdpa-backend/src/reasoning/claim_checker.py, deployments/dpdpa-backend/src/reasoning/guardrails.py, deployments/dpdpa-backend/src/tests/test_claim_checker.py
- risk: tier1
- size: M
- complexity: 6
- verify: cd deployments/dpdpa-backend && python3 -m pytest src/tests/test_claim_checker.py src/tests/test_hardening.py -q
- notes: reuse the verbatim-quote matching in schemas/corpus_contract.py, do not write a
  second one. Test cases must include "Data Personal Breach Inquiry", a fine of ₹300
  crore, and "Section 45".

### T9: Write the prompt-only voice and the blind preference test
- implements: AC13
- depends_on: T7, T8
- files: deployments/dpdpa-backend/src/reasoning/voice_prompt.md, evals/voice_pairs.py, evals/test_voice_pairs.py
- risk: tier1
- size: M
- complexity: 6
- verify: python3 -m pytest evals/test_voice_pairs.py -q
- notes: the test script writes A/B pairs with the side shuffled and the key kept apart, for
  two human readers. The voice prompt is a prompt change, so Dilip approves the text.

### T10: Write the LoRA voice job and dry-run it (no real run)
- implements: AC13
- depends_on: T7, T9
- files: scripts/voice/train_lora.py, scripts/voice/test_train_lora.py
- risk: tier1
- size: M
- complexity: 6
- verify: python3 -m pytest scripts/voice/test_train_lora.py -q
- notes: the script must exit unless `--confirm-d3` is passed; the test checks that.
  Dry run validates the data format and estimates GPU hours only. Base model follows D1.

### T11: Serve `/v1/answer` with the spec's request, response and errors
- implements: AC1, AC8, AC11
- depends_on: T8
- files: deployments/dpdpa-backend/src/api/api_service.py, deployments/dpdpa-backend/src/api/v1_answer.py, deployments/dpdpa-backend/src/tests/test_v1_answer.py
- risk: tier1
- size: M
- complexity: 6
- verify: cd deployments/dpdpa-backend && python3 -m pytest src/tests/test_v1_answer.py src/tests/test_model_unavailable.py -q
- notes: audience and format change only the wording instructions, never retrieval; AC1's
  test asserts identical URNs across two formats.

### T12: Add per-client keys, rate limits and log redaction
- implements: AC10, AC11
- depends_on: T11
- files: deployments/dpdpa-backend/src/api/clients.py, deployments/dpdpa-backend/src/api/api_service.py, deployments/dpdpa-backend/src/tests/test_clients.py
- risk: tier1
- size: S
- complexity: 5
- verify: cd deployments/dpdpa-backend && python3 -m pytest src/tests/test_clients.py -q
- notes: keys come from environment secrets, one per client; reuse CREDIT_CARD_REGEX and
  INDIAN_PAN_REGEX from guardrails.py for redaction.

### T13: Draft explainers with quotes and a grade-8 gate
- implements: AC14, AC15
- depends_on: T8
- files: scripts/explainers/draft_explainers.py, scripts/explainers/gate.py, scripts/explainers/test_gate.py, requirements.txt
- risk: tier1
- size: M
- complexity: 6
- verify: python3 -m pytest scripts/explainers/test_gate.py -q
- notes: the gate is pure code (quote check plus grade); drafts may come from a model but
  are only drafts. Mask the section 2 defined terms before grading.

### T14: Store explainers and serve only signed ones
- implements: AC16
- depends_on: T13
- files: deployments/dpdpa-backend/src/api/v1_explainers.py, deployments/dpdpa-backend/supabase_schema.sql, deployments/dpdpa-backend/src/tests/test_v1_explainers.py
- risk: tier1
- size: M
- complexity: 7
- verify: cd deployments/dpdpa-backend && python3 -m pytest src/tests/test_v1_explainers.py -q
- notes: a new table is a migration; Dilip runs the live schema change. Hard part: the
  explainer must be invalidated when its provision's text changes (hash check).

### T15: Run the comprehension check on 10 explainers
- implements: AC15
- depends_on: T13
- files: evals/explainer_comprehension.md
- risk: tier2
- size: S
- complexity: 3
- verify: test -s evals/explainer_comprehension.md && grep -q 'Result:' evals/explainer_comprehension.md
- notes: two readers outside law, three questions each; tests A6.

### T16: Point the wiki's Ask at `/v1/answer` behind a flag
- implements: AC1
- depends_on: T11, T12
- files: deployments/dpdpa-wiki/src/components/screens/AskIntelligence.jsx, deployments/dpdpa-wiki/src/lib/api.js
- risk: tier2
- size: S
- complexity: 4
- verify: cd deployments/dpdpa-wiki && npm run build
- notes: default the flag off; the old path stays until the live eval and street set pass
  on the new one. Other clients follow the same contract in their own repos.
