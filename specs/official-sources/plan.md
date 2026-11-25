# Plan — official sources in the law lane

**Status:** draft
**Spec:** ./spec.md
**Date:** 2026-10-03

Dependency order: T1 → T2 → T3 → (T4, T5) → T6. T7 and T8 can start any time after T2.
Live-store writes (T6) are run by the founder.

### T1 — Enforce the two lanes in tests
- status: todo
- implements: AC9, AC4
- depends_on: none
- files: deployments/dpdpa-backend/src/tests/test_lanes.py, .gitignore
- risk: tier2
- notes: assert every path under staging/competitive_intel/market-map/ is ignored and
         untracked; assert no market-map domain appears as a source_urn in the eval corpus
- verify: cd deployments/dpdpa-backend && python -m pytest -q src/tests/test_lanes.py

### T2 — Source registry, allowlist and fetcher
- status: todo
- implements: AC1, AC2, AC6, AC8
- depends_on: T1
- files: sources/official.yaml, src/competitive_intel/official_sources.py,
         deployments/dpdpa-backend/src/tests/test_official_sources.py,
         deployments/dpdpa-backend/src/tests/fixtures/official/
- risk: tier1
- notes: loader validates the allowlist and manual-review rule; fetch writes the file
         and extracted text under staging/official_sources/<id>/ and fills the hashes;
         a changed file is reported, never written over; tests use fixtures only
- verify: cd deployments/dpdpa-backend && python -m pytest -q src/tests/test_official_sources.py

### T3 — Extend the corpus contract to registered sources
- status: todo
- implements: AC3, AC4, AC5
- depends_on: T2
- files: deployments/dpdpa-backend/src/schemas/corpus_contract.py,
         deployments/dpdpa-backend/src/tests/test_corpus_contract.py
- risk: tier1
- notes: evidence with a registry urn is checked against that source's text and
         text_sha256; unregistered and superseded sources fail; the existing gazette
         checks are unchanged
- verify: cd deployments/dpdpa-backend && python -m pytest -q src/tests/test_corpus_contract.py

### T4 — Act commencement dates from the notification
- status: todo
- implements: AC7
- depends_on: T3
- files: sources/official.yaml, deployments/dpdpa-wiki/scripts/sync-law.mjs,
         deployments/dpdpa-wiki/src/data/law/provisions.json,
         deployments/dpdpa-wiki/src/components/screens/Provision.jsx,
         deployments/dpdpa-wiki/tests/law-data.test.js
- risk: tier1
- notes: register the commencement notification(s) after confirming them from the
         gazette (assumption A1); sync-law reads dates only from registered text, never
         typed in by hand. Found 2026-11-25: G.S.R. 843(E) of 13 Nov 2025
         (meity.gov.in/static/uploads/2025/11/c56ceae6c383460ca69577428d36828b.pdf) sets
         three dates: 13 Nov 2025 for s.1(2), 2, 18-26, 35, 38-43, 44(1), 44(3); one year
         later for s.6(9) and 27(1)(d); eighteen months later for the rest. A local copy and
         a parsed record are in staging/law-import/ (from the DPDPA Daily Brief project);
         fetch fresh from the official URL, do not copy. The issue is dated 13 Nov but was
         uploaded on 14 Nov; record the printed date and note the difference
- verify: cd deployments/dpdpa-wiki && node scripts/sync-law.mjs && npm run build && npx vitest run tests/law-data.test.js

### T5 — First batch of verified objects from official sources
- status: todo
- implements: AC11, AC3
- depends_on: T3
- files: sources/official.yaml, src/competitive_intel/build_knowledge_objects.py,
         evals/test_corpus_contract.py
- risk: tier1
- notes: register CERT-In's 2022 directions, the Puttaswamy judgment and the RBI and
         SEBI directions the seed objects named; build one verbatim object per source with
         an `official` step; nothing is published from this task
- verify: python3 src/competitive_intel/build_knowledge_objects.py official --dry-run && python -m pytest -q evals/test_corpus_contract.py

### T6 — Publish and audit
- status: todo
- implements: AC11
- depends_on: T4, T5
- files: memory/STATE.md
- risk: tier1
- notes: founder runs `official` then `audit`; prerequisite: OpenAI credits restored,
         and the store repair (`conform`, `quarantine`) done
- verify: python3 src/competitive_intel/build_knowledge_objects.py audit

### T8 — Apply the Removal of Difficulties Order to the Act text
- status: todo
- implements: AC7, G1
- depends_on: T2
- files: sources/official.yaml, src/competitive_intel/ground_truth.py,
         deployments/dpdpa-wiki/src/data/law/provisions.json,
         deployments/dpdpa-wiki/tests/law-data.test.js
- risk: tier1
- notes: S.O. 5458(E), the DPDP (Removal of Difficulties) Order, 2026, dated 5-6 Oct 2026
         (egazette.gov.in/WriteReadData/2026/276885.pdf). Per its text (checked from a local
         copy only), s.9(1) reads "a child or of a person with disability" and
         s.10(2)(c)(ii) reads "periodic data audit". The live site still shows the old
         wording. Register the order, then apply both corrections in the ground-truth
         script (law text is never hand-edited) with an amended_by note naming the order;
         the affected Act KOs (S9, S10) and any answer quoting them get a new version
         through `revise`, never an overwrite
- verify: cd deployments/dpdpa-wiki && node scripts/sync-law.mjs && npx vitest run tests/law-data.test.js

### T7 — Weekly watch for new issuances
- status: todo
- implements: AC10, AC6
- depends_on: T2
- files: src/competitive_intel/official_watch.py,
         deployments/dpdpa-backend/src/tests/test_official_watch.py
- risk: tier2
- notes: compares registered file hashes and scans the allowlisted listing pages for
         "Digital Personal Data Protection"; writes the watch report; offline tests use
         fixture listings
- verify: cd deployments/dpdpa-backend && python -m pytest -q src/tests/test_official_watch.py
