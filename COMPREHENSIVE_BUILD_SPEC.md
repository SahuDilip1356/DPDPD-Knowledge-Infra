# DPDP Knowledge Infrastructure — Comprehensive Build Specification

**Document status:** Proposed implementation baseline

**Baseline date:** 2026-09-08

**Product surfaces:** `dpdpa.wiki`, reasoning API, research factory, `dpdpa.shiksha` integration

**Primary audience:** Product owner, backend engineer, frontend engineer, knowledge editor, security reviewer

**Authority:** This document is the umbrella delivery specification. Where older planning documents conflict with it, this document governs after approval. `HARDENING_SPEC.md` remains the detailed implementation note for the immediate hardening work.

---

## 1. Executive summary

The repository contains a substantial MVP: a public React knowledge site, a Python/FastAPI reasoning service, a Supabase data layer, a Pinecone-backed retrieval path, a multi-stage research factory, a 12-module learning site, and an initial evaluation harness. The public site is live and can read knowledge objects from Supabase.

It is not yet a production-safe, end-to-end product. The live Ask experience falls back to local mock behavior, the public admin screen displays fabricated data when its API call fails, admin APIs have no authentication, two backend source trees have diverged, the 45 seed knowledge objects fail the declared schema, some frontend workflows are non-persistent, and the evaluation set does not yet validate live legal answers.

This specification defines the work needed to turn that MVP into a trustworthy, operable DPDP knowledge platform. The required delivery order is:

```text
One backend source of truth
          ↓
Security and abuse controls
          ↓
Valid, migrated knowledge corpus
          ↓
Deployed API and real frontend wiring
          ↓
Persistent editorial workflows
          ↓
Live evaluations, monitoring, and release
```

The expected delivery is **6–8 calendar weeks for two engineers plus a part-time legal/knowledge reviewer**, including a 25% contingency. A single full-time engineer should plan for approximately **10–13 weeks**.

---

## 2. Product definition

### 2.1 Product promise

DPDP Knowledge Infrastructure gives Indian organizations a traceable, current, and actionable understanding of the Digital Personal Data Protection Act and its implementing rules. Every substantive legal claim must be connected to retrievable source evidence and must make uncertainty visible.

### 2.2 Intended users

| Persona | Primary need | Authorized capabilities |
|---|---|---|
| Public reader | Understand DPDP obligations in plain language | Browse guides, knowledge, changes, Bible, and public answers |
| Compliance operator | Turn obligations into organizational actions | Search, ask, review change impact, manage action evidence |
| Knowledge editor | Convert authoritative sources into reviewed knowledge | Run ingestion, edit drafts, resolve duplicates/conflicts, publish |
| Administrator | Operate and audit the platform | View system health, search audit, ingestion audit, eval results, user roles |
| Legal reviewer | Validate legal meaning and citations | Approve/reject knowledge objects and release-blocking eval cases |

### 2.3 Goals

1. Serve source-grounded answers with explicit citations and honest insufficiency behavior.
2. Maintain a schema-valid, versioned, bi-temporal knowledge graph.
3. Support a reviewable source-to-publication research workflow.
4. Protect administrative, query, and audit data with appropriate authorization.
5. Make every production release testable, observable, and reversible.
6. Connect public education, operational actions, and the knowledge base without silently using fabricated data.

### 2.4 Non-goals for the first production release

- Providing legal advice or representing answers as a substitute for counsel.
- Automated publication of legal interpretations without human approval.
- General-purpose document management, GRC, or ticketing replacement.
- Fine-tuning a foundation model.
- Native mobile applications.
- Multi-tenant enterprise billing or customer-specific private corpora.
- Rebuilding `dpdpa.shiksha`; the initial requirement is stable cross-product linking and shared content provenance.

### 2.5 Success measures

| Measure | Release target | Measurement source |
|---|---:|---|
| Published knowledge objects passing schema validation | 100% | Migration/CI validation report |
| Citation integrity on release eval set | 100% | Deterministic scorer + legal review |
| Unsupported material claims | 0 critical failures | Human-reviewed eval set |
| Admin endpoint access without valid credentials | 0 successful requests | Security integration tests |
| API availability | 99.5% monthly after launch | Hosted uptime monitor |
| p95 cached/public read latency | < 500 ms | API telemetry |
| p95 Ask latency | < 12 s | API telemetry |
| Frontend critical accessibility violations | 0 | Automated scan + keyboard review |
| Fabricated fallback data in production UI | 0 occurrences | Source scan + end-to-end tests |
| Production rollback time | < 15 minutes | Release exercise |

---

## 3. Current-state baseline

### 3.1 Developed and demonstrable

- `dpdpa.wiki` is live with a public home page, a knowledge explorer, change/action/factory/admin screens, the DPDP Bible, an Ask surface, and one prerendered long-form guide.
- `dpdpa.shiksha` is live with a 12-module course.
- The live knowledge explorer reads records from Supabase.
- The FastAPI service implements health, knowledge query, object lookup, graph diff, Bible, admin audit, and stats routes.
- The research factory includes scouting, parsing/OCR, citation hashing, structuring, ontology, relationship, deduplication, reasoning, business translation, publishing, and webhook concepts.
- The reasoning layer includes retrieval, model generation, citation handling, and—only in the root work-in-progress tree—structured output, guardrails, tracing, and eval promotion.
- The repository includes SQL schema, knowledge-object JSON Schema, seed/ingestion scripts, 88 root tests, 82 deploy-backend tests, and a 15-case synthetic evaluation dataset.
- React static generation exists for the home, guide index, and one guide route.

### 3.2 Incomplete or unsafe

| Area | Current gap | Release consequence |
|---|---|---|
| Backend source | Root `src/` and deploy backend have diverged | Fixes can be lost depending on deployment root |
| Ask wiring | Live frontend lacks a working deployed reasoning API | Users receive mock/local behavior instead of the product promise |
| Admin authorization | UI route is public; backend admin routes are unauthenticated | Search and operational data can be disclosed after deployment |
| Admin truthfulness | Failed calls become hard-coded metrics and logs | Production UI can present invented operational facts |
| Abuse protection | No enforced rate or payload limits | Cost, availability, and prompt-abuse risk |
| Knowledge integrity | All 45 seed objects fail the declared schema | Retrieval can cite structurally invalid evidence |
| Audit persistence | Search/ingestion tables are not fully migrated | Operational history is unreliable or deployment-specific |
| Editorial workflow | Factory cards and evidence actions are partly in-memory/no-op | Work appears saved when it is not |
| Provider routing | OpenRouter path has inconsistent key checks; no runtime failover | Configured providers may fail at runtime |
| Frontend quality | No frontend test suite; current lint warnings include runtime risk | Regressions are not gated |
| Evaluation quality | Current 45-run result uses mock generation and one synthetic corpus | Passing score does not establish factual production quality |
| Subscription | UI claims an email was sent after only a database insert | Misleading user experience and missing delivery system |
| SEO/content | One guide; sitemap/robots coverage is incomplete | Weak discoverability and shallow content surface |

### 3.3 Existing artifacts to retain

- `KNOWLEDGE_CONSTITUTION.md` for knowledge principles.
- `DPDPA_BIBLE.md` for domain synthesis, subject to editorial verification.
- `RESEARCH_FACTORY_DESIGN.md` for pipeline intent.
- `HARDENING_SPEC.md` for the four immediate pre-deploy fixes.
- `EVAL_SPEC.md` as historical design input; it must be updated after this plan because its zero-eval baseline is stale.
- `SYSTEM_ARCHITECTURE.md`, `DEPLOY.md`, and deployment READMEs, updated during implementation to match the final topology.

---

## 4. Target system architecture

```text
Public browser
  ├── dpdpa.wiki (React/Vite, Vercel)
  │     ├── public/prerendered content
  │     ├── authenticated operator workspace
  │     └── calls only the configured HTTPS API origin
  └── dpdpa.shiksha
        └── deep links to canonical wiki content and source versions

FastAPI service (Railway or approved equivalent)
  ├── public read/query API
  ├── authenticated operator/admin API
  ├── reasoning orchestration and guardrails
  ├── ingestion/review workflow API
  └── structured logs, traces, metrics, and health checks

Data and model services
  ├── Supabase Postgres/Auth/Storage — canonical records and identity
  ├── Pinecone — derived retrieval index, rebuildable from Postgres
  ├── Gemini/OpenAI/OpenRouter-compatible providers — generation/OCR/embeddings
  └── Email provider — confirmed subscriptions and notifications

Offline/controlled jobs
  ├── source discovery and download
  ├── parse/OCR, hash, structure, and enrich
  ├── human legal review
  ├── publish transaction
  └── index/update/reconciliation
```

### 4.1 Architectural rules

1. **Postgres is canonical.** Pinecone is a derived index and must be rebuildable.
2. **One backend tree exists.** `deployments/dpdpa-backend/` becomes the source of truth unless an explicit architecture decision relocates it.
3. **No silent mock in production.** Mock data is available only behind an explicit development/test flag.
4. **Publication is human-approved.** Automation creates drafts; an authorized reviewer publishes.
5. **Evidence is immutable.** Source artifacts and hashes cannot be edited in place after publication; corrections create versions.
6. **Configuration is validated at startup.** Missing required production configuration fails closed.
7. **Authorization is server-enforced.** Hiding a frontend route is not a security control.
8. **Every model answer is treated as untrusted output.** Schema, citation, and policy checks run before response delivery.

### 4.2 Target repository layout

```text
/
├── COMPREHENSIVE_BUILD_SPEC.md
├── docs/
│   ├── architecture.md
│   ├── operations.md
│   ├── security.md
│   └── adr/
├── deployments/
│   ├── dpdpa-backend/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── scripts/
│   │   ├── migrations/
│   │   └── Dockerfile
│   └── dpdpa-wiki/
│       ├── src/
│       ├── tests/
│       └── scripts/
└── evals/
    ├── datasets/
    ├── reports/        # generated reports ignored unless intentionally baselined
    └── runners/
```

No duplicate root Python package, root backend Dockerfile, or broken compose frontend path remains after consolidation.

---

## 5. Roles, identity, and authorization

### 5.1 Roles

| Role | Read public | Ask | Manage own actions | Edit drafts | Publish | View audits | Manage roles |
|---|---:|---:|---:|---:|---:|---:|---:|
| Anonymous | Yes | Limited | No | No | No | No | No |
| Authenticated user | Yes | Yes | Yes | No | No | No | No |
| Editor | Yes | Yes | Yes | Yes | No | Limited | No |
| Reviewer | Yes | Yes | Yes | Yes | Yes | Limited | No |
| Admin | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

### 5.2 Authentication decision

The transitional release may use the shared `X-Admin-Key` control described in `HARDENING_SPEC.md` to make the first backend deployment safe. The target implementation uses Supabase JWT verification plus a server-side `user_roles` table. Open signup never grants editor, reviewer, or admin privileges.

### 5.3 Authorization requirements

- API verifies token signature, issuer, audience, expiry, and role for every protected request.
- Row-level security complements API checks; it does not replace them.
- Only reviewers/admins publish or supersede knowledge objects.
- Only admins access raw search-audit data and role management.
- Search query bodies are treated as potentially sensitive data and have a documented retention period.
- Administrative access is logged with actor, request ID, resource, action, outcome, and timestamp.
- Production refuses to start if admin authentication is not configured.

---

## 6. Functional requirements

Priority labels: **P0** release blocker, **P1** required shortly after launch, **P2** later enhancement.

### 6.1 Public home and guides

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| WEB-001 | P0 | Home accurately reports platform availability | API failure renders a factual unavailable/degraded state; no invented metrics |
| WEB-002 | P0 | Guide routes are prerendered and directly addressable | Refreshing each published guide returns 200 with indexable content |
| WEB-003 | P0 | Generate sitemap and robots directives | Sitemap includes every public canonical route and is linked from `robots.txt` |
| WEB-004 | P0 | Provide per-page canonical, title, description, and share metadata | Automated metadata test passes for every prerendered route |
| WEB-005 | P1 | Show content version and last-reviewed date | Values come from canonical content metadata |
| WEB-006 | P1 | Link relevant course modules to canonical knowledge objects | Broken-link test passes; links include stable URNs or slugs |

### 6.2 Knowledge explorer and graph

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| KB-001 | P0 | List only published, schema-valid objects by default | Draft/invalid objects never appear anonymously |
| KB-002 | P0 | Filter by type, entity, obligation, source, effective date, and status | Filters are server-backed, shareable, and covered by integration tests |
| KB-003 | P0 | Display source excerpts and precise citation coordinates | Every displayed claim links to its evidence and content hash |
| KB-004 | P1 | Navigate typed relationships and version history | Graph and history views expose relationship type, validity, and provenance |
| KB-005 | P1 | Compare two valid-time/system-time states | Diff accurately shows added, removed, superseded, and unchanged facts |

### 6.3 Ask intelligence

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| ASK-001 | P0 | Send questions to the configured production API | Production bundle contains no localhost endpoint and smoke query reaches hosted API |
| ASK-002 | P0 | Return a structured response contract | Client renders answer, citations, grounded flag, limitations, request ID, and timing |
| ASK-003 | P0 | Decline when evidence is insufficient | Insufficient cases return a stable status and no unsupported definitive answer |
| ASK-004 | P0 | Confine citations to retrieved evidence | Any invented/mutated citation is rejected before delivery |
| ASK-005 | P0 | Enforce input/output guardrails | Injection, oversized input, secrets, and invalid output have tested outcomes |
| ASK-006 | P1 | Allow feedback tied to request ID | Feedback is stored without exposing private query text publicly |
| ASK-007 | P1 | Support conversational follow-up with bounded context | Context is explicit, size-limited, and not silently persisted beyond policy |

### 6.4 Changes and operational actions

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| CHG-001 | P0 | Show real regulatory events with effective/publication dates | Empty state is factual and does not substitute mock events |
| CHG-002 | P1 | Calculate affected knowledge objects and business actions | Each impact edge is traceable to a published version |
| ACT-001 | P0 | Persist action state per authenticated user/organization | Refresh and re-login preserve authorized changes |
| ACT-002 | P0 | Save action evidence through a real handler | Upload/link action returns persisted evidence metadata and audit event |
| ACT-003 | P1 | Track assignee, due date, status, and source obligation | RLS prevents unauthorized reads/writes |
| ACT-004 | P1 | Export an evidence packet | Export includes object versions, evidence hashes, and timestamps |

### 6.5 Research factory and review

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| FAC-001 | P0 | Persist every pipeline item and state transition | Board reload reproduces server state; no constant mutation is used |
| FAC-002 | P0 | Store source artifact, retrieval metadata, and SHA-256 hash | Re-ingesting identical source is idempotent |
| FAC-003 | P0 | Validate draft objects before review and before publication | Invalid object cannot transition to `published` |
| FAC-004 | P0 | Require reviewer identity and decision for publication | Publish audit contains actor, timestamp, input version, and outcome |
| FAC-005 | P0 | Handle duplicate and superseding sources | Reviewer can merge, reject, or create a new version without losing history |
| FAC-006 | P1 | Retry transient stages and quarantine terminal failures | Retry count/backoff recorded; dead-letter state is visible |
| FAC-007 | P1 | Reconcile Postgres publications with Pinecone | Job reports missing, stale, and orphaned vectors and can repair them |

Required lifecycle:

```text
discovered → downloaded → parsed → structured → validated → enriched
          → needs_review → approved → published → indexed
                           └→ rejected
Any transient stage ───────→ retrying
Any terminal failure ──────→ quarantined
Published object ──────────→ superseded (never overwritten)
```

### 6.6 Admin and operations

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| ADM-001 | P0 | Protect admin route and every admin API | Anonymous/ordinary user receives 401/403; admin succeeds |
| ADM-002 | P0 | Remove fallback operational data | API errors render error states with retry and request ID |
| ADM-003 | P0 | Show real service, corpus, index, and ingestion health | Values are computed or explicitly marked unavailable with observation time |
| ADM-004 | P0 | Paginate/redact search audit | Query values follow retention/redaction policy; access is logged |
| ADM-005 | P1 | View failed pipeline runs and retry authorized jobs | Retry is idempotent and produces an audit entry |
| ADM-006 | P1 | View evaluation history and release gate | Report links to dataset/model/corpus versions |

### 6.7 Subscription and notifications

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| SUB-001 | P0 | Do not claim an email was sent unless accepted by the email provider | UI message reflects actual state: saved, confirmation sent, or failed |
| SUB-002 | P1 | Use double opt-in and unsubscribe tokens | Consent and unsubscribe integration tests pass |
| SUB-003 | P1 | Store consent provenance and status | Record includes timestamp, policy version, source, status, and minimal delivery metadata |
| SUB-004 | P1 | Prevent enumeration and subscription abuse | Uniform response, rate limit, and bot control are enforced |

---

## 7. API specification

### 7.1 Conventions

- Base path for versioned application APIs: `/api/v1`.
- JSON uses `snake_case`; timestamps use UTC RFC 3339; identifiers are opaque strings or URNs.
- Every response includes or returns the `X-Request-ID` value.
- Errors use one envelope:

```json
{
  "error": {
    "code": "INSUFFICIENT_EVIDENCE",
    "message": "A safe user-facing explanation.",
    "request_id": "req_...",
    "details": {}
  }
}
```

- No stack trace, provider secret, prompt, or internal connection string is returned.
- Pagination uses `limit` plus opaque `cursor`; maximum limit is server-controlled.
- Existing unversioned routes remain only as temporary compatibility aliases and emit deprecation headers.

### 7.2 Required endpoints

| Method/path | Access | Purpose | Required release behavior |
|---|---|---|---|
| `GET /health/live` | Public | Process liveness | Does not call dependencies |
| `GET /health/ready` | Public/monitor | Dependency readiness | Reports safe status for Postgres, index, and configured model path |
| `POST /api/v1/knowledge/query` | Public, rate-limited | Grounded question answering | Structured response; query length/cost limits; audit ID |
| `GET /api/v1/knowledge/objects/{urn}` | Public for published | Canonical object read | ETag/version, evidence, relationships, history summary |
| `GET /api/v1/knowledge/objects` | Public | Browse/filter | Cursor pagination and allowlisted filters |
| `GET /api/v1/knowledge/graph/diff` | Public | Bi-temporal comparison | Validated time parameters and deterministic categories |
| `GET /api/v1/knowledge/bible` | Public | Curated synthesis | Version and review metadata |
| `GET /api/v1/changes` | Public | Regulatory events | Real data or truthful empty state |
| `GET/POST/PATCH /api/v1/actions` | Authenticated | User action tracking | Ownership/RLS/audit enforcement |
| `POST /api/v1/actions/{id}/evidence` | Authenticated | Attach evidence | Validated file/link, storage metadata, audit event |
| `GET /api/v1/factory/runs` | Editor+ | Pipeline board | Persistent paginated state |
| `POST /api/v1/factory/runs` | Editor+ | Start ingestion | Idempotency key required |
| `POST /api/v1/factory/drafts/{id}/decision` | Reviewer+ | Approve/reject | Optimistic version check and reviewer note |
| `GET /api/v1/admin/stats` | Admin | System metrics | Real values only |
| `GET /api/v1/admin/search-audit` | Admin | Query audit | Redacted, paginated, retention-limited |
| `GET /api/v1/admin/ingestion-audit` | Admin | Pipeline audit | Real, filterable records |
| `POST /api/v1/admin/evals/promote` | Admin/reviewer | Promote failure to eval | Deduplicated immutable eval case |
| `POST /api/v1/subscriptions` | Public, rate-limited | Request subscription | Provider-aware state and no enumeration |
| `POST /api/v1/subscriptions/confirm` | Public | Confirm opt-in | Single-use expiring token |
| `POST /api/v1/subscriptions/unsubscribe` | Public | Withdraw | Idempotent and audited |

### 7.3 Ask request and response

Request:

```json
{
  "question": "What notice must a data fiduciary provide?",
  "jurisdiction": "IN",
  "as_of": "2026-09-08",
  "conversation": [],
  "filters": {
    "source_types": ["statute", "rule", "official_guidance"]
  }
}
```

Response:

```json
{
  "answer": "...",
  "status": "grounded",
  "grounded": true,
  "citations": [
    {
      "knowledge_object_urn": "urn:dpdpa:...",
      "source_id": "src_...",
      "label": "DPDP Act, section ...",
      "excerpt": "...",
      "coordinates": {"page": 4, "start": 120, "end": 248, "hash": "sha256:..."}
    }
  ],
  "limitations": [],
  "request_id": "req_...",
  "corpus_version": "...",
  "model_route": "provider/model-class",
  "latency_ms": 2400
}
```

Allowed `status` values are `grounded`, `partially_grounded`, `insufficient_evidence`, and `blocked`. The client must branch on `status`, not inspect answer text.

### 7.4 Rate and payload controls

Initial limits, configurable server-side:

- Public query: 10 requests/minute/IP and 100/day/IP, with stricter anonymous model budget.
- Authenticated query: 30 requests/minute/user and plan-specific daily budget.
- Subscription: 5 requests/hour/IP and 3/day/address hash.
- Admin: 60 requests/minute/admin, plus provider-side protections.
- Question length: 4,000 UTF-8 characters; conversation context: 12 turns and 24,000 characters.
- Upload limits: allowlisted MIME types, malware scan, 20 MB default, no active content execution.

Limits must return `429` with `Retry-After`; payload violations return `413` or `422` without invoking a model.

---

## 8. Canonical data model

### 8.1 Database changes

Use versioned migrations; `supabase_schema.sql` becomes a generated/bootstrap convenience, not the only migration history.

| Table | Purpose | Key fields/constraints |
|---|---|---|
| `sources` | Canonical source metadata | `id`, URL/storage path, publisher, source type, publication/effective dates, content hash; unique hash |
| `source_artifacts` | Immutable downloaded/parsed artifacts | `source_id`, artifact type, storage key, hash, parser version, created time |
| `knowledge_objects` | Stable identity and current publication pointer | `urn`, type, lifecycle status, current version ID |
| `knowledge_object_versions` | Immutable object versions | JSON payload, schema version, valid/system time, source set, reviewer, supersession link |
| `evidence_spans` | Precise evidence coordinates | version ID, source ID, page/offset, excerpt, coordinate hash |
| `graph_edges` | Typed version-aware relationships | from/to URN, relationship type, validity/system time, provenance |
| `regulatory_events` | Change feed | event dates, source ID, status, summary |
| `action_items` | User/org compliance work | owner/org, source URN/version, state, assignee, due date |
| `action_evidence` | Stored action proof | action ID, storage key/link, hash, actor, created time |
| `factory_runs` | Ingestion job identity and status | idempotency key, source, state, attempts, timestamps, error code |
| `factory_events` | Append-only state transitions | run ID, stage, actor/service, input/output refs, timing, outcome |
| `review_decisions` | Human approval record | draft/version, reviewer, decision, note, timestamp |
| `search_audit` | Controlled query telemetry | actor pseudonym/IP hash, query redaction/hash, status, citations, latency, expiry |
| `subscribers` | Subscription consent | normalized email encryption/hash strategy, status, consent provenance, policy version |
| `user_roles` | Server-authoritative authorization | user ID, role, granted by/at; unique user-role |
| `feedback` | Answer feedback | request ID, rating/category/comment, actor, created time |
| `evaluation_runs` | Reproducible release eval metadata | dataset, corpus, prompts, provider/model, code commit, scores |

### 8.2 Knowledge object version contract

Every published object must contain:

- Stable `urn` and immutable version identifier.
- `schema_version`, object `type`, lifecycle `status`, title, canonical proposition/summary.
- Canonical entities and typed obligations drawn from a governed ontology.
- At least one authoritative `source` and one evidence span for material legal claims.
- Evidence coordinates containing the declared hash in the schema-prescribed location.
- `date` metadata separating publication, effective, valid-from/to, and system-recorded times.
- `history` with creation, review, publication, and supersession events.
- Model/parser versions for machine-produced fields.
- Reviewer identity for every publication.

The schema and seed/migration code must agree on field placement. Scripts may not upsert directly into published state without invoking the same validation and publication rules as the API.

### 8.3 Seed corpus migration

The existing 45 objects are input candidates, not trusted published records. Migration must:

1. Snapshot/export the current rows and source artifacts.
2. Transform fields into the approved schema version.
3. Map noncanonical entity values through an explicit reviewed mapping.
4. Recompute evidence coordinate hashes from canonical source bytes.
5. Reject any object whose source cannot be reproduced.
6. Run schema and semantic validators.
7. Require legal/editor review for changed propositions.
8. Publish through the canonical publication service.
9. Rebuild Pinecone and reconcile every vector to an existing published version.
10. Produce a signed migration report: input, transformed, published, quarantined, and rejected counts.

No target pass count is assumed: a smaller verified corpus is acceptable; publishing unverifiable objects is not.

### 8.4 Retention and privacy defaults

- Raw question text: 30 days maximum unless the user explicitly saves it; then follow the account retention policy.
- Redacted aggregate query metrics: 12 months.
- Admin/security audit events: 12 months minimum.
- Rejected drafts and pipeline diagnostics: 180 days, excluding immutable source provenance required for published versions.
- Unconfirmed subscriptions: delete after 30 days.
- Account/action data: delete or export through a documented request workflow, subject to legal retention requirements.

Final retention values require owner/legal approval before production; the implementation must make them configurable and enforceable.

---

## 9. Reasoning and model behavior

### 9.1 Retrieval pipeline

1. Normalize and validate the user question.
2. Apply input safety and prompt-injection classification.
3. Generate an embedding using the configured route.
4. Retrieve candidate version IDs from Pinecone.
5. Hydrate canonical published versions and evidence from Postgres.
6. Apply jurisdiction, date, lifecycle, authority, and access filters.
7. Rerank and fit evidence to a bounded context budget.
8. Generate a schema-constrained answer.
9. Validate output structure and citation membership.
10. Calculate groundedness from claims/citations—not substring matching.
11. Return or downgrade to `insufficient_evidence`/`blocked`.
12. Record a redacted trace and metrics.

### 9.2 Provider configuration

- Use explicit variables such as `OPENAI_API_KEY`, `GEMINI_API_KEY`, and `OPENROUTER_API_KEY`; the service does not inherit the operator's ChatGPT/Codex OAuth session.
- Define independent routes for generation, vision/OCR, embeddings, and evaluation judge.
- Validate each route against the key it actually uses.
- Implement bounded runtime failover only between models confirmed compatible with the required response schema.
- Record provider/model identifiers without storing secrets or full sensitive prompts.
- In production, no-key configuration fails readiness; it never silently becomes mock mode.

### 9.3 Answer policy

- Cite only evidence supplied by the retrieval/hydration stage.
- Separate statutory text, official guidance, interpretation, and business recommendation.
- Mark effective date and known temporal limitations when they materially affect the answer.
- Do not infer a mandatory legal obligation from a lower-authority source without labeling the inference.
- If evidence conflicts, present the conflict and route it to review rather than selecting silently.
- Include a concise non-legal-advice statement without obscuring the useful answer.
- Never reveal system prompts, credentials, private audit records, or hidden retrieved data.

### 9.4 Trace contract

Each query trace records request ID, pseudonymous actor, input size/hash, safety decision, retrieval IDs/scores, corpus version, prompt template version, provider/model, validation decisions, final status, latency, token/cost estimates, and expiry. Raw text is stored only according to retention policy and access controls.

---

## 10. Security and privacy requirements

### 10.1 Release-blocking controls

- Admin APIs and UI are authenticated and authorized; shared-key transition fails closed.
- CORS uses an explicit production-origin allowlist and no wildcard credentials combination.
- Rate limits, payload limits, timeouts, and concurrency caps cover model-backed and upload endpoints.
- Secrets exist only in platform secret stores/local ignored files; a secret scan gates CI.
- Supabase RLS policies are tested for anonymous, user, editor, reviewer, and admin roles.
- Server validates all object IDs, filters, URLs, filenames, and model outputs.
- Uploads use randomized storage keys, MIME/content validation, malware scanning, and signed access URLs.
- External source fetching blocks private/link-local networks, redirect abuse, and oversized downloads.
- Logs redact authorization headers, email addresses, raw tokens, and configured sensitive fields.
- Dependencies and container images receive automated vulnerability checks.
- Backups and a restore exercise exist before general availability.

### 10.2 Threat cases that require tests

1. Anonymous caller requests `/admin/*`.
2. Ordinary account attempts role escalation or another user's action access.
3. Prompt requests disclosure of system instructions or unrelated retrieved content.
4. Model emits a citation not present in retrieval results.
5. Source URL points to localhost, cloud metadata, or private IP space.
6. Oversized/active document is uploaded.
7. Duplicate ingestion is replayed concurrently.
8. Missing production secret/configuration would otherwise enable a fallback.
9. Query/audit data is requested after retention expiry.
10. A stale reviewer modifies a draft after another reviewer published it.

### 10.3 Privacy UX

- Explain what query and account data is stored at the point of collection.
- Separate newsletter consent from product terms.
- Provide accessible unsubscribe and data-request paths.
- Avoid analytics/session replay on query content unless separately reviewed and redacted.

---

## 11. Reliability, observability, and operations

### 11.1 Service-level objectives

| Signal | Target |
|---|---|
| Public read API availability | 99.5% monthly |
| Query API availability | 99.0% monthly initially |
| p95 read latency | < 500 ms excluding cold start |
| p95 query latency | < 12 s; hard timeout 30 s |
| Failed published-to-index reconciliation | 0 unresolved > 15 minutes |
| Critical alert acknowledgement | < 30 minutes during support hours |

### 11.2 Required telemetry

- Structured JSON logs with request/run ID and environment.
- Metrics for request count, status, latency, rate-limit outcomes, provider errors, token/cost, retrieval count, grounded status, factory stage duration, queue depth, and index drift.
- Traces across API → retrieval → database → provider, with sensitive bodies omitted by default.
- Alerts for readiness failure, 5xx surge, provider failure, cost anomaly, factory backlog, schema rejection spike, and index drift.
- Public/user-facing status states distinguish unavailable, degraded, and empty data.

### 11.3 Backup and recovery

- Automated Supabase/Postgres backups with documented retention.
- Source artifacts stored durably with versioning or immutability controls.
- Pinecone recovery is a rebuild procedure, not a primary backup.
- Quarterly restore exercise; record recovery time and gaps.
- Target RPO: 24 hours initially. Target RTO: 4 hours initially.

---

## 12. Frontend experience and quality

### 12.1 State handling

Every data-backed screen implements distinct loading, empty, success, degraded, authorization, and error states. Error states retain a request ID and retry option. Production never falls back from an API error to realistic-looking fixture data.

### 12.2 Accessibility

- WCAG 2.2 AA target.
- Complete keyboard operation, visible focus, semantic headings/landmarks, labeled controls, announced async status, accessible graph alternative, and reduced-motion support.
- Color is not the only means of communicating status.
- Automated axe checks plus manual keyboard/screen-reader smoke tests gate release.

### 12.3 Performance and SEO

- Public landing and guide pages ship prerendered HTML.
- Route-level code splitting keeps admin/factory code out of the public initial bundle.
- Images have dimensions, modern formats, lazy loading where appropriate, and meaningful alt text.
- Target mobile Lighthouse: performance ≥ 85, accessibility ≥ 95, best practices ≥ 95, SEO ≥ 95 on key public pages.
- Generate sitemap, robots, canonical links, Open Graph metadata, and structured article/breadcrumb data where valid.

### 12.4 Browser support

Latest two stable versions of Chrome, Edge, Firefox, and Safari; current mobile Safari and Chrome. Unsupported features require graceful fallback.

---

## 13. Testing and evaluation strategy

### 13.1 Test pyramid

| Layer | Required coverage |
|---|---|
| Static | Python formatting/type checks where adopted, ESLint with zero warnings, schema checks, secret/dependency scans |
| Unit | Parsing, hashing, normalization, state transitions, authorization helpers, guardrails, groundedness, UI reducers/components |
| Integration | Postgres/RLS, API contracts, provider adapters, Pinecone reconciliation, storage uploads, email lifecycle |
| End-to-end | Public browse, Ask success/insufficiency, login/roles, action evidence, factory review/publish, admin denial/success |
| Evaluation | Legal factuality, citation validity, temporal handling, conflict handling, injection resistance, safe insufficiency |
| Operational | Migrations, backup restore, deployment smoke, rollback, alert delivery |

### 13.2 Evaluation dataset

The release set must include at least:

- 40 answerable questions across the major obligations and roles.
- 15 deliberately unanswerable or out-of-scope questions.
- 10 temporal/version-sensitive questions.
- 10 conflicting/ambiguous evidence cases.
- 10 prompt-injection or data-exfiltration cases.
- 10 citation-coordinate integrity cases.
- 5 plain-language/business translation cases.

At least 50 cases must use the real migrated corpus, and every legal expected result must be reviewed by a named legal/knowledge reviewer. Synthetic tests remain useful but are reported separately.

Each run pins code commit, dataset version, corpus/index version, prompt version, provider/model, runtime configuration, and scorer versions. A mock-model run can test plumbing but cannot satisfy the production quality gate.

### 13.3 Release gates

- Backend and frontend tests pass from a clean checkout.
- Test count does not drop unexpectedly from the approved baseline.
- ESLint has zero errors and zero warnings; production build and prerender exit normally.
- 100% schema validity and citation referential integrity for published objects.
- 100% admin/auth negative tests pass.
- No severity-critical/high open security defect.
- No critical eval failure; citation precision 100%; insufficiency recall ≥ 95% on the release set.
- Deployment smoke tests pass against preview and production.
- Legal reviewer signs off on corpus migration and release eval report.

---

## 14. Environments, configuration, and deployment

### 14.1 Environments

| Environment | Purpose | Data/provider policy |
|---|---|---|
| Local | Development | Local/test project; explicit mock flag allowed |
| CI | Deterministic tests | Ephemeral services/fixtures; no production credentials |
| Preview | Branch/release candidate | Isolated Supabase/index namespace; low provider budget |
| Production | Public service | Production stores, strict secrets, no mock fallback |

### 14.2 Configuration rules

- Frontend has one validated API-base configuration module; no component-local URLs.
- Server configuration is typed and validated once at startup.
- Blank variables are treated as absent.
- `VITE_*` variables are public by definition and never contain secrets.
- `.env.example` lists names and safe explanations only.
- Environment manifest documents Supabase URL/keys, allowed origins, provider routes/keys, index name, storage bucket, admin auth transition, email provider, logging level, and retention controls.

### 14.3 Deployment pipeline

1. Pull request runs static checks, unit/integration tests, schema validation, frontend build/prerender, scans, and offline evals.
2. Merge deploys preview/staging and runs migrations followed by smoke tests.
3. Release candidate runs live-provider/corpus evals with budget controls.
4. Human approval promotes the exact tested artifacts to production.
5. Post-deploy smoke checks health, public content, Ask, auth denial, admin success, and a known citation.
6. Failed gates automatically stop promotion; rollback uses the prior immutable image/frontend deployment and backward-compatible DB migration plan.

---

## 15. Delivery plan

### 15.1 Team and assumptions

Planning basis:

- Backend/AI engineer: 40 h/week.
- Frontend/full-stack engineer: 40 h/week.
- Knowledge/legal reviewer: 8–12 h/week.
- Product owner: milestone decisions and weekly acceptance.
- Estimates are engineering effort, not elapsed time, and include local verification but not the 25% program contingency.

### 15.2 Milestones

| # | Milestone | Target | Owner | Success criterion |
|---|---|---|---|---|
| M1 | Safe canonical backend | End week 1 | Backend | One deploy tree; admin protected; mocks disabled in production; tests green |
| M2 | Trusted corpus and data layer | End week 3 | Backend + reviewer | Migrations applied; reviewed corpus schema-valid; index reconciled |
| M3 | Real production user path | End week 4 | Full stack | Hosted Ask, reads, auth, actions, and truthful states work end to end |
| M4 | Operable research workflow | End week 6 | Backend + frontend | Factory state, reviews, publication, audits, and evidence are persistent |
| M5 | Production release | End week 7 | Team | Quality/security/eval gates pass; monitoring and rollback proven |
| M6 | Contingency/content finish | Week 8 | Team | Critical residuals closed; initial content/SEO expansion shipped |

### 15.3 Phase 1 — Canonicalize and harden (week 1)

| ID | Task | Effort | Owner | Depends on | Done criterion |
|---|---|---:|---|---|---|
| P1-01 | Record clean baseline: git state, tests, build, routes | 3 h | Backend | — | Reproducible baseline report committed without altering user WIP |
| P1-02 | Merge root reasoning/guardrail/trace changes into deploy backend | 8 h | Backend | P1-01 | Deploy tree contains intended newer behavior and all relevant tests pass |
| P1-03 | Move five operational scripts under deploy backend | 3 h | Backend | P1-02 | Scripts import and `--help`/dry-run from deploy root |
| P1-04 | Remove duplicate root backend artifacts and repair docs/compose decision | 4 h | Backend | P1-03 | Exactly one tracked backend source tree; no invalid build path |
| P1-05 | Add fail-closed transitional admin authentication | 5 h | Backend | P1-02 | All admin endpoint positive/negative tests pass |
| P1-06 | Add frontend admin credential/error flow and remove fake data | 5 h | Frontend | P1-05 | Public visit cannot see data; failed API shows factual error |
| P1-07 | Centralize/validate frontend API base and remove localhost use | 3 h | Frontend | P1-01 | Production source/bundle scan finds no localhost API |
| P1-08 | Add rate, payload, timeout, and concurrency controls | 6 h | Backend | P1-02 | Boundary and 429/413 tests pass |
| P1-09 | Fix provider-key routing and production no-mock behavior | 4 h | Backend | P1-02 | OpenRouter-only/config-error tests pass; readiness fails closed |
| P1-10 | Resolve current lint/runtime defects | 4 h | Frontend | P1-01 | Undefined component/duplicate key fixed; lint has zero warnings |

### 15.4 Phase 2 — Data integrity and migrations (weeks 2–3)

| ID | Task | Effort | Owner | Depends on | Done criterion |
|---|---|---:|---|---|---|
| P2-01 | Approve KO schema v2 and ontology mapping | 8 h | Backend + reviewer | M1 | Schema examples and entity mapping signed off |
| P2-02 | Introduce migration tooling and baseline existing SQL | 6 h | Backend | M1 | Fresh and upgrade database paths pass in CI |
| P2-03 | Add sources, artifacts, version, evidence, role, audit, factory, feedback tables | 8 h | Backend | P2-02 | Migrations, constraints, indexes, and rollback notes reviewed |
| P2-04 | Implement/test RLS policies by role | 8 h | Backend | P2-03 | Role matrix integration suite passes |
| P2-05 | Build deterministic 45-object transformer | 8 h | Backend | P2-01 | Produces valid candidates or explicit quarantine reasons |
| P2-06 | Reconstruct/verify source artifacts and evidence hashes, batch A | 8 h | Reviewer + backend | P2-05 | Batch report has reproducible hashes and reviewer disposition |
| P2-07 | Reconstruct/verify source artifacts and evidence hashes, batch B | 8 h | Reviewer + backend | P2-06 | Remaining objects dispositioned; none bypass validation |
| P2-08 | Implement canonical publication transaction | 8 h | Backend | P2-03 | Publish atomically stores version/evidence/history/audit |
| P2-09 | Publish approved migration and generate report | 5 h | Backend + reviewer | P2-04,P2-07,P2-08 | Counts reconcile; reviewer signs report |
| P2-10 | Rebuild and reconcile Pinecone index | 5 h | Backend | P2-09 | No missing, stale, or orphaned vectors |

### 15.5 Phase 3 — Deploy and connect the real product (week 4)

| ID | Task | Effort | Owner | Depends on | Done criterion |
|---|---|---:|---|---|---|
| P3-01 | Configure preview backend deployment and secrets | 4 h | Backend | M1,M2 | Preview readiness green; config manifest complete |
| P3-02 | Add versioned API/error/request-ID middleware | 6 h | Backend | M1 | Contract tests pass; compatibility aliases documented |
| P3-03 | Wire Ask UI to structured response contract | 8 h | Frontend | P3-01,P3-02 | Grounded, insufficient, blocked, and error states pass E2E |
| P3-04 | Wire knowledge/change/Bible surfaces without mock fallback | 6 h | Frontend | P3-01 | API failure and empty-state E2E tests pass |
| P3-05 | Implement Supabase JWT verification and `user_roles` authorization | 8 h | Backend | P2-04 | Transitional key can be retired; role tests pass |
| P3-06 | Guard frontend workspace/admin routes | 5 h | Frontend | P3-05 | Role-based navigation and direct-route denial pass |
| P3-07 | Implement persistent actions and evidence API | 8 h | Backend | P2-03,P3-05 | Ownership, upload/link, audit, and RLS tests pass |
| P3-08 | Connect actions/evidence frontend | 6 h | Frontend | P3-07 | State persists across refresh and account session |
| P3-09 | Run preview cross-surface smoke test | 4 h | Full stack | P3-03–P3-08 | Signed smoke report has no P0 defect |

### 15.6 Phase 4 — Complete the factory and operations (weeks 5–6)

| ID | Task | Effort | Owner | Depends on | Done criterion |
|---|---|---:|---|---|---|
| P4-01 | Implement persisted factory run/event state machine | 8 h | Backend | P2-03,P2-08 | Legal transitions enforced; replay/idempotency tests pass |
| P4-02 | Add source-fetch SSRF/size/type protections | 6 h | Backend | P4-01 | Threat-case integration tests pass |
| P4-03 | Add retries, quarantine, and idempotency | 6 h | Backend | P4-01 | Transient/terminal/concurrent tests pass |
| P4-04 | Add review decision API with optimistic locking | 6 h | Backend | P4-01 | Stale decision is rejected; audit identifies reviewer |
| P4-05 | Replace FactoryBoard constants with API state | 8 h | Frontend | P4-01,P4-04 | Reload-safe board supports decision workflow |
| P4-06 | Build real admin metrics and paginated audits | 8 h | Backend | P2-03,P4-01 | Results reconcile with fixture DB and enforce retention |
| P4-07 | Connect admin screens and retry controls | 6 h | Frontend | P4-06 | All state branches and authorized retry pass E2E |
| P4-08 | Implement index reconciliation job and alert | 5 h | Backend | P2-10,P4-01 | Drift is detected, repaired, and alert-tested |
| P4-09 | Add email provider and double opt-in lifecycle | 8 h | Full stack | P2-03 | Provider accepted/failure/confirm/unsubscribe paths pass |
| P4-10 | Add operational dashboards and alerts | 8 h | Backend | P3-01,P4-06 | Synthetic fault triggers test alert and runbook link |

### 15.7 Phase 5 — Quality, evaluation, and launch (week 7)

| ID | Task | Effort | Owner | Depends on | Done criterion |
|---|---|---:|---|---|---|
| P5-01 | Add frontend unit/component test foundation | 6 h | Frontend | M3 | CI runs representative tests for every critical state |
| P5-02 | Add Playwright critical-path E2E suite | 8 h | Frontend | M3,M4 | Public/Ask/auth/action/factory/admin journeys pass in preview |
| P5-03 | Expand real-corpus eval dataset, batch A | 8 h | Reviewer + backend | M2 | Reviewed cases cover answerable/unanswerable/temporal classes |
| P5-04 | Expand security/conflict/citation evals, batch B | 8 h | Reviewer + backend | P5-03 | Required category counts and expected evidence complete |
| P5-05 | Make eval runs reproducible and release-gating | 6 h | Backend | P5-03,P5-04 | Report pins all versions and CI/promotion consumes thresholds |
| P5-06 | Accessibility and browser remediation | 8 h | Frontend | P5-02 | Automated and manual acceptance criteria pass |
| P5-07 | Performance, prerender, sitemap, and metadata gate | 6 h | Frontend | P5-02 | Build exits; route/SEO/Lighthouse targets pass |
| P5-08 | Backup restore and rollback rehearsal | 6 h | Backend | M4 | Timed restore/rollback report meets targets |
| P5-09 | Security review and release checklist | 8 h | Team | P5-02,P5-05 | No critical/high release blocker; sign-offs recorded |
| P5-10 | Production deployment and post-deploy verification | 5 h | Team | P5-09 | Exact candidate promoted; smoke/monitoring green |

### 15.8 Phase 6 — Content and post-launch finish (week 8 and ongoing)

| ID | Task | Effort | Owner | Depends on | Done criterion |
|---|---|---:|---|---|---|
| P6-01 | Publish initial priority guide batch | 8 h/batch | Reviewer/content | M2 | Each guide reviewed, cited, prerendered, and discoverable |
| P6-02 | Map course modules to stable knowledge references | 6 h | Content + frontend | M3 | Links and displayed versions pass automated checks |
| P6-03 | Review query/eval failures and add regression cases | 4 h/week | Reviewer + backend | M5 | Every accepted product defect has a regression case |
| P6-04 | Review reliability, cost, and search gaps | 3 h/week | Product + backend | M5 | Weekly decisions and owners recorded |

### 15.9 Critical path and parallel work

```text
P1-01 → P1-02 → P1-04 → M1
                    ↓
P2-01 → P2-05 → P2-06/07 → P2-09 → P2-10 → M2
          ↑                   ↑
P2-02 → P2-03 → P2-04 → P2-08
                                      ↓
P3-01/02 → P3-03/04 → P3-09 → M3
P3-05 → P3-06/07 → P3-08 ─────┘
                                      ↓
P4-01 → P4-04 → P4-05 → M4 → P5-02/05/09 → P5-10
```

Frontend P1 fixes can run beside backend consolidation. Schema/ontology approval can start while hardening is in review. Evaluation-case authoring can begin as soon as the migrated corpus stabilizes, while factory UI work continues.

### 15.10 Effort and schedule range

The listed implementation tasks total roughly **260–300 engineering hours**, plus **45–65 reviewer/content hours**. With review overhead and a 25% uncertainty buffer, plan approximately **390–455 team hours**. External service setup, legal review delays, and recovery of missing source artifacts are the largest schedule variables.

---

## 16. Risks and mitigations

| Risk | Impact | Probability | Mitigation/trigger |
|---|---|---|---|
| Source evidence for seed objects cannot be reproduced | High | Medium | Quarantine objects; launch with smaller verified corpus; never fabricate coordinates |
| Backend consolidation overwrites uncommitted work | High | Medium | Snapshot/diff user WIP, merge deliberately, preserve commits, compare test counts |
| RLS differs between local and hosted Supabase | High | Medium | Role-matrix tests run against preview project before production |
| Model/provider changes degrade structured output | High | Medium | Adapter contract tests, pinned route, live release eval, failover qualification |
| Legal reviewer availability blocks corpus approval | High | Medium | Prioritize core obligations, review in small batches, publish only approved subset |
| Production spend spikes from automated queries | High | Medium | Rate/budget/concurrency caps, cost alerts, degraded mode |
| Audit logs collect unnecessary personal data | High | Medium | Redaction, pseudonymization, access logs, retention jobs, privacy review |
| Factory retries create duplicate publications | High | Low | Idempotency keys, unique constraints, atomic publication, concurrency tests |
| SEO work distracts from trust/safety path | Medium | Medium | Keep content expansion after M5; only technical SEO is P0 |
| Existing docs continue to direct stale deployment | Medium | High | Documentation reconciliation is part of M1/M5 acceptance |
| External course repo drifts from canonical content | Medium | Medium | Stable URNs, version metadata, scheduled link/provenance checks |

---

## 17. Definition of done

### 17.1 Feature definition of done

A task is done only when code/configuration is merged, tests are added and passing, authorization/error/accessibility states are handled, telemetry exists where appropriate, documentation is updated, and the behavior is demonstrated in preview. “UI present,” “API returns once,” or “mock works” is not done.

### 17.2 Production release acceptance

The platform may be called production-ready only when all of the following are true:

- One authoritative backend tree is built and deployed.
- Hosted frontend talks to the hosted API through the validated configuration.
- Admin and editorial capabilities are server-authorized.
- No production path silently displays or persists mock data.
- The published corpus and citations pass schema/integrity validation.
- A human-reviewed, real-corpus evaluation meets release thresholds.
- Factory transitions, publication, actions, evidence, audit, and subscriptions persist correctly.
- Rate limits, input/output guardrails, CORS, RLS, secret scanning, and key threat tests pass.
- Frontend tests, build, prerender, lint, accessibility, and critical E2E checks pass.
- Monitoring, alerting, backup restore, rollback, and incident ownership are documented and exercised.
- Product owner and knowledge/legal reviewer record release approval.

---

## 18. Required decisions before implementation

| Decision | Recommended default | Decision owner | Needed by |
|---|---|---|---|
| Canonical backend location | `deployments/dpdpa-backend/` | Tech owner | P1-02 |
| Production admin identity | Supabase JWT + `user_roles`; shared key only transitional | Tech/product | P3-05 |
| Authoritative source hierarchy | Statute/rules → official guidance → judgments → reviewed commentary | Legal/product | P2-01 |
| Ontology values | Governed DPDP-specific entities with explicit aliases | Legal/knowledge | P2-01 |
| Query retention | 30-day raw maximum; 12-month redacted aggregate | Product/privacy | P2-03 |
| Hosting | Vercel frontend + Railway API + Supabase + Pinecone | Tech/product | P3-01 |
| Email provider | Transactional provider with double opt-in/webhooks | Product/tech | P4-09 |
| Anonymous Ask budget | Limited public tier with daily budget | Product | P1-08 |
| Legal release sign-off | Named reviewer required for corpus/eval | Product/legal | P2-09 |

If an owner rejects a recommended default, record the alternative and its consequences in an architecture decision record before dependent work starts.

---

## 19. Traceability to known repository findings

| Finding | Requirements/tasks that close it |
|---|---|
| Duplicate divergent backend trees | Architecture rule 2; P1-02–P1-04 |
| Live Ask not connected | ASK-001; P1-07; P3-01–P3-04 |
| Public/unauthenticated admin | ADM-001; section 5; P1-05–P1-06; P3-05–P3-06 |
| Fabricated admin fallback | Architecture rule 3; ADM-002; P1-06 |
| No abuse controls | Section 7.4; P1-08 |
| Invalid 45-object seed corpus | Sections 8.2–8.3; P2-01; P2-05–P2-10 |
| Missing DB migrations/tables | Section 8.1; P2-02–P2-04 |
| In-memory/no-op workflows | ACT-002; FAC-001; P3-07–P3-08; P4-01–P4-05 |
| Provider/key inconsistency | Section 9.2; P1-09 |
| Mock-only eval confidence | Section 13.2; P5-03–P5-05 |
| Frontend has no tests/lint warnings | Sections 12–13; P1-10; P5-01–P5-02 |
| Subscription claims unsent email | Section 6.7; P4-09 |
| Incomplete SEO/content | Sections 6.1 and 12.3; P5-07; P6-01 |

---

## 20. Repository implementation map

| Current artifact | Intended treatment | Governing work |
|---|---|---|
| `src/` | Merge unique guardrail, trace, reasoning, API, and test work into the deploy backend; then remove the duplicate tree | P1-02, P1-04 |
| `deployments/dpdpa-backend/src/` | Canonical backend package | P1-02 onward |
| Root ingestion/seed/storage scripts | Move under `deployments/dpdpa-backend/scripts/` and make validation mandatory | P1-03, P2-05 |
| Root `Dockerfile`, `requirements.txt`, `docker-compose.yml` | Remove duplicates or replace with an explicitly tested root orchestration file | P1-04 |
| `supabase_schema.sql` and deploy copy | Baseline into ordered migrations; retain one generated/bootstrap representation | P2-02–P2-04 |
| `src/schemas/knowledge_object_schema.json` and deploy copy | Approve one schema v2, store only with canonical backend, publish examples | P2-01 |
| `seed_full_knowledge_base.py` | Convert from direct production upsert to migration input using publication service | P2-05–P2-09 |
| `src/reasoning/model_client.py` and deploy copy | Merge structured-output behavior and correct per-provider routing/config checks | P1-02, P1-09 |
| `src/reasoning/guardrails.py`, `tracer.py` | Integrate into canonical query path and test all failure modes | P1-02, ASK-005 |
| `deployments/dpdpa-wiki/src/App.jsx` | Use central API configuration and protected route policy | P1-07, P3-06 |
| `AdminAudit.jsx` | Remove hard-coded fallback and consume authenticated real APIs | P1-06, P4-07 |
| `FactoryBoard.jsx` | Replace imported constant mutation with factory API/state machine | P4-05 |
| `ChangeWorkspace.jsx` | Fix undefined empty-state component and cover empty data in tests | P1-10, P5-01 |
| `mockData.js` | Fix duplicate fields; limit fixtures to explicit test/dev imports | P1-10 |
| `Home.jsx` subscription flow | Use subscription API and provider-confirmed messaging | P4-09 |
| `evals/` | Split synthetic and real-corpus datasets; pin run metadata and gate releases | P5-03–P5-05 |
| `README.md`, `PLAN.md`, `DEPLOY.md`, architecture docs | Reconcile after M1 and before M5; remove stale paths/status claims | M1, P5-09 |

---

## 21. Immediate next action

Approve or amend the nine decisions in section 18, then execute **P1-01 through P1-04 as one consolidation workstream** and **P1-05 through P1-10 as parallel hardening work**. Do not deploy the reasoning backend publicly until M1 is accepted.
