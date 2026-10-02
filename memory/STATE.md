# Project State — DPDPD Knowledge Infra

**Last updated:** 2026-10-02
**Production:** dpdpa.wiki serves `main` @ 7074dae (route splitting #5 and trusted corpus #6 merged 2 Oct). Preview-before-prod applies to every release.
**Resume cue:** "resume Knowledge Infra" / "continue from STATE"

## Where we are

The public site, **DPDPA Wiki — SaralPrivacy Knowledge Infra**, is live: 75 law pages
(44 sections, the Schedule, 23 Rules, 7 Schedules) in the gazette's words with commencement dates, a 32-term
glossary, a six-module visual course with self-tests, and three decision aids — 127 prerendered pages. Every
legal statement passes a build-time citation guard. The founder workspace lives under `/workspace` (noindex,
lazily loaded) and now includes Codex's Acts / Rules / Interpretations / Discussions screens.

Knowledge store (Supabase + Pinecone `dpdpa-knowledge`): verbatim primary objects for every provision (Act
sections at v2 after the gazette-furniture cleanup), 511 verified answer objects, graph edges. Competitive
intelligence corpus: 7,446 pages, 15,564 claims verified against the law, 1,779 canonical questions
(`staging/competitive_intel/`, gitignored; backup in the main checkout).

## Layout

| Path | What |
|---|---|
| `deployments/dpdpa-wiki/` | Public site + workspace (React 19, Vite 8, custom prerender). `npm run build && npx vitest run` |
| `deployments/dpdpa-backend/` | Canonical FastAPI backend. `python -m pytest -q` (122 tests) |
| `evals/` | Eval runner — imports the canonical backend. `python evals/runner.py --offline` (synthetic); `--corpus real` scores citations over the verified law + 511 answer objects (`golden_corpus.jsonl`, rebuilt by `build_golden.py`); `--live` calls the model and prints cost |
| `src/competitive_intel/` | Crawl, ground truth, claims, question graph, knowledge-object builder (`audit`, `repair`, `conform`, `quarantine` hold the store to the corpus contract) |
| `deployments/dpdpa-backend/src/schemas/corpus_contract.py` | What every live object must satisfy: `stored_object_schema.json`, plus every gazette quote and hash checked against the law file the site is built from |
| `specs/dpdpa-wiki-reimagine/` | Intent → spec → plan for the site (validator passes) |
| `.github/workflows/` | `spec-chain.yml`, `release-gate.yml` (site build+tests, backend tests, offline evals) |

## Open loops

1. **Store write: the founder runs it** (Claude's auto mode blocks writes to the shared store) (`build_knowledge_objects.py conform`, then `quarantine`). The live
   audit on 30 Sep: 616 live objects, 203 conform. 384 answers carry evidence hashes of the Act text from before
   the gazette-furniture cleanup, and 4 of them quote a margin note as part of Section 10(1); `conform` publishes
   a re-verified version of each and verified records for the Act and the Rules as documents. 27 hand-written
   seed objects (5 penalty, 10 opinion, 4 rule, 2 case, 2 notification, 2 circular, 1 judgement, and
   `notice-test` with two live versions) have no verifiable source; `quarantine` closes them. The staged answers
   and the eval snapshot are already repaired, so until `conform` runs they are one version ahead of the store.
2. **Two schemas.** `knowledge_object_schema.json` is the factory's ledger document; `stored_object_schema.json`
   is what is live. The factory path (`publishing_agent`, `publish_ko`) does not yet produce rows that pass the
   stored contract (no evidence hash at item level, no `source_credibility`).
3. **Retrieval.** The ranked fallback lifts offline citation recall from 1.4% to 44.7% and refuses 2 of 4
   withheld-support cases. `--corpus real --live` has not been run (costs cents; needs the founder's opt-in).
4. **Not built:** server-enforced roles, persistent Factory review board, hosted Ask end to end, email delivery.
5. **Video pilot (spec T20–T21):** provisions not chosen (recommendation S6, S8, R7).
6. **Security:** an OpenAI key is visible in Cursor's process environment — rotate it.
7. **www.dpdpa.wiki** does not resolve; add it in Vercel as a redirect and create the DNS record.

## Decisions (settled — don't re-litigate)

- Competitor content is discovery only: never canonical, never republished, never embedded, never used for fine-tuning. RAG over our own corpus, no fine-tuning.
- Law text is written only by `src/competitive_intel/*ground_truth*.py` → `scripts/sync-law.mjs`; never hand-edited.
- Knowledge objects are never overwritten: new version + `system_time_end` on the old one (`build_knowledge_objects.py revise` / `conform`).
- The seed scripts are retired (they exit without writing): their objects are unverified and share URNs with the verbatim Act sections. Publishing goes through `build_knowledge_objects.py`, which refuses anything that breaks the corpus contract.
- Site name "DPDPA Wiki", owner line "SaralPrivacy Knowledge Infra". MSME guide retired (301 → /learn/what-is-dpdpa). Module 6 hands off to saralprivacy.com/assessment.
- Lessons: short version → one mechanism figure → worked example → full text folded; colour = role.
