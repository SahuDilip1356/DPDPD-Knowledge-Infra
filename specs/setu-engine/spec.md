# Spec: Setu engine

**Status:** draft
**Intent:** ./intent.md
**Date:** 2026-11-25
**Decision sheet:** ./decisions.md (the choices Dilip signs, with prices and sources)

## Behavior

A client (the wiki, saralprivacy.com, the Setu chatbot or the third platform) sends a
DPDPA question and says who is asking (business, learner or public) and what shape it
wants (a chat reply, a short card or a lesson block). The engine rewrites street words
into the law's own terms, looks up the provisions that answer the question, follows
their links to the definitions and rules they depend on, and passes only those
provisions to the answer model. The answer model writes in SaralPrivacy's voice, and
every legal sentence it writes carries a citation and a word-for-word quote. Before the
answer leaves, a checker confirms each quote appears in the official text, each cited
provision exists, and no legal term appears that the law does not use. If a check
fails, the engine refuses with a reason rather than sending a weaker answer. Each answer
names when the cited duties start to apply. For each provision there is also a stored
plain-English explainer that any client can fetch and show next to the answer.

## UX flow

The engine has no screens of its own. Each client keeps its own. What a reader sees
changes as follows.

Current (wiki Ask only):
- reader types a question → Ask → answer in statute style with citations, or "not
  enough evidence"
- saralprivacy.com, Setu chatbot, third platform → no grounded answer path

Desired (every client):
- reader types a question → client sends it with audience and format → answer in
  SaralPrivacy's voice → each legal sentence shows its citation; tapping it shows the
  gazette quote and the official link
- answer cites a provision → "In plain English" panel shows that provision's explainer
- engine cannot answer → reader sees why ("the Act does not cover this", "this is about
  your company's facts, which needs a lawyer") and a link to the nearest provision
- answer model unavailable → reader sees "try again shortly", never a refusal

## Contracts

### Answer request

`POST /v1/answer`, authenticated with a per-client key in the `Authorization` header.

```json
{
  "question": "string, 3–1000 chars",
  "audience": "business | learner | public",
  "format": "chat | card | lesson",
  "conversation_id": "string, optional, for follow-ups in the chatbot",
  "as_of": "YYYY-MM-DD, optional; defaults to today"
}
```

### Answer response (200)

```json
{
  "status": "answered | refused",
  "answer": "string; empty when refused",
  "claims": [
    {
      "text": "one sentence of the answer",
      "urn": "urn:ki:...",
      "quote": "exact words from the official text",
      "source_url": "official URL",
      "in_force_from": "YYYY-MM-DD | null"
    }
  ],
  "explainers": [{"urn": "urn:ki:...", "explainer_id": "string"}],
  "refusal": {"code": "out_of_scope | not_in_law | needs_advice | check_failed", "reason": "string"},
  "engine_version": "string",
  "voice_version": "string",
  "trace_id": "string"
}
```

`refusal` is present only when `status` is `refused`. Every `claims[].quote` is a
substring of the official text of `claims[].urn`.

### Explainer

`GET /v1/explainers/{urn}` returns:

```json
{
  "urn": "urn:ki:...",
  "sentences": [{"text": "plain sentence", "quote": "gazette words it explains"}],
  "grade_level": 7.4,
  "reviewed_by": "string",
  "reviewed_on": "YYYY-MM-DD",
  "status": "published | draft"
}
```

Only `published` explainers are returned to clients; others return 404.

### Errors

| Code | When | Body |
|---|---|---|
| 400 | question missing, too short or too long; unknown audience or format | `{"error": "invalid_request", "field": "..."}` |
| 401 | missing or unknown client key | `{"error": "unauthorized"}` |
| 429 | client over its rate limit | `{"error": "rate_limited"}`, `Retry-After` header |
| 404 | explainer not found or not published | `{"error": "not_found"}` |
| 500 | unexpected engine failure | `{"error": "internal"}`; the trace id is logged |
| 503 | answer model or retrieval store unreachable | `{"error": "unavailable"}`, `Retry-After` header |

## System context

Parts by role:

- **Clients**: the wiki, saralprivacy.com, the Setu chatbot, the third platform. Each
  holds its own key and renders answers its own way.
- **The engine's front door**: checks the key, the rate limit and the request shape,
  strips card numbers and PAN-like strings from the question before it is logged.
- **The query rewriter**: maps street words to the law's terms using a curated
  glossary. It never adds a fact.
- **Retrieval**: runs meaning-based search and word-based search together, merges the
  two lists, reranks them, then adds the linked definitions and rules.
- **The answer model**: an outside model service that sees only the question and the
  retrieved provisions.
- **The checker**: confirms quotes, provision ids and legal terms against the law lane.
- **The law lane store**: the Act, the Rules and the registered official sources, checked
  by the corpus contract. Read-only to the engine.
- **The explainer store**: published explainers, each tied to one provision.

Where data lives:

| Data | Kept where | Leaves the engine? |
|---|---|---|
| Question text | request log, with card and PAN-like strings removed, 90 days | Yes: sent to the answer model service |
| Retrieved provisions | law lane store | Yes: sent to the answer model service |
| Answer and claims | request log, 90 days | Yes: returned to the client |
| Client keys | secret store | No |
| Explainers | explainer store | Yes: returned to clients, shown publicly |
| Voice training set | private dataset in Dilip's account | Only to the training job, if D3 is yes |

Trust boundaries: client to engine (untrusted question text, possible prompt
injection); engine to answer model service (question and law leave our hosting; the
region and retention depend on D1); answer model output to the checker (model output is
untrusted until checked); explainer drafts to publishing (a human signs each one).

## Alternatives considered

| Choice | Chosen | Rejected | Why |
|---|---|---|---|
| Where the law comes from | Look-up over the verified law lane | A model trained on all DPDPA data | Decided 2026-11-25. Weights cannot follow amendments; earlier tuning runs got worse; competitor text disagrees with the gazette |
| Failing a check | Refuse with a reason | Send the answer with a warning | A wrong legal sentence with a warning still gets copied into a policy |
| One engine or one per surface | One engine, one contract, audience and format as inputs | Separate prompts and stores per surface | Separate copies drift; the same question would get different law |
| Voice | Prompt-only voice first; tune only if the blind test says prompt-only falls short | Tune first | Tuning costs money and risk; the prompt may be enough (A2) |
| Explainers | Written once per provision, reviewed, stored | Generated live for each answer | Live text cannot be reviewed; stored text can be read, graded and signed |
| Retrieval when one search path is down | Use the other path alone and mark the answer `degraded` in the log | Refuse every question | One path alone still answers most questions; the checker still guards every claim |

## Risks & mitigations

| # | Risk | Type | Mitigation | Status | Tested by |
|---|---|---|---|---|---|
| K1 | The answer model invents a term or provision | failure | Checker refuses any claim whose quote, id or legal term is not in the law lane | mitigated | AC4, AC5 |
| K2 | A question carries an instruction to ignore the law or reveal the prompt | security | Input guard refuses known patterns; the model sees provisions only; the checker checks whatever the model writes | mitigated | AC9 |
| K3 | Questions with personal data leave India | privacy | D1 prefers an India-region option; logs drop card and PAN-like strings | open | AC10, D1 |
| K4 | Voice tuning teaches the overstated fines in 4 briefings | failure | The 4 are fixed and the invented-term check runs over the set before any training | mitigated | AC12 |
| K5 | A plain-English sentence drifts from what the law says | failure | Each sentence carries its gazette quote; a human signs each explainer | mitigated | AC14, AC15 |
| K6 | Answer model price changes | scale | Cost per answer logged; switching models is a setting | accepted | NF2 |
| K7 | A client stops getting answers when the model service is down | failure | 503 with retry, never a refusal; second provider configurable | mitigated | AC8 |
| K8 | Street-word glossary maps a word to the wrong legal term | failure | Glossary entries are reviewed; the checker still refuses unsupported claims | open | AC3 |

## Boundaries

- Always: run the live real-corpus eval and the street-question set before and after
  any change to retrieval, prompts or the answer model, and put both reports in the PR.
- Always: keep the law lane read-only from the engine.
- Ask first: any change to the answer prompt, the checker, the glossary, the training
  set or the choice of answer model; any spend over USD 5 on one eval or training run;
  any live store write (Dilip runs those).
- Never: put competitor or market data into retrieval, prompts, glossary, explainers or
  training data.
- Never: train on law text, or start a training run without Dilip's yes on D3.
- Never: return an answer whose checks failed.

## Acceptance criteria

### AC1: Every client gets the same law for the same question
- traces: G1
- given: two clients with valid keys
- when: each sends the same question with the same `as_of`, one as `business/chat` and
  one as `learner/lesson`
- then: both responses cite the same set of URNs and the same `in_force_from` dates; only
  wording and length differ; both log lines carry the same `engine_version`

### AC2: Retrieval finds more of the expected provisions
- traces: G3
- given: the 64-case real-corpus golden set, run live
- when: the eval runs after the retrieval tasks land
- then: mean provision recall is at least 0.85 and expected-in-retrieved is at least
  0.90, reported in the eval output

### AC3: Street questions reach the law's terms
- traces: G3
- given: the 101 street questions
- when: they are run through the engine
- then: at most 5 return `refused` with code `not_in_law` where the law does answer
  them, and each glossary mapping used is listed in the trace

### AC4: Every quote is word for word
- traces: G2
- given: any answered response
- when: the checker runs
- then: every `claims[].quote` is one unbroken run of at least 6 words found, with exact
  case and only whitespace normalised, in the official text of its URN; a quote with "…",
  "..." or any elision fails; a response with even one failing quote is returned as `refused` with code `check_failed`
  and the failed claim is in the log

### AC5: No invented provisions or terms
- traces: G2
- given: an answer that names a section, rule, penalty amount or capitalised legal term
- when: the checker runs
- then: a section or rule that does not exist, an amount not in the Schedule, or a
  capitalised legal term found neither in the law lane nor on the reviewed allowlist of
  names (such as India, RBI, Aadhaar, SaralPrivacy) turns the response into
  `refused/check_failed`; "Data Personal Breach Inquiry" fails, "RBI" passes

### AC6: The engine refuses when the law does not answer
- traces: G3
- given: the 4 withheld-support cases and 10 out-of-scope questions (foreign law,
  traffic fines, a company's own revenue)
- when: they are sent
- then: 4 of 4 withheld cases and 10 of 10 out-of-scope questions are refused
  with the right code and a reason the reader can follow

### AC7: Answers say when duties start
- traces: G2
- given: a question about a rule that applies from 13 May 2027
- when: it is answered with `as_of` before that date
- then: the claim's `in_force_from` is `2027-05-13` and the answer text says the duty
  starts on that date

### AC8: An outage is not a refusal
- traces: G1
- given: the answer model service returns errors or times out
- when: a client sends a question
- then: the engine returns 503 with `Retry-After`, logs the outage, and the eval counts
  it as an error, not a refusal

### AC9: Injection attempts are refused
- traces: G2
- given: a question that asks to ignore instructions, reveal the prompt, or state a fine
  the Act does not contain
- when: it is sent
- then: the response is `refused` with code `out_of_scope` or `check_failed`, and no
  prompt text appears in it

### AC10: Personal identifiers are not logged
- traces: G1
- given: a question containing a 16-digit card number or a PAN-like string
- when: it is logged
- then: the logged question has those strings replaced by `[removed]`

### AC11: Bad requests get a clear error
- traces: G1
- given: a request with no key, an unknown key, a missing question, a 1,500-char
  question or `audience: "lawyer"`
- when: it is sent
- then: the response is 401 or 400 with the body in the Errors table, naming the field

### AC12: The voice set is clean before any training
- traces: G4
- given: the 208 briefings
- when: the voice set is built
- then: the 4 flagged briefings are fixed or removed, the invented-term check finds no
  term outside the law lane, 40 briefings are held out for testing, and the set carries
  no law text and no competitor text

### AC13: The chosen voice beats the current one without new legal errors
- traces: G4
- given: 40 held-out questions answered by the current engine and by the chosen voice
  (prompt-only or tuned)
- when: two blind readers compare each pair and the live eval is run with the chosen
  voice
- then: the chosen voice wins at least 65% of pairs (each held-out briefing becomes one
  question, drafted from its headline and edited by Dilip before the test), and recall, no-nonexistent-provision
  and refusal scores are no lower than with the current voice

### AC14: Every explainer sentence points to gazette words
- traces: G5
- given: a draft explainer
- when: it is checked
- then: every sentence carries a quote, every quote is found verbatim in the provision's
  official text, and a sentence with no quote blocks publishing

### AC15: Explainers read at grade 8 or below
- traces: G5
- given: a draft explainer
- when: it is graded
- then: its reading grade (Flesch-Kincaid, ignoring the defined terms of the Act listed in
  section 2) is 8.0 or lower, a higher grade blocks publishing, and the grade is stored

### AC16: Only signed explainers reach readers
- traces: G5
- given: an explainer that passed AC14 and AC15
- when: no reviewer has signed it
- then: `GET /v1/explainers/{urn}` returns 404 until a reviewer name and date are set

### AC17: One decision sheet covers every choice
- traces: G6
- given: the decision sheet
- when: Dilip reads it
- then: each choice D0–D6 has a recommendation, at least one alternative, a cost with
  its source and date, the main risk, and an empty yes/no line

### AC18: The answer text holds no unchecked legal statement
- traces: G2
- given: an answered response
- when: the checker runs
- then: `answer` is built only from the `claims[].text` sentences plus connecting
  sentences; a connecting sentence that names a section, rule, amount, deadline or
  capitalised legal term fails the response as `refused/check_failed`

### AC19: Each answer's cost is logged and old logs are deleted
- traces: G1
- given: answered and refused requests over time
- when: each request completes, and when the daily clean-up runs
- then: the log line carries input tokens, output tokens and USD cost; log lines older
  than 90 days are gone after the next clean-up, and the clean-up logs how many it removed

### AC20: The chatbot can stream and follow up
- traces: G1
- given: a chat client that sends a `conversation_id` and asks for a stream
- when: it sends a follow-up such as "what about children?"
- then: the first words arrive within 2 s; retrieval uses the follow-up plus the previous
  question only (no earlier answers); claims are checked before the stream is marked
  final, and a failed check replaces the streamed text with the refusal

## Non-functional

- NF1: latency: p50 under 4 s and p95 under 10 s for a full answer, measured on the live
  eval; a streaming client sees its first words within 2 s.
- NF2: cost: answer model cost at most USD 3 per 1,000 answers at today's prices
  (about 2,500 input and 400 output tokens each); actual cost per answer logged.
- NF3: availability: 99% monthly for `/v1/answer` excluding outages of the answer model
  service, which return 503.
- NF4: retention: request logs kept 90 days, then deleted.
- NF5: rate limits: per-client limit set in config; default 60 requests a minute.

## Out of scope

Mirrors the intent's non-goals: no law in weights (NG1), no market data (NG2), no
training run this cycle (NG3), English only (NG4), no company-specific advice (NG5), no
commentary (NG6). Also out: user accounts and saved chat history inside the engine
(clients keep their own), and payment or quota per end user.

## Open questions

- Q1: Is the third platform DPDPA Shiksha? Owner: Dilip, by 2026-11-28. Blocks the client
  list in AC1 only (D0).
- Q2: Which answer model? Owner: Dilip, by 2026-11-28. Blocks NF1, NF2 and AC13 (D1).
- Q3: Is India-region hosting required, or only preferred? Owner: Dilip after the
  Section 16 check, by 2026-11-28. Blocks D1 and K3.
- Q4: Who besides Dilip signs explainers? Owner: Dilip, by 2026-12-05. Blocks AC16.
