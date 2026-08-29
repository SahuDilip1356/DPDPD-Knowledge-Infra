# Current State

_Last updated: 2026-08-29 20:25 · mid-session checkpoint_

## Handoff (auto-summary — no explicit block found)


**git diff --stat:**
```
.agent/CURRENT.md                      | 65 +++++++++++++--------------------
 .agent/sessions/2026-08-22-90c6538c.md | 67 ++++++++++++++++++++++++++++++++++
 2 files changed, 92 insertions(+), 40 deletions(-)
 2 files changed, 92 insertions(+), 40 deletions(-)
```

**Topics this session:**
- Sidebar hyperlink is not aligned with the subject

**Key points / decisions:**
- What was wrong
- The fix
- Also added

**Last assistant note:**
rights-do-your-customers-employees-and-candidates-have  emitted=true
```

## Also added

The sidebar now **tracks your scroll position** — the active section is marked as you read. Previously it showed where you could go but never where you were, which in a 7,000-word document is most of what a contents list is for. Marked with a saffron rule on the left edge plus weight, not colour alone.

Pushed as `5f7265c`; I'm watching for the deploy and will confirm.

Once it's up, reload and click a few TOC entries — they should now jump to the right section, and the sidebar should follow as you scroll.
