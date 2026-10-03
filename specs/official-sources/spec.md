# Spec — official sources in the law lane

**Status:** draft
**Intent:** ./intent.md
**Date:** 2026-10-03

## Behavior

A maintainer adds an official document by adding one entry to the source registry. A
command fetches the document from the official URL in the entry, records its hash and
extracts its text, and stores both under the gitignored staging folder. The registry
entry is committed with that hash.

From then on, any knowledge object may quote the document. The corpus contract checks
each quote word for word against the stored text, and checks the hash. An object that
quotes an unregistered source, or a source outside the allowlist of issuing authorities,
breaks the contract and cannot be published.

The commencement notification(s) for the Act are among the first documents registered.
`sync-law.mjs` reads the dates from them, so every Act provision page shows the date it
applies from and names the notification.

A weekly watch checks every registered URL for changes and searches each authority's
listing for new DPDP-related issuances, then writes a review list.

Competitor and market data never enters this path. It stays under
`staging/competitive_intel/market-map/`, which git ignores, and a test enforces both
rules.

## Contracts

### Source registry — `sources/official.yaml` (committed)

```yaml
- id: meity-act-commencement-2025          # stable, lowercase, hyphenated
  urn: urn:ki:in:dpdp:source:meity-act-commencement-2025
  authority: meity        # one of: meity, dpb, egazette, indiacode, certin, rbi, sebi, irdai, sci
  kind: notification      # notification | direction | order | circular | judgment | faq
  title: "<as printed>"
  reference: "<S.O./G.S.R. number, or case citation>"
  issued_on: 2025-11-13   # as printed on the document
  url: https://...        # must be on the authority's own domain (allowlist below)
  sha256: <64 hex>        # of the fetched file
  text_sha256: <64 hex>   # of the extracted text
  text_method: pdf | html | manual   # manual = typed from an image-only document, reviewed
  reviewed_by: <name>     # required when text_method is manual
  status: active          # active | superseded
  superseded_by: null     # id of the replacement, when superseded
```

### Authority allowlist (committed, in the registry loader)

| authority | domains |
|---|---|
| meity | meity.gov.in |
| dpb | the Board's official domain, added when it is published |
| egazette | egazette.gov.in |
| indiacode | indiacode.nic.in |
| certin | cert-in.org.in |
| rbi | rbi.org.in |
| sebi | sebi.gov.in |
| irdai | irdai.gov.in |
| sci | main.sci.gov.in, sci.gov.in |

### Stored text (gitignored)

`staging/official_sources/<id>/source.<pdf|html>` and `staging/official_sources/<id>/text.txt`.

### Corpus contract, extended

The checks in `corpus_contract.py` for an evidence item:

| `source_urn` | The quote must appear in | Its `chunk_sha256` must equal |
|---|---|---|
| Act or Rules gazette source | that provision's text in `provisions.json` | that provision's text hash, as today |
| A registry `urn` with status `active` | the registered source's `text.txt` | the registry's `text_sha256` |
| A registry `urn` with status `superseded` | — fails: "cites a superseded source" | — |
| Anything else, including any market-lane domain | — fails: "cites an unregistered source" | — |

### Act commencement in `provisions.json`

Each Act provision gets `in_force_from: YYYY-MM-DD` and
`in_force_source: <registry id>`. A provision still awaiting a date keeps `null` and
says so on its page.

### Watch report

`staging/official_sources/watch-YYYY-MM-DD.md` lists:
- changed: a registered URL whose file hash differs from the registry;
- unreachable: a registered URL that failed;
- new: listing entries that mention "Digital Personal Data Protection" and are not yet
  registered.

## Non-functional

- Fetching respects each site's robots rules, sends at most one request per second per
  domain, and identifies itself in the User-Agent.
- No step overwrites a registered source. A changed document becomes a new registry
  entry; the old one is marked `superseded`.
- CI runs offline. Tests use small fixture documents, never the network.

## Acceptance criteria

### AC1 — A registered source is fetched, hashed and extracted
- traces: G1
- given: a registry entry with an allowlisted URL
- when: the fetch command runs
- then: the file and its extracted text exist under `staging/official_sources/<id>/`,
        and `sha256` and `text_sha256` are written to the entry

### AC2 — A URL outside the allowlist is refused
- traces: G1, G4
- given: a registry entry whose URL is not on its authority's domains
- when: the registry is loaded
- then: loading fails, naming the entry and the domain

### AC3 — A quote from a registered source is checked word for word
- traces: G1, G3
- given: an object whose evidence cites an active registry urn
- when: the corpus contract checks it
- then: it conforms only if every quote fragment appears in that source's text and the
        hash equals `text_sha256`

### AC4 — An unregistered or market-lane source fails the contract
- traces: G4
- given: an object whose evidence cites a urn not in the registry, or a competitor URL
- when: the corpus contract checks it, or `push` tries to publish it
- then: it fails with "cites an unregistered source", and `push` refuses the batch

### AC5 — A superseded source cannot be newly cited
- traces: G1
- given: a registry entry with status `superseded`
- when: an object cites it
- then: the contract fails with "cites a superseded source"

### AC6 — A changed document never overwrites the registered one
- traces: G1, G5
- given: a registered URL whose file has changed
- when: the fetch or the watch runs
- then: the registry entry and its stored text are unchanged, and the change is
        reported for review

### AC7 — Every Act provision shows when it applies
- traces: G2
- given: the commencement notification(s) are registered
- when: `sync-law.mjs` runs and the site is built
- then: every Act provision page shows its `in_force_from` date and names the
        notification; a provision with no date says it awaits notification

### AC8 — An image-only document needs a named reviewer
- traces: G1
- given: a source whose text cannot be extracted
- when: it is registered with `text_method: manual`
- then: loading fails unless `reviewed_by` is set

### AC9 — The market lane cannot be committed
- traces: G4
- given: any file under `staging/competitive_intel/market-map/`
- when: the lane test runs
- then: it fails if git tracks the file or would not ignore it

### AC10 — The watch lists changes and new issuances
- traces: G5
- given: the registry and the authorities' listing pages
- when: the weekly watch runs
- then: it writes a watch report with changed, unreachable and new entries, and exits
        non-zero if any registered URL changed

### AC11 — The first verified objects replace the quarantined seed topics
- traces: G3
- given: the quarantined seed objects on Puttaswamy and on the CERT-In and sector
         directions
- when: their official sources are registered and objects are built from them
- then: the new objects pass the contract, and `audit` reports every live object
        conforming
