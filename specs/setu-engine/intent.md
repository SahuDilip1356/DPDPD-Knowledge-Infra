# Intent: Setu engine, one answer engine for every SaralPrivacy surface

**Status:** draft
**Owner:** Dilip Sahu
**Date:** 2026-11-25
**For:** A founder, compliance lead or student in India who types a DPDPA question
(often in street words, such as "can they sell my number?") on dpdpa.wiki, on
saralprivacy.com, in the Setu chatbot or in the third platform, and needs an answer
they can act on and check.

## Problem

Today each place that answers a DPDPA question would need its own way of doing it, and
only the wiki's Ask has one. Its answers are grounded in the Act and the Rules, but it
finds the right provision for only part of each question: on the 64-case real-corpus
eval it recalls 44.7% of the expected provisions offline and 71% live. On a 101-question
set of street questions, 17 got no answer at all.

Answers written freely by a general model are not safe: earlier gpt-4o drafts invented
legal terms such as "Data Personal Breach Inquiry", which appear nowhere in the law.
Answers also read like the statute. A small business owner or a student cannot follow
them, and they do not sound like SaralPrivacy.

Dilip has asked for "a model trained on all DPDPA data". On 2026-11-25 he decided that
the law reaches users only through look-up over the verified law text, never from what a
model memorised. Training is limited to voice and format, on SaralPrivacy's own writing.
This plan does not reopen that decision.

## Goals

### G1: One engine answers for every surface
The wiki, saralprivacy.com, the Setu chatbot and the third platform get their DPDPA
answers from the same engine, so the same question gets the same law, the same
citations and the same in-force dates everywhere.

### G2: Every legal statement can be checked against the gazette
Every legal claim in an answer carries a citation and a word-for-word quote from the
official text, and no answer names a provision, penalty or term that the law does not
contain.

### G3: More questions get the right provision
The engine finds the provisions a question needs more often, including questions in
street language, and it says so plainly when the law does not answer a question rather
than guessing.

### G4: Answers sound like SaralPrivacy
Readers judge answers to be in SaralPrivacy's voice (short, practical, Indian business
examples) more often than they judge the current answers to be, with no rise in legal
errors.

### G5: Every provision has a plain-English explainer
Each section of the Act and each rule has an explainer that an 8th-grader can read, and
every sentence of it points to the gazette words it explains.

### G6: Dilip can decide each choice from one sheet
Each open choice (answer model, retrieval changes, voice tuning, the explainer layer, the
shared interface, the third platform's name) has a recommendation, a cost, a risk and a
yes/no line on one page.

## Non-goals

### NG1: Teaching the law to a model's weights
Decided on 2026-11-25. Law changes by notification (for example S.O. 5458(E) on sections
9 and 10), and memorised law cannot follow it.

### NG2: Using competitor or market data
That data stays in the market lane: internal, never stored as knowledge, never indexed,
never used for training.

### NG3: Running a training job in this cycle
This cycle writes the plan, the data preparation and the evals. Any training run waits
for Dilip's yes on the decision sheet.

### NG4: Hindi, Hinglish and other Indian languages
The law files and briefings are English only. Languages are a later cycle.

### NG5: Legal advice for one company's facts
The engine explains the law and gives worked examples. It does not tell a named company
what to do, and it says so.

### NG6: Commentary, opinion and case analysis
Layer 4–5 material is a separate cycle under its own labelling rules.

## Assumptions

### A1: Retrieval, not the answer model, is the main reason questions go unanswered
The offline eval shows 27.5% of expected objects are never retrieved at all, and the
answer model cannot cite what it never sees.
- validate_by: run the live real-corpus eval with retrieval held fixed and the answer
  model swapped (T2); if the answer model changes recall by more than 5 points, this is
  wrong. Week 1.
- if_wrong: the answer model choice moves up the priority list and retrieval work
  shrinks.

### A2: SaralPrivacy's voice can be had from instructions and examples alone
A style guide and 5–8 example briefings in the prompt may reach the voice without any
training.
- validate_by: blind preference test, prompt-only voice against current answers, on 40
  held-out questions (T9). Week 2.
- if_wrong: voice tuning on the briefings goes ahead, subject to the legal-error gate.

### A3: The 208 briefings teach voice without teaching wrong law
They carry no section numbers, and 4 overstate a fine. Once the 4 are fixed, the rest
are assumed to hold no other legal error.
- validate_by: a second legal read of a random 30 of the 204 others, and the invented
  term check run over all 208 (T7). Before any training.
- if_wrong: the bad rows are cut or fixed, and the voice set shrinks.

### A4: The third platform Dilip called "DPDPA sector" is DPDPA Shiksha
- validate_by: Dilip confirms on the decision sheet (D0).
- if_wrong: the client list in the spec changes; the engine does not.

### A5: Questions to the engine may contain personal data, and India hosting is preferred but not required by the Act
Section 16 lets the Central Government restrict transfers to countries it notifies.
Whether any country is notified today has to be checked in the law lane before a
non-India host is used.
- validate_by: check the notifications in the law lane before D1 is signed (T1).
- if_wrong: only India-region hosting options stay on the sheet.

### A6: Readability scores are a fair proxy for "an 8th-grader can read it"
- validate_by: 10 explainers read by two people outside law, who answer three questions
  each about what the provision means (T13). Week 3.
- if_wrong: the gate adds a human comprehension check, and the grade target is reset.

## Success criterion

- leading: on the live real-corpus eval, provision recall rises from 71% to at least
  85%, with 100% of answers free of non-existent provisions and at least 3 of 4
  withheld-support cases refused; checked from the eval report on the first run after
  the retrieval tasks land.
- lagging: of the 101 street questions, at most 5 get no answer (from 17), and blind
  readers prefer the new answers in at least 65% of pairs, with zero new legal errors
  found by the legal review; checked 6 weeks after the engine serves all surfaces.

## Rollback

The engine sits behind a version flag per client. Each client can be pointed back to the
current Ask behaviour by changing its flag, with no data change. A tuned voice is a
separate model setting and can be switched back to the prompt-only voice in the same way.
Explainers are published per provision and can be unpublished one at a time. Nothing in
this plan changes the stored law text, so no data migration needs a down path.
