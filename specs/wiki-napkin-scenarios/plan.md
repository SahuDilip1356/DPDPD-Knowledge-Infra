# Plan: six napkin scenarios on dpdpa.wiki

### T1 — Content pipeline and page
- status: done
- implements: AC1
- depends_on: none
- files: deployments/dpdpa-wiki/src/content/scenarios.md, src/lib/scenarios.js, src/components/screens/Scenarios.jsx, src/components/learn/Lesson.jsx, src/App.jsx, src/lib/seo.js, scripts/vite-content.mjs, src/lib/module-build.js
- risk: tier2
- verify: cd deployments/dpdpa-wiki && npm run build && npx vitest run tests/scenarios.test.js

### T2 — Map and plot figures
- status: done
- implements: AC2
- depends_on: none
- files: deployments/dpdpa-wiki/src/components/learn/Figure.jsx, src/styles/figures.css
- risk: tier2
- verify: cd deployments/dpdpa-wiki && npx vitest run tests/scenarios.test.js

### T3 — Citation gate and exactness tests
- status: done
- implements: AC3, AC4
- depends_on: T1
- files: deployments/dpdpa-wiki/scripts/check-citations.mjs, tests/scenarios.test.js
- risk: tier2
- verify: cd deployments/dpdpa-wiki && npm run check:citations && npx vitest run tests/scenarios.test.js

### T4 — Phone and keyboard check
- status: done
- implements: AC5
- depends_on: T1, T2
- files: deployments/dpdpa-wiki/src/styles/learn.css
- risk: tier2
- verify: cd deployments/dpdpa-wiki && npx vitest run tests/scenarios.test.js
