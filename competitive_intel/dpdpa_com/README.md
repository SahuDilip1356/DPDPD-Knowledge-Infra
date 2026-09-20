# DPDPA.com Knowledge Cards

These cards are a **competitive discovery pile**, not Setu’s trusted knowledge base.

- Every card has `source_class: COMPETITOR` and `publication_eligible: false`.
- Claims must still pass a Source Truth check against the Act, Rules, Gazette, MeitY, the Board, or a court.
- Raw page bodies stay in `raw/` (gitignored). Only the cards are stored.

## Rebuild

```bash
PYTHONPATH=. python -m src.competitive_intel.build_cards
PYTHONPATH=. python -m src.competitive_intel.build_source_truth
```

## Read

- `cards/knowledge_cards.jsonl` — 195 cards, one per usable page
- `cards/summary.json` — counts by tray
- `truth/claims_registry.jsonl` — Source Truth stamps on extracted claims
- `truth/competitor_topic_matrix.json` — they / we / primary / gap
- Rebuild skips Cloudflare interstitials and 404s. Cards stay unpublished.
- `publication_allowed` on a claim means the *fact* may be restated with the Act citation — not that DPDPA.com may be copied.
