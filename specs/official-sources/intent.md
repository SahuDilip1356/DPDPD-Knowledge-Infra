# Intent — grow the law lane with official sources, keep the market lane out

**Status:** draft
**Owner:** Dilip Sahu
**Date:** 2026-10-03

## Problem

The knowledge base holds two documents in their own words: the Act and the DPDP Rules
2025. Compliance in India depends on more than that. When each section of the Act came
into force is set by notification, not by the Act, so every Act provision in the site's
law file carries `in_force_from: null`. A breach also has to be reported under CERT-In's
directions, and banks, insurers and listed companies answer to their own regulators.
The Data Protection Board will issue orders. Courts have already shaped the right to
privacy.

None of this is in the base in a form anyone can trust. The only objects on these topics
are 27 hand-written seed records with no source text (Puttaswamy, RBI, SEBI, penalty
cards, law-firm opinions), and the corpus contract correctly marks every one of them as
failing. The contract can only check a quote against the Act and the Rules, so a real
Board order or judgment would fail it too.

At the same time the market-map pack (106 competitor and market sites) has arrived.
That data is useful for product and editorial decisions, but between 10% and 31% of
the legal claims on those sites are wrong or unsupported. If any of it reached Ask or
the site, the base would get less accurate, not more.

## Goals

### G1 — Every official source in the base is held in its own words, from an official URL
An official document enters the base only as its original text, fetched from the
issuing authority's website, with a SHA-256 hash recorded. Any quote from it can be
checked word for word against that text.

### G2 — Each Act provision says from when it applies
The site shows, for each section of the Act, the date it came or comes into force, and
names the notification that set that date.

### G3 — Ask and the site can cite official sources beyond the Act and the Rules
A knowledge object may rest on a registered official source, such as a notification,
direction, order or judgment, with the same word-for-word guarantee the Act and the
Rules have today.

### G4 — Market data never enters the law lane
Competitor and market data stays internal. No knowledge object, search vector or public
page is built from it, and a check fails if anyone tries.

### G5 — A new official issuance is noticed within a week
When the Board, MeitY or a listed regulator publishes something new on DPDP, it is on
a review list within seven days, before anyone asks about it.

## Non-goals

### NG1 — Ingesting competitor or market data as knowledge
That data belongs to the market lane: internal analysis only.

### NG2 — Commentary and opinion, including law-firm notes
Layer 4–5 material is a later cycle, under its own rules for labelling opinion.

### NG3 — Summaries or explainers of the new sources
This cycle stores and verifies the sources. Plain-language notes and course lessons
built on them come afterwards.

### NG4 — Translation into Indian languages
Not in this cycle.

## Assumptions

### A1 — The commencement dates of the Act were notified, and the notification is published
The dates may be in one notification or several. Their exact form is still to be
confirmed from the gazette.
- validate_by: T4: find the notification(s) on eGazette or meity.gov.in before registering

### A2 — Official texts are available as text, not only as scanned images
If a document is image-only, its text is entered by hand and reviewed before it can be
quoted.
- validate_by: T2: the fetcher reports text_method per source; count the manual ones

### A3 — The Board has issued no orders yet
The pipeline must work with zero orders and pick up the first one when it appears.
- validate_by: T7: the first watch run lists any Board issuance

### A4 — A short allowlist of issuing authorities is enough
MeitY, the Board, eGazette, India Code, CERT-In, RBI, SEBI, IRDAI and the Supreme Court
cover what readers need this year.
- validate_by: T7: the watch's new-issuance list stays within these authorities for a month

### A5 — The 27 failing seed objects are closed before this work lands
Founder-run `quarantine`. Verified objects on the same topics replace them.
- validate_by: T6: `audit` lists no seed urn before the first official object is published

## Success criterion

`build_knowledge_objects.py audit` reports every live object conforming, including at
least one object from an official source other than the Act and the Rules. Every Act
provision in `provisions.json` has an `in_force_from` date with a cited notification.
The lane test fails when a law-lane object cites an unregistered source or when any
file under `staging/competitive_intel/market-map/` is tracked by git.
