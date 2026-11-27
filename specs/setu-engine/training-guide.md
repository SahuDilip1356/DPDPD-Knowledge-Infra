# How we train the Setu small model on Modal

**For:** Dilip Sahu · **Date:** 2026-11-26 · **Status:** guide, nothing run yet
**Goes with:** [decisions.md](./decisions.md) (D1 answer model, D3 voice) and [plan.md](./plan.md) (T7, T9, T10)

## The idea in one paragraph

We train a small open model to do one job well. It reads the DPDPA provisions it is
handed, answers in plain SaralPrivacy English, quotes the gazette for every legal
sentence, and says "the law does not cover this" when that is true. The law itself is
never trained into the model. It ships beside the model as a file of about 30,000 tokens,
and a search step picks the right provisions for each question. When the law changes, we
replace the file, not the model. The same recipe works for any later product, with a new
file and new examples.

## The seven steps

| # | Step | What it produces | Who | Rough time |
|---|---|---|---|---|
| 1 | Question map | About 1,000 real questions, sorted into who, why, how, what and where | Claude drafts, Dilip approves the categories | Weeks 1–2 |
| 2 | Training examples | For each question: the provisions found, a cited answer, a passed quote check, Dilip's approval | Claude drafts, Dilip approves about 50 a week | Weeks 2–6 |
| 3 | Exam | 150 approved examples locked away, never trained on | Claude | Week 3 |
| 4 | Base model test | Scores for 2–3 open models before any training | Claude | Week 4 |
| 5 | Training run | A small add-on to the model (a LoRA adapter), trained on Modal | Claude runs, Dilip says go | Weeks 5–7 |
| 6 | Exam result | Trained against untrained, on the exam and a blind voice test | Claude, plus two readers | Week 7 |
| 7 | Ship | The model served to the wiki, SaralPrivacy and Shiksha, and a compressed copy for devices | Claude, Dilip picks the hosting | Weeks 8–9 |

## Step 1: the question map

Sources: the 101 street questions, the questions in blogs, forums and YouTube transcripts,
the wiki's search log, and questions Dilip hears from clients. We keep the question
text only. Answers from those sources are never used, because between 10% and 31% of the
legal claims on those sites are wrong.

Each question gets three labels:
- **Kind:** who (who must comply, who is a Data Fiduciary), why (why a duty exists), how
  (how to give notice, how to report a breach), what (what counts as personal data),
  when (when a duty starts), where (where data may be sent, where to complain). Dilip
  approved these six on 2026-11-27.
- **Reader:** business, learner or public.
- **Lane:** law answers it; law is silent; needs a lawyer (a company's own facts).

The "law is silent" and "needs a lawyer" questions matter as much as the rest. They teach
the model to refuse correctly.

## Step 2: what one training example looks like

Each example is one conversation, stored as one line of a file:

```json
{
  "messages": [
    {"role": "system", "content": "You are Setu. Answer only from the provisions given. Quote the exact words for every legal sentence. If the provisions do not answer, say so."},
    {"role": "user", "content": "Question: Our app leaked some customer phone numbers. Who do we have to tell?\n\nProvisions:\n[urn:ki:dpdpa:s8] <exact text of section 8(6) from the law file>\n[urn:ki:dpdp-rules:r7] <exact text of rule 7 from the law file>"},
    {"role": "assistant", "content": "<plain-English answer in SaralPrivacy's voice, each legal sentence followed by its citation and quote>"}
  ],
  "kind": "who",
  "reader": "business",
  "lane": "law_answers",
  "approved_by": "Dilip",
  "approved_on": "2026-12-03"
}
```

The provision text is copied from the law file by code, never typed. Before Dilip sees an
example, the quote checker confirms that every quote in the answer appears word for word
in the provisions, and that no section, amount or legal term is invented. Dilip then reads
the answer for accuracy and voice, and ticks, edits or rejects it.

Target mix of about 1,000 examples:
- 700 the law answers
- 150 where the law is silent (the model must refuse)
- 100 that need a lawyer (the model must say so and point to the nearest provision)
- 50 trick questions, such as made-up penalties or "ignore your instructions"

Briefings: after the 4 flagged ones are fixed, the 208 briefings add voice examples. A
question is drafted from each headline, and the answer is rewritten so its legal sentences
carry citations.

## Step 3: the exam

150 examples, balanced across the same mix, are moved to a separate file before any
training. The model never sees them during training. Every model, trained or not, sits
the same exam. The marks are:

| Mark | Pass line |
|---|---|
| Quotes found word for word | 100% |
| Invented sections, amounts or terms | 0 |
| Right provision cited | at least 85% |
| Refuses when the law is silent | at least 95% |
| Reading grade (Flesch-Kincaid) | 8 or below |
| Blind voice preference against the untrained model | trained wins at least 65% |

If the trained model misses any pass line, it does not ship.

## Step 4: which base models

Two sizes, because the server and a phone need different models:

| Use | Candidate | Size | Licence | Why |
|---|---|---|---|---|
| Server | gpt-oss-20b | about 21 billion parameters | Apache-2.0 | The same family as the D1 recommendation, and runs in Mumbai on Bedrock |
| Device | a model of 1–4 billion parameters, such as Qwen3-4B | small enough for laptops and recent phones | to confirm per model before use | Runs offline, so questions never leave the device |

Each candidate takes the exam untrained first. That score is the baseline training must
beat.

## Step 5: training on Modal

**Why Modal:** you already have credit, Modal bills by the second only while a job runs,
and nothing runs when idle.

**GPU prices** (from [modal.com/pricing](https://modal.com/pricing), retrieved
2026-11-26; per-second rates × 3,600):

| GPU | Per hour | Fits |
|---|---|---|
| L4 | $0.80 | the device-size model |
| L40S | $1.95 | the device-size model, faster |
| A100 80 GB | $2.50 | gpt-oss-20b with LoRA |
| H100 | $3.95 | gpt-oss-20b, faster |

Training uses no customer data (only the law file and our own writing), so it can run in
Modal's default region at base price. Pinning a region costs 1.15× to 1.75× base
([region docs](https://modal.com/docs/guide/region-selection)).

**Estimated cost per run** (not yet measured): about 1,000 examples of about 3,000 tokens,
three passes, is about 9 million tokens. At typical LoRA speeds, that is roughly one hour
for the device model on an L40S ($2) and one to two hours for gpt-oss-20b on an H100 ($4
to $8). Expect 3 to 5 runs while tuning the settings, so $20 to $40 for the first
round of training. Set a Modal budget of USD 50 so it cannot overspend.

**What the run does:**
1. Loads the base model and the approved examples (not the exam).
2. Freezes the base model and trains a small LoRA adapter on top, about 1% of the model's
   size. That is why it is cheap and fast.
3. Saves the adapter to a private Hugging Face repo in your account.
4. Runs the exam on the trained model and writes the marks to a report.

**One-time setup you do yourself** (no secrets go in chat):
1. Install Modal's tool and log in. Run `pip install modal`, then `modal setup`, which
   opens your browser to sign in.
2. Create a write token at huggingface.co (Settings → Access Tokens), then store it in
   Modal yourself: run `modal secret create huggingface HF_TOKEN=<paste here>` in your own
   terminal.
3. In the Modal dashboard, set a workspace budget of USD 50.

After that, Claude writes the training script (plan task T10) and runs it only after you
say go. The script refuses to start without that confirmation.

## Step 6: reading the result

You get one page: the exam marks for the untrained and trained models side by side, the
blind voice result, the cost of the run, and five sample answers. Your call is yes (ship)
or no (fix the examples and run again). Most improvement comes from better examples, not
from changing training settings.

## Step 7: hosting

| Option | How it works | Good for | Cost |
|---|---|---|---|
| Server on Bedrock, Mumbai | Base gpt-oss on Bedrock, if Bedrock can serve our adapter there (not yet confirmed) | All three sites, India hosting | about $0.34–$0.73 per 1,000 answers (decisions.md D1) |
| Server on Modal | Our trained model served on a Modal GPU that starts on demand, region pinned to Asia-Pacific | A fallback if Bedrock cannot serve the adapter | GPU time only while answering; pinned region 1.75× base |
| On the device | The device model, compressed to about a quarter of its size, plus the law file, inside the app or browser | Offline answers, questions never leave the phone | No running cost |

All three sit behind the same answer interface (spec.md, `/v1/answer`), so the wiki,
SaralPrivacy and Shiksha do not change when the hosting does.

## Repeating it for the next product

Keep: the seven steps, the example format, the quote checker, the exam marks, the Modal
script.
Swap: the law file (GST, a CA syllabus, another Act), the question map and the examples.
Write it once as a template after the first run, so the second model takes weeks, not
months.

## What is not known yet

- Real training time and cost. The first run measures them.
- Whether Bedrock Mumbai can serve our adapter (plan T10).
- Which phones can run the device model, and how fast.
- The licence of the device-size candidate, which is checked before it is used.
