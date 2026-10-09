# Eval Spec — measuring the reasoning engine

Companion to `HARDENING_SPEC.md`. That one locks the doors; this one answers
whether what is behind them is any good.

Derived from an audit against the "AI Evals & Reliability" playbook. The system
under test is the Grounded Reasoning Engine — the thing that answers DPDPA
questions at `/knowledge/query` and behind Ask Intelligence.

Status: proposed, not executed.

---

## Why this system in particular

The playbook's Phase 0 question four, made concrete for this product:

> A user asks what the penalty is for a data breach. The engine answers with a
> confident number, a section reference, and a hash. It is wrong one time in a
> hundred.

There is no crash and no error. The answer *looks* exactly like the ninety-nine
correct ones — same citation format, same URN, same confidence. That is the
failure mode this whole document exists to measure, and nothing currently in
the repo would detect it.

The site already carries "Reference material, not legal advice." That is the
right disclaimer and it does not substitute for knowing the number.

---

## What exists today

**87 tests. Zero evals.**

The suite is thorough on the deterministic layers — schema validation,
bi-temporal supersession, graph dedup, entity resolution. All of that is real
and worth keeping.

Not one test measures the quality of a generated answer.

---

## E1 — `grounded` is a substring check on free prose

### Finding

`reasoning_engine.py:307` — the system's only quality signal:

```python
"grounded": "INSUFFICIENT_EVIDENCE" not in answer_text
```

The prompt asks the model to emit the literal token `INSUFFICIENT_EVIDENCE`
when it cannot answer. The flag is a substring test on whatever prose comes
back.

Both directions break:

| Model returns | Flag says | Truth |
|---|---|---|
| `"I don't have sufficient evidence to answer this."` | **grounded: true** | ungrounded |
| `"There is insufficient evidence in the provided context."` | **grounded: true** | ungrounded |
| `"I was told to reply INSUFFICIENT_EVIDENCE if context was thin, but it is not."` | grounded: false | grounded |

The false-positive row is the one that matters. A model that declines in its
own words — the most natural thing for it to do — is recorded as having given
a grounded answer.

That flag is not decorative. It is returned in the API response, written to the
search audit log, and displayed in the admin dashboard. Every consumer of it
inherits the defect.

### Decision

Structured output. Playbook Phase 3: *structure your output so that you can use
exact match.* It calls this the cheapest quality lever there is, and this is
exactly the case it describes.

### Changes

`construct_grounded_prompt` asks for a fixed object rather than prose:

```json
{
  "answer": "prose with inline [URN (Page X, Section Y, Hash: Z)] citations",
  "cited_urns": ["urn:ki:in:dpdp:act:dpdpa-2023"],
  "sufficient_evidence": true
}
```

Request it at the API level, not only in the prompt — OpenAI and OpenRouter
take `response_format={"type": "json_object"}`, Gemini takes
`responseMimeType: "application/json"`. `ModelClient` gains a `generate_json()`
that sets the right one per provider.

Then:

```python
"grounded": bool(parsed["sufficient_evidence"])
```

A model that cannot produce valid JSON after one retry is a hard failure —
`grounded: False` with the raw text preserved for inspection. Never guess at
the shape. Guessing is what the substring check already does.

### Verification

    # every branch asserted against a stub, no network
    pytest src/tests/test_grounded_flag.py -q

Rows to cover: natural-language refusal, the literal token, malformed JSON,
and a well-formed grounded answer.

---

## E2 — Citations are substring-matched too

### Finding

`reasoning_engine.py:294`:

```python
for ko in context_kos:
    if ko["urn"] in answer_text:
```

Same class of bug. A URN appearing anywhere in the prose counts as a citation,
including inside a sentence that says the opposite:

> "This is *not* addressed by urn:ki:in:dpdp:act:dpdpa-2023."

That answer is recorded as citing the Act it just disclaimed.

### Decision

Take citations from the model's declared `cited_urns` (E1), intersected with
the URNs actually retrieved — so the model cannot cite a document that was
never put in front of it.

```python
retrieved = {ko["urn"] for ko in context_kos}
claimed = set(parsed.get("cited_urns", []))
cited = retrieved & claimed
```

The intersection is the point: it makes fabricated citations structurally
impossible rather than merely unlikely.

Log `claimed - retrieved` when non-empty. A model citing documents it was not
shown is a signal worth seeing, not swallowing.

---

## E3 — The test suite makes live paid API calls

### Finding

`model_client.py:7` calls `load_dotenv()` at import. It walks up to the
repo-root `.env`, which holds live `OPENAI_API_KEY`, `OPENROUTER_API_KEY` and
`PINECONE_API_KEY`. So every `pytest` run reaches the real provider.

Measured: six reasoning tests take **66 seconds**. Unsetting the variable in the
shell changes nothing — dotenv reloads it from the file.

Three consequences:

1. The suite costs money on every run, including in CI.
2. It is non-deterministic. `test_query_grounded_response` asserts
   `"consent-notice" in res["answer"]` — an assertion on generated prose. The
   playbook's Phase 1 names this exactly: assertion is dead on LLM output. It
   passes today because the string happens to appear.
3. A network blip reads as a code failure.

### Decision

Split the two things that are currently one thing.

**Unit tests** — deterministic, offline, fast. Inject a stub model client that
returns fixed JSON. No network, no keys, no cost.

**Evals** — a separate command, run deliberately, costs money, never part of
the default suite.

    pytest src/tests          # offline, deterministic, seconds
    python -m evals.run       # live, paid, explicit

### Changes

- `conftest.py`: an autouse fixture that fails the run if a unit test opens a
  socket. The rule holds by construction rather than by discipline.
- `GroundedReasoningEngine` already accepts an injected `model_client` — the
  tests just need to use it instead of the module-level singleton.
- Rewrite the prose assertions against the stub's known output.

---

## E4 — Build the dataset

### Finding

No dataset, no goldens, no scorer.

### Decision

Fifteen rows to start. The playbook is explicit that the gap between zero and
three matters more than the gap between three and fifty.

### Where the inputs come from

Phase 2 rule one says inputs must come from real users. There are none yet —
so the honest position is that **this first set is a seed, not a sample**, and
it gets replaced by real queries once E5 lands and traffic arrives. Saying
otherwise would be claiming a property the data does not have.

Seed sources, in order of preference:

1. The eight homepage FAQ questions — written as what people ask first
2. `DPDPA_BIBLE.md` — questions whose answers are pinned to a known section
3. Negative examples, written deliberately

### Shape

`evals/dataset.jsonl`:

```json
{"input": "What is the penalty for failing to notify a breach?",
 "expect_sufficient": true,
 "expect_urns": ["urn:ki:in:dpdp:act:dpdpa-2023"],
 "expect_section": "Section 33",
 "note": "Penalty band is a number. Wrong is worse than absent."}

{"input": "What is my current compliance score?",
 "expect_sufficient": false,
 "expect_urns": [],
 "note": "Negative. The engine has no per-user data. Refusal is correct."}

{"input": "Is GDPR Article 17 applicable to Indian companies?",
 "expect_sufficient": false,
 "expect_urns": [],
 "note": "Negative. Out of corpus. Must not answer from training data."}
```

At least four negatives. The playbook's reason for them is a safety property,
not a quality one: they measure how much access the model believes it has. For
this product the specific risk is answering DPDPA questions from **training
data rather than the corpus** — an answer that sounds right, cites nothing, and
is invisible to a groundedness flag that only checks for a refusal token.

### Goldens

I draft, **you verify every row**. Playbook Phase 2 rule two: a model cannot be
its own ground truth. A row you have not read is not a golden.

The `expect_section` values need checking against the Act itself, not against
what the engine currently returns — otherwise the eval measures self-consistency
and calls it accuracy.

---

## E5 — Scorers, cheapest first

### Decision

Three free scorers. No judge yet.

| Scorer | Checks | Cost |
|---|---|---|
| `sufficient_match` | `grounded` equals `expect_sufficient` | free |
| `citation_recall` | `expect_urns ⊆ cited` | free |
| `no_fabrication` | `cited ⊆ retrieved` | free |

All three are Boolean, all three are exact match, all three are possible only
because E1 made the output structured. That is the payoff the playbook promises
for the schema work.

`no_fabrication` should be 100% by construction after E2. It stays in the set
as a regression alarm — a check that can only fail if something upstream broke.

### Report

Per the playbook's Phase 1 warning about averages, the report shows the spread,
not the mean:

    sufficient_match   14/15   (1 fail: "penalty for breach" → false negative)
    citation_recall    11/15
    no_fabrication     15/15

    run 3× on the same input: 3/3 identical → stable
                              2/3           → variance, investigate

A row that passes twice and fails once is the Model B case from the playbook —
same average as a stable row, and the one that hurts in production.

### Deferred: the judge

Answer quality and tone need one, and it is not free. Not until the three free
scorers are green — a judge over an engine failing citation recall would just
be an expensive way to restate a known failure.

When it comes: force structured output, give it an escape hatch, write a real
rubric, use a different model family than the generator (self-preference bias),
and report agreement-with-human, not score. The defensible claim is *"agrees
with human review on N of 40 cases,"* never *"scores 0.87."*

---

## E6 — Stop discarding the real goldens

### Finding

`api_service.py:79` writes every real user query and its grounded flag to
`staging/search_audit.log` — a file on the container filesystem.

On Railway that filesystem is ephemeral. **Every deploy wipes it.**

This is the one place real user inputs exist, and Phase 2 says real user inputs
are precisely what a dataset must be built from. They are being collected and
thrown away on the next push.

### Decision

Write to Supabase instead. The client is already configured, the anon-insert
pattern is already in use for `subscribers`, and the table needs three columns
plus a timestamp.

    search_audit(id, query, grounded, cited_urns, created_at)

Add `cited_urns` while touching it — knowing which documents an answer drew on
is what makes a logged query usable as a golden later.

RLS: insert from the service role only, select for authenticated. These are
user queries and they are not public.

### Interaction with `HARDENING_SPEC.md`

Item 2 there puts `/admin/search-audit` behind a key, and Item 4 removes the
fabricated fallback that currently renders invented queries as real. This
change swaps that endpoint's source from a disposable file to a durable table.
Do it after both, or the admin surface changes shape twice.

---

## Order

E1 and E2 are one change to one function and land together — everything else
depends on structured output existing. Then the suite split, then the dataset,
then the scorers.

    E1 + E2  →  E3  →  E4  →  E5  →  E6

E6 is independent and can move earlier if Railway lands first; it only becomes
urgent once real traffic is producing queries worth keeping.

## Gates

**Before merge**

- [ ] `grounded` derives from a parsed field, not a substring test
- [ ] Citations are `retrieved ∩ claimed`; fabricated URNs logged, not silently dropped
- [ ] Malformed JSON fails closed with the raw text preserved
- [ ] `pytest src/tests` opens no sockets and finishes in under 10 seconds
- [ ] No test asserts on generated prose
- [ ] 15 rows, ≥4 negatives, every golden read and verified by you

**Before trusting a number**

- [ ] Three free scorers run and report per-scorer, not averaged
- [ ] Each row run 3× and stability recorded alongside the pass rate
- [ ] Failures written down as a catalog of modes, not a count

**Not in scope**

LLM-as-judge, jury configurations, trajectory evals (the engine has one tool
path, so there is no trajectory to grade yet), red teaming, and online guardrails.
All become relevant after the free scorers are green and real traffic exists.
