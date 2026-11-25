# Deployment Runbook

Follow top to bottom. Each phase depends on the one before it.
**No real keys appear in this file** — it tells you which line of `.env` to copy from.

Legend: 🟦 you, in a browser · ⬜ me, in code

---

## Where your values live

Open `.env` in VS Code: press `Cmd+P`, type `.env`, Enter.
*(Hidden files don't show in the sidebar; `Cmd+P` finds them.)*

| Value | File | Line |
| :--- | :--- | ---: |
| `SUPABASE_URL` | `.env` | 1 |
| `SUPABASE_SERVICE_KEY` | `.env` | 2 |
| `PINECONE_API_KEY` | `.env` | 10 |
| `PINECONE_INDEX_NAME` | `.env` | 14 |
| `OPENAI_API_KEY` | `.env` | 19 |
| `OPENROUTER_API_KEY` | `.env` | 26 |
| `VITE_SUPABASE_URL` | `deployments/dpdpa-wiki/.env` | 1 |
| `VITE_SUPABASE_ANON_KEY` | `deployments/dpdpa-wiki/.env` | 2 |

> `SUPABASE_URL` and `VITE_SUPABASE_URL` hold the same value. The **anon** key
> and the **service** key are different and must never be swapped: every `VITE_`
> value is compiled into the public browser bundle.

---

# PHASE 1 — Backend on Railway 🟦

Everything downstream needs the URL this produces. Do it first.

### 1.1 Create the service
1. Go to **https://railway.app** → **Login with GitHub**
2. **New Project** → **Deploy from GitHub repo**
3. Choose **`DPDPD-Knowledge-Infra`**
4. Railway starts building and **it will fail**. That is expected — fix it in 1.2.

### 1.2 Set the root directory ⚠️ most-missed step
1. Open the service → **Settings** tab
2. Find **Root Directory** → set to:
   ```
   deployments/dpdpa-backend
   ```
3. Save. Without this Railway looks at the repo root, finds no Dockerfile, and fails.

### 1.3 Add the variables
**Variables** tab → **Raw Editor** → paste this block, replacing each
`<paste ...>` with the real value from the table above:

```
SUPABASE_URL=<paste .env line 1>
SUPABASE_SERVICE_KEY=<paste .env line 2>
PINECONE_API_KEY=<paste .env line 10>
PINECONE_INDEX_NAME=dpdpa-knowledge
OPENAI_API_KEY=<paste .env line 19>
OPENROUTER_API_KEY=<paste .env line 26>
ALLOWED_ORIGINS=https://dpdpa.wiki,https://dpdpa.shiksha
```

**Do NOT add `PORT`** — Railway injects it and the Dockerfile reads it.
**Do NOT add `DATABASE_URL`** — blank is correct; the Supabase client is used.

### 1.4 Generate a public URL
**Settings → Networking → Generate Domain**

### 1.5 Verify
Open `https://<your-railway-url>/health` in a browser. Expect:
```json
{"status":"HEALTHY","timestamp":"..."}
```

✅ **Send me that URL.** I wire it into both frontends and push. ⬜

---

# PHASE 2 — Wiki on Vercel 🟦

*Do this after I confirm the API URL is pushed.*

1. **https://vercel.com** → **Add New → Project**
2. Import **`DPDPD-Knowledge-Infra`**
3. Settings:

| Field | Value |
| :--- | :--- |
| Framework Preset | **Vite** |
| **Root Directory** | **`deployments/dpdpa-wiki`** |
| Build Command | `npm run build` |
| Output Directory | `dist` |

4. **Environment Variables** — add these four:

```
VITE_SUPABASE_URL=<paste wiki .env line 1>
VITE_SUPABASE_ANON_KEY=<paste wiki .env line 2>
VITE_API_URL=<your Railway URL from 1.4>
VITE_SHIKSHA_URL=https://dpdpa.shiksha
```

5. **Deploy** → you get a `xxx.vercel.app` preview URL. **Don't add the domain yet.**

---

# PHASE 3 — Shiksha on Vercel 🟦

1. **Add New → Project** → import **`dpdpa-shiksha`**
2. Settings:

| Field | Value |
| :--- | :--- |
| Framework Preset | **Vite** |
| **Root Directory** | **leave empty** ← differs from wiki |
| Build Command | `npm run build` |
| Output Directory | `dist` |

3. **Environment Variables**:

```
VITE_SUPABASE_URL=<same as wiki>
VITE_SUPABASE_ANON_KEY=<same as wiki>
VITE_API_URL=<your Railway URL>
VITE_WIKI_URL=https://dpdpa.wiki
```

> Shiksha needs **no** Pinecone, LLM or service key. Retrieval and generation
> happen in the backend, which only the wiki calls.

4. **Deploy**

---

# PHASE 4 — Verify on preview 🟦 ⚠️ do not skip

Your own standing rule: nothing reaches production unverified.
Open both `.vercel.app` URLs and check:

**Wiki**
- [ ] Today / Command Center renders
- [ ] Knowledge Explorer lists objects (live Supabase data)
- [ ] **Ask Intelligence returns a cited answer** ← proves the whole RAG chain
- [ ] Top bar shows "Live API Online", not "Sandbox Mode"
- [ ] "DPDPA Certification" in the sidebar jumps to the shiksha URL

**Shiksha**
- [ ] Course loads at `/`
- [ ] Left rail shows the module list with a progress bar
- [ ] Clicking a module in the rail switches the content
- [ ] "Knowledge Base ↗" jumps to the wiki URL

Anything broken → tell me, I fix and push, Vercel redeploys automatically. ⬜

---

# PHASE 5 — Point the domains 🟦

*Only after Phase 4 passes.*

1. In each Vercel project: **Settings → Domains → Add**
   - wiki project → `dpdpa.wiki`
   - shiksha project → `dpdpa.shiksha`
2. Vercel shows the exact DNS records needed. **Copy them from Vercel** — don't
   use values from memory or a blog post; they change.
3. In **Hostinger → Domains → DNS Zone**, add those records.
   **Keep Hostinger as your DNS host** — do not switch nameservers. Adding
   records is lower-risk and reversible.
4. Wait for SSL to issue (usually minutes, up to an hour).

### Confirm it's really live
Both domains currently return `server: hcdn` — that's Hostinger's parking page.
When the cutover has worked you will see `server: Vercel` instead.

---

## Cost

| Service | Cost |
| :--- | :--- |
| Vercel | Free (Hobby) for both frontends |
| Railway | **No free tier** — usage-based, ~$5/month minimum |
| Supabase | Free tier |
| Pinecone | Free (Starter) |
| OpenAI | Pay per use — pennies at this volume |

Railway is the only guaranteed monthly cost. Render has a free tier if you'd
rather trade cold starts for $5/month.

---

## If something fails

| Symptom | Cause |
| :--- | :--- |
| Railway build: "no Dockerfile" | Root Directory not set (step 1.2) |
| Railway deploys but healthcheck fails | Check logs; a missing env var raises on import |
| Wiki shows "Sandbox Mode" | `VITE_API_URL` wrong/missing, or `ALLOWED_ORIGINS` doesn't include the domain |
| Ask Intelligence returns nothing | Backend can't reach Pinecone or OpenAI — check those two vars |
| Vercel build fails on shiksha | Root Directory must be **empty**, not `deployments/dpdpa-shiksha` |
| Browser console CORS error | Add the exact origin to `ALLOWED_ORIGINS` in Railway |

Send me the error text and I'll diagnose it.
