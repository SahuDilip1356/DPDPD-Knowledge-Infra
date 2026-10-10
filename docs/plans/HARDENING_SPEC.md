# Hardening Spec — pre-Railway

Derived from an audit of this repo against the "Vibe Coding to Production"
playbook. Four items. All land **before** the backend reaches Railway, so the
preview-before-prod rule holds without a special case.

Status: implementation in progress as of 2026-09-08.

Items 2–4 are implemented in the canonical deploy backend/frontend. Item 1 now
routes both Docker entry points to `deployments/dpdpa-backend/` and the five
operational scripts have moved there. The older root `src/` tree is temporarily
retained so pre-existing uncommitted eval-promotion work is not destroyed; it is
not used by either deployment image. The initial rate limiter is a dependency-free,
process-local sliding window with minute/day limits rather than SlowAPI. A shared
external limiter remains necessary before horizontally scaling the API.

---

## Corrections to the earlier audit summary

Two things I reported were wrong or incomplete. Both change the work.

**1. "Delete root `src/` — 26 files" was incomplete.** Five root-level scripts
import `from src.…` and none of them exist in the backend deployable:

    ingest_document.py  run_mock_ingestion.py  seed_full_knowledge_base.py
    seed_supabase.py    setup_document_storage.py

A bare deletion breaks the ingestion pipeline that populates the knowledge
base. The work is a **consolidation**, not a deletion.

**2. There is a fourth finding, and it is live in production.** See Item 4.
It is the only one of the four currently affecting a real page.

---

## Item 1 — Consolidate the duplicate backend tree

### Finding

Two copies of `src/` exist with identical file sets (26 files each) and
divergent contents (196 changed lines across three files). The root copy is
pre-fix:

| Fix | `deployments/dpdpa-backend/src/` | root `src/` |
|---|---|---|
| Blank-env-var bug (broke all 50 embeddings) | fixed | **present** |
| `cfg()` env helper | yes | no |
| OpenRouter fallback | yes | no |
| Bi-temporal `superseded_at_birth` | yes | no |

Root `Dockerfile:26` runs `src.api.api_service:app` against the stale copy. If
Railway's root directory lands on the repo root, that is what deploys. Vercel
reset exactly this setting on us twice.

`docker-compose.yml` is already dead — it builds `./frontend`, a directory that
no longer exists.

### Decision

`deployments/dpdpa-backend/` becomes the single source of truth for the backend.
The repo root keeps no Python.

### Changes

Move (git mv, preserving history) into `deployments/dpdpa-backend/`:

    ingest_document.py  run_mock_ingestion.py  seed_full_knowledge_base.py
    seed_supabase.py    setup_document_storage.py

Delete:

    src/                 (26 files — the stale copy)
    Dockerfile           (deploys the stale copy)
    requirements.txt     (byte-identical to the backend's)
    docker-compose.yml   (already broken; references ./frontend)

No import rewrites are needed: the scripts use `from src.…`, which resolves
against the working directory, and that becomes `deployments/dpdpa-backend/`.

### Verification

    cd deployments/dpdpa-backend && python -m pytest src/tests -q
    cd deployments/dpdpa-backend && python -c "import ast,sys;[ast.parse(open(f).read()) for f in ['ingest_document.py','run_mock_ingestion.py','seed_supabase.py']]"
    git ls-files | grep -c '^src/'          # expect 0
    git ls-files | grep -c '^Dockerfile$'   # expect 0

Test suite must pass at the same count as before the move. Record the
before-count first — a passing suite that runs fewer tests is a regression.

### Rollback

Single commit; `git revert`. No deployed surface changes.

---

## Item 2 — Authenticate `/admin/*`

### Finding

Three endpoints, no auth of any kind. Zero `Depends`, `HTTPBearer`, or
`Security()` anywhere in the backend.

    api_service.py:234  @app.get("/admin/search-audit")     → 100 recent user queries
    api_service.py:254  @app.get("/admin/stats")            → database statistics
    api_service.py:300  @app.get("/admin/ingestion-audit")  → pipeline logs

`/admin/search-audit` discloses what users searched for. Not currently exposed
— the backend is not deployed — so this is a fix-before-Railway item, not an
incident.

### Decision

A shared admin key, held in the platform environment and entered once per
browser session by the operator. **Not** a `VITE_` variable — those are inlined
into the public bundle by construction.

Rejected for now: Supabase JWT verification with an email allowlist. It is the
better answer for more than one admin, but it needs the project's JWT signing
scheme pinned down (HS256 shared secret vs. ES256 JWKS) plus a new dependency,
and there is exactly one admin. Revisit when there are two.

### Changes — backend

`deployments/dpdpa-backend/src/api/api_service.py`:

```python
import secrets
from fastapi import Depends, Header

ADMIN_API_KEY = (os.getenv("ADMIN_API_KEY") or "").strip()


def require_admin(x_admin_key: str = Header(default="")) -> None:
    """
    Gate for /admin/*. The key lives in the platform environment and in the
    operator's browser session — never in the client bundle, which is public.

    An unset key denies rather than allows. A missing environment variable on
    a fresh deploy must not silently reopen the audit surface, which is the
    failure mode this whole item exists to close.
    """
    if not ADMIN_API_KEY:
        raise HTTPException(status_code=503, detail="Admin surface not configured.")
    if not secrets.compare_digest(x_admin_key, ADMIN_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing admin key.")
```

Attach to all three routes:

```python
@app.get("/admin/stats", dependencies=[Depends(require_admin)])
```

`compare_digest` rather than `==` so the comparison does not leak length or
prefix through timing.

CORS already sends `allow_headers=["*"]`, so `X-Admin-Key` passes preflight
with no change.

### Changes — frontend

`deployments/dpdpa-wiki/src/components/screens/AdminAudit.jsx`:

- Read the key from `sessionStorage` (`dpdpa_admin_key`). `sessionStorage`, not
  `localStorage`: the key should not outlive the tab.
- With no key stored, render a key-entry form in place of the dashboard.
- Send `X-Admin-Key` on all three requests.
- On 401, clear the stored key and return to the entry form.
- **Delete the mock-data fallback.** See Item 4 — it is the live bug.

### Secrets

Add to `SECRETS.md` and `.env.example` as a documented name with no value:

    ADMIN_API_KEY=          # 32+ random chars; Railway env only, never VITE_

Generate with `openssl rand -base64 32`. It goes in Railway's environment and
nowhere in the repo.

### Verification

    curl -s -o /dev/null -w '%{http_code}\n' $API/admin/stats                        # 401
    curl -s -o /dev/null -w '%{http_code}\n' -H 'X-Admin-Key: wrong' $API/admin/stats # 401
    curl -s -o /dev/null -w '%{http_code}\n' -H "X-Admin-Key: $KEY" $API/admin/stats  # 200

Then unset `ADMIN_API_KEY` in a local run and confirm 503 rather than 200 —
the fail-closed path is the one worth testing, because it is the one that only
matters when something else has already gone wrong.

---

## Item 3 — Rate-limit the LLM endpoint

### Finding

No rate limiting anywhere in the backend. `/knowledge/query` calls the model
provider on every request. Uncapped, a loop against it burns paid credits
directly.

### Decision

`slowapi` (the FastAPI-native wrapper over `limits`), keyed on caller IP, with
a tight limit on `/knowledge/query` and a loose global default.

### Changes

`deployments/dpdpa-backend/requirements.txt`:

    slowapi==0.1.10

`api_service.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


def client_key(request: Request) -> str:
    """
    Railway terminates TLS at its edge, so request.client.host is the proxy and
    every caller would share one bucket. The first hop in X-Forwarded-For is
    the real caller.

    X-Forwarded-For is caller-supplied and therefore spoofable; the platform
    appends rather than replaces. This raises the cost of a naive loop, which
    is what it is for. It is not a defence against a determined attacker, and
    the actual backstop is the spend cap on the provider account.
    """
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else get_remote_address(request)


limiter = Limiter(key_func=client_key, default_limits=["120/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

On the expensive route only:

```python
@app.post("/knowledge/query", response_model=QueryResponse)
@limiter.limit("10/minute")
def query_knowledge(request: Request, ...):
```

`slowapi` requires the endpoint to accept a parameter named exactly `request`
typed `Request`; the decorator raises at import time otherwise, so a mistake
here fails the deploy rather than silently disabling the limit.

### Also do

Set a hard monthly spend cap in the OpenAI and OpenRouter dashboards. The rate
limit bounds one caller; the spend cap bounds the bill. Only the second one is
a guarantee, and it is a dashboard setting, not code.

### Verification

    for i in $(seq 1 12); do
      curl -s -o /dev/null -w '%{http_code} ' -X POST $API/knowledge/query \
        -H 'Content-Type: application/json' -d '{"query":"test"}'
    done; echo

Expect ten `200`s then `429`s.

---

## Item 4 — Hardcoded API URLs, and the fabricated admin data

### Finding

Four `http://localhost:8000` literals ship in the production bundle:

    Bible.jsx:274        → /knowledge/bible
    AdminAudit.jsx:20    → /admin/stats
    AdminAudit.jsx:25    → /admin/search-audit
    AdminAudit.jsx:30    → /admin/ingestion-audit

They fail on every production page load. `Bible.jsx` is the `/knowledge/bible`
404 we traced earlier — the cause was here, not only in the image.

`AdminAudit.jsx` is worse. Its `catch` block substitutes **invented data** and
renders it as real: 45 knowledge objects, five fabricated user search queries,
two fabricated pipeline runs with plausible timestamps and durations. Nothing
on the page marks it as mock. `/admin` on dpdpa.wiki is showing made-up numbers
right now, and has been since it deployed.

This is the only finding of the four with a live effect, and it is the one to
fix first.

### Decision

One shared API base, resolved from `VITE_API_URL`. A failed admin fetch shows
an error, never a fabrication.

### Changes

New `deployments/dpdpa-wiki/src/lib/api.js`:

```javascript
/* Single source for the backend origin. Hardcoding it means production calls
   localhost, which fails silently in a browser and is invisible in a build. */
export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

- `App.jsx`: import from `lib/api` instead of recomputing the constant.
- `Bible.jsx:274`: `fetch(\`${API_BASE_URL}/knowledge/bible\`)`.
- `AdminAudit.jsx`: same for all three, and **delete the mock fallback** — the
  `catch` sets an error state and the component renders it.
- `AskIntelligence.jsx`: keep the prop, default it to `API_BASE_URL`.

Then confirm `VITE_API_URL` is set in the Vercel project. Until Railway is up
it should stay unset, so the calls fail visibly against localhost rather than
against a wrong host.

### Verification

    grep -rn 'localhost:8000' deployments/dpdpa-wiki/src   # only lib/api.js
    npm run build && grep -c 'localhost:8000' dist/assets/*.js

The second count is only meaningful with `VITE_API_URL` set at build time —
unset, the fallback is correct and expected.

Then load `/admin` and confirm it shows an error or a key prompt, and never
a number that came from nowhere.

---

## Order

Item 4 first — it is the only one with a live effect, and it is independent.
Then 1 (mechanical, largest diff, easiest to review alone). Then 2 and 3, which
both touch `api_service.py` and are best reviewed together.

    4 → 1 → 2 + 3

Four commits, so any one reverts alone.

## Gates

**Before merge**

- [ ] Test suite passes from `deployments/dpdpa-backend/`, same count as before
- [ ] `git ls-files` shows no root `src/`, `Dockerfile`, `requirements.txt`, `docker-compose.yml`
- [ ] No `localhost:8000` outside `lib/api.js`
- [ ] No fabricated data path remains in `AdminAudit.jsx`
- [ ] `ADMIN_API_KEY` documented in `SECRETS.md`, value absent from the repo

**On the Railway preview, before production**

- [ ] Railway root directory is `deployments/dpdpa-backend` — confirmed in the dashboard, not assumed
- [ ] `/admin/stats` → 401 without a key, 200 with one, 503 with the variable unset
- [ ] Eleventh `/knowledge/query` in a minute → 429
- [ ] `/health` → 200
- [ ] Spend caps set on OpenAI and OpenRouter

**Not in scope**

Supabase JWT admin auth, renaming `/admin` to an unguessable path (authentication
supersedes it), staging environment separation, and the 680 inline styles.
