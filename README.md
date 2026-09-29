# DPDPA Privacy Knowledge Infrastructure

An enterprise compliance knowledge management system for the **Digital Personal Data Protection Act (DPDPA), 2023**. Built with a bitemporal graph database model, automated layout-aware LLM vision ingestion, Outbound Webhook alerts, and a grounded Reasoning Assistant.

The canonical runtime backend is `deployments/dpdpa-backend/`. The root Dockerfile
is a compatibility entry point that builds that directory. The older root `src/`
tree is retained temporarily only to preserve uncommitted evaluation work and must
not be used for deployment.

---

## 🏗️ System Architecture

```
                               ┌────────────────────────┐
                               │     Vite React UI      │ (Port 5173)
                               └───────────┬────────────┘
                                           │ API Requests
                               ┌───────────▼────────────┐
                               │  FastAPI Gateway API   │ (Port 8000)
                               └─────┬────────────┬─────┘
                                     │            │
             ┌───────────────────────▼┐          ┌▼───────────────────────┐
             │   Supabase Postgres    │          │  Pinecone Vector DB    │
             │  (Bitemporal Schema)   │          │ (Grounded Embeddings)  │
             └────────────────────────┘          └────────────────────────┘
```

---

## ⚡ Quick Start

### 1. Configure Environment Variables (`.env`)
Create a `.env` file in the root directory:
```bash
# Server & API Keys
DATABASE_URL="postgresql://postgres:[password]@db.[reference].supabase.co:5432/postgres"
GEMINI_API_KEY="your-gemini-api-key"
OPENAI_API_KEY="your-openai-api-key"
PINECONE_API_KEY="your-pinecone-api-key"
PINECONE_INDEX_NAME="dpdpa-knowledge"
ADMIN_API_KEY="generate-a-32-plus-character-random-value"
APP_ENV="development"

# Webhooks & Auth
SUBSCRIBER_WEBHOOK_URL="https://your-domain.com/webhook"
VITE_SUPABASE_URL="https://[reference].supabase.co"
VITE_SUPABASE_ANON_KEY="your-anon-key"
```

### 2. Run Locally (Developer Mode)

#### Start Python Backend Service
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r deployments/dpdpa-backend/requirements.txt
cd deployments/dpdpa-backend
uvicorn src.api.api_service:app --port 8000 --reload
```
The API Swagger documentation will be available at: **`http://localhost:8000/docs`**

#### Start React Client Dashboard
```bash
cd deployments/dpdpa-wiki
npm install
npm run dev
```
Access the dashboard UI at: **`http://localhost:5173`**

---

## 🐳 3. Start Containerized Deployment (Docker Compose)
To run both backend and frontend services in production-ready containerized environments, launch:
```bash
docker compose up --build
```
*   **Frontend Client:** Maps Nginx static assets to port `5173`.
*   **Backend API Gateway:** Maps Uvicorn to port `8000`.

---

## 🤖 4. Administrative Ingestion Pipeline

### Set Up Document Storage Bucket
Before running the crawler, set up the public PDF hosting storage bucket and database security policies:
```bash
cd deployments/dpdpa-backend
python3 scripts/setup_document_storage.py
```
*(Copy the generated SQL policies and run them in the Supabase SQL Editor).*

### Run automated Document Ingestion CLI
To scrape MeitY's site and ingest the latest rules automatically:
```bash
# Poll MeitY for privacy circulars
python3 scripts/ingest_document.py --poll

# Load a specific document URN from a URL
python3 scripts/ingest_document.py "https://egazette.gov.in/notif.pdf" --urn "urn:ki:in:dpdp:rule:new-notification" --layer 1
```

---

## 🛡️ 5. Administrative Audit & Security Panel

### Current guardrail boundary

The backend protects every `/admin/*` endpoint with the transitional
`X-Admin-Key` control. The actions and factory screens still require the role-based,
server-enforced workflow described in `COMPREHENSIVE_BUILD_SPEC.md`; their current
client-side login state is not an authorization boundary.

### Accessing the Admin Audit Panel (`/admin`)
1. Generate an admin key, store it in `ADMIN_API_KEY` for the backend, and restart the service.
2. Open `http://localhost:5173/admin`.
3. Enter the same key in the admin authorization form. It is retained only in the browser tab's `sessionStorage`.
4. The dashboard then loads:
   - **Live Search Logs:** Real-time log table of user searches submitted to the Grounded Assistant.
   - **Layer Statistics Chart:** Percentage distribution of Primary Core vs Expert Advisories.
