# DPDPA Knowledge Infrastructure — Chief Architect Specification

**Date:** 2026-09-10  
**Prepared for:** Dilip  
**Scope:** `deployments/dpdpa-backend` + `deployments/dpdpa-wiki`  

## 1) What this platform is already good at

The repo already follows a strong product direction and most foundational pieces are in place:

1. **Clear three-layer architecture**
   - Layer 1: immutable knowledge infrastructure (ledger + schema + storage)
   - Layer 2: reasoning/query layer (retrieval + model prompting + guardrails)
   - Layer 3: application UX/API surfaces

2. **Core runtime exists end-to-end**
   - FastAPI gateway with `/health`, `/knowledge/query`, `/knowledge/objects/{urn}`, `/knowledge/graph/diff`, `/knowledge/bible`
   - Admin routes with `X-Admin-Key` enforcement
   - Frontend routes for Today / Changes / Knowledge / Actions / Factory / Ask / Bible / Admin
   - Cross-link to `dpdpa.shiksha` via `VITE_SHIKSHA_URL`

3. **Research Factory skeleton is implemented**
   - 8-department style pipeline modules are present and modular
   - Validation, deduplication, ontology normalization, graph relationship proposal, publishing logic are already there

4. **Schema and bitemporal discipline are established**
- Knowledge object schema exists
- Bi-temporal query support (`system_time_*`, `legal_time_*`)
- Git ledger pathing and DB mirror design exists

5. **Guardrails are not decorative**
   - Query payload limits, input refusals, grounded output checks, retry-safe rate limits, and readiness checks are already present.

---

## 2) What is likely incomplete for production

This is the part we should harden first:

### A) Single source of truth and persistence consistency
- Keep one runtime source for backend code (`deployments/dpdpa-backend`).  
- Ensure DB model fields match what gets published (e.g., `entities`, `relations`, `source_credibility`, `forum_published` should be consistently represented either in SQL columns or inside `body` in a consistent contract).
- Make DB/ledger/API response behavior deterministic across Supabase sync and SQLite fallback.

### B) Remove mock-mode behavior from production paths
- Several UI screens currently hydrate from `MOCKS_ENABLED` when API/db is unavailable.
- In production, these screens must always render **real service states** (even if empty), with clear “not available” UX.
- Keep mock fixtures for local developer mode only, strictly behind `import.meta.env.DEV`.

### C) Editorial and action workflows are partially hardcoded
- `DecisionsActions`, `ChangeWorkspace`, `FactoryBoard`, `CommandCenter` depend heavily on local datasets.
- Replace these with:
  - `/knowledge/events`, `/knowledge/actions`, `/knowledge/conflicts`, `/knowledge/workflow/{id}` endpoints
  - status history + ownership + due date states

### D) Security posture needs user-level controls
- `X-Admin-Key` is an acceptable transitional control, but role-aware auth should become a real path:
  - Supabase-authenticated admin roles (or enterprise SSO path)
  - action-level permission checks (read/search/admin)

### E) Model/provider configuration and cost safety
- Model client currently supports Gemini/OpenAI/OpenRouter by API key.
- Ensure provider configuration is explicit and audited:
  - one primary provider + fallback chain
  - structured prompts + schema checks + cost per request logging
  - production readiness fail-closed if no model key

### F) Data quality for knowledge corpus
- Current seeded KOs are a strong start but need ongoing quality gate:
  - every KO must have valid evidence coordinates, at least one canonical relation for core nodes, and explicit layer assignment
  - unresolved evidence/coverage should be query-visible and surfaced as gaps

---

## 3) What to retain (do not rebuild from scratch)

Keep these exactly:

1. **URN architecture + event lineage**
   - `urn:ki:in:dpdp:<type>:<id>` style IDs provide durable linkage across all surfaces.

2. **Bitemporal model**
   - You need legal validity and publication validity independently.

3. **Factory department boundaries**
- The 8-department metaphor is excellent for ownership, testing, and accountability.

4. **Separated API + wiki responsibilities**
   - The wiki should consume the API; ingestion logic should stay on the backend.

5. **SaralKnowledge link points**
   - Keep the certification handoff and shared corpus behavior. This is strategically correct.

---

## 4) What to change immediately (keep your momentum)

## 4.1 Layer 1 (Knowledge Infrastructure) – do this first

Priority: **P0**

1. Finalize canonical data contract:
   - `knowledge_objects` SQL columns for frequently queried fields and nested JSON for large payloads
   - Standard JSON response contract from `/knowledge/objects/{urn}`
   - Standardized error contracts for empty/inactive versions

2. Add migration-safe ingestion:
   - all publishes write ledger first, then DB, then vector index, then webhook notify
   - idempotent publish operation using `(urn, version)` and hash

3. Add data quality gates:
   - required evidence + evidence hash + at least one source + source layer mapping

## 4.2 Layer 2 (Reasoning/Intelligence) – production-safe behavior

Priority: **P1**

1. Require explicit trace object for each query:
   - request_id, policy-version, model-provider, token usage, retrieval source

2. Remove all silent fallback “invented truth” behavior
   - if retrieval insufficient => `grounded=false` + clear insufficiency reason
   - if model malformed => safe failure with source-safe fallback

3. Add `/knowledge/search` endpoint with:
   - structured filters (`type`, `time_range`, `confidence_min`, `layer`)
   - pagination + ordering

## 4.3 Layer 3 (Applications) – ship reliability, then polish

Priority: **P2**

1. Replace hardcoded/fixture-first screens with API-first screens:
   - `/changes` uses DB/ledger records and conflict events
   - `/actions` uses persisted action items, owners, evidence, completion
   - `/factory` exposes real pipeline metrics + pending tasks + failed steps
   - `/ask` is strictly API-backed and always shows grounding state

2. Introduce role-based nav:
   - public routes stay public
   - editor/admin routes require auth

3. Add fallback banners, not fake numbers:
   - show "No live metrics" instead of hardcoded dashboard stats

---

## 5) How to link this strongly with SaralPrivacy + DPDPA Shiksha

Think of **two independent products with one shared legal core**:

- `dpdpa.wiki` (knowledge and compliance intelligence)
- `dpdpa.shiksha` (course + practitioner flow + workflows)

Recommended integration architecture:

1. **Single knowledge contract**
   - both products use the same URN, relation type, evidence schema
   - shiksha should never duplicate KO text; it should reference URNs

2. **API-driven integration**
   - shiksha consumes:
     - `/knowledge/objects/{urn}`
     - `/knowledge/graph/diff`
     - `/knowledge/query`
   - both apps use same environment-level feature flag for corpus version

3. **Cross-product events**
   - when a KO is published, publish change event:
     - changed sections
     - affected obligations
     - impacted roles/processes
     - downstream remediation actions
   - shiksha can subscribe and update user assignments

4. **Identity handoff**
   - keep `VITE_SHIKSHA_URL` redirect as user journey bridge
   - move to shared SSO plan (Supabase/JWT) in phase-2 when budget/time allow

---

## 6) Can we do Apple/iOS-style liquid-glass and chips?

**Yes — without redesigning everything.**

Recommended visual migration:

- Add reusable glass classes in `design-tokens.css` + `components.css`:
  - `--surface-glass`, `--surface-glass-strong`, `--chip-glass`
  - `backdrop-filter: blur(14px);`
  - layered border highlights (`rgba` + inset border)
- Replace inline screen-level visual styling progressively with component classes.
- Prioritize:
  1. Shell chrome (nav/topbar)
  2. Knowledge cards / query cards / citation blocks
  3. Chips + pills
  4. Micro-interaction polish (hover + selected states + depth transitions)
- Keep serif headings, but make controls and metadata strict modern sans for scanning.

This can be phased:
- **Phase 1 (1 week):** token foundation + 6 reusable glass primitives
- **Phase 2 (1 week):** migrate 5 core screens (`/today`, `/knowledge`, `/ask`, `/changes`, `/factory`)
- **Phase 3 (ongoing):** motion tuning, accessibility, and responsive refinements.

---

## 7) Suggested sequencing (production sequence)

### Week 1
- Resolve source-of-truth mismatch
- Standardize API contracts and db model/schema alignment
- Remove all mock data from protected/published views

### Week 2
- Harden admin and auth boundary + auditability
- Add action/events endpoints and wire UI to live data

### Week 3
- Add cross-product event contract and integrate Shiksha
- Complete data-quality pipeline gates

### Week 4
- Apple/iOS glass migration pass (UI layer)
- Accessibility + responsiveness hardening + load/perf checks

---

## 8) Vercel preview status (from this environment)

I attempted a preview deployment command, but outbound network is blocked in this environment (`vercel.com` lookup fails), so a preview URL cannot be created here.

Run this from your machine:

```bash
cd deployments/dpdpa-wiki
vercel
```

Then share the returned URL and I can review it quickly against this spec.

---

If you want, I can now do the **“Phase 1 hardening PR”** plan next:

- finalize the Layer-1 contract,
- strip mock fallbacks from production UI screens,
- and produce a concrete diff you can ship.
