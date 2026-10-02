## Learned User Preferences

- Start explanations with a short “Here is the learnings —” analogy, then the answer in plain language
- Read architecture and code first, then present comprehensively; do not skip the read-then-explain step for this repo
- After interruptions or laptop restarts, resume from `memory/STATE.md`; save a checkpoint there when asked to remember state
- Treat DPDPA.com as competitive intelligence and taxonomy discovery, not canonical law; do not copy competitor templates or courses
- Exclude training and certification from competitor harvest stacking; use GPT-OSS as a retrieval model over the graph, not weight training

## Learned Workspace Facts

- DPDPD Knowledge Infra is SaralPrivacy’s DPDPA knowledge system; Setu is the trusted canonical layer
- Architecture is three layers: permanent knowledge (Git ledger + Supabase Postgres + Pinecone), grounded reasoning, then consumer apps
- Core knowledge is Trust Layers 1–2 (Act/Rules/Judgements) with evidence and URNs; Bible, Changes, Actions, Ask, and Factory are windows onto the same graph
- Ingestion runs through factory agents (scout → parse → cite → structure → ontology → relations → dedup → reason → translate → publish), usually started via `ingest_document.py`
- The seed scripts (`deployments/dpdpa-backend/scripts/seed_full_knowledge_base.py`, `seed_supabase.py`) are retired and exit without writing: their objects are unverified. The live corpus is published by `src/competitive_intel/build_knowledge_objects.py` and must pass `deployments/dpdpa-backend/src/schemas/corpus_contract.py`; session handoff files live under `memory/`; competitor harvest JSONL lives under `staging/harvest/` and is classified with `harvest/classify_pages.py`
- React dashboard lives in `frontend/`; Command Center is `/today` on local Vite at `http://127.0.0.1:5173`
- Apify MCP is connected; competitor crawls use `apify/website-content-crawler` on public pages only (no login, admin, app, or dashboard); skip gotrust.in, perfios.ai, and leegality.com, and crawl GoTrust’s DPDPA product at gotrust.tech
- Never import DPDPA.com or other competitor pages into Setu; keep a separate Competitive Intelligence Corpus as Layer 4–5 opinions, not law
- Classifier trays are LAW/RULES, INTERPRETATION, FAQ, BLOG, TEMPLATE, CASE LAW, TOOL, COURSE, and COMMERCIAL
- Competitor pages default to unpublished; claims must be verified against Act, Rules, Gazette, MeitY, DPB, or courts before canonical use
- DPDPA.com case-law lists are JavaScript-rendered; use Playwright with a content wait, not an HTTP-only crawl; their DPDPA Board-order groups are still empty / “coming soon”
- This project was originally built in Antigravity and is now continued in Cursor
- The backend lives only in `deployments/dpdpa-backend/`. The old copy at the repo root (`src/api`, `src/reasoning`, `src/storage`, `src/factory`, `src/schemas`, `src/tests`) was removed on 2026-10-02; root `src/` now holds only `competitive_intel/`
