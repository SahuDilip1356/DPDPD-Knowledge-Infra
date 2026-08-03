# DPDPA Compliance API Gateway (dpdpa-backend)

This repository contains the FastAPI API gateway and administrative ingestion pipelines supporting the **DPDPA Knowledge Infrastructure**.

## 🛠️ Main Components
- **FastAPI API Gateway (`src/api/api_service.py`):** Serves grounded Q&A intelligence searches, health endpoints, and action logging.
- **Administrative Ingestion Pipeline (`ingest_document.py`):** Automatically polls/scrapes MeitY circulars, parses layout-aware structures, and populates Pinecone vector databases and Supabase PostgreSQL tables.
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
- `SUBSCRIBER_WEBHOOK_URL` (Optional): Target URL to push real-time regulatory change webhooks.

---

## 💾 BaaS setup (Supabase Schema Initialization)
To initialize the Supabase database instance:
1. Log into your Supabase Console.
2. Open the **SQL Editor** tab.
3. Paste the contents of `supabase_schema.sql` and click **Run**.
4. Set up storage buckets by running:
   ```bash
   python3 setup_document_storage.py
   ```
   *(Copy the output RLS policies into Supabase SQL Editor).*
