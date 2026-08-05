# DPDPA Knowledge Infra Frontend (dpdpa.wiki)

This repository contains the enterprise compliance knowledge management dashboard for the **Digital Personal Data Protection Act (DPDPA), 2023**.

It includes the following views:
- **📅 Today (Command Center):** Interactive regulatory compliance overview.
- **📊 Architecture Visual:** Dynamic blueprint representing data flow.
- **🔄 Changes Feed:** Tracking legal modifications & notifications.
- **📚 Knowledge Explorer:** Graph visualization of legal URNs.
- **💼 Decisions & Actions:** Operational checklist guardrails.
- **🏗️ Research Factory:** Administrative ingestion staging board.
- **🧠 Ask Grounded Q&A:** Grounded search querying MeitY circulars and statutory layers.
- **🛡️ Admin Audit Log:** Live analytics and search logs dashboard.

---

## ⚡ Vercel Deployment Guide

1. **Import Project:** Select the `dpdpa-wiki` directory on Vercel.
2. **Framework Preset:** Choose **Vite** (or Other/Create React App).
3. **Build & Development Settings:**
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. **Environment Variables:**
   - `VITE_SUPABASE_URL`: Your Supabase Project URL.
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anonymous client key.
   - `VITE_API_URL`: URL of your hosted FastAPI backend server (e.g. on Cloud Run / Render).
   - `VITE_SHIKSHA_URL`: Domain of the certification frontend (`https://dpdpa.shiksha`).

---

## 🛠️ Local Development

```bash
npm install
npm run dev
```
Access the application at `http://localhost:5173`.
