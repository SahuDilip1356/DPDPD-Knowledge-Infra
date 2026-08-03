# Secrets & Configuration Runbook

**This file contains NO real keys — only names, sources and instructions.**
Real values live in `.env` files on your machine (gitignored) and in the Vercel
dashboard. Never paste a real key into this file, into any `.md`, or into chat.

Last reviewed: 2026-08-02

---

## 1. Status — what you already have

| Variable | Status | Where it is now |
| :--- | :--- | :--- |
| `SUPABASE_URL` | ✅ **Have it** | root `.env` |
| `SUPABASE_SERVICE_KEY` | ✅ **Have it** | root `.env` |
| `VITE_SUPABASE_URL` | ✅ **Have it** | both app `.env` files |
| `VITE_SUPABASE_ANON_KEY` | ✅ **Have it** | both app `.env` files |
| `OPENAI_API_KEY` | ✅ **Have it** | root `.env` (moved from your shell) |
| `VITE_API_URL` | ✅ Set for local dev | both app `.env` files |
| `VITE_WIKI_URL` / `VITE_SHIKSHA_URL` | ✅ Set for local dev | both app `.env` files |
| **`PINECONE_API_KEY`** | ❌ **YOU NEED TO GET THIS** | — |
| **`PINECONE_INDEX_NAME`** | ⚠️ Placeholder set (`dpdpa-knowledge`) | needs the index actually created |
| `OPENROUTER_API_KEY` | ➖ Optional fallback | blank slot ready in root `.env` |
| `GEMINI_API_KEY` | ➖ Optional | not needed — OpenAI covers it |
| `DATABASE_URL` | ➖ Optional | blank; Supabase client used instead |

### LLM provider chain

The system tries providers in this order and uses the first one with a key:

**`GEMINI_API_KEY` → `OPENAI_API_KEY` → `OPENROUTER_API_KEY`**

You currently have OpenAI, so that is what runs. To use OpenRouter as a genuine
fallback, paste a key into `OPENROUTER_API_KEY` in the root `.env`; it activates
automatically if the OpenAI key is ever removed or fails to load.

> **Why OpenRouter is safe as a fallback:** it serves
> `openai/text-embedding-3-small`, which produces **1536-dimensional** vectors —
> identical to direct OpenAI. Your Pinecone index works with either provider, so
> falling back never requires rebuilding the index.
>
> Gemini is different: `text-embedding-004` produces **768** dimensions. Switching
> to Gemini *would* force a full re-index. That is the real reason to prefer
> OpenRouter over Gemini as your fallback.

To get an OpenRouter key: **https://openrouter.ai/keys** → *Create Key* → copy →
paste into `OPENROUTER_API_KEY=` in the root `.env`.

Optional `CHAT_MODEL` / `EMBED_MODEL` overrides exist if you ever want to pin a
different model. Leave them blank to use sensible defaults.

**Bottom line: you only need to fetch ONE new thing — the Pinecone key — plus
create the Pinecone index.** Everything else is already in place.

---

## 2. The one rule that matters

**Anything named `VITE_...` becomes PUBLIC.** Vite compiles those values into the
JavaScript that ships to every visitor's browser. Anyone can press F12 and read them.

- `VITE_SUPABASE_ANON_KEY` — safe to be public. Row Level Security is enabled on all
  five tables, so this key can only do what your policies allow.
- `SUPABASE_SERVICE_KEY` — **bypasses Row Level Security completely.** Full read/write
  on your entire database. If this ever reaches a browser, assume total compromise.

> **Never put a service key, Pinecone key or LLM key behind a `VITE_` name.**

---

## 3. How to get the Pinecone key — step by step

You need two things from Pinecone: an **API key** and an **index**.

### 3a. Create the API key

1. Open **https://app.pinecone.io** in your browser
2. Sign up (free tier is enough to start) or sign in
3. In the left sidebar, click **API Keys**
4. Click **Create API key**
5. Give it a name — e.g. `dpdpa-knowledge-infra`
6. Click **Create**, then **Copy** the key
   - ⚠️ It is shown **once**. Copy it now.
7. Paste it into the root `.env` file on the line `PINECONE_API_KEY=`
   (see section 5 for how to open that file)

### 3b. Create the index

1. Still in Pinecone, click **Indexes** in the left sidebar
2. Click **Create index**
3. Fill in exactly:

   | Field | Value | Why |
   | :--- | :--- | :--- |
   | **Name** | `dpdpa-knowledge` | must match `PINECONE_INDEX_NAME` |
   | **Dimension** | **`1536`** | matches OpenAI `text-embedding-3-small` |
   | **Metric** | `cosine` | standard for text similarity |
   | **Type** | Serverless | cheapest; scales to zero |

4. Click **Create index** and wait until status shows **Ready**

> ⚠️ **Dimension is permanent.** 1536 is correct because you are using OpenAI.
> If you ever switch to Gemini embeddings (768 dimensions), you must delete this
> index and build a new one. Decide the provider before indexing.

### 3c. Load your knowledge into the index

Once the key and index exist, tell me and I will run the indexing script. It reads
your 45 Knowledge Objects from Supabase, converts each to a vector via OpenAI, and
uploads them to Pinecone. Until this runs, the index is empty and search falls back
to keyword matching.

---

## 4. Optional — where the other keys come from

Only needed if you want to change providers. **You do not need these today.**

| Key | Where to get it |
| :--- | :--- |
| `GEMINI_API_KEY` | https://aistudio.google.com/apikey → **Create API key** |
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys → **Create new secret key** |
| `SUPABASE_SERVICE_KEY` | Supabase dashboard → your project → **Project Settings → API** → under *Project API keys*, reveal the **`service_role` / secret** key |
| `DATABASE_URL` | Supabase dashboard → **Project Settings → Database** → *Connection string* → URI |

---

## 5. How to open the files

**In VS Code** — the files are in your project. Press `Cmd+P` and type the filename:

- `.env` — root, server-side secrets
- `deployments/dpdpa-wiki/.env` — wiki public config
- `deployments/dpdpa-shiksha/.env` — shiksha public config

> If `.env` does not appear in the VS Code sidebar, that is normal — hidden files
> starting with `.` are often filtered. `Cmd+P` finds them anyway.

**In Finder** — press `Cmd+Shift+.` (period) to toggle hidden files on and off.

---

## 6. What goes into Vercel when you deploy

Vercel does **not** read your local `.env` files. You paste values into its dashboard:
**Project → Settings → Environment Variables**.

### Project: `dpdpa-wiki`

| Variable | Value | Notes |
| :--- | :--- | :--- |
| `VITE_SUPABASE_URL` | copy from root `.env` | public |
| `VITE_SUPABASE_ANON_KEY` | copy from app `.env` | public |
| `VITE_API_URL` | your deployed API URL | public |
| `VITE_SHIKSHA_URL` | `https://dpdpa.shiksha` | public — **not** localhost |
| `SUPABASE_SERVICE_KEY` | copy from root `.env` | 🔒 mark **Sensitive** |
| `PINECONE_API_KEY` | from step 3a | 🔒 mark **Sensitive** |
| `PINECONE_INDEX_NAME` | `dpdpa-knowledge` | |
| `OPENAI_API_KEY` | copy from root `.env` | 🔒 mark **Sensitive** |

### Project: `dpdpa-shiksha`

| Variable | Value | Notes |
| :--- | :--- | :--- |
| `VITE_SUPABASE_URL` | copy from root `.env` | public |
| `VITE_SUPABASE_ANON_KEY` | copy from app `.env` | public |
| `VITE_API_URL` | your deployed API URL | public |
| `VITE_WIKI_URL` | `https://dpdpa.wiki` | public — **not** localhost |

> The course app never touches Pinecone, the LLM, or the service key.
> Do not add them there — every extra copy of a secret is another place it can leak.

**Remember to change the two URL values from `localhost` to the real domains.**
Local `.env` uses localhost for testing; Vercel must use the live domains.

---

## 7. If a key leaks — rotate it

Rotating means: create a new key, update everywhere, then delete the old one.

| Key | How to rotate |
| :--- | :--- |
| `PINECONE_API_KEY` | Pinecone → API Keys → create new → update `.env` + Vercel → delete old |
| `OPENAI_API_KEY` | platform.openai.com → API keys → create new → update → revoke old |
| `SUPABASE_SERVICE_KEY` | Supabase → Project Settings → API → **Roll** the service key ⚠️ breaks all running services until updated everywhere |
| `VITE_SUPABASE_ANON_KEY` | Rarely needed — it is public by design and guarded by RLS |

**After rotating, redeploy both Vercel projects** so the new values are picked up.

---

## 8. Never put secrets in

- Git — `.gitignore` now blocks `.env`, `.env.local`, `.env.backup-*` and every
  other variant, while still tracking `.env.example`
- `memory/`, `CLAUDE.md`, `.agent/` — your own standing rule
- Any `.md` file, including this one
- Chat messages, screenshots, or issue trackers
