/**
 * The six napkin scenarios at /learn/scenarios.
 * Evals: specs/wiki-napkin-scenarios/evals.md, N1–N5 and N8.
 */
import { describe, it, expect } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import Figure from "../src/components/learn/Figure.jsx";
import { lessonBlocks } from "../src/lib/module-build.js";
import { readPage, ROOT } from "./helpers/dist.js";

const FILE = path.join(ROOT, "src/content/scenarios.md");
const SRC = fs.readFileSync(FILE, "utf8");
const { provisions } = JSON.parse(fs.readFileSync(path.join(ROOT, "src/data/law/provisions.json"), "utf8"));
const LAW = Object.fromEntries(provisions.map((p) => [p.label, p]));
const listed = /^provisions:\s*\[([^\]]*)\]/m.exec(SRC)[1].split(",").map((s) => s.trim());
const lessons = SRC.split(/^(?=##\s)/m).slice(1);
const norm = (t) => t.replace(/(\w) -(\w)/g, "$1-$2").replace(/\s+/g, " ").trim().toLowerCase();
const figures = (sec) => lessonBlocks(sec.replace(/^##.*\n/, ""), "scenarios").filter((b) => b.type === "figure").map((b) => b.spec);
const allFigures = lessons.flatMap(figures);
/** Every "Section 6(1)" or "Rule 7(2)" or "Schedule" the figures and prose cite, as labels. */
const citeLabels = (text) => [...text.matchAll(/\b(Section|Rule)\s+(\d+)/g)].map(([, w, n]) => `${w[0] === "S" ? "S" : "R"}${n}`);

describe("napkin scenarios: content (N1–N3)", () => {
  it("has six scenarios, each with a short version, a figure and a question to try", () => {
    expect(lessons).toHaveLength(6);
    for (const sec of lessons) {
      const kinds = lessonBlocks(sec.replace(/^##.*\n/, ""), "scenarios").map((b) => b.type);
      expect(kinds, sec.slice(0, 60)).toEqual(expect.arrayContaining(["short", "figure", "try", "prose"]));
    }
  });

  it("lists only real provisions", () => {
    for (const l of listed) expect(LAW[l], l).toBeTruthy();
  });

  it("N1: the citation gate covers the page and fails a citation outside its list", () => {
    const run = (file) => {
      try {
        execFileSync("node", ["scripts/check-citations.mjs"], { cwd: ROOT, env: { ...process.env, CHECK_SCENARIOS_FILE: file }, stdio: "pipe" });
        return "";
      } catch (err) {
        return String(err.stdout) + String(err.stderr);
      }
    };
    expect(run(FILE)).toBe("");
    const planted = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "napkin-")), "scenarios.md");
    fs.writeFileSync(planted, SRC.replace("## Who is who", "Section 44 is cited here.\n\n## Who is who"));
    expect(run(planted)).toMatch(/scenarios\.md.*cites S44, outside the module's provisions/);
  });

  it("N2: every curly-quoted fragment is word for word in the provision cited next to it", () => {
    // A quote is checked against the last citation before it in its own paragraph,
    // or the first one after it when none comes before
    // ("Section 6(1)", "Rule 7(2)", "the Schedule"). A paragraph with no citation
    // falls back to the provisions its scenario cites.
    const cites = (text) => [...text.matchAll(/\b(Section|Rule)\s+(\d+)|\bSchedule\b/g)].map((m) => ({
      at: m.index,
      label: m[1] ? `${m[1][0] === "S" ? "S" : "R"}${m[2]}` : "ACT-SCHEDULE"
    }));
    let checked = 0;
    for (const sec of lessons) {
      const secLabels = [...new Set(cites(sec).map((c) => c.label))];
      for (const para of sec.split(/\n\s*\n/)) {
        const near = cites(para);
        for (const m of para.matchAll(/“([^”]+)”/g)) {
          checked++;
          const before = near.filter((c) => c.at < m.index).at(-1);
          const after = near.find((c) => c.at > m.index);
          const pool = before || after ? [(before || after).label] : secLabels;
          const hit = pool.some((l) => LAW[l] && norm(LAW[l].text).includes(norm(m[1])));
          expect(hit, `“${m[1]}” not found in ${pool.join(", ")}`).toBe(true);
        }
      }
    }
    expect(checked).toBeGreaterThan(20);
  });

  it("N3: every rupee amount is a Schedule row, and every date a Rule start date", () => {
    const schedule = LAW["ACT-SCHEDULE"].text;
    const allowed = { "250 crore": "two hundred and fifty crore", "200 crore": "two hundred crore", "150 crore": "one hundred and fifty crore", "50 crore": "fifty crore", "10,000": "ten thousand rupees" };
    const amounts = [...SRC.matchAll(/₹\s?([\d,]+(?: crore)?)/g)].map((m) => m[1]);
    expect(amounts.length).toBeGreaterThan(5);
    for (const a of amounts) {
      expect(allowed[a], `₹${a} is not a Schedule amount`).toBeTruthy();
      expect(schedule).toContain(allowed[a]);
    }
    const ruleDates = new Set(provisions.filter((p) => p.kind === "rule").map((p) => p.in_force_from));
    for (const f of allFigures.filter((f) => f.type === "timeline")) {
      for (const e of f.events) expect(ruleDates.has(e.date), e.date).toBe(true);
    }
    for (const d of [...SRC.matchAll(/(\d{1,2}) (November|May) (\d{4})/g)].map((m) => m[0])) {
      expect(["13 November 2025", "13 November 2026", "13 May 2027"], d).toContain(d);
    }
  });

  it("every figure cite names a listed provision", () => {
    const cites = JSON.stringify(allFigures).match(/"cite":"[^"]+"/g) || [];
    expect(cites.length).toBeGreaterThan(20);
    for (const c of cites) {
      const labels = citeLabels(c).concat(/Schedule/.test(c) ? ["ACT-SCHEDULE"] : []);
      expect(labels.length, c).toBeGreaterThan(0);
      for (const l of labels) expect(listed, c).toContain(l);
    }
  });
});

describe("napkin scenarios: new figure types (N5, N6)", () => {
  it("N6: the plot and map use role colours and shape only, no colour of their own", () => {
    const css = fs.readFileSync(path.join(ROOT, "src/styles/figures.css"), "utf8");
    const own = css.slice(css.indexOf("/* ── map:"));
    const hexes = (own.match(/#[0-9a-fA-F]{3,6}\b/g) || []).filter((h) => !/^#(fff|FFF|CBD3DF)$/.test(h));
    expect(hexes).toEqual([]);
  });

  const html = (spec) => renderToStaticMarkup(React.createElement(MemoryRouter, null, React.createElement(Figure, { spec })));
  const map = allFigures.find((f) => f.type === "map");
  const plot = allFigures.find((f) => f.type === "plot");

  it("renders the map with its regions, places and routes, complete without motion", () => {
    const out = html(map);
    expect(out).toContain("In India");
    expect(out).toContain("Outside India");
    expect(out).toContain("Cloud server");
    expect(out).toContain("map-routes");
    expect(out).not.toContain("is-anim"); // no JS has run: nothing is hidden
  });

  it("renders the plot with numbered points and a key that names each verdict", () => {
    const out = html(plot);
    expect((out.match(/class="plot-dot/g) || []).length).toBe(plot.points.length);
    for (const p of plot.points) {
      expect(out).toContain(p.label);
      expect(out).toContain(p.verdict);
    }
    expect(out).toMatch(/left:\s*82%/);
  });

  it("a malformed figure fails the build", () => {
    expect(() => lessonBlocks("::: figure\n{ \"type\": \"plot\", }\n:::", "test")).toThrow(/not valid JSON/);
  });
});

describe("napkin scenarios: the built page (N4, N8)", () => {
  const page = readPage("/learn/scenarios");

  it.skipIf(!page)("is prerendered with all six scenarios, figures and answers in the HTML", () => {
    const headings = lessons.map((s) => /^##\s+(.+)$/m.exec(s)[1].trim());
    for (const h of headings) expect(page).toContain(h.replace(/'/g, "&#x27;"));
    expect((page.match(/<figure class="fig /g) || []).length).toBe(allFigures.length);
    expect((page.match(/<details class="lesson-try">/g) || []).length).toBe(6);
    expect(page).toContain("by late Monday");
    expect(page).toMatch(/<title>Six napkins/);
    expect(page).toContain('rel="canonical" href="https://dpdpa.wiki/learn/scenarios"');
  });

  it.skipIf(!page)("is in the sitemap and linked from /learn", () => {
    const sitemap = fs.readFileSync(path.join(ROOT, "dist/sitemap.xml"), "utf8");
    expect(sitemap).toContain("<loc>https://dpdpa.wiki/learn/scenarios</loc>");
    expect(readPage("/learn")).toContain('href="/learn/scenarios"');
  });

  it.skipIf(!page)("N8: every question to try opens from its summary, a native keyboard control", () => {
    const tries = page.match(/<details class="lesson-try"><summary>/g) || [];
    expect(tries).toHaveLength(6);
  });
});
