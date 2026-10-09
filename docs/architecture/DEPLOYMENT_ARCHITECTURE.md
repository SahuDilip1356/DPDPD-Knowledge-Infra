# Master Deployment Architecture: dpdpa.wiki & dpdpa.shiksha

This document outlines the multi-site production deployment plan to split the DPDPA system into **two decoupled client frontends**, **one central FastAPI Python backend**, and **one shared Supabase BaaS instance**.

---

## 🗺️ System Blueprint

```
                      ┌────────────────────────────────┐
                      │    Shared Supabase BaaS        │
                      │  (Auth, Database, PDF Storage) │
                      └────▲──────────────────────▲────┘
                           │                      │
          ┌────────────────┴──────────────┐  ┌────┴──────────────────────────┐
          │   https://dpdpa.wiki          │  │   https://dpdpa.shiksha       │
          │  (Knowledge Infra Frontend)   │  │  (DPDPA Certification Course) │
          │  Vercel SPA: dpdpa-wiki       │  │  Vercel SPA: dpdpa-shiksha    │
          └────────────────┬──────────────┘  └────┬──────────────────────────┘
                           │                      │
                           │ API Q&A Searches     │ API Exam Logs
                           └─────────────┐ ┌──────┘
                                         ▼ ▼
                      ┌────────────────────────────────┐
                      │    FastAPI Python Backend API  │
                      │  (Render / Railway / CloudRun) │
                      └────┬──────────────────────┬────┘
                           │                      │
                           ▼                      ▼
                     [Pinecone Vector]      [MeitY Ingestion]
```

---

## 📍 Repository layout

The two frontends live in **separate repositories** and deploy independently.

| Repo | Contains | Vercel root directory |
| :--- | :--- | :--- |
| [`DPDPD-Knowledge-Infra`](https://github.com/SahuDilip1356/DPDPD-Knowledge-Infra) *(this repo)* | `dpdpa.wiki` frontend + FastAPI backend | `deployments/dpdpa-wiki` |
| [`dpdpa-shiksha`](https://github.com/SahuDilip1356/dpdpa-shiksha) | `dpdpa.shiksha` certification course | *(repo root — leave empty)* |

On disk: `Product Dev/DPDPD Knowldge Infra/` and `Product Dev/DPDPA Shiksha/`.

The backend deploys to **Railway** from this repo with root directory
`deployments/dpdpa-backend`.

---

## 🧭 Ownership Partition

Each frontend owns its screens outright — no shared screen code, no dead routes.
A file lives in exactly one app unless it is on the shared list below.

### `dpdpa.wiki` — *the knowledge* (reference + the factory that produces it)

| Route | Screen | Supporting components |
| :--- | :--- | :--- |
| `/today` | CommandCenter | — |
| `/changes`, `/changes/:id` | ChangesFeed, ChangeWorkspace | GitTimeline |
| `/knowledge` | KnowledgeExplorer | GraphExplorer |
| `/ask` | AskIntelligence | ChatInterface |
| `/bible` | Bible | — |
| `/infographic` | InfographicDashboard | — |
| `/factory` | FactoryBoard | — |
| `/actions` | DecisionsActions | BusinessActions |
| `/admin` | AdminAudit | — |
| `/course` | → 302 to `dpdpa.shiksha` | — |

Owns `data/mockData.js`, `ui/SearchOverlay.jsx`, `ui/SharedComponents.jsx`.

### `dpdpa.shiksha` — *the capability* (learn + certify)

| Route | Screen | Supporting components |
| :--- | :--- | :--- |
| `/` | CertificationCourse — onboarding → diagnostic → 12 modules → capstone → exam → credential | CourseShell, CourseProgressContext |
| `*` | → `/` | — |

Owns `data/certificationData.js` and the `cert_*.png` design references.

Shiksha runs a **course-native progress rail** rather than the wiki's portal drawer:
module list with completion state, progress meter, gated capstone/exam entries, and a
single `Knowledge Base ↗` hand-off to `dpdpa.wiki`. `CertificationCourse` keeps its own
state and mirrors the rail's slice through `CourseProgressContext`; the rail jumps
modules through an action the course registers on the same context.

### Shared (intentionally duplicated in both trees)

`ui/SaralPrivacyLogo.jsx` · `ui/AuthModal.jsx` · `data/supabaseClient.js` ·
`styles/design-tokens.css` · `styles/global.css` · `styles/components.css`

At runtime both apps share one Supabase project and one FastAPI backend.
If this list grows, promote it to a workspace package rather than widening the copy.

### Build impact

| Build | Bundle | Gzip |
| :--- | ---: | ---: |
| Pre-split monolith (`frontend/`) | 738.3 kB | 198.5 kB |
| `dpdpa-wiki` | 674.3 kB | 181.6 kB |
| `dpdpa-shiksha` | 521.1 kB | 150.4 kB |

### ⚠️ Known gap — cross-domain session

`dpdpa.wiki` and `dpdpa.shiksha` are different eTLD+1, so the Supabase session does not
cross between them. A user signed in on one lands signed-out on the other. Blast radius
today is small (only `/admin` and gated `/factory` actions read `user`), but this must be
solved before learner accounts carry real credential state — most likely a short-lived
handoff token exchanged for a session on arrival.

---

## 🏷️ Attribution

Both properties carry **"A SaralPrivacy Initiative"** in the sidebar footer and the
`<title>`. The certificate artifact keeps its own, more formal issuer of record —
*SaralPrivacy Board of Review* — because a credential needs an issuer, not a byline.

---

## 📦 Directory Structure Setup

The project has been split into three distinct directories under **`deployments/`** in your workspace:

1. **`deployments/dpdpa-wiki/`**
   - **Target Host:** Vercel (bind to custom domain `dpdpa.wiki`)
   - **Vite Client Routing:** Internal routing for Today, Graph Visuals, Ingestion Boards, Ask Grounded Q&A, and Bible.
   - **Cross-Domain Hand-off:** Links pointing to `/course` automatically redirect to `https://dpdpa.shiksha`.
   - **Vercel Routing:** Custom `vercel.json` SPA configuration included.

2. **`dpdpa-shiksha` (separate repository)**
   - **Target Host:** Vercel (bind to custom domain `dpdpa.shiksha`)
   - **Vite Client Routing:** Root `/` directly serves the personalized Certification onboarding, diagnostic, syllabus workouts, simulations, and final exam.
   - **Cross-Domain Hand-off:** Links pointing to Today, Visuals, Ingestion, Ask Q&A, etc. automatically redirect to `https://dpdpa.wiki/...`.
   - **Vercel Routing:** Custom `vercel.json` SPA configuration included.

3. **`deployments/dpdpa-backend/`**
   - **Target Host:** Render, Railway, or Google Cloud Run.
   - **Port:** Configured to standard `8000`.
   - **Deployment:** Dockerfile & requirements are included for container build and deploy.

---

## ⚡ Repository status

| Repo | State |
| :--- | :--- |
| `DPDPD-Knowledge-Infra` | Hosts `dpdpa.wiki` **and** the backend. No further split needed — Vercel and Railway both point at subdirectories of this repo. |
| `dpdpa-shiksha` | ✅ Created and pushed: https://github.com/SahuDilip1356/dpdpa-shiksha |

`dpdpa-wiki` and `dpdpa-backend` intentionally do **not** get their own
repositories. Both Vercel and Railway support a root-directory setting, so a
third and fourth repo would add synchronisation work with no benefit.

---

## 🔑 Shared Environment Variables Configuration

Ensure you populate the environment variables on Vercel and your API Gateway as follows:

| Environment Variable | Where to set it | Value / Description |
| :--- | :--- | :--- |
| `VITE_SUPABASE_URL` | Vercel (both apps) | `https://hgjxuljgfbmlgcsagorj.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Vercel (both apps) | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `VITE_API_URL` | Vercel (both apps) | URL of your hosted backend (e.g. `https://api.dpdpa.wiki`) |
| `VITE_WIKI_URL` | Vercel (shiksha app) | Link to knowledge base: `https://dpdpa.wiki` |
| `VITE_SHIKSHA_URL` | Vercel (wiki app) | Link to certification: `https://dpdpa.shiksha` |
| `DATABASE_URL` | Backend Host | Supabase Postgres URL |
| `GEMINI_API_KEY` | Backend Host | Gemini API key for Q&A and Vision parser |
| `PINECONE_API_KEY` | Backend Host | Vector database credentials |
| `PINECONE_INDEX_NAME` | Backend Host | Name of vector index |
