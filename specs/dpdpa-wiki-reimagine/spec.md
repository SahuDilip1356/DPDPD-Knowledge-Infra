# Spec — dpdpa.wiki reimagined

**Status:** draft
**Intent:** ./intent.md
**Date:** 2026-09-27

## Behavior

A visitor arriving at dpdpa.wiki sees a public site with four kinds of page: the home
page, a page for every provision of the Act and the Rules, a six-module course, and a
small set of decision aids. Every provision page shows the gazette's own text, a
plain-language note, the date the provision applies from, the questions readers ask
about it, and links to the module that teaches it. Every module page teaches one stage
of the law in plain language, cites provisions inline, ends with a short self-test and a
link to the next module, and the final module hands the reader to saralprivacy.com for
assessment and tools. Three provision pages also carry a captioned explainer video with
its transcript on the page. Every public page is served as complete HTML, appears in
the sitemap, and works at phone width. The workspace (Today, Knowledge, Actions,
Factory, Ask, Admin) is no longer reachable from public navigation and no longer
displays any legal statement that is not sourced. Nothing anywhere on the site cites a
section or rule number that does not say what the site claims.

## Contracts

### URL scheme (public, all prerendered)

```
/                                   home
/act                                index of the Act: 9 chapters → 44 sections + Schedule
/act/section-{n}                    n = 1..44
/act/schedule                       the penalty Schedule
/rules                              index of the DPDP Rules 2025: 23 rules + 7 schedules
/rules/rule-{n}                     n = 1..23
/rules/schedule-{first..seventh}
/learn                              the course index: 6 modules in order
/learn/{module-slug}                one module; slugs fixed below
/learn/{module-slug}/quiz           the module's self-test
/tools/does-dpdpa-apply             decision aid
/tools/is-this-consent-valid        decision aid
/tools/significant-data-fiduciary   decision aid
/glossary                           one entry per defined term in Section 2 and Rule 2
/glossary/{term-slug}
/sitemap.xml   /robots.txt   /404   (real files / real 404 status)
```

Module slugs, in order: `what-is-dpdpa`, `core-rules`, `peoples-rights`,
`special-cases`, `enforcement`, `in-your-business`.

Any URL not in this scheme returns HTTP 404 with the 404 page, not the home page.

### Provision record (the only source a provision page may render from)

```
{ label: "S6" | "ACT-SCHEDULE" | "R7" | "SCH-FIRST",
  urn: string,                       // urn:ki:in:dpdp:...
  title: string,                     // heading as printed in the gazette
  text: string,                      // verbatim gazette text, corrigendum applied
  source: { document: string, notification: string, sha256: string },
  in_force_from: iso-date,
  note: string | null,               // plain-language note; null renders "note pending"
  note_cites: string[],              // labels every citation in the note must be drawn from
  questions: [{ id: string, question: string }],   // canonical questions mapped here
  module: module-slug }
```

### Module record

```
{ slug, order: 1..6, title, summary,
  lessons: [{ heading, body_markdown, cites: string[] }],
  provisions: string[],              // labels covered
  quiz: [{ q: string, options: string[4], answer: 0..3, cites: string[] }],  // 5..8 items
  next: module-slug | null,
  handoff: { label, url } | null }   // only the last module sets this
```

### Video record (per pilot clip)

```
{ provision: label, src_mp4: url, src_webm: url, poster: url, captions_vtt: url,
  transcript: string, duration_s: number, law_version: string, rendered_at: iso-date }
```

### Structured data emitted per page type

home → WebSite (no SearchAction while Ask is hidden) · provision → Legislation +
BreadcrumbList · module → Course/LearningResource + BreadcrumbList · quiz → Quiz ·
glossary entry → DefinedTerm · video page → adds VideoObject.

### Head tags on every public page

`<title>`, `meta description`, `link rel=canonical` (self), `og:title`, `og:description`,
`og:image` (a real image URL), `twitter:card`.

## Acceptance criteria

### AC1 — Every provision page renders the gazette text verbatim
- traces: G1, G2
- given: the provision record for any of the 75 provisions
- when: its page is built
- then: the page body contains the record's `text` unchanged, the `title` as printed,
        the `in_force_from` date, and the source document and notification names

### AC2 — A note may only cite provisions it is allowed to
- traces: G1
- given: a provision record whose `note` mentions "Section N" or "Rule N"
- when: the site is built
- then: the build fails with the offending label and page named unless every such
        reference appears in `note_cites` and `note_cites` ⊆ the 75 known labels

### AC3 — A provision with no note still has a page
- traces: G2
- given: a provision record whose `note` is null
- when: its page is built
- then: the gazette text renders in full and a visible "Plain-language note pending"
        marker replaces the note; the page is still in the sitemap

### AC4 — Rules not yet in force say so
- traces: G1, G2
- given: a Rule whose `in_force_from` is later than the build date
- when: its page is built
- then: a badge reading "Applies from {date}" appears above the text, and the same badge
        appears on any module lesson that cites it

### AC5 — Every module links forward and the last hands off
- traces: G3, G5
- given: the six module records
- when: their pages are built
- then: modules 1–5 each end with a link to the next module's URL; module 6 ends with the
        handoff link to saralprivacy.com and no "next" link; `/learn` lists all six in order
        with their summaries

### AC6 — Module lessons cite only provisions in the module
- traces: G1, G3
- given: a lesson whose body mentions "Section N" or "Rule N"
- when: the site is built
- then: the build fails unless every reference is in the lesson's `cites` and in the
        module's `provisions`

### AC7 — Every quiz is answerable and self-marking
- traces: G4
- given: a module quiz with 5–8 items
- when: a reader selects an option and submits
- then: the page shows correct/incorrect per item, the correct option, and the cited
        provision with a link to its page; with no option selected, submit is disabled and
        no score is shown; the score is stored only in the reader's browser

### AC8 — Decision aids reach a conclusion from the law
- traces: G4, G1
- given: any path through a decision aid
- when: the reader answers each step
- then: every step's question and every terminal conclusion display the provision they
        rest on, and a terminal that says "the Act applies" or "does not apply" links to
        `/act/section-3`; a reader can go back one step without restarting

### AC9 — Home page and navigation lead to lessons, not the workspace
- traces: G3, G5
- given: the built home page
- when: rendered
- then: the primary call to action links to `/learn/what-is-dpdpa`; journey cards link only
        to `/learn/*`, `/act`, `/rules`, `/tools/*` or `/glossary`; no public page links to
        `/today`, `/knowledge`, `/actions`, `/factory`, `/ask` or `/admin`

### AC10 — No public page carries an unsourced legal statement or a fake metric
- traces: G1
- given: the built public HTML
- when: scanned
- then: none of these strings appear on any public page: "Sec 6(1)" as a notice label,
        "0.0%", "100% GROUNDED", "Zero-Hallucination", "MEITY.FEED.LIVE", "Draft Phase",
        "Consent Notice Rules 2024", "Rule 23", "Rule 5: Verifiable Consent",
        "Rule 14: Consent Manager", "checklist is on its way"

### AC11 — The Bible penalty table matches the Schedule
- traces: G1
- given: any page that lists penalties
- when: rendered
- then: it lists exactly the 7 rows of the Act's Schedule with the amounts as gazetted,
        and no section page shows a penalty amount the Schedule does not attach to it

### AC12 — The MSME guide no longer competes with saralprivacy.com
- traces: G5
- given: the founder's decision (Open question Q1)
- when: the site is built
- then: either `/guide/dpdp-act-explained-indian-msmes` returns 301 to
        `/learn/what-is-dpdpa`, or it renders with `link rel=canonical` pointing to the
        saralprivacy.com URL the founder names; `/guide` is removed from navigation

### AC13 — Every public page is real HTML with correct head tags
- traces: G6
- given: any URL in the scheme
- when: fetched without executing JavaScript
- then: the response body contains the page's main text, its own `<title>`, meta
        description, self-canonical, `og:image`, and the structured-data block named in
        Contracts for that page type

### AC14 — Unknown URLs are 404s
- traces: G6
- given: a URL not in the scheme, including every former workspace route
- when: fetched
- then: HTTP status 404 and the 404 page, whose canonical is not the home page

### AC15 — Sitemap and robots exist
- traces: G6
- given: the built site
- when: `/sitemap.xml` and `/robots.txt` are fetched
- then: `sitemap.xml` is valid XML listing every public URL (≥ 75 + 6 + 6 + 3 + 1 + glossary
        entries) with `lastmod`; `robots.txt` allows `/` and references the sitemap

### AC16 — Works at phone width
- traces: G6
- given: any public page at 375px viewport
- when: rendered
- then: no horizontal scroll, a menu control opens the full navigation, tap targets are
        ≥ 44px, and body text is ≥ 16px

### AC17 — Video pages degrade to text
- traces: G7, G6
- given: a provision page with a video record
- when: rendered, and separately when the video file is unavailable
- then: the transcript is present as text in the HTML either way; the video element does
        not autoplay with sound, has a poster and a captions track, and the VideoObject
        block carries `name`, `thumbnailUrl`, `uploadDate`, `duration`; `law_version` is
        shown under the player

### AC18 — Reduced motion is respected
- traces: G6
- given: a reader with `prefers-reduced-motion: reduce`
- when: any animated diagram or scroll-linked element renders
- then: it shows its final state with no motion, and remains readable

### AC19 — Glossary entries come from the definitions provisions
- traces: G1, G2
- given: the glossary
- when: built
- then: every entry's definition text is a verbatim substring of Section 2 or Rule 2, and
        each entry links to that provision page; the count of entries equals the number of
        defined terms in those two provisions

## Non-functional

- Largest public page ≤ 250 KB HTML + CSS before images; no page loads a JavaScript
  bundle larger than 200 KB gzipped for first render.
- Videos: MP4 (H.264) + WebM, ≤ 12 MB per clip, `preload="none"`; served from object
  storage, not the site bundle.
- Build: full prerender of all public pages completes in under 5 minutes on Vercel.
- Lighthouse (mobile) on a provision page and a module page: Performance ≥ 85,
  Accessibility ≥ 95, SEO ≥ 95, measured on the preview before each production release.
- Preview gate: every release is verified on a Vercel preview URL by the founder before
  promotion to production. No exceptions.

## Out of scope

Workspace redesign; Ask repair; Hindi; best-practice (non-law) answers; a clip per
section; user accounts or server-side progress; comments; search within the site
(browser find + provision index suffice this cycle).

## Open questions

- **Q1** — Retire the MSME guide (301) or keep it with a canonical to saralprivacy.com?
  Owner: Dilip · by: 2026-10-03 · blocks: AC12
- **Q2** — Which saralprivacy.com URL is the module-6 handoff target (assessment page or
  /learn)? Owner: Dilip · by: 2026-10-03 · blocks: AC5
- **Q3** — Which three provisions get the pilot clips? Recommendation: Section 6
  (consent), Section 8 (obligations), Rule 7 (breach). Owner: Dilip · by: 2026-10-17 ·
  blocks: AC17
- **Q4** — Does dpdpa.wiki get its own logo, or keep the SaralPrivacy mark? Owner: Dilip ·
  by: 2026-10-10 · blocks: nothing (branding task waits)
