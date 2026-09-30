# Project State — DPDPD Knowledge Infra

**Last updated:** 2026-09-29
**Working branch:** `reconcile/trial` (the DPDPA Wiki rebuild merged with Codex's backend hardening); nothing merged to `main` yet
**Production:** dpdpa.wiki still serves `main` @ a3dab16 (29 Aug). Preview-before-prod applies to every release.
**Resume cue:** "resume Knowledge Infra" / "continue from STATE"

## Where we are

The public site, **DPDPA Wiki — SaralPrivacy Knowledge Infra**, is rebuilt and approved on preview: 75 law pages
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
| `deployments/dpdpa-backend/` | Canonical FastAPI backend. `python -m pytest -q` (98 tests) |
| `evals/` | Eval runner — imports the canonical backend. `python evals/runner.py --offline` |
| `src/competitive_intel/` | Crawl, ground truth, claims, question graph, knowledge-object builder |
| `src/` (api, reasoning, storage, tests) | **Legacy copy** of the backend, drifted from the canonical tree; not deployed |
| `specs/dpdpa-wiki-reimagine/` | Intent → spec → plan for the site (validator passes) |
| `.github/workflows/` | `spec-chain.yml`, `release-gate.yml` (site build+tests, backend tests, offline evals) |

## Open loops

1. **Adopt and release:** founder review of `reconcile/trial` preview → merge to `main` → production.
2. **Remove the legacy root `src/` backend copy** once nothing imports it (evals no longer do).
3. **Corpus integrity (M2):** 12 questionable live objects (fake "Consent Notice Rules 2024", mock notice-test,
   duplicate Rule 7, draft Rule 4, 7 unsourced opinions) await "close them"; seed script objects are
   schema-invalid.
4. **Evals are synthetic** (one fabricated object, mock model) — add real-corpus cases.
5. **Bundle:** public JS 229–231 KB gz vs 200 KB budget — route-level splitting task running separately.
6. **Not built:** server-enforced roles, persistent Factory review board, hosted Ask end to end, email delivery.
7. **Video pilot (spec T20–T21):** provisions not chosen (recommendation S6, S8, R7).
8. **Security:** an OpenAI key is visible in Cursor's process environment — rotate it.

## Decisions (settled — don't re-litigate)

- Competitor content is discovery only: never canonical, never republished, never embedded, never used for fine-tuning. RAG over our own corpus, no fine-tuning.
- Law text is written only by `src/competitive_intel/*ground_truth*.py` → `scripts/sync-law.mjs`; never hand-edited.
- Knowledge objects are never overwritten: new version + `system_time_end` on the old one (`build_knowledge_objects.py revise`).
- Site name "DPDPA Wiki", owner line "SaralPrivacy Knowledge Infra". MSME guide retired (301 → /learn/what-is-dpdpa). Module 6 hands off to saralprivacy.com/assessment.
- Lessons: short version → one mechanism figure → worked example → full text folded; colour = role.
