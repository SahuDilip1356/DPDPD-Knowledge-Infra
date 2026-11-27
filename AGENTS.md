## Learned User Preferences

- Start explanations with a short “Here is the learnings —” analogy, then the answer in plain language
- Read architecture and code first, then present comprehensively; do not skip the read-then-explain step for this repo
- After interruptions or laptop restarts, resume from `context/STATE.md`; save a checkpoint there when asked to remember state
- Treat DPDPA.com as competitive intelligence and taxonomy discovery, not canonical law; do not copy competitor templates or courses
- Exclude training and certification from competitor harvest stacking. Law answers come from retrieval over the verified graph (GPT-OSS or any model as the reader), never from model weights. Fine-tuning is allowed for voice and format only, on SaralPrivacy's own writing (e.g. the daily briefings, after the flagged ones are fixed); never on law text, competitor or market data (decided 2026-11-25)

## Learned Workspace Facts

- DPDPD Knowledge Infra is SaralPrivacy’s DPDPA knowledge system; Setu is the trusted canonical layer
- Architecture is three layers: permanent knowledge (Git ledger + Supabase Postgres + Pinecone), grounded reasoning, then consumer apps
- Core knowledge is Trust Layers 1–2 (Act/Rules/Judgements) with evidence and URNs; Bible, Changes, Actions, Ask, and Factory are windows onto the same graph
- Ingestion runs through factory agents (scout → parse → cite → structure → ontology → relations → dedup → reason → translate → publish), usually started via `ingest_document.py`
- The seed scripts (`deployments/dpdpa-backend/scripts/seed_full_knowledge_base.py`, `seed_supabase.py`) are retired and exit without writing: their objects are unverified. The live corpus is published by `src/competitive_intel/build_knowledge_objects.py` and must pass `deployments/dpdpa-backend/src/schemas/corpus_contract.py`; project state lives in `context/STATE.md` and dated checkpoints in `archives/episodic/`; competitor harvest JSONL lives under `staging/harvest/` and is classified with `harvest/classify_pages.py`
- The site (public DPDPA Wiki + founder workspace) lives in `deployments/dpdpa-wiki/`; Command Center is `/workspace/today` on local Vite at `http://127.0.0.1:5173`
- Documentation follows Nate Herk's AIS-OS layout (adopted 2026-11-25): `context/` (state, founding memo, constitution), `decisions/log.md`, `references/` (architecture, runbooks, design; index `references/README.md`), `archives/` (old plans, kept, never deleted), `connections.md`. No notes/misc/tmp folders; add a folder only when something needs it. Private material (thread exports, own drafts awaiting a legal check, market data) goes in gitignored `staging/`
- Apify MCP is connected; competitor crawls use `apify/website-content-crawler` on public pages only (no login, admin, app, or dashboard); skip gotrust.in, perfios.ai, and leegality.com, and crawl GoTrust’s DPDPA product at gotrust.tech
- Never import DPDPA.com or other competitor pages into Setu; keep a separate Competitive Intelligence Corpus as Layer 4–5 opinions, not law
- Two lanes, decided 2026-10-03. **Law lane:** the Act, the Rules and other official sources (notifications, Board orders, regulator directions, judgments), each held in its own words from an official URL and checked by the corpus contract; only this lane feeds Ask, the knowledge store, the search index and the public site. **Market lane:** competitor and market data (sites, products, pricing, accuracy scores, the market-map pack in `staging/competitive_intel/market-map/`); internal, gitignored, read by people and editorial planning only, never stored as knowledge objects, never indexed, never published under a competitor's name
- Classifier trays are LAW/RULES, INTERPRETATION, FAQ, BLOG, TEMPLATE, CASE LAW, TOOL, COURSE, and COMMERCIAL
- Competitor pages default to unpublished; claims must be verified against Act, Rules, Gazette, MeitY, DPB, or courts before canonical use
- DPDPA.com case-law lists are JavaScript-rendered; use Playwright with a content wait, not an HTTP-only crawl; their DPDPA Board-order groups are still empty / “coming soon”
- This project was originally built in Antigravity and is now continued in Cursor
- The backend lives only in `deployments/dpdpa-backend/`. The old copy at the repo root (`src/api`, `src/reasoning`, `src/storage`, `src/factory`, `src/schemas`, `src/tests`) was removed on 2026-10-02; root `src/` now holds only `competitive_intel/`
