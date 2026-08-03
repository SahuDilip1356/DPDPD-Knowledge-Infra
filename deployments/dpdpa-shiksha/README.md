# DPDPA Certification Course (dpdpa.shiksha)

This repository contains the interactive training, baseline diagnostic, and capability assessment system for the **Digital Personal Data Protection Act (DPDPA), 2023**.

It includes the following features:
- **🎯 Candidate Profile & Personalization:** Adapts scenarios to selected industry & work role.
- **📋 5-Question Adaptive Diagnostic:** Determines baseline compliance maturity score.
- **🎓 12 Interactive Curriculum Cards:** Checklists and themed syllabus workouts.
- **🕹️ Live Game/Simulations:** Hotspot hunting, consent noticing, and breach timeline containment.
- **🎓 Final Examination:** 10 dynamic, role-adaptive questions.
- **📜 Verified Digital Credentials:** Generates printable certificates and 30-day implementation action plans.

---

## ⚡ Vercel Deployment Guide

1. **Import Project:** Select the `dpdpa-shiksha` directory on Vercel.
2. **Framework Preset:** Choose **Vite**.
3. **Build & Development Settings:**
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. **Environment Variables:**
   - `VITE_SUPABASE_URL`: Your Supabase Project URL.
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anonymous client key.
   - `VITE_API_URL`: URL of your hosted FastAPI backend server (e.g. on Cloud Run / Render).
   - `VITE_WIKI_URL`: Domain of the Knowledge Infra frontend (`https://dpdpa.wiki`).

---

## 🛠️ Local Development

```bash
npm install
npm run dev
```
Access the course application at `http://localhost:5173`.
