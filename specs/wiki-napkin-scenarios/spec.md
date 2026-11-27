# Spec: six napkin scenarios on dpdpa.wiki

Evals: `evals.md` (N1–N9).

## Acceptance criteria

### AC1 — The page exists and reads without JavaScript
- traces: G1
- given: a production build
- when: `/learn/scenarios` is prerendered
- then: the HTML holds six scenarios, each with a short version, a figure and a question
        to try with its answer, and the route is in the sitemap and linked from `/learn`

### AC2 — Map and plot figures render
- traces: G1
- given: a figure spec of type `map` or `plot`
- when: it renders on the server
- then: every place, route, point and verdict is in the markup, and nothing is hidden
        until JavaScript runs

### AC3 — The citation gate covers the page
- traces: G2
- given: `src/content/scenarios.md`
- when: `check-citations.mjs` runs
- then: it passes, and fails when the page cites a provision outside its list

### AC4 — Quotes, amounts and dates are exact
- traces: G2
- given: the page source and the law file
- when: the scenario tests run
- then: every curly-quoted fragment is found in the provision it cites, every ₹ amount
        is a Schedule row, and every date is a Rule start date

### AC5 — Phone width and keyboard
- traces: G1
- given: the built page at 375 px
- when: it is opened
- then: the page does not scroll sideways, and every question to try opens from a native
        `details` summary
