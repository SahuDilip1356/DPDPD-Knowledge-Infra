import fs from "node:fs";
import path from "node:path";
import { describe, it, expect } from "vitest";
import { ROOT, readPage, builtRoutes } from "./helpers/dist.js";

// AC10: strings that must never reach a public page. Each one is either a wrong
// legal label (Notice is Section 5, not 6(1); the notified Rules renumbered the
// draft), a metric nobody measured, a feed that does not exist, or a promise
// the site cannot keep.
const FORBIDDEN = [
  "Sec 6(1)",
  "0.0%",
  "100% GROUNDED",
  "Zero-Hallucination",
  "MEITY.FEED.LIVE",
  "Draft Phase",
  "Consent Notice Rules 2024",
  "Rule 5: Verifiable Consent",
  "Rule 14: Consent Manager",
  "checklist is on its way"
];

// AC11: one distinctive fragment from each of the 7 Schedule rows, verbatim.
const SCHEDULE_FRAGMENTS = [
  "reasonable security safeguards",
  "notice of a personal data breach",
  "in relation to children",
  "Significant Data Fiduciary under section 10",
  "duties under section 15",
  "voluntary undertaking",
  "any other provision"
];

const SOURCE_FILES = [
  "src/components/screens/CommandCenter.jsx",
  "src/components/screens/AskIntelligence.jsx",
  "src/components/screens/Bible.jsx",
  "src/components/screens/Home.jsx",
  "src/data/mockData.js"
];

const read = (rel) => fs.readFileSync(path.join(ROOT, rel), "utf8");

// "Rule 23" needs context. In the January 2025 draft it was the cross-border
// transfer rule, and that is the fabrication AC10 forbids. In the notified Rules
// (G.S.R. 846(E)) cross-border transfer is Rule 15 and Rule 23 is "Calling for
// information from Data Fiduciary or intermediary", which the /rules pages
// legitimately render. So: flag "Rule 23" only when it is presented as the
// transfer rule.
function rule23AsCrossBorder(text) {
  const plain = text.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
  const re = /Rule 23/g;
  let m;
  while ((m = re.exec(plain))) {
    const window = plain.slice(Math.max(0, m.index - 200), m.index + 200).toLowerCase();
    if (/cross[- ]border|transfer/.test(window)) return true;
  }
  return false;
}

function offenders(text) {
  const found = FORBIDDEN.filter((s) => text.toUpperCase().includes(s.toUpperCase()));
  if (rule23AsCrossBorder(text)) found.push("Rule 23 (as cross-border transfer)");
  return found;
}

describe("AC10 — built public HTML carries no unsourced legal label or fake metric", () => {
  const routes = builtRoutes();

  it("has prerendered routes to scan (run `npm run build` first)", () => {
    expect(routes.length).toBeGreaterThan(0);
  });

  for (const route of routes) {
    it(`${route} is clean`, () => {
      const html = readPage(route);
      expect(html).toBeTruthy();
      expect(offenders(html), `found on ${route}`).toEqual([]);
    });
  }
});

describe("AC10 — workspace screens and sample data (source level, not prerendered)", () => {
  for (const rel of SOURCE_FILES) {
    it(`${rel} contains none of the forbidden strings`, () => {
      expect(offenders(read(rel)), rel).toEqual([]);
    });
  }
});

describe("AC11 — Bible lists the Act's Schedule", () => {
  const bible = read("src/components/screens/Bible.jsx");

  it("carries all 7 Schedule rows", () => {
    for (const fragment of SCHEDULE_FRAGMENTS) {
      expect(bible, fragment).toContain(fragment);
    }
    expect(bible.match(/\bserial: \d\b/g)).toHaveLength(7);
  });

  it("no longer attaches a penalty cap to every section", () => {
    expect(bible).not.toMatch(/max_penalty/);
    expect(bible).not.toMatch(/Max Cap/);
    expect(bible).not.toMatch(/₹250 Cr\b/);
  });

  it("says who imposes the penalties and that the amounts are maximums", () => {
    expect(bible).toMatch(/Data Protection Board of India under Section 33/);
    expect(bible).toMatch(/maximum/i);
  });
});
