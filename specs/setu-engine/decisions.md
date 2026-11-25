# Setu engine: decision sheet

**For:** Dilip Sahu · **Date:** 2026-11-25 · **Chain:** [intent](./intent.md) · [spec](./spec.md) · [plan](./plan.md)

Tick one box per decision. Nothing is built or spent until the box is ticked. Settled on
2026-11-25 and not reopened here: law reaches users only by look-up over the verified
law lane, never from model weights; tuning is for voice and format only, on
SaralPrivacy's own writing. The decision is recorded as "Retrieval for law, fine-tuning for
voice only" on PR #12.

## If you still want "a model trained on all DPDPA data"

Here is the learning: a trained model is a student who read the Act once and answers
from memory. A look-up engine is a student who opens the gazette every time and points
at the line. When MeitY issues the next notification, the second student is right the
same day; the first is wrong until someone retrains them, and you cannot tell which
answers they got wrong.

In plain terms:

| | Train the law into a model | Look up the law (chosen) |
|---|---|---|
| A new notification (like S.O. 5458(E)) | Wrong until retrained and re-tested | Right once the notification is added to the law lane |
| Can a reader check a sentence? | No: the model cannot show where it learned it | Yes: every sentence carries the gazette quote |
| What went wrong before | 9 LoRA runs on 28–29 Sep 2026 trained on 33 generic chats and got worse on larger models | Recall rose from 15% to 71% after one prompt fix (PR #9) |
| Data available | About 30K tokens of law: too little to teach law, enough to look up | Same 30K tokens, used whole |
| Cost of a change | A training run plus a full re-test | Re-index one document |

What training can do well is make the engine sound like SaralPrivacy. That is D3.

- [ ] Yes, keep the 2026-11-25 decision (law by look-up, training for voice only)
- [ ] No, I still want law trained into a model. My reason: ______

---

## D0: Which is the third platform?

You said "DPDPA sector". The plan assumes you mean **DPDPA Shiksha**, the learning
platform. That platform would call the engine as `audience: learner`,
`format: lesson`.

- [ ] Yes, it is DPDPA Shiksha
- [ ] No, it is: ______

## D1: Which model reads the provisions and writes the answer?

The model only reads the 5–8 provisions that retrieval hands it and writes from them.
Legal accuracy comes from retrieval and the checker, not from what the model knows. That
is why a small, cheap model can do the job.

All prices were retrieved on 2026-11-25. Each answer is costed at the measured mean of
2,502 prompt tokens (eval baseline) plus 400 output tokens.

| Option | $ in / out per 1M tokens | Per 1,000 answers | Runs in India? | Licence | Source |
|---|---|---|---|---|---|
| **A. gpt-oss-120b on Amazon Bedrock, Mumbai (recommended)** | 0.18 / 0.71 | **$0.73** | Yes: the AWS card lists ap-south-1 as "In-Region" | Apache-2.0, open weights | [AWS model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-oss-120b.html), [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) (price feed, Mumbai) |
| B. gpt-oss-20b on Bedrock, Mumbai | 0.08 / 0.35 | $0.34 | Yes, as for A | Apache-2.0 | [AWS model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-oss-20b.html), same pricing page |
| C. Claude Haiku 5.5 (Anthropic API, or Bedrock Global) | 0.10 / 0.50 | $0.45 ($0.495 if pinned to the US) | No: Bedrock Mumbai and Hyderabad offer "Global" only, and the API's geo setting is "global" or "us" | Proprietary API; this plan has no way to tune it (not checked further) | [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing), [Bedrock regions](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock#regions), [data residency](https://platform.claude.com/docs/en/manage-claude/data-residency) |
| Baseline today: gpt-4o-mini on OpenRouter | 0.15 / 0.60 | $0.62 | No | Proprietary | [OpenRouter endpoints](https://openrouter.ai/api/v1/models/openai/gpt-4o-mini/endpoints) |
| Not recommended: gpt-oss-120b through OpenRouter, cheapest provider | 0.03 / 0.15 | $0.14 | No endpoint is tagged India | Apache-2.0 | [OpenRouter endpoints](https://openrouter.ai/api/v1/models/openai/gpt-oss-120b/endpoints) |
| Not recommended: Claude Sonnet 5.5 | 2 / 10 | $9.00 | No | Proprietary | [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| Not recommended: Sarvam 105B | ₹10 / ₹25 | ₹35 | Not stated on the pricing page | Apache-2.0 | [Sarvam pricing](https://www.sarvam.ai/api-pricing) ("introductory pricing") |

At 30,000 answers a month, A costs about $22 a month and C about $14. Every option
except Sonnet fits the spec's cap of $3 per 1,000 answers.

**Latency:** no provider publishes it. OpenRouter's latency and throughput fields are
empty for every gpt-oss endpoint. T2 measures p50 and p95 on the live eval for each
candidate before anything is switched over.

**Two caveats:**
- gpt-oss counts its reasoning as output tokens, so real output may be well above 400.
  T2 measures actual tokens. Even at 3× the output, A stays under $1.60 per 1,000.
- Before India hosting can be called a requirement, T1 checks the law lane: section 16
  notifications, the Rules' provision on transfers outside India, and sector rules that
  section 16(2) keeps in force (assumption A5).

Hosting check result: [NEED: T1 fills this in before you sign D1]

**Why A:** it is the only strong option that keeps questions, which may hold personal
data, inside India. It is open-weight, so a voice adapter (D3) can be trained on its
smaller sibling. It is near the price of today's model. C may write better and costs
less. If you rule that hosting in India is not needed, T2's bake-off decides between A
and C on the eval.

**Rule for the bake-off (T2):** every option must have zero non-existent provisions. Pick
the cheapest India-hosted option that scores within 3 points of the best option on
recall and refusals. If no India-hosted option is within 3 points, this sheet comes back
to you with the numbers.

**Linked to D3:** if you also say yes to tuning in D3 and tuning wins, answers move from
120b to gpt-oss-20b plus the adapter. That reader must pass the same rule, and must be
servable from Mumbai (T10 checks). If it cannot be served from Mumbai, D3 comes back to
you.

- [ ] Yes: A, decided by the T2 bake-off against B and C under the rule above
- [ ] Yes, but India hosting is not required: let T2 choose freely among A, B and C
- [ ] No, use: ______

## D2: Which three retrieval changes first?

What exists today: Pinecone vector search returns the top 5 objects. A BM25 word search
(keyword_ranker.py) runs only as a fallback: when Pinecone is down, unconfigured, or
returns no match above its score floor. The 64-case real-corpus eval
(evals/runner.py) scores offline recall at 44.7%, full recall at 25%, and 72.5% of the
expected objects retrieved. Live recall after PR #9 is 71%. Answers were withheld in 17
of the 101 street questions.

| # | Change | What it fixes | Cost | Measured by |
|---|---|---|---|---|
| R1 | Run vector and word search together, merge the lists, then rerank 20 candidates down to 5 (T3, T4) | A question whose exact words match a provision that vector search ranks low, and the reverse | Reranker calls at a fraction of a cent per question; no new data | Expected-in-retrieved from 72.5% to at least 90% |
| R2 | Follow each retrieved provision to the section 2 definitions and the rules it links to (T5) | "What is a Significant Data Fiduciary's duty?" needs section 10 *and* the rule on audits | None; uses the existing graph links, capped at 3 extra objects | Full recall from 25% upward; answers carry the rule's start date |
| R3 | Rewrite street words into the law's terms with a reviewed glossary, such as "data leak" to "personal data breach" (T6) | The 17 street questions with no answer | Your review time on the glossary | Unanswered street questions from 17 to at most 5 |

Not chosen this cycle: smaller chunks (sub-section-level objects). That needs a
re-index, which is a live store write you run, and R1–R3 come first.

- [ ] Yes, R1, R2 and R3 in that order
- [ ] Change the order or set: ______

## D3: Tune the voice, and how?

**Data:** the 208 briefings (24 Mar to 25 Oct 2026, about 112K tokens) in
`staging/own/briefings/`. First, fix the 4 briefings in REVIEW-BEFORE-PUBLISHING.md
(2026-05-13, 06-04, 08-31, 09-30), on the website and then in the dataset. Then hold
out 40 for testing and train on 168 (T7). Never use law text, competitor text or
machine-suggested labels.

**Step 1, no training (recommended first):** write a voice guide with 5–8 example
briefings into the prompt (T9), then run the blind test below. Cost: only eval runs, a
few cents each.

**Step 2, only if step 1 loses the blind test:** train a LoRA adapter.

| Where | Base model | Cost for 168 rows × 3 epochs (about 0.3M training tokens) | Note | Source |
|---|---|---|---|---|
| **Hugging Face Jobs, your account (recommended)** | gpt-oss-20b (sibling of D1's A) | A100 80 GB at $2.50/hour, billed per minute. Estimate 1–2 hours, so $2.50–$5. Not measured; T10's dry run estimates it | Adapter goes to a private repo you own; data stays in your account | [HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing) |
| Together AI hosted fine-tune | gpt-oss-20b | $0.40 per 1M tokens, $4 minimum, so $4 | Data leaves to Together | [Together pricing](https://www.together.ai/pricing) |
| OpenAI hosted fine-tune | gpt-4.1-mini | Not available: "closed to new users" | Ruled out | [OpenAI pricing](https://developers.openai.com/api/docs/pricing) |

**The catch:** a tuned adapter has to be served somewhere. This research did not confirm
that Bedrock Mumbai can serve a custom gpt-oss adapter. If it cannot, tuning trades India
hosting for voice. T10 checks this before any run. Tuning also means answers come from
gpt-oss-20b plus the adapter, not from 120b, so the tuned reader must pass the same T2
eval rule as D1. We cannot tune a Claude model, so if D1 lands on C, only step 1
applies.

**Eval that decides it (AC13):** 40 held-out questions, each answered by today's engine
and by the new voice. Two readers see each pair blind, with sides shuffled. The new
voice must win at least 65% of pairs. On the live eval, recall, refusals and "no
non-existent provision" must be no worse. The invented-term check must find no term
outside the law, such as "Data Personal Breach Inquiry". Budget cap for all of D3:
USD 25.

- [ ] Yes: fix the 4 briefings, try prompt-only, and tune on HF Jobs only if it loses the blind test
- [ ] Yes, but skip tuning entirely; prompt-only voice is enough
- [ ] No: ______

## D4: Plain-English explainers, built how?

Each of the 44 sections and 23 rules gets an explainer. Each sentence carries the
gazette words it explains, and a check confirms those words appear verbatim (T13).
A grade gate requires Flesch-Kincaid grade 8.0 or lower, with the Act's defined terms
(such as "Data Fiduciary") masked so they don't count against it. A model may draft;
a person signs each explainer before readers see it (T14). Ten explainers are also read
by two people outside law, who answer three questions each, to check that grade 8
really means readable (T15).

Cost: about 67 drafts at well under $0.01 each, plus review time: about 10 minutes per
explainer, or 11 hours in all.

- [ ] Yes, as described, with me signing (or name a co-signer: ______)
- [ ] Yes, but start with the 10 most-asked provisions only
- [ ] No: ______

## D5: One interface for every surface

One endpoint, `POST /v1/answer` (see the spec). Each client sends `audience`
(business, learner, public) and `format` (chat, card, lesson). Only the wording
changes; the law and citations are the same everywhere (AC1). Each client gets its own
key and rate limit. Questions are logged for 90 days with card and PAN-like numbers
removed. Explainers come from `GET /v1/explainers/{urn}`.

| Client | Sends |
|---|---|
| dpdpa.wiki Ask | public, chat |
| Setu chatbot (on the wiki and saralprivacy.com) | business or public, chat, with a conversation_id |
| saralprivacy.com briefing pages | business, card |
| Third platform (D0) | learner, lesson |

The current `/knowledge/query` keeps working. The wiki moves to `/v1/answer` behind a
flag (T16), and switches over only after the live eval and the street set pass.

- [ ] Yes
- [ ] No / change: ______

## D6: Order of work and what needs you

Order: T1, T2 and T8 first (the facts, the bake-off and the checker), then retrieval
(T3–T6), refusals (T17), the interface (T11, T12, T16, T18, T19), voice (T7, T9, T10)
and explainers (T13–T15). The project rules still describe GPT-OSS as "a retrieval
model over the graph, not weight training"; PR #12 updates them to the voice-only
wording, so no rules change is made here.
You are needed for: every live eval run (cents each), the glossary review, the voice
prompt text, the 4 briefing fixes, explainer sign-off, the explainer table migration and
any training run.

- [ ] Yes, this order
- [ ] Change: ______

## Sources and gaps

Full price research with every figure, its URL and its arithmetic, retrieved 2026-11-25,
is in the shared notes folder for this session group as `setu-engine-pricing.md`.

Not confirmed:
- Azure Central India and Google asia-south1 hosting for gpt-oss or Claude. Not
  checked.
- Claude's Bedrock price in Mumbai.
- Whether Bedrock can serve a custom gpt-oss adapter in Mumbai. T10 checks this.
- Published latency for any option. T2 measures it.
- The sources disagree on Bedrock's gpt-oss-20b output price: the AWS price feed says
  $0.30 per 1M in N. Virginia, while OpenRouter lists $0.15.
