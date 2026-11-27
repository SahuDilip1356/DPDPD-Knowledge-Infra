# References

Where to look, and how far to trust each document. For where the project stands today,
read [`context/STATE.md`](../context/STATE.md) first; it overrides anything dated earlier here.
Decisions are logged in [`decisions/log.md`](../decisions/log.md).

## context/ — principles (still in force)

| Doc | What |
| :--- | :--- |
| [FOUNDING_MEMO.md](../context/FOUNDING_MEMO.md) | Vision, mental model and invariants (Jul 2026) |
| [KNOWLEDGE_CONSTITUTION.md](../context/KNOWLEDGE_CONSTITUTION.md) | Ontology, trust layers, versioning rules for knowledge objects |

## architecture/ — how the system is built

| Doc | What | Status |
| :--- | :--- | :--- |
| [SYSTEM_ARCHITECTURE.md](architecture/SYSTEM_ARCHITECTURE.md) | Three-layer architecture, factory departments | Original design (Jul) |
| [SYSTEM_CONSTRUCT.md](architecture/SYSTEM_CONSTRUCT.md) | Storage construct, schemas, agent handshakes | Original design (Jul) |
| [RESEARCH_FACTORY_DESIGN.md](architecture/RESEARCH_FACTORY_DESIGN.md) | Factory pipeline, agent by agent | Original design (Jul) |
| [COMPREHENSIVE_ARCHITECT_SPEC.md](architecture/COMPREHENSIVE_ARCHITECT_SPEC.md) | Architect review of backend + wiki | 10 Sep |
| [DEPLOYMENT_ARCHITECTURE.md](architecture/DEPLOYMENT_ARCHITECTURE.md) | dpdpa.wiki, dpdpa.shiksha, backend, shared Supabase | Topology current; route table predates `/workspace` |

## runbooks/ — how to operate it

| Doc | What |
| :--- | :--- |
| [DEPLOY.md](runbooks/DEPLOY.md) | Deployment steps, Railway and Vercel |
| [SECRETS.md](runbooks/SECRETS.md) | Every secret's name, source and home (no values) |

## archives/plans/ — delivery plans and status snapshots (historical)

Kept for decisions and reasoning; their status claims are dated. Current work is planned in `specs/`.

| Doc | Date |
| :--- | :--- |
| [SPRINT_PLAN.md](../archives/plans/SPRINT_PLAN.md) | Jul |
| [PLAN.md](../archives/plans/PLAN.md) | 20 Aug |
| [COMPREHENSIVE_BUILD_SPEC.md](../archives/plans/COMPREHENSIVE_BUILD_SPEC.md) | 8 Sep, umbrella delivery spec (M1–M5) |
| [HARDENING_SPEC.md](../archives/plans/HARDENING_SPEC.md) | 8 Sep, pre-Railway fixes |
| [EVAL_SPEC.md](../archives/plans/EVAL_SPEC.md) | Sep, eval design |
| [M1_BASELINE.md](../archives/plans/M1_BASELINE.md) | 8 Sep |
| [DEVELOPMENT_STATUS_2026-09-28.md](../archives/plans/DEVELOPMENT_STATUS_2026-09-28.md) | 28 Sep |

## design/

- [ui-ux-studio/](design/ui-ux-studio/) — product understanding and UI/UX specification
- [brand/](design/brand/) — SaralPrivacy Knowledge Infra logo

## competitive_intel/ — market lane reports (internal)

Generated coverage, gap matrix and question sources. Discovery only, never law.

## archives/ — superseded

- [FIREBASE_FIRESTORE_SCHEMA.md](../archives/FIREBASE_FIRESTORE_SCHEMA.md) — Firestore design; the system runs on Supabase Postgres + Pinecone
- [episodic/](../archives/episodic/) — dated session checkpoints
