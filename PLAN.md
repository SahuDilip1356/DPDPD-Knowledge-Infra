# DPDPA Platform — Comprehensive Plan

_Last updated: 2026-08-20_

Legend: 🟦 you (browser/account) · ⬜ me (code) · 🟨 decision needed

---

## Where we actually are

**Live in production**

| Surface | State |
| :--- | :--- |
| https://dpdpa.wiki | ✅ Live on Vercel |
| https://dpdpa.shiksha | ✅ Live on Vercel |
| Supabase (`DPDPA-Knowledge-Infra`) | ✅ Healthy · 50 objects, 49 active |
| Pinecone `dpdpa-knowledge` | ✅ 49 vectors, 1536-dim, cosine |
| GitHub — 2 repos | ✅ Both pushed and in sync |

**Working but not hosted**

- RAG pipeline — verified end to end locally: semantic retrieval → Supabase → OpenAI → cited answer.
  No host, so **Ask Intelligence does not work on the live site**.

**Built, not yet committed**

- Public homepage for dpdpa.wiki (9 sections, 2 conversion paths)
- `subscribers` table in Supabase, RLS-protected
- A `CommandCenter.jsx` rewrite from another tool — **unreviewed**

---

## The critical problem

The whole acquisition strategy is organic search on high-intent legal questions.
**The site ships 45 bytes of HTML body.** Everything is injected by JavaScript.

```
Is the FAQ text in the served HTML?   ABSENT
Body content:                          45 bytes
```

Google renders JS on a delayed second pass. Bing, AI answer engines, and social
unfurlers largely do not. A Vite SPA is the wrong vehicle for an SEO-first
content site, and no amount of copy fixes it.

**This is the single highest-leverage item on the list.** Everything else is
plumbing; this determines whether the content strategy works at all.

---

# Phase 1 — Make it real (this week)

### 1.1 Review the homepage 🟦 ⚠️ blocking
Run `npm run dev` in `deployments/dpdpa-wiki`, open `/`.
Nobody has seen it render — I verified build output, routes, SEO tags and the
database, not pixels. Check the hero, the assessment interaction, mobile width.

### 1.2 Decide on the CommandCenter rewrite 🟨
130 uncommitted lines from another tool — an "Editorial Statute-Book" hero with
a monospace gazette watermark. Not mine, not reviewed, not live. Keep or revert.

### 1.3 Commit and deploy ⬜
Homepage, routing split, `?q=` wiring, SEO metadata. Vercel auto-deploys on push.

### 1.4 Prerender the public routes ⬜
Add build-time static generation for `/` so real HTML ships. The workspace stays
a SPA. This is contained — no framework migration.
**Exit test:** `curl https://dpdpa.wiki/ | grep "Who does the DPDP Act apply to"` returns the text.

---

# Phase 2 — Turn the engine on (this week)

### 2.1 Deploy the backend to Railway 🟦
Per [DEPLOY.md](DEPLOY.md) Phase 1. Root directory `deployments/dpdpa-backend`,
six variables, generate a domain, confirm `/health` returns 200.

### 2.2 Wire the API into the frontends ⬜
Add `VITE_API_URL` to both Vercel projects, redeploy.
**Exit test:** Ask Intelligence returns a cited answer on the live site, and the
top bar reads "Live API Online" rather than "Sandbox Mode".

### 2.3 Confirm the checklist actually sends 🟦🟨
The form writes to `subscribers` — nothing emails anyone yet. Decide the
mechanism: a Supabase webhook, Resend, or manual export while volume is low.
**Shipping a "Send me the checklist" button that sends nothing is worse than
not having the button.**

---

# Phase 3 — Earn the traffic (2–4 weeks)

The homepage alone will not rank. Search intent for DPDPA is long-tail and
specific — "dpdp act penalty", "consent notice requirements india",
"significant data fiduciary criteria".

### 3.1 Article surface ⬜🟨
Build `/guide/:slug` as prerendered pages, one per high-intent question. The
knowledge graph already holds the substance; this is a rendering surface over
data you have, not new research.

### 3.2 Internal linking ⬜
Every article links to its sections, related obligations, and the relevant
conversion module — checklist on implementation pages, templates on operational
pages, consultation on readiness and breach pages.

### 3.3 Technical SEO ⬜
`sitemap.xml`, `robots.txt`, per-page canonicals and OG tags, `Article` and
`LegalService` structured data.

### 3.4 Freshness ⬜
The changes feed already tracks amendments. Surface "last reviewed" and
"version history" on every legal page — this is the trust signal the brief
calls for, and you have the bi-temporal data to back it honestly.

---

# Phase 4 — Product debt (ongoing)

| Item | Why it matters |
| :--- | :--- |
| 680 inline `style={{}}` blocks | Bypass the token system; screens drift |
| Cross-domain sessions | wiki and shiksha are different eTLD+1 — sign-in doesn't carry. Blocks learner accounts holding credential state |
| Shared files forked across repos | `SaralPrivacyLogo`, `AuthModal`, `supabaseClient`, stylesheets exist twice. Every change must be made twice |
| No custom 404 | Unknown paths currently redirect to `/` |
| iCloud sync artifacts | Keeps generating duplicate " 2" files in the repo |

---

## Decisions I need from you

1. **CommandCenter rewrite** — keep or revert?
2. **Prerender** — go ahead? (I recommend yes, before any content work)
3. **Checklist delivery** — what actually sends the email?
4. **Article surface** — is `/guide/:slug` the right shape, and which 5 questions first?

## What I cannot do

Vercel, Railway, Hostinger and Supabase dashboards are your accounts. I hold no
keys. And I cannot see rendered pixels — visual sign-off is yours, which is also
your own standing rule: nothing reaches production unverified on preview.

---

## Recommended order

```
1.1 review  →  1.2 decide  →  1.3 commit  →  1.4 prerender
                                   ↓
2.1 Railway →  2.2 wire API  →  2.3 email delivery
                                   ↓
3.x content and technical SEO
```

Phase 1 and 2 are days. Phase 3 is where the traffic actually comes from, and
it is the longest. Phase 4 can run alongside.
