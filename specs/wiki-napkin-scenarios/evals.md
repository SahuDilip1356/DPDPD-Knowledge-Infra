# Evals: six napkin scenarios on dpdpa.wiki

**Status:** approved by Dilip on 2026-11-26.
**Branch:** `feat/wiki-napkin-scenarios`, cut from `main`.
**Approved mockup:** https://claude.ai/artifact/6SHNGt6inCUBWjJ6jSvxQQ (2026-11-26).

## What gets built

A new page, `/learn/scenarios`, linked from `/learn`, called "Six napkins". It follows one
made-up person (Asha in Pune) and one unnamed tiffin service (the mockup's "TiffinBox" is
dropped, since the course never names a business that could be real). There
are six scenarios, one for each napkin question, and each uses the approved lesson pattern:
a short version, one figure, plain prose, the law's exact words, and a "Try it" question.

| Question | Figure | Figure type |
|---|---|---|
| Who? | the five roles | `roles` (exists) |
| How much? | the Schedule's highest penalties | `scale` (exists) |
| Where? | where Asha's data travels, with the border of India | `map` (new) |
| When? | when the Rules start, and the breach clock | `timeline` (exists) and `steps` (exists) |
| How? | erasure, then grievance, then the Board | `gate` (exists) |
| Why? | is it needed, and did she agree | `plot` (new) |

The content lives in `src/content/scenarios.md`, in the same format as the course modules.

## Risk

Medium. This puts new legal statements on a public page and adds a route. It does not touch
the store, the law file or the backend. A wrong statement can be fixed and redeployed.

## Checks

Command: `cd deployments/dpdpa-wiki && npm run build && npx vitest run`

| # | Check | Pass when |
|---|---|---|
| N1 | Citations are checked | `check:citations` covers `scenarios.md`. A test that adds a citation outside the page's `provisions` list makes it fail |
| N2 | Quotes are exact | every “curly-quoted” fragment on the page appears word for word in the provision it cites (a new test using the law file) |
| N3 | Amounts come from the Schedule | every ₹ amount on the page is one of the Schedule's seven rows. Dates are only the Rule dates in the modules README |
| N4 | The page works without JavaScript | `dist/learn/scenarios/index.html` holds all six headings, all six figures and all six answers, and the route is in `sitemap.xml` |
| N5 | New figure types work | `map` and `plot` render in tests. A malformed spec fails the build. Under reduced motion they render as still images |
| N6 | Colour means role | the figures use only the `ROLES` colours. The site has no dark theme, so this is checked in light only |
| N7 | No regressions | the full build, every vitest suite and the bundle budget test pass |
| N8 | Phone and keyboard | at 375 px wide there is no sideways scroll on the page itself (wide figures scroll inside their own box), and every Try it opens with the keyboard |
| N9 | A first-time reader gets it | an agent that has not read the code answers all six Try it questions from the live preview, in plain words, and names anything it found confusing |

Then a separate code review (sd-code-review). A Vercel preview goes to Dilip before production.

## Revert

`git revert` the merge commit. Nothing outside the wiki changes.
