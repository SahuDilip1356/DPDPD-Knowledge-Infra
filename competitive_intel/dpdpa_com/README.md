# DPDPA.com Knowledge Cards

These cards are a **competitive discovery pile**, not Setu’s trusted knowledge base.

- Every card has `source_class: COMPETITOR` and `publication_eligible: false`.
- Claims must still pass a Source Truth check against the Act, Rules, Gazette, MeitY, the Board, or a court.
- Raw page bodies stay in `raw/` (gitignored). Only the cards are stored.

## Rebuild

```bash
PYTHONPATH=. python -m src.competitive_intel.build_cards
```

## Read

- `cards/knowledge_cards.jsonl` — 195 cards, one per usable page
- `cards/summary.json` — counts by tray
- Rebuild skips Cloudflare interstitials and 404s. Nothing is publication-eligible.
