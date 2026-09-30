# Decisions

> CANDIDATE = auto-extracted (unverified). A human flips to active.

## 2026-08-04 — CANDIDATE (auto-extracted · session 90c6538c)
- close all rows with the same URN where `version < current` and `system_time_end IS NULL` — rather than guessing at `version - 1`.
- — where does `/knowledge/query` run? This is the only thing blocking Vercel:
