# Development status — 28 September 2026

Assessment based on repository memory, planning documents, current source, Git history, and local verification. Hosted deployments, cloud data, model service availability, and visual acceptance were not verified. No application source was changed during this assessment.

## Overall position

The project has a substantial MVP and an ongoing production-hardening/revamp effort. The reusable foundations exist, and the public website builds successfully. Persistent editorial workflows, trustworthy corpus migration, production integration, and release verification remain incomplete.

Using the proposed September comprehensive build specification as a reference, M1 is substantially implemented locally but not closed. M2 remains a major blocker. Parts of M3 and M5 have been started ahead of their dependencies. This is a capability assessment, not a claim that the proposed plan has been formally approved.

## Current architecture and framework

- Frontend: React 19, Vite 8, React Router 7, Supabase client, custom CSS/design tokens, Markdown guide content, and custom build-time React prerendering.
- Canonical runtime backend: `deployments/dpdpa-backend/`, using Python/FastAPI.
- Permanent knowledge design: URNs, evidence, version history, Git ledger, Supabase/Postgres, and a derived Pinecone retrieval index.
- Reasoning: retrieval, structured model output, citation validation, guardrails, and tracing. Provider adapters include GPT-OSS through an OpenAI-compatible endpoint, Gemini, OpenAI, and OpenRouter. Provider implementation is not proof of a functioning hosted service.
- Applications: public home/guides and the knowledge/workspace pages. The course route redirects to the separate Shiksha site; that site's current implementation was not audited here.

There is no implemented Next.js/Astro migration in the inspected application. The revamp currently evolves React/Vite and adds prerendering. A newer development workflow also exists: `specs/README.md`, `scripts/validate_chain.py`, and a GitHub workflow define an intent → specification → plan chain. No feature-specific chains were present under `specs/`.

## Implemented foundations

| Area | Evidence and boundary |
|---|---|
| Public home | Homepage, public shell, assessment, FAQs, and subscription capture exist. Email delivery is not enabled. |
| Guides and SEO | Guide index and one long-form MSME guide; canonical/OG tags and structured data; three public routes prerender successfully. |
| Workspace | Today, knowledge, changes, actions, factory, Ask, Bible, admin, and infographic surfaces exist. Screen existence does not imply a complete workflow. |
| Knowledge infrastructure | JSON Schema, validation, bitemporal storage, graph edges, Git ledger, and factory stage modules exist. Seed compatibility and publication integrity still need work. |
| Reasoning | Retrieval, parsed structured responses, retrieved-versus-claimed citation checks, guardrails, and tracing are integrated into the canonical backend. |
| Immediate hardening | Shared-key admin authorization, query length/rate controls, provider configuration readiness, central frontend API base, and development-only mock gating exist. |
| Ingestion tooling | Five operational scripts moved beneath the canonical backend. Root Docker entry point targets that backend. |
| Evaluation tooling | Dataset, deterministic scorers, repeat runs, optional judge, reports, and error catalog exist. Current recorded scores are synthetic/mock evidence, not live legal quality assurance. |

## In progress / partially complete

1. **UI revamp:** new Acts, Rules, Interpretations, Discussions, and shared KnowledgeCategory screens are wired; Bible styling, homepage visuals, navigation, and infographic changes are local WIP. Discussions is a filtered knowledge view, not an implemented user discussion system.
2. **Knowledge API:** search, changes, section history, object lookup, graph diff, Bible, and text diff routes exist. Preview-level integration across these surfaces is unverified.
3. **Backend consolidation:** deployment uses one canonical tree, but the older root `src/` remains. The eval runner still imports the root tree. Consolidation therefore remains unfinished.
4. **Ask:** frontend requests the API and shows an unavailable state without production mock answers. A hosted end-to-end cited answer was not verified.
5. **Actions:** Supabase reads and status writes exist. Role/ownership enforcement, evidence lifecycle, and reliable audit history do not constitute a completed workflow yet.
6. **Factory:** backend pipeline modules exist, but FactoryBoard uses development fixtures and local object mutation; production has no connected persistent review board.
7. **Change detail:** ChangeWorkspace currently resolves its event from mock data only when development mocks are enabled. It is not a completed real-data change workspace.
8. **Authentication:** Supabase sign-in and a transitional admin key exist. Server-enforced user roles and protected operator workflows remain pending.
9. **Subscriptions:** the form inserts into Supabase and now truthfully says email delivery is not enabled. Delivery, confirmation, and unsubscribe lifecycle remain pending.

## Milestone assessment

| Milestone from proposed build spec | Assessment |
|---|---|
| M1 — Safe canonical backend | Substantially implemented locally; duplicate source/eval path and failing tests prevent closure. |
| M2 — Trusted corpus/data | Pending substantive implementation: schema reconciliation, reviewed migration, evidence verification, ordered DB migrations, role policies, publication integrity, index reconciliation. |
| M3 — Real production user path | Partial code exists; hosted Ask/read/auth/action acceptance remains unverified or incomplete. |
| M4 — Operable research workflow | Pipeline foundation exists; persistent runs, review decisions, retries, quarantine, publication audit, and real board wiring remain. |
| M5 — Production release | Some guardrails/eval tooling exists; frontend tests, E2E, real-corpus evals, monitoring, restore/rollback exercises, and preview acceptance remain. |
| M6 — Content expansion | One guide exists. Reviewed guide expansion, broader discoverability, and stable cross-product provenance remain. |

The specification's 6–8 week estimate assumes two engineers and a part-time reviewer; it is a planning estimate, not a measured remaining-time forecast.

## Verification performed today

- Canonical backend full suite: **96 passed, 2 failed**, 10 warnings. Failures were `test_admin_routes_require_correct_key` and `test_query_rate_limit_returns_retry_after`; observed symptoms were SQLite disk I/O and a query returning 500.
- Follow-up test-order probe, hardening before API tests: **13 passed, 10 failed**, with missing-table errors. Source inspection shows shared global API clients, import-time database configuration, and module teardown that deletes the shared SQLite file. This points to test isolation/lifecycle problems; it does not prove a hosted API outage.
- Frontend lint: exit 0, **two React hook dependency warnings** in KnowledgeCategory.
- Frontend production build: **passed**. Main client JavaScript: **761.64 kB**, **217.79 kB gzip**; chunk-size warning remains.
- Prerender: **3/3 routes** emitted: home, guide index, and MSME guide.
- Safe offline inspection of literal seed data, without importing/running the seeder: **45 objects, zero schema-valid, 45 invalid**, plus 6 events and 5 actions. Violations include missing required source/date/history/hash fields and ontology enum mismatches. This is a structural finding, not a legal-accuracy judgment or a current cloud inventory.
- Latest recorded eval report: **15 cases × 3 runs = 45 passes**, using the synthetic/mock setup described in the build spec and supported by the runner. The runner constructs a single synthetic knowledge object and can use MockModelClient. These scores do not establish production answer quality.

## Repository and documentation condition

- Latest commit visible in this checkout: `a3dab16`, 29 August 2026, public-route prerendering.
- Before adding this report: 48 changed tracked paths and 48 untracked Git status entries; directory entries may contain multiple files. Much of the September implementation is local uncommitted work. Commit history alone understates progress.
- `memory/STATE.md` is dated 1 August and still points to the old `frontend/` layout. Current frontend is `deployments/dpdpa-wiki/`.
- `PLAN.md` predates completed homepage/guide/prerender work. Its live service counts and deployment assertions are historical.
- `COMPREHENSIVE_BUILD_SPEC.md` is a proposed baseline dated 8 September; its original gap list predates several hardening fixes. `M1_BASELINE.md` records an earlier passing run, not today's result.
- September session captures mostly contain diff statistics, making them weak evidence of accepted outcomes.
- Current CI only validates specification chains when present. No backend/frontend/E2E/eval release gate was found in the inspected workflows.

## Recommended next sequence

1. Preserve and review local WIP in logical change groups; reconcile the active status documents and finish canonical backend/eval ownership.
2. Close M1 verification: repair test database lifecycle/isolation, resolve lint warnings, and demonstrate the hardening on preview.
3. Complete M2: agree the schema/ontology, transform or quarantine seed objects, verify evidence, migrate data through a consistent publication path, and reconcile vectors.
4. Demonstrate one complete preview journey: real knowledge → Ask with citations → action status/evidence → audit record, with real authorization and clear failure states.
5. Complete the persisted factory/reviewer workflow and email lifecycle.
6. Add live-corpus evaluations, frontend/E2E release gates, operational monitoring and recovery checks; obtain preview acceptance before production promotion.

## Handoff

- **State:** Repository analysis complete; frontend build/prerender passed; backend tests and seed validation reveal unresolved gates. Application source was not changed.
- **Open loops:** Current hosted deployment/DB/vector status, visual acceptance, approved roadmap scope, corpus migration, backend test isolation, persistent editorial workflow, and release gates.
- **Next step:** Close M1 with preserved WIP and reproducible tests, then prioritize M2 corpus integrity before broader feature expansion.
