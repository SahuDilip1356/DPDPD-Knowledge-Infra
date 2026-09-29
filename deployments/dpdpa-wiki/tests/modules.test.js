import { describe, it, expect } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { readPage, jsonLd, title, ROOT } from "./helpers/dist.js";

const dir = path.join(ROOT, "src/content/modules");
const files = fs.readdirSync(dir).filter((f) => /^\d\d-.+\.md$/.test(f)).sort();
const { provisions } = JSON.parse(fs.readFileSync(path.join(ROOT, "src/data/law/provisions.json"), "utf8"));
const LABELS = new Set(provisions.map((p) => p.label));
const ROUTES = new Set(provisions.map((p) =>
  p.kind === "section" ? `/act/section-${p.number}` :
  p.kind === "act-schedule" ? "/act/schedule" :
  p.kind === "rule" ? `/rules/rule-${p.number}` :
  `/rules/schedule-${p.label.replace("SCH-", "").toLowerCase()}`));

// Minimal front-matter read, independent of the app's parser, so a parser bug cannot hide a content bug.
function front(file) {
  const src = fs.readFileSync(path.join(dir, file), "utf8");
  const fm = /^---\r?\n([\s\S]*?)\r?\n---/.exec(src)[1];
  const get = (k) => (new RegExp(`^${k}:\\s*(.*)$`, "m").exec(fm)?.[1] || "").trim().replace(/^["']|["']$/g, "");
  const list = (v) => v.replace(/^\[|\]$/g, "").split(",").map((s) => s.trim()).filter(Boolean);
  const quiz = fm.split(/^\s*- q:/m).slice(1).map((block) => {
    const f = (k) => (new RegExp(`^\\s*${k}:\\s*(.*)$`, "m").exec(block)?.[1] || "").trim().replace(/^["']|["']$/g, "");
    return { q: block.split("\n")[0].trim().replace(/^["']|["']$/g, ""), opts: ["a", "b", "c", "d"].map(f), answer: f("answer"), cites: list(f("cites")) };
  });
  return { slug: get("slug"), order: Number(get("order")), title: get("title"), next: get("next"), provisions: list(get("provisions")), handoff: get("handoff_url"), quiz };
}
const modules = files.map(front).sort((a, b) => a.order - b.order);

describe("module content (AC5, AC6, AC7 data)", () => {
  it("at least one module exists and slugs follow the spec", () => {
    expect(modules.length).toBeGreaterThanOrEqual(1);
    const allowed = ["what-is-dpdpa", "core-rules", "peoples-rights", "special-cases", "enforcement", "in-your-business"];
    for (const m of modules) expect(allowed[m.order - 1], m.slug).toBe(m.slug);
  });

  for (const m of modules) {
    it(`${m.slug}: provisions are real, quiz is 5–8 well-formed items citing only its provisions`, () => {
      expect(m.title.length).toBeGreaterThan(3);
      for (const l of m.provisions) expect(LABELS.has(l), `${m.slug} lists ${l}`).toBe(true);
      expect(m.quiz.length).toBeGreaterThanOrEqual(5);
      expect(m.quiz.length).toBeLessThanOrEqual(8);
      for (const q of m.quiz) {
        expect(q.q.length, "question text").toBeGreaterThan(8);
        for (const o of q.opts) expect(o.length, `${m.slug}: "${q.q}" option`).toBeGreaterThan(0);
        expect(["a", "b", "c", "d"]).toContain(q.answer);
        expect(q.cites.length).toBeGreaterThan(0);
        for (const c of q.cites) expect(m.provisions, `${m.slug} quiz cites ${c}`).toContain(c);
      }
      if (m.order < 6) expect(m.next).not.toBe("null");
      if (m.order === 6) {
        expect(m.handoff).toBe("https://saralprivacy.com/assessment");
        expect(["null", "", "~"]).toContain(m.next);
      }
    });
  }
});

describe("course pages (T14, T15)", () => {
  it("/learn lists every module in order", () => {
    const html = readPage("/learn");
    expect(html).toBeTruthy();
    let at = -1;
    for (const m of modules) {
      const i = html.indexOf(`href="/learn/${m.slug}"`);
      expect(i, m.slug).toBeGreaterThan(at);
      at = i;
    }
    expect(title(html)).toMatch(/\| DPDPA Wiki$/);
  });

  for (const m of modules) {
    it(`/learn/${m.slug} renders, links forward (or hands off) and every citation resolves`, () => {
      const html = readPage(`/learn/${m.slug}`);
      expect(html, "built").toBeTruthy();
      expect(title(html)).toBe(`${m.title} — Module ${m.order} of 6 | DPDPA Wiki`);
      const types = jsonLd(html).map((j) => j["@type"]);
      expect(types).toContain("Course");
      expect(types).toContain("BreadcrumbList");
      expect(html).toContain(`href="/learn/${m.slug}/quiz"`);
      const cites = [...html.matchAll(/<a class="cite" href="([^"]+)"/g)].map((x) => x[1]);
      expect(cites.length, "lessons cite provisions").toBeGreaterThan(0);
      for (const href of cites) expect(ROUTES.has(href), href).toBe(true);
      if (m.order === 6) {
        expect(html).toContain('href="https://saralprivacy.com/assessment"');
        expect(html).not.toContain("learn-next");
      } else if (modules.some((x) => x.slug === m.next)) {
        expect(html).toContain(`href="/learn/${m.next}"`);
      }
    });

    it(`/learn/${m.slug}/quiz shows the questions and not the answer key`, () => {
      const html = readPage(`/learn/${m.slug}/quiz`);
      expect(html, "built").toBeTruthy();
      const body = /<body[^>]*>([\s\S]*)<\/body>/.exec(html)[1].replace(/<script[\s\S]*?<\/script>/g, "");
      for (const q of m.quiz) expect(body).toContain(q.q.replace(/&/g, "&amp;").replace(/"/g, "&quot;").slice(0, 30).replace(/&quot;/g, "\"").slice(0, 20));
      expect(body).not.toContain("is-answer");
      expect(body).not.toContain("data-answer");
      expect(body).not.toMatch(/The answer is/);
      expect(jsonLd(html).map((j) => j["@type"])).toContain("Quiz");
      const quizLd = jsonLd(html).find((j) => j["@type"] === "Quiz");
      expect(JSON.stringify(quizLd)).not.toMatch(/acceptedAnswer|"answer"/);
    });
  }
});
