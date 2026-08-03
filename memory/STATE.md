# Project State — DPDPD Knowledge Infra

**Last updated:** 2026-08-01 13:55 IST  
**Branch:** `main`  
**Phase:** Post Sprint 1–7 spine — product polish + knowledge growth strategy  
**Resume cue:** “resume Knowledge Infra” / “continue from STATE”

---

## Where we are (one paragraph)

DPDPA Privacy Knowledge Infrastructure is largely built: schemas, Git ledger, factory agents, grounded reasoning API, Supabase/Pinecone path, Docker, and React dashboard. Seeded knowledge = **45 KOs + ~52 graph edges + 6 events + 5 actions**. Session work focused on understanding architecture, knowledge/graph inventory (Section 6 walkthrough), UI look/blank-page troubleshooting, and a strategy discussion on how to add topics to Core vs other trust layers. **Lots of local uncommitted UI/content work** (Bible, Certification Course, Infographic, branding, style polish) — not committed yet.

---

## Working on now / parked mid-flight

1. **Uncommitted WIP on `main`** (do not lose on restart):
   - New: `DPDPA_BIBLE.md`, `Bible.jsx`, `CertificationCourse.jsx`, `InfographicDashboard.jsx`, `certificationData.js`, `SaralPrivacyLogo.jsx`, Brand Guidelines folder
   - Routes wired: `/bible`, `/course`, `/infographic` (+ nav for course/bible)
   - Modified: App shell, AdminAudit, Ask, CommandCenter, Factory, KnowledgeExplorer, mockData, design tokens/CSS, API service, orchestrator, schema, tests
   - Also: `.agent/`, `.cursor/` local agent folders

2. **Frontend runtime:** Vite was restarted successfully at `http://127.0.0.1:5173/` — blank preview was usually a stuck Cursor tab, not a compile failure. Production `npm run build` succeeded (large JS chunk warning only).

3. **Knowledge growth decision (discussed, not decided):**
   - Core = Trust L1/L2 primary law objects with evidence + URNs
   - Other UI sections are windows onto the same graph (not separate encyclopedias)
   - Fork offered: **A) statute-complete Core backlog** vs **B) 5 business clusters** (Consent, Breach, Children, SDF, Cross-border)
   - Dilip had not yet chosen A vs B before pause

---

## Solid foundation (already committed historically)

| Area | Status |
|------|--------|
| Sprints 1–6 (schema → factory → API/reasoning) | Done on `main` |
| Sprint 7 dashboard + Admin Audit + Docker | Done on `main` |
| Seed corpus (~45 KOs across trust layers) | In `seed_full_knowledge_base.py` |
| MeitY poll + ingest CLI + Gemini OCR path | Exists |
| Staging inbox PDF | `staging/inbox/G.S.R_102_E_25_07_2026.pdf` |
| Local ledger samples | 2 KOs under `staging/temp_ledger/` |

---

## Next session — suggested first moves

1. Read this file + last episodic digest  
2. `git status` — review uncommitted WIP; commit in logical chunks if Dilip wants  
3. Ask Dilip to pick knowledge growth strategy **A vs B** (or hybrid)  
4. If B: draft the 5 clusters with required KOs/edges/actions  
5. If A: list missing Act sections / Rules nodes vs seed  
6. Optionally harden Bible so it always syncs from KO URNs (avoid drift)

---

## How to run (quick)

```bash
# Backend
source .venv/bin/activate
uvicorn src.api.api_service:app --port 8000 --reload

# Frontend
cd frontend && npm run dev -- --host 127.0.0.1 --port 5173
# Open http://127.0.0.1:5173/today
```

---

## Open questions for Dilip

- Knowledge growth: statute-complete Core first, or SaralPrivacy-critical clusters first?
- Commit the Bible / Certification / Infographic / brand WIP this session?
- Is Certification Course in-scope for Knowledge Infra MVP, or a parallel product surface?
