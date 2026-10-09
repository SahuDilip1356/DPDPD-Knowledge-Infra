# Milestone 1 Baseline and Verification Record

**Captured:** 2026-09-08

**Branch:** `main`

**Starting commit:** `a3dab16`

## Preservation boundary

The repository already contained modified and untracked work in `.agent/`, the
root `src/` reasoning/API/tests, `EVAL_SPEC.md`, `HARDENING_SPEC.md`, and `evals/`.
That work was treated as user-owned. The root `src/` tree remains temporarily so
the uncommitted eval-promotion implementation is not destroyed during the first
canonicalization pass.

The deployable source of truth is now `deployments/dpdpa-backend/`. Both backend
Dockerfiles resolve to that source.

## Pre-change gates

| Gate | Result |
|---|---|
| Root backend tests | 88 passed, 10 warnings, 7.81 s |
| Deploy backend tests | 82 passed, 10 warnings, 5.97 s |
| Frontend lint | Exit 0 with 12 warnings |
| Frontend production build | Previously succeeded only with blank public service configuration; client build was slow |

## Post-hardening gates

| Gate | Result |
|---|---|
| Canonical deploy backend tests | 94 passed, 10 dependency/runtime warnings, 0.80 s |
| Preserved root tests | 88 passed, 10 dependency/runtime warnings, 0.89 s |
| Frontend lint | Zero warnings/errors |
| Frontend production build and prerender | Clean exit; 3/3 routes generated; 519.42 kB main chunk |
| Script parsing/import path | All five moved scripts parse; ingestion CLI help loads canonical `src` |
| Source scan | No component-local `localhost:8000`; only central development default remains |
| Security checks | Admin 503 when unconfigured, 401 for wrong/missing key, 200 for correct key; query limits return 422/429 |
| Docker Compose | `docker compose config --quiet` passes |

## Known non-blocking baseline warnings

- Local Python 3.9 triggers dependency deprecation warnings; production should
  move to a currently supported Python version in a separately reviewed change.
- Frontend client output is approximately 594 kB before gzip and triggers Vite's
  chunk-size advisory. Route-level code splitting is scheduled after hardening.
- Root `src/` removal is deferred until the eval-promotion work is redesigned or
  safely relocated; it is not referenced by the deployment images.
