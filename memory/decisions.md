# Decisions — DPDPD Knowledge Infra

## 2026-08-01 — Knowledge placement model (discussed; operating guidance)

**Decision (working rule, pending product priority fork):**  
Treat **Core** as Trust Layer 1–2 Knowledge Objects (Act/Rules/Judgements) with evidence and URNs. Other product sections (Bible, Changes, Actions, Ask, Factory) are windows/workflows onto the same graph — not separate content silos. Lower layers may Interpret/Support/Conflict, never overwrite normative Core.

**Alternatives considered:**
- Put all commentary into Core for faster Ask answers → rejected (dilutes trust, violates constitution)
- Maintain Bible as independent copy of Act text → risk of drift; prefer URN-linked Bible entries

**Open fork (not decided):**
- **A)** Statute-complete Core first  
- **B)** Five business clusters first (Consent, Breach, Children, SDF, Cross-border)  
- **Hybrid** recommended in discussion: light Core skeleton + deep clusters

**Rationale:** Aligns with Knowledge Constitution and Founding Memo (evidence-first, events over documents, infrastructure before apps).

## 2026-11-25 — Retrieval for law, fine-tuning for voice only

**Decision (Dilip):** DPDPA facts come only from retrieval over the verified law lane (the Act, the Rules and registered official sources, checked by the corpus contract). A model may be fine-tuned for tone and format only, and only on SaralPrivacy's own writing, such as the 208 daily briefings once the four flagged ones are fixed. No fine-tuning on law text, competitor pages, market data or machine-suggested labels.

**Why:** the nine LoRA/QLoRA runs of 28–29 Sep 2026 trained on 33 generic sample chats, not DPDPA, and the larger models got worse on the check set. Weights cannot be updated when the law changes (S.O. 5458(E) of Oct 2026 already amended the Act's wording), and competitor text disagrees with the gazette. Retrieval picks up a change the day the verified text changes.
