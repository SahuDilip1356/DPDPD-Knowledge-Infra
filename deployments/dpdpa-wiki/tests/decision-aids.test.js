import { describe, it, expect } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { readPage, bodyText, jsonLd, title, meta, canonical, DIST } from "./helpers/dist.js";
import { listTools, getTool, toolRoutes, headForTool, validateTree, treeLabels } from "../src/lib/tools.js";
import { KNOWN_LABELS, extractCitations } from "../src/lib/citations.js";
import { getProvision, routeFor, formatDate } from "../src/lib/law.js";

const SITE = "https://dpdpa.wiki";
const SLUGS = ["does-dpdpa-apply", "is-this-consent-valid", "significant-data-fiduciary"];
const collapse = (s) => String(s).replace(/\s+/g, " ").trim();
const types = (html) => jsonLd(html).map((b) => b["@type"]);

const nodesOf = (tree) => Object.entries(tree.nodes).map(([id, n]) => ({ id, ...n }));
const results = (tree) => nodesOf(tree).filter((n) => n.type === "result");
const allText = (n) => [n.text, n.result?.verdict, n.result?.explanation].filter(Boolean).join(" ");
const allCites = (n) => [...new Set([...(n.cites || []), ...(n.result?.cites || [])])];

/* A small sound tree to mutate in the negative tests. */
const fixture = () => ({
  slug: "fixture",
  title: "Fixture",
  summary: "A fixture.",
  start: "a",
  nodes: {
    a: { type: "question", text: "A?", cites: ["S3"], options: [{ label: "yes", next: "b" }, { label: "no", next: "c" }] },
    b: { type: "result", text: "B", cites: ["S3"], result: { verdict: "Yes", explanation: "Because.", cites: ["S3"] } },
    c: { type: "result", text: "C", cites: ["S17"], result: { verdict: "No", explanation: "Because not.", cites: ["S17"] } }
  }
});

describe("decision trees as data (T16)", () => {
  it("there are exactly the three tools of the URL scheme, in order", () => {
    expect(listTools().map((t) => t.slug)).toEqual(SLUGS);
    expect(toolRoutes()).toEqual(SLUGS.map((s) => `/tools/${s}`));
    for (const s of SLUGS) expect(getTool(s)?.slug).toBe(s);
    expect(getTool("nope")).toBeNull();
  });

  it("validateTree passes for all three trees against the 75 labels", () => {
    expect(KNOWN_LABELS.size).toBe(75);
    for (const t of listTools()) expect(validateTree(t, KNOWN_LABELS), t.slug).toEqual([]);
  });

  it("validateTree accepts the fixture and reports a bad label", () => {
    expect(validateTree(fixture(), KNOWN_LABELS)).toEqual([]);
    const bad = fixture();
    bad.nodes.b.result.cites = ["S99"];
    bad.nodes.c.cites = ["RULE-7"];
    const problems = validateTree(bad, KNOWN_LABELS);
    expect(problems.some((p) => /unknown label S99/.test(p))).toBe(true);
    expect(problems.some((p) => /unknown label RULE-7/.test(p))).toBe(true);
  });

  it("validateTree reports empty cites, a dangling next, an unreachable node and a cycle", () => {
    const empty = fixture();
    empty.nodes.a.cites = [];
    expect(validateTree(empty, KNOWN_LABELS).some((p) => /cites is empty/.test(p))).toBe(true);

    const dangling = fixture();
    dangling.nodes.a.options[0].next = "zz";
    expect(validateTree(dangling, KNOWN_LABELS).some((p) => /missing node "zz"/.test(p))).toBe(true);

    const orphan = fixture();
    orphan.nodes.d = { type: "result", text: "D", cites: ["S3"], result: { verdict: "D", explanation: "d", cites: ["S3"] } };
    expect(validateTree(orphan, KNOWN_LABELS).some((p) => /d: unreachable/.test(p))).toBe(true);

    const loop = fixture();
    loop.nodes.b = { type: "question", text: "B?", cites: ["S3"], options: [{ label: "back", next: "a" }, { label: "on", next: "c" }] };
    expect(validateTree(loop, KNOWN_LABELS).some((p) => /cycle a → b → a/.test(p))).toBe(true);

    const noStart = fixture();
    noStart.start = "q";
    expect(validateTree(noStart, KNOWN_LABELS).some((p) => /start node "q" does not exist/.test(p))).toBe(true);
  });

  it("every node's cites resolve to real provisions with routes", () => {
    for (const t of listTools()) {
      for (const n of nodesOf(t)) {
        for (const l of allCites(n)) {
          expect(getProvision(l), `${t.slug}/${n.id} cites ${l}`).toBeTruthy();
          expect(routeFor(l), `${t.slug}/${n.id} cites ${l}`).toMatch(/^\/(act|rules)\//);
        }
      }
      expect(treeLabels(t).length).toBeGreaterThan(0);
    }
  });

  it("every provision a step's words name is among that step's cites", () => {
    // The same discipline as provision notes: a tool may not mention a section
    // or rule it does not declare, so nothing on the page cites what it does not link.
    for (const t of listTools()) {
      for (const n of nodesOf(t)) {
        const named = extractCitations(allText(n));
        const declared = new Set(allCites(n));
        for (const l of named) expect(declared.has(l), `${t.slug}/${n.id} names ${l} but does not cite it`).toBe(true);
      }
    }
  });

  it("every rule commencement date quoted in a tool matches the provision record", () => {
    let seen = 0;
    for (const t of listTools()) {
      for (const n of nodesOf(t)) {
        for (const m of allText(n).matchAll(/Rule (\d+), which applies from (\d{1,2} [A-Z][a-z]+ \d{4})/g)) {
          seen++;
          const p = getProvision(`R${m[1]}`);
          expect(p, `${t.slug}/${n.id}: Rule ${m[1]}`).toBeTruthy();
          expect(m[2], `${t.slug}/${n.id}: Rule ${m[1]}`).toBe(formatDate(p.in_force_from));
        }
      }
    }
    expect(seen).toBeGreaterThanOrEqual(3);
  });

  it("the applicability tree: every terminal cites Section 3 and uses one of three verdicts", () => {
    const t = getTool("does-dpdpa-apply");
    const verdicts = new Set(["The Act applies", "The Act does not apply", "The Act applies with exemptions"]);
    const rs = results(t);
    expect(rs.length).toBeGreaterThanOrEqual(3);
    for (const r of rs) {
      expect(r.result.cites, r.id).toContain("S3");
      expect(verdicts.has(r.result.verdict), `${r.id}: ${r.result.verdict}`).toBe(true);
    }
    for (const v of verdicts) expect(rs.some((r) => r.result.verdict === v), v).toBe(true);
    expect(rs.filter((r) => r.result.verdict === "The Act applies with exemptions").every((r) => r.result.cites.includes("S17"))).toBe(true);
  });

  it("the consent tree: verdicts are valid / not valid / consent not required, and Section 7 is the alternative ground", () => {
    const t = getTool("is-this-consent-valid");
    const rs = results(t);
    const legit = rs.filter((r) => r.result.verdict.startsWith("Consent not required"));
    expect(legit).toHaveLength(1);
    expect(legit[0].result.cites).toContain("S7");
    expect(rs.filter((r) => r.result.verdict === "Valid on these facts").length).toBeGreaterThanOrEqual(1);
    const fails = rs.filter((r) => r.result.verdict.startsWith("Not valid"));
    expect(fails.length).toBeGreaterThanOrEqual(7);
    for (const f of fails) expect(f.result.verdict, f.id).toMatch(/^Not valid[^:]*: fails /);
    // Every Section 6(1) word is tested somewhere.
    const questions = nodesOf(t).filter((n) => n.type === "question").map((n) => n.text.toLowerCase()).join(" ");
    for (const w of ["freely", "specific", "informed", "unconditional", "unambiguous", "affirmative action", "necessary", "withdraw", "notice", "consent manager"]) {
      expect(questions, w).toContain(w);
    }
    const start = t.nodes[t.start];
    expect(start.cites).toContain("S4");
  });

  it("the SDF tree is short and turns on the Government's notification", () => {
    const t = getTool("significant-data-fiduciary");
    expect(Object.keys(t.nodes)).toHaveLength(3);
    const start = t.nodes[t.start];
    expect(start.type).toBe("question");
    expect(start.text).toMatch(/Central Government/);
    expect(start.cites).toContain("S10");
    const rs = results(t);
    expect(rs).toHaveLength(2);
    const yes = rs.find((r) => r.result.verdict === "You are a Significant Data Fiduciary");
    expect(yes.result.cites).toEqual(expect.arrayContaining(["S10", "R13"]));
    const no = rs.find((r) => /cannot self-designate/.test(r.result.verdict));
    expect(no.result.explanation).toMatch(/volume and sensitivity/);
    expect(no.result.explanation).toMatch(/electoral democracy/);
  });
});

describe("decision aid head tags", () => {
  it("headForTool returns title, description, canonical, WebPage + BreadcrumbList; null for unknown paths", () => {
    for (const t of listTools()) {
      const h = headForTool(`/tools/${t.slug}`);
      expect(h.title).toBe(`${t.title} | DPDPA Wiki`);
      expect(h.description).toBe(t.summary);
      expect(h.canonical).toBe(`${SITE}/tools/${t.slug}`);
      expect(h.ogType).toBe("website");
      expect(h.jsonld.map((b) => b["@type"])).toEqual(["WebPage", "BreadcrumbList"]);
      const about = h.jsonld[0].about;
      expect(about.length).toBe(treeLabels(t).length);
      for (const a of about) expect(a.url.startsWith(`${SITE}/`)).toBe(true);
      expect(headForTool(`/tools/${t.slug}/`)).toEqual(h);
    }
    expect(headForTool("/tools/nope")).toBeNull();
    expect(headForTool("/tools")).toBeNull();
    expect(headForTool("/act/section-3")).toBeNull();
  });
});

describe("decision aid pages (built)", () => {
  it("the three routes are prerendered with the first step, the full step list and the head tags", () => {
    for (const t of listTools()) {
      const route = `/tools/${t.slug}`;
      const html = readPage(route);
      expect(html, `${route} — run \`npm run build\` first`).toBeTruthy();
      const text = bodyText(html);

      expect(text, route).toContain(collapse(t.title));
      expect(text, route).toContain(collapse(t.nodes[t.start].text));
      expect(text, route).toContain("All steps in this tool");
      for (const n of nodesOf(t)) {
        expect(text, `${route} step ${n.id}`).toContain(collapse(n.text));
        if (n.type === "result") expect(text, `${route} step ${n.id}`).toContain(collapse(n.result.explanation));
        for (const l of allCites(n)) expect(html, `${route} step ${n.id} cites ${l}`).toContain(`href="${routeFor(l)}"`);
      }
      // Breadcrumb Home › Tools › title.
      expect(text).toMatch(new RegExp(`Home\\s*›\\s*Tools\\s*›\\s*${collapse(t.title).replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`));
      // Controls: at least two answer buttons and Back disabled at the start.
      expect((html.match(/class="tool-option"/g) || []).length).toBeGreaterThanOrEqual(2);
      expect(html).toMatch(/class="tool-nav-btn"[^>]*disabled/);

      expect(title(html), route).toBe(`${t.title} | DPDPA Wiki`);
      expect(meta(html, "description"), route).toBe(t.summary.replace(/&/g, "&amp;").replace(/"/g, "&quot;"));
      expect(canonical(html), route).toBe(`${SITE}${route}`);
      expect(meta(html, "og:url"), route).toBe(`${SITE}${route}`);
      expect(meta(html, "og:image"), route).toBe(`${SITE}/og-default.png`);
      expect(meta(html, "twitter:card"), route).toBe("summary_large_image");
      expect((html.match(/<title>/g) || []).length, route).toBe(1);
      expect(types(html), route).toContain("WebPage");
      expect(types(html), route).toContain("BreadcrumbList");
      const crumbs = jsonLd(html).find((b) => b["@type"] === "BreadcrumbList");
      expect(crumbs.itemListElement.map((i) => i.name)).toEqual(["Home", t.title]);
      const page = jsonLd(html).find((b) => b["@type"] === "WebPage");
      expect(page.about.every((a) => a["@type"] === "Legislation")).toBe(true);
    }
  });

  it("the applicability page links every terminal to /act/section-3", () => {
    const html = readPage("/tools/does-dpdpa-apply");
    expect(html).toBeTruthy();
    expect(html).toContain('href="/act/section-3"');
    // Every terminal's cites include S3, so each terminal in the step list links there.
    const t = getTool("does-dpdpa-apply");
    for (const r of results(t)) expect(r.result.cites).toContain("S3");
    const stepList = /<details class="tool-steps">([\s\S]*?)<\/details>/.exec(html)?.[1];
    expect(stepList).toBeTruthy();
    const items = stepList.split(/<li id="step-/).slice(1).filter((s) => /tool-steps-result/.test(s.split(">")[0] + ">" + s.slice(0, 200)));
    expect(items.length).toBe(results(t).length);
    for (const item of items) expect(item).toContain('href="/act/section-3"');
  });

  it("the tool routes are in the sitemap", () => {
    const sitemap = fs.readFileSync(path.join(DIST, "sitemap.xml"), "utf8");
    for (const r of toolRoutes()) expect(sitemap).toContain(`<loc>${SITE}${r}</loc>`);
  });
});
