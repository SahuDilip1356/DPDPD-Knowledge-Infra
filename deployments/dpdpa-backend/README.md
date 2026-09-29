# DPDPA Compliance API Gateway (dpdpa-backend)

This repository contains the FastAPI API gateway and administrative ingestion pipelines supporting the **DPDPA Knowledge Infrastructure**.

## 🛠️ Main Components
- **FastAPI API Gateway (`src/api/api_service.py`):** Serves grounded Q&A intelligence searches, health endpoints, and action logging.
- **Administrative Ingestion Pipeline (currently in the repository root):** Parses reviewed source documents and populates the knowledge stores. It is scheduled to move into this deployable during final repository consolidation.
- **Supabase BaaS Model (`supabase_schema.sql`):** Bitemporal database schema structure for legal nodes, regulatory audit logs, and search metrics.

---

## ⚡ Deployment Options

### Option A: Google Cloud Run (Recommended)
You can build and deploy the containerized application using the included `Dockerfile`:
```bash
# Build and submit container image
gcloud builds submit --tag gcr.io/your-project-id/dpdpa-backend

# Deploy to Cloud Run
gcloud run deploy dpdpa-backend \
  --image gcr.io/your-project-id/dpdpa-backend \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="SUPABASE_URL=...,SUPABASE_SERVICE_KEY=...,GEMINI_API_KEY=...,PINECONE_API_KEY=...,PINECONE_INDEX_NAME=..."
```

### Option B: Render or Railway
1. Push this folder to a GitHub repository.
2. Select **Web Service** on Render / Railway.
3. Configure the start command as:
   ```bash
   uvicorn src.api.api_service:app --host 0.0.0.0 --port 8000
   ```
4. Bind the required Environment Variables.

---

## 🔒 Required Environment Variables
- `DATABASE_URL`: Connection string to your Supabase PostgreSQL database.
- `GEMINI_API_KEY`: API key for Gemini models (used in the Ingestion Pipeline & Grounded Q&A).
- `OPENAI_API_KEY` (Optional): API key for fallback OpenAI models.
- `PINECONE_API_KEY`: Pinecone Vector Database credentials.
- `PINECONE_INDEX_NAME`: Name of your vector index.
- `ADMIN_API_KEY`: Transitional, server-only key protecting every `/admin/*` route. Generate 32+ random characters and never use a `VITE_` prefix.
- `APP_ENV`: Set to `production` in Railway so readiness fails closed when no model provider is configured.
- `ALLOWED_ORIGINS`: Comma-separated browser origin allowlist.
- `QUERY_RATE_LIMIT_PER_MINUTE` / `QUERY_RATE_LIMIT_PER_DAY`: Public reasoning limits.
- `SUBSCRIBER_WEBHOOK_URL` (Optional): Target URL to push real-time regulatory change webhooks.

Copy `.env.example` for the complete configuration manifest. API credentials are ordinary provider API keys; a developer's ChatGPT/Codex OAuth session is not available to this service.

---

## 💾 BaaS setup (Supabase Schema Initialization)
To initialize the Supabase database instance:
1. Log into your Supabase Console.
2. Open the **SQL Editor** tab.
3. Paste the contents of `supabase_schema.sql` and click **Run**.
4. Set up storage buckets by running:
   ```bash
   python3 scripts/setup_document_storage.py
   ```
   *(Copy the output RLS policies into Supabase SQL Editor).*
