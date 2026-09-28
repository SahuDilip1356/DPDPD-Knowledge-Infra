# Intent — dpdpa.wiki reimagined as the annotated law and the DPDPA course

**Status:** draft
**Owner:** Dilip Sahu
**Date:** 2026-09-27

## Problem

Someone who wants to understand India's DPDP Act — a founder, a clinic owner, an HR
manager, a student — lands on dpdpa.wiki and finds three real pages and a workspace
full of sample data presented as live. Some of that sample data states the law wrongly:
notice attributed to the wrong section, a ₹250 crore cap on every section, Rules cited by
their draft numbers, court cases that may not exist. The one good guide duplicates
saralprivacy.com's own learning hub, so the two sites compete for the same search
results. There is no sequence to follow, nothing to test yourself with, and the site does
not work on a phone. For a site whose promise is "every statement traces to a section",
a reader who checks one citation and finds it wrong will not come back.

## Goals

### G1 — Nothing on the site states the law wrongly
Every legal statement shown to a reader is either the gazette's own words or a
plain-language note that cites the provision it rests on, and a spot-check of any
citation finds it correct.

### G2 — The whole law is readable, one page per provision
A reader can open any of the 44 sections of the Act, its Schedule, any of the 23 Rules
and any of the 7 Schedules to the Rules as its own page, in the gazette's words, with a
plain-language note and the date from which it applies.

### G3 — A beginner can walk from "what is DPDPA" to "what must my business do"
There is a numbered path of modules a first-time reader can follow in order, each
module ending with a link to the next, and the last module handing off to the tools
that help a business act.

### G4 — Readers can check their own understanding
Every module offers a short self-test, and the site offers at least three
decision aids that answer a reader's own situation (does the Act apply to me, is this
consent valid, am I a Significant Data Fiduciary).

### G5 — dpdpa.wiki and saralprivacy.com stop competing
Each learning topic is owned by exactly one of the two sites; the other links to it.
dpdpa.wiki owns the law and the course; saralprivacy.com owns assessment, templates,
industry playbooks and tooling.

### G6 — The site is findable and usable on a phone
Every public page is indexable as real HTML, is listed in a sitemap, and can be read and
navigated at phone width without sideways scrolling.

### G7 — Short explainer videos exist for the most-asked provisions
A reader can watch a captioned, transcript-backed clip of under two minutes for at least
three provisions, and each clip records which version of the law it reflects.

## Non-goals

### NG1 — Rebuilding the workspace (Today, Knowledge, Actions, Factory, Admin)
Different problem. This cycle only removes it from public navigation and stops it
serving wrong law. Its own redesign waits for the hosted backend.

### NG2 — Fixing Ask Intelligence
The backend is not hosted and the answer store is not loaded. Ask is hidden from public
navigation this cycle, not repaired.

### NG3 — Hindi or regional-language editions
Real need, separate cycle. saralprivacy.com already carries Hindi lessons.

### NG4 — Answering questions the law does not answer
Best-practice questions (how to run a DPIA, what a RoPA looks like) need a separately
labelled layer with its own trust rules. Not this cycle.

### NG5 — A video per section
Only a pilot of three clips. Scaling waits on measured engagement.

## Assumptions

### A1 — The verified ground-truth text of the Act and Rules is correct
- validate_by: SHA-256 of both source PDFs recorded; 60 provisions spot-read against the
  gazette by a person before launch — week 1
- if_wrong: the affected provision pages are corrected at source and rebuilt; nothing
  else changes because every page derives from the same files

### A2 — Search engines will index prerendered provision pages
- validate_by: Google Search Console shows ≥50 of the 75 provision pages indexed within
  30 days of launch
- if_wrong: add per-page internal links from the course modules and request indexing;
  if still under 50 at 60 days, the SEO thesis of the site needs re-examining

### A3 — Readers want a sequence, not just a reference
- validate_by: within 30 days of launch, ≥25% of sessions that open a module click the
  "next module" link
- if_wrong: keep the provision pages and the decision aids; demote the ladder to a
  secondary navigation and invest in search-led entry instead

### A4 — SaralPrivacy will accept owning the "business application" half
- validate_by: founder decision on retiring the MSME guide from dpdpa.wiki — before
  week 2 starts
- if_wrong: keep the guide on dpdpa.wiki with a canonical tag pointing to
  saralprivacy.com, and G5 weakens to "no new duplication"

### A5 — HTML-to-video rendering runs unattended in CI
- validate_by: one clip renders end to end in a GitHub Actions job in week 4
- if_wrong: render the three pilot clips on a laptop and publish them as files; the
  pipeline question is deferred, G7 still holds

## Success criterion

By **2026-11-15**: all 75 provision pages and the 6-module ladder are live in
production; a 60-citation spot audit finds **0** wrong citations; Google Search Console
shows **≥50** provision pages indexed; and **≥25%** of module sessions click "next".

## Rollback

Content is files in git and pages are prerendered, so any release is undone by promoting
the previous Vercel deployment (instant, no data path). No database migration is part
of this cycle. Removing the MSME guide is a git revert. Video files live in object
storage keyed by version and are never overwritten, so an old clip can be re-pointed to.
