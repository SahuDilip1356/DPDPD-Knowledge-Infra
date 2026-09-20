# DPDPA.com Knowledge Cards

These cards are a **competitive discovery pile**, not Setu’s trusted knowledge base.

- Every card has `source_class: COMPETITOR` and `publication_eligible: false`.
- Claims must still pass a Source Truth check against the Act, Rules, Gazette, MeitY, the Board, or a court.
- Raw page bodies stay in `raw/` (gitignored). Only the cards, questions, and briefs are stored.

## Rebuild

```bash
PYTHONPATH=. python -m src.competitive_intel.build_intel
```

That rebuilds cards from `raw/`, then Source Truth, the question universe, article briefs, and the counsel worksheet.

## Read

- `cards/knowledge_cards.jsonl` — one unpublished card per usable page
- `cards/summary.json` — counts by tray
- `truth/claims_registry.jsonl` — Source Truth stamps
- `truth/competitor_topic_matrix.json` — they / we / primary / gap
- `truth/counsel_queue.md` — rows a human lawyer must still sign
- `questions/question_universe.jsonl` — questions customers actually ask
- `gaps/content_gap_briefs.jsonl` — articles Setu should write, citing the Act

## Sitemap coverage

- Sitemap HTML pages: 197
- Fetched, including the two later misses and the robots-disallowed FAQ copy:
  - `https://www.dpdpa.com/ccl.html` (course / commercial certification)
  - `https://www.dpdpa.com/dpdpa-faq-comprehensive.html` (FAQ hub; canonical points at `dpdpa-faq.html`)
  - `https://www.dpdpa.com/dpdpa-faq-comprehensive_1.html` (fetched on request; **byte-identical** stub of the hub above; `robots.txt` Disallow)
- Public HTML only. No PDFs. No login or admin.

## Guardrails

- `publication_allowed` on a claim means the *fact* may be restated with the Act citation — not that DPDPA.com may be copied.
- `counsel_signed` is false until a human lawyer stamps the queue. The machine does not sign as counsel.
- Article briefs in `gaps/` stay unpublished factory notes. When you write the article, cite the Gazette, not the competitor.
