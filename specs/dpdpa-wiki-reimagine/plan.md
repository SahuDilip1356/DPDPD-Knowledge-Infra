# Plan — dpdpa.wiki reimagined

**Status:** in progress — gate 1 signed off 2026-09-28; phase 2 (course, tools, home) built 2026-09-29; preview gate 2 pending
**Spec:** ./spec.md
**Date:** 2026-09-27

## Architecture

```
staging/competitive_intel/ground_truth/{act,rules}_sections.json   (verified law; hashed)
staging/competitive_intel/questions/question_graph.jsonl          (1,779 canonical questions)
        │  scripts/sync-law.mjs  (copies + validates, fails on missing labels)
        ▼
deployments/dpdpa-wiki/src/data/law/{provisions.json, glossary.json}
deployments/dpdpa-wiki/src/content/modules/*.md   (6 modules, front-matter = Module record)
deployments/dpdpa-wiki/src/content/videos.json
        │  src/lib/{law,modules,tools}.js  (loaders + citation guards, run at build)
        ▼
src/components/screens/{Provision,ProvisionIndex,Module,Quiz,DecisionAid,Glossary}.jsx
src/lib/seo.js publicRoutes() → scripts/prerender.mjs → dist/**/index.html + sitemap.xml
vercel.json: 404 for unknown routes; workspace routes behind /workspace/* only
.github/workflows/render-videos.yml → hyperframes render → Vercel Blob
```

All public pages are static output of the existing Vite + SSR + prerender pipeline. No
runtime data fetching on public routes. The workspace keeps working at `/workspace/*`
for the founder but is unlinked and `noindex`.

## Decisions

- Provision text is copied from the verified ground-truth JSON, never hand-edited in
  the wiki; a sync script is the only writer. Rejected: editing law text in JSX.
- Citation guards run at build time and fail the build. Rejected: a lint warning
  (would be ignored).
- Modules are Markdown with front-matter, same as guides. Rejected: a CMS (no host,
  no need).
- Videos are rendered in GitHub Actions and stored in Vercel Blob; the page embeds a
  plain `<video>`. Rejected: the HyperFrames live player (2.2 MB, iframe, no SEO).
- Tests use Vitest (Vite-native). Rejected: Playwright this cycle — the preview gate is
  the founder's manual check; add browser tests when the workspace returns.
- Quiz scores stay in localStorage. Rejected: accounts (NG).

## Tasks

### T1 — Add Vitest and a build-output test harness
- status: done (2026-09-28)
- implements: AC13
- depends_on: none
- files: deployments/dpdpa-wiki/package.json, deployments/dpdpa-wiki/vitest.config.js,
         deployments/dpdpa-wiki/tests/helpers/dist.js, deployments/dpdpa-wiki/tests/smoke.test.js
- risk: tier2
- size: S
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/smoke.test.js
- notes: `tests/helpers/dist.js` exposes `readPage(route)` returning the prerendered
         HTML string from `dist/`. Smoke test asserts `/` has a `<title>`. Add
         `"test": "vitest run"` to scripts.

### T2 — Sync verified law into the wiki as data
- status: done (2026-09-28)
- implements: AC1, AC3
- depends_on: none
- files: deployments/dpdpa-wiki/scripts/sync-law.mjs, deployments/dpdpa-wiki/src/data/law/provisions.json,
         deployments/dpdpa-wiki/tests/law-data.test.js
- risk: tier1
- size: M
- verify: cd deployments/dpdpa-wiki && node scripts/sync-law.mjs && npx vitest run tests/law-data.test.js
- notes: Source files are `staging/competitive_intel/ground_truth/act_sections.json`
         (44 sections + `schedule`) and `rules_sections.json` (23 rules + 7 schedules +
         `commencement`). Emit exactly 75 Provision records (spec Contracts); `note: null`
         for all at this stage; `source.sha256` from the JSON. Test asserts 75 records,
         every `text` non-empty, R1/R2/R17–R21 `in_force_from` = 2025-11-13, R4 =
         2026-11-13, others 2027-05-13, and that S6 text contains "free, specific,
         informed, unconditional and unambiguous".

### T3 — Attach canonical questions to provisions
- status: done (2026-09-28)
- implements: AC1
- depends_on: T2
- files: deployments/dpdpa-wiki/scripts/sync-law.mjs, deployments/dpdpa-wiki/src/data/law/provisions.json,
         deployments/dpdpa-wiki/tests/law-data.test.js
- risk: tier2
- size: S
- verify: cd deployments/dpdpa-wiki && node scripts/sync-law.mjs && npx vitest run tests/law-data.test.js
- notes: Read `staging/competitive_intel/questions/question_graph.jsonl`; for each
         record's `provisions` labels append `{id, question}` to the matching provision,
         top 8 by `demand_sites`. Skip questions whose label isn't one of the 75. Test:
         S6 has ≥ 5 questions.

### T4 — Provision pages, index pages and the Act Schedule
- status: done (2026-09-28)
- implements: AC1, AC3, AC4, AC13
- depends_on: T1, T2
- files: deployments/dpdpa-wiki/src/lib/law.js, deployments/dpdpa-wiki/src/components/screens/Provision.jsx,
         deployments/dpdpa-wiki/src/components/screens/ProvisionIndex.jsx, deployments/dpdpa-wiki/src/App.jsx,
         deployments/dpdpa-wiki/tests/provision-pages.test.js
- risk: tier2
- size: M
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/provision-pages.test.js
- notes: Routes per spec URL scheme. `law.js` exports `listProvisions()`, `getProvision(label)`,
         `provisionRoutes()`. Render gazette text in a `<pre>`-like measure-limited block
         with sub-clauses on their own lines (split on ` (\d+) ` and ` \([a-z]\) `). Badge
         "Applies from {date}" when `in_force_from > build date`. Test: `/act/section-6`
         HTML contains the S6 text; `/rules/rule-7` contains "Applies from 13 May 2027";
         `/act/schedule` lists 7 rows.

### T5 — Register provision routes for prerender + head tags
- status: done (2026-09-28)
- implements: AC13
- depends_on: T4
- files: deployments/dpdpa-wiki/src/lib/seo.js, deployments/dpdpa-wiki/tests/provision-seo.test.js
- risk: tier2
- size: S
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/provision-seo.test.js
- notes: Extend `publicRoutes()` and `headFor()`. Title pattern "Section 6 — Consent |
         DPDPA 2023 | dpdpa.wiki". Emit `Legislation` + `BreadcrumbList` JSON-LD. Test
         asserts title, description, self-canonical and both JSON-LD types on
         `/act/section-6` and `/rules/rule-7`.

### T6 — Citation guard for notes and lessons
- status: done (2026-09-28)
- implements: AC2, AC6
- depends_on: T2
- files: deployments/dpdpa-wiki/src/lib/citations.js, deployments/dpdpa-wiki/scripts/check-citations.mjs,
         deployments/dpdpa-wiki/package.json, deployments/dpdpa-wiki/tests/citations.test.js
- risk: tier1
- size: M
- verify: cd deployments/dpdpa-wiki && npx vitest run tests/citations.test.js
- notes: `extractCitations(text)` → labels from "Section 6(4)", "Rule 7", "First Schedule",
         "the Schedule". `checkCitations(text, allowed)` returns offenders. The script runs
         over every provision `note` and every module lesson and exits 1 with page + label
         on any offender. Wire it as the first step of `npm run build`. Tests cover a
         passing note, a note citing an unknown label, a lesson citing outside its module.

### T7 — Glossary from Section 2 and Rule 2
- status: done (2026-09-28)
- implements: AC19, AC13
- depends_on: T4, T6
- files: deployments/dpdpa-wiki/scripts/sync-law.mjs, deployments/dpdpa-wiki/src/data/law/glossary.json,
         deployments/dpdpa-wiki/src/components/screens/Glossary.jsx, deployments/dpdpa-wiki/src/lib/seo.js,
         deployments/dpdpa-wiki/tests/glossary.test.js
- risk: tier2
- size: M
- verify: cd deployments/dpdpa-wiki && node scripts/sync-law.mjs && npm run build && npx vitest run tests/glossary.test.js
- notes: Parse defined terms with the pattern `\(([a-z]+)\) “([^”]+)” means` from S2 and
         R2 text; entry = {term, slug, definition (verbatim clause), provision}. Test: every
         definition is a substring of its provision text; entry count equals pattern
         matches; `/glossary/data-fiduciary` exists and emits `DefinedTerm`.

### T8 — Trust cleanup of the existing public and workspace pages
- status: done (2026-09-28)
- implements: AC10, AC11, AC9
- depends_on: none
- files: deployments/dpdpa-wiki/src/components/screens/CommandCenter.jsx,
         deployments/dpdpa-wiki/src/components/screens/AskIntelligence.jsx,
         deployments/dpdpa-wiki/src/components/screens/Bible.jsx,
         deployments/dpdpa-wiki/src/components/screens/Home.jsx, deployments/dpdpa-wiki/tests/trust.test.js
- risk: tier1
- size: M
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/trust.test.js
- notes: Remove the hard-coded "100%"/"0.0%"/"Zero-Hallucination" block; fix "Notice Sec
         6(1)" → Section 5; Bible penalty table becomes the 7 Schedule rows and per-section
         `max_penalty` is dropped; Home's checklist success copy stops promising an email
         (say "You're on the list"). Test scans every built public HTML for the AC10 strings
         and asserts none appear. Do not touch `mockData.js` here (T9).

### T9 — Remove fabricated legal items from sample data
- status: done (2026-09-28)
- implements: AC10
- depends_on: none
- files: deployments/dpdpa-wiki/src/data/mockData.js, deployments/dpdpa-wiki/tests/mockdata.test.js
- risk: tier1
- size: M
- verify: cd deployments/dpdpa-wiki && npx vitest run tests/mockdata.test.js
- notes: Delete the draft-numbered rule items (r23 cross-border, r5 children, r14 net
         worth), "Consent Notice Rules 2024", the unconfirmed court cases (WP(C) 177/2026,
         Bombay HC erasure, SC stay hearing, Constitution Bench item), and law-firm
         "opinions" unless a URL to the firm's own publication is added. Anything kept
         must carry `source_url`. Test: no item lacks `source_url`; none of the deleted
         titles remain.

### T10 — Move the workspace off public navigation and behind /workspace
- status: done (2026-09-28)
- implements: AC9, AC14
- depends_on: T8
- files: deployments/dpdpa-wiki/src/App.jsx, deployments/dpdpa-wiki/src/components/marketing/PublicShell.jsx,
         deployments/dpdpa-wiki/src/components/AppShell.jsx, deployments/dpdpa-wiki/vercel.json,
         deployments/dpdpa-wiki/tests/navigation.test.js
- risk: tier2
- size: M
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/navigation.test.js
- notes: Prefix every workspace route with `/workspace`; old paths redirect there.
         Public shell nav = Learn · The Act · The Rules · Glossary · Tools. Fix the
         `AppShell.jsx:81` icon bug while there (render an icon, not the name). Add
         `<meta name="robots" content="noindex">` to workspace HTML. Test: no public HTML
         links to a workspace path; workspace HTML has noindex.

### T11 — Real 404, sitemap.xml, robots.txt, og:image
- status: done (2026-09-28)
- implements: AC13, AC14, AC15
- depends_on: T5
- files: deployments/dpdpa-wiki/scripts/prerender.mjs, deployments/dpdpa-wiki/public/robots.txt,
         deployments/dpdpa-wiki/src/components/screens/NotFound.jsx, deployments/dpdpa-wiki/vercel.json,
         deployments/dpdpa-wiki/tests/site-files.test.js
- risk: tier2
- size: M
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/site-files.test.js
- notes: prerender writes `dist/sitemap.xml` from `publicRoutes()` with `lastmod` = build
         date; `dist/404.html` from a NotFound screen; vercel.json serves it with status
         404 for unmatched paths (no catch-all rewrite to index). One static
         `public/og-default.png` (1200×630) referenced by every page until per-page images
         exist. Test: sitemap parses and lists ≥ 90 URLs; 404.html canonical ≠ home;
         every public page has `og:image`.

### T12 — Author module 1: What is DPDPA
- status: done (2026-09-29)
- implements: AC5, AC6
- depends_on: T6
- files: deployments/dpdpa-wiki/src/content/modules/01-what-is-dpdpa.md
- risk: tier1
- size: M
- verify: cd deployments/dpdpa-wiki && node scripts/check-citations.mjs
- notes: Applies to modules T12, T23–T26 and T13. Source material: the 252 answer KOs in
         `staging/competitive_intel/knowledge_objects/answer_kos.jsonl` (each carries
         verbatim evidence and `cited`), grouped by the six stages in spec. Every lesson
         `cites` only labels in the module's `provisions`. Plain English for a business
         owner; Data Principal / Data Fiduciary terms, never "data subject". Front-matter
         is the Module record from spec Contracts; `quiz:` items are authored here too.
         Founder reviews each module before merge. Module 1 covers S1–S3, S2 key terms,
         S44 (what changed), the commencement timeline (R1).

### T23 — Author module 2: The core rules
- status: done (2026-09-29)
- implements: AC5, AC6
- depends_on: T6
- files: deployments/dpdpa-wiki/src/content/modules/02-core-rules.md
- risk: tier1
- size: M
- verify: cd deployments/dpdpa-wiki && node scripts/check-citations.mjs
- notes: Covers S4–S8, R3, R6, R7, R8; the 666-question stage — keep to the 8 most-asked
         (valid consent, notice, legitimate uses, DPO, breach, retention). Same rules as T12.

### T24 — Author module 3: People's rights
- status: done (2026-09-29)
- implements: AC5, AC6
- depends_on: T6
- files: deployments/dpdpa-wiki/src/content/modules/03-peoples-rights.md
- risk: tier1
- size: M
- verify: cd deployments/dpdpa-wiki && node scripts/check-citations.mjs
- notes: Covers S9, S11–S15, R9–R14. Same rules as T12.

### T25 — Author module 4: Special cases
- status: done (2026-09-29)
- implements: AC5, AC6
- depends_on: T6
- files: deployments/dpdpa-wiki/src/content/modules/04-special-cases.md
- risk: tier1
- size: M
- verify: cd deployments/dpdpa-wiki && node scripts/check-citations.mjs
- notes: Covers S10, S16, S17, S6(7)–(9) Consent Manager, R4, R13, R15, R16, First
         Schedule. Same rules as T12.

### T26 — Author module 5: Enforcement
- status: done (2026-09-29)
- implements: AC5, AC6
- depends_on: T6
- files: deployments/dpdpa-wiki/src/content/modules/05-enforcement.md
- risk: tier1
- size: M
- verify: cd deployments/dpdpa-wiki && node scripts/check-citations.mjs
- notes: Covers S18–S39, the Act's Schedule (7 penalty rows), R17–R22. Same rules as T12.

### T13 — Module 6 and the handoff to saralprivacy.com
- status: done (2026-09-29)
- implements: AC5
- depends_on: T12
- files: deployments/dpdpa-wiki/src/content/modules/06-in-your-business.md
- risk: tier1
- size: M
- verify: cd deployments/dpdpa-wiki && node scripts/check-citations.mjs && rg -q "saralprivacy.com" deployments/dpdpa-wiki/src/content/modules/06-in-your-business.md
- notes: Blocked on Q2 for the exact URL. Content: what a business does first (notice,
         consent capture, a grievance contact, retention, breach playbook), each pointing
         at the provision and then at the SaralPrivacy tool. Sets `handoff`, `next: null`.

### T14 — Module pages, course index, next/previous
- status: done (2026-09-29)
- implements: AC5, AC4, AC13
- depends_on: T4, T12, T13, T23, T24, T25, T26
- files: deployments/dpdpa-wiki/src/lib/modules.js, deployments/dpdpa-wiki/src/components/screens/Module.jsx,
         deployments/dpdpa-wiki/src/components/screens/LearnIndex.jsx, deployments/dpdpa-wiki/src/lib/seo.js,
         deployments/dpdpa-wiki/tests/modules.test.js
- risk: tier2
- size: M
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/modules.test.js
- notes: Reuse the guide markdown pipeline in `lib/guides.js` (front-matter → record).
         Inline citations become links to provision pages; a cited Rule not in force gets
         the "Applies from" badge inline. Emit `Course`/`LearningResource` + Breadcrumb.
         Test: modules 1–5 HTML contain the next module's URL; module 6 contains the
         handoff URL and no `/learn/` next link; `/learn` lists 6 in order.

### T15 — Quizzes
- status: done (2026-09-29)
- implements: AC7
- depends_on: T14
- files: deployments/dpdpa-wiki/src/components/screens/Quiz.jsx, deployments/dpdpa-wiki/src/lib/modules.js,
         deployments/dpdpa-wiki/src/lib/seo.js, deployments/dpdpa-wiki/tests/quiz.test.js
- risk: tier2
- size: M
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/quiz.test.js
- notes: Quiz items live in module front-matter (`quiz:`); 5–8 per module; each item
         `cites` a label. Client state only; localStorage key `dpdpa.quiz.{slug}` wrapped
         in try/catch. Submit disabled until every item has a selection. Emit `Quiz`
         JSON-LD. Test: each module has 5–8 items with 4 options and a valid answer index
         and a cited label present in the module; quiz HTML contains no answer key in
         plain text before submit (render answers from JSON in script, not markup).

### T16 — Decision aids
- status: done (2026-09-29)
- implements: AC8
- depends_on: T4
- files: deployments/dpdpa-wiki/src/data/tools/decision-trees.json,
         deployments/dpdpa-wiki/src/components/screens/DecisionAid.jsx, deployments/dpdpa-wiki/src/App.jsx,
         deployments/dpdpa-wiki/src/lib/seo.js, deployments/dpdpa-wiki/tests/decision-aids.test.js
- risk: tier1
- size: M
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/decision-aids.test.js
- notes: Three trees as data: applicability (S3 + S17 exemptions), valid consent
         (S6(1) tests + S5 notice), SDF (S10(1) factors → "government designates; you
         cannot self-designate"). Every node has `cites`. Back button pops history.
         Test: every node's `cites` ⊆ known labels; every terminal has a provision link;
         applicability terminals link to `/act/section-3`.

### T17 — Mobile navigation and responsive public pages
- status: done (2026-09-28)
- implements: AC16, AC18
- depends_on: T10
- files: deployments/dpdpa-wiki/src/components/marketing/PublicShell.jsx, deployments/dpdpa-wiki/src/styles/home.css,
         deployments/dpdpa-wiki/src/styles/guide.css, deployments/dpdpa-wiki/src/styles/components.css
- risk: tier2
- size: M
- verify: cd deployments/dpdpa-wiki && npm run build && rg -q "prefers-reduced-motion" src/styles/ && rg -q "aria-expanded" src/components/marketing/PublicShell.jsx
- notes: Hamburger below 860px with `aria-expanded`; body text 16px minimum; tap targets
         44px; `@media (prefers-reduced-motion: reduce)` disables transitions on the
         infographic components. Automated check is a presence check only — the founder
         verifies at 375px on the preview (tier2 + preview gate).

### T18 — Home page rewired to the course
- status: done (2026-09-28)
- implements: AC9
- depends_on: T14, T16
- files: deployments/dpdpa-wiki/src/data/homeContent.js, deployments/dpdpa-wiki/src/components/screens/Home.jsx,
         deployments/dpdpa-wiki/tests/home.test.js
- risk: tier2
- size: M
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/home.test.js
- notes: Hero CTA → `/learn/what-is-dpdpa`; secondary → `/act`. Journey cards → module or
         tool URLs. Drop the readiness assessment (SaralPrivacy owns it) and link to it
         instead. Keep the FAQ but each answer cites a provision page. Remove the
         `SearchAction` JSON-LD while Ask is hidden. Test: CTA href, no workspace links,
         FAQ answers each contain a `/act/` or `/rules/` link.

### T19 — Retire or canonicalise the MSME guide
- status: done (2026-09-28)
- implements: AC12
- depends_on: T14
- files: deployments/dpdpa-wiki/vercel.json, deployments/dpdpa-wiki/src/lib/seo.js,
         deployments/dpdpa-wiki/src/components/marketing/PublicShell.jsx, deployments/dpdpa-wiki/tests/guide-retire.test.js
- risk: tier1
- size: S
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/guide-retire.test.js
- notes: Blocked on Q1. Branch A: 301 in vercel.json to `/learn/what-is-dpdpa`, drop from
         `publicRoutes()`. Branch B: keep route, `headFor()` sets canonical to the
         saralprivacy.com URL. Either way `/guide` leaves the nav. Test asserts the chosen
         branch.

### T20 — HyperFrames pilot: composition and CI render
- implements: AC17
- depends_on: T4
- files: video/package.json, video/compositions/provision.html, video/data/pilot.json,
         .github/workflows/render-videos.yml, video/README.md
- risk: tier2
- size: M
- verify: cd video && npx hyperframes lint compositions/provision.html
- notes: Pin `hyperframes` to an exact version (pre-1.0, near-daily releases). One HTML
         template parameterised by provision label; script text comes from the answer KO
         for that provision, reviewed by the founder before render. Workflow renders
         16:9 MP4 + WebM + 9:16 MP4 + captions VTT, uploads to Vercel Blob under
         `videos/{label}/{law_version}/`, and writes the Video record to
         `src/content/videos.json` via PR. Full end-to-end render is verified by the
         workflow run itself (A5); local verify is the lint.

### T21 — Video embed on provision pages
- implements: AC17, AC18
- depends_on: T5, T20
- files: deployments/dpdpa-wiki/src/content/videos.json, deployments/dpdpa-wiki/src/components/screens/Provision.jsx,
         deployments/dpdpa-wiki/src/lib/seo.js, deployments/dpdpa-wiki/tests/video.test.js
- risk: tier2
- size: S
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/video.test.js
- notes: `<video preload="none" poster controls>` with `<track kind="captions">`; the
         transcript rendered as text below; `law_version` shown. `VideoObject` JSON-LD
         only on pages with a record. Test: for each record, the page HTML contains the
         transcript text, the poster URL, a `<track`, and VideoObject with `duration`.

### T22 — Preview release checklist
- implements: AC13, AC16
- depends_on: T5, T7, T8, T9, T10, T11, T14, T15, T16, T17, T18
- files: deployments/dpdpa-wiki/RELEASE.md
- risk: tier1
- size: S
- verify: manual — founder opens the Vercel preview URL, walks /learn end to end on a
         phone, spot-reads 60 citations against the gazette, runs Lighthouse on
         /act/section-6 and /learn/core-rules, then promotes to production
- notes: The checklist file records the preview URL, the 60 citations checked, and the
         Lighthouse scores for each release. This is the ABSOLUTE LAW gate.
