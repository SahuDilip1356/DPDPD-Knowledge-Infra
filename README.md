# DPDPA Privacy Knowledge Infrastructure

An enterprise compliance knowledge management system for the **Digital Personal Data Protection Act (DPDPA), 2023**. Built with a bitemporal graph database model, automated layout-aware LLM vision ingestion, Outbound Webhook alerts, and a grounded Reasoning Assistant.

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
pip install -r requirements.txt
uvicorn src.api.api_service:app --port 8000 --reload
```
The API Swagger documentation will be available at: **`http://localhost:8000/docs`**

#### Start React Client Dashboard
```bash
cd frontend
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
python3 setup_document_storage.py
```
*(Copy the generated SQL policies and run them in the Supabase SQL Editor).*

### Run automated Document Ingestion CLI
To scrape MeitY's site and ingest the latest rules automatically:
```bash
# Poll MeitY for privacy circulars
python3 ingest_document.py --poll

# Load a specific document URN from a URL
python3 ingest_document.py --url "https://egazette.gov.in/notif.pdf" --urn "urn:ki:in:dpdp:rule:new-notification" --layer 1
```

---

## 🛡️ 5. Administrative Audit & Security Panel

### Actions Guardrails
The system protects critical compliance states and manual ingestion boards from unauthorized modifications:
- **Checklist States (`/actions`):** Requires admin login to check or toggle regulatory tasks.
- **Ingestion Pipeline (`/factory`):** Requires admin login to approve and advance staging documents.

### Accessing the Admin Audit Panel (`/admin`)
1. Open the browser and visit `http://localhost:5173`.
2. Click **Sign In** (top-right header).
3. **Sandbox Fallback:** If cloud credentials are not loaded, enter **any email and password** (e.g. `admin@dpdpa.gov` / `admin123`) to bypass verification and log in.
4. Once authenticated, a new **Admin Audit** link will appear in the left sidebar. Navigate to it to view:
   - **Live Search Logs:** Real-time log table of user searches submitted to the Grounded Assistant.
   - **Layer Statistics Chart:** Percentage distribution of Primary Core vs Expert Advisories.
