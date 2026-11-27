# Evals: official sources, T1 and T2

**Status:** awaiting Dilip's approval. No code is written until he approves.
**Branch:** `feat/official-sources-t1-t2`
**Baseline (2026-11-25):** backend `python -m pytest -q`: 127 passed.

## Risk

| Task | Tier | Why |
|---|---|---|
| T1 lane tests + contract fix | Medium | A CI gate and a change to the corpus contract. A wrong rule would block publishing, which can be undone. It does not touch the live store. |
| T2 registry + fetcher | High | It decides which text counts as an official source. Every later quote is checked against that text, so a bad text would let a legal claim through. It also fetches and parses PDFs from outside sites. |

T2 also gets an sd-security pass.

## Finding that changes T1

The corpus contract skips any evidence item whose `source_urn` is not the Act or the Rules
(`corpus_contract.py:94`, `continue`). An answer that is otherwise valid passes with an
extra evidence item citing `urn:ki:in:dpdp:source:competitor-blog`. I checked this by
adding that item to a conforming object from the eval snapshot: `check_object` returned no
problems.

None of the 511 staged answers or the 57 staged primary objects cites another source, so
closing the hole now breaks nothing that is staged. T1 therefore also makes the contract
reject any source other than the Act and the Rules. T3 later allows active registry
sources.

## T1: lane tests and contract fix

Command: `cd deployments/dpdpa-backend && python -m pytest -q src/tests/test_lanes.py src/tests/test_corpus_contract.py`

| # | Check | Pass when |
|---|---|---|
| E1.1 | Market lane is ignored | `git check-ignore` reports every path under `staging/competitive_intel/market-map/` as ignored, including a file that does not exist yet |
| E1.2 | Market lane is untracked | `git ls-files staging/` returns nothing |
| E1.3 | Eval corpus sources are law-lane only | every `source_urn` in `evals/corpus/answer_kos.jsonl.gz` is the Act or the Rules gazette URN (an allowlist, so no competitor domains are named in this public repo) |
| E1.4 | Unregistered source fails | an object with an extra evidence item citing `urn:ki:in:dpdp:source:competitor-blog` gets the problem "cites an unregistered source" |
| E1.5 | `push` refuses it | `push(dry_run=True)`, pointed at a temporary staged file holding that object, exits with "refused" and the report names the object; nothing reaches Supabase |
| E1.6 | Nothing staged breaks | `check_corpus` on the 511 snapshot answers returns the same result as before the change |
| E1.7 | No regressions | full backend suite: 127 old tests plus the new ones pass; `python evals/runner.py --offline --runs 1` passes its gate |

## T2: source registry, allowlist and fetcher

Command: `cd deployments/dpdpa-backend && python -m pytest -q src/tests/test_official_sources.py`.
The tests run offline, on fixture files and a stubbed HTTP session, never the network.

| # | Check | Pass when |
|---|---|---|
| E2.1 | Valid entry loads | a fixture registry with one complete `meity` entry on `meity.gov.in` loads without error |
| E2.2 | Off-domain URL refused (AC2) | an `rbi` entry with a URL on `example.com` fails to load, and the error names the entry id and the domain |
| E2.3 | Lookalike domain refused | `meity.gov.in.evil.com` and `evilmeity.gov.in` are refused; `www.meity.gov.in` is accepted |
| E2.4 | Unknown authority refused | `authority: dpdpa-com` fails to load |
| E2.5 | Manual text needs a reviewer (AC8) | `text_method: manual` without `reviewed_by` fails; with it, the entry loads |
| E2.6 | Duplicate id or urn refused | two entries sharing an id or a urn fail to load |
| E2.7 | Fetch stores, hashes and extracts (AC1) | fetching a fixture PDF writes `source.pdf` and `text.txt` under `staging/official_sources/<id>/`, and `sha256` and `text_sha256` equal the hashes of those two files |
| E2.8 | HTML source works | a fixture HTML page is stored as `source.html`, and its text excludes scripts and navigation |
| E2.9 | Image-only PDF is flagged | a PDF with no extractable text writes no `text.txt` and is reported as needing `text_method: manual` |
| E2.10 | Changed document is never overwritten (AC6) | refetching an entry whose file now differs leaves the registry entry, `source.*` and `text.txt` unchanged, and reports the entry as changed |
| E2.11 | Redirect off the allowlist refused | a fetch that redirects to a domain outside the allowlist stores nothing |
| E2.12 | Polite fetching | the User-Agent names the project, `robots.txt` is honoured, and two fetches to one domain are at least one second apart (checked on a stubbed clock) |
| E2.13 | Size limit | a response over 25 MB is refused |
| E2.14 | No regressions | full backend suite passes |

## Choices I made (say if you want them changed)

- PDF text comes from `pypdf`, which the Act and Rules ground truth already use.
- `pyyaml` is added to the backend requirements, since CI installs only those and the registry is YAML.
- The registry starts empty. Real documents are registered in T4 and T5, after each is confirmed on the issuing site.
- The Board (`dpb`) has no domain in the allowlist until its official site is confirmed (spec, Authority allowlist).
