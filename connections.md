# Connections

Every outside system this project reaches. Names only: the values live in `.env` files
(gitignored) and in each platform's secret store. Variable names and rotation steps are in
[references/runbooks/SECRETS.md](references/runbooks/SECRETS.md).

| System | What it does here | Used by | Settings |
|---|---|---|---|
| Supabase (Postgres) | Knowledge store: objects, versions, evidence, graph edges | backend, `src/competitive_intel/build_knowledge_objects.py` | `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (optional `DATABASE_URL`); site uses `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` |
| Pinecone | Search index `dpdpa-knowledge` | backend, builder | `PINECONE_API_KEY`, `PINECONE_INDEX_NAME` |
| Vercel | Hosts dpdpa.wiki from `deployments/dpdpa-wiki/`, with a preview per PR | site | project settings on Vercel |
| Railway | Hosts the FastAPI backend from `deployments/dpdpa-backend/` | backend | `ADMIN_API_KEY` and the keys above, set on Railway |
| GPT-OSS, Gemini, OpenAI, OpenRouter | The model that reads retrieved law, first configured wins: GPT-OSS (any OpenAI-compatible endpoint, local Ollama by default), then Gemini, then OpenAI, then OpenRouter. Embeddings never use GPT-OSS | backend, `evals/runner.py --live` | `REASONING_PROVIDER`, `GPT_OSS_BASE_URL`, `GPT_OSS_MODEL`, `GPT_OSS_API_KEY`, `GEMINI_API_KEY` (or `GOOGLE_API_KEY`), `OPENAI_API_KEY`, `OPENROUTER_API_KEY` |
| Apify | Public-page crawls for the market lane (`apify/website-content-crawler`) | `harvest/`, `src/competitive_intel/` | Apify account token, local only |
| GitHub | Repo, pull requests, CI (`spec-chain.yml`, `release-gate.yml`) | everyone | repo settings and Actions secrets |

Official law sources (Gazette, MeitY, the Board, courts) are fetched by
`src/competitive_intel/official_sources.py` from the allowlist in `sources/official.yaml`; they
need no credentials.

Writes to the live store (`conform`, `quarantine`, `official`) are run by Dilip.
