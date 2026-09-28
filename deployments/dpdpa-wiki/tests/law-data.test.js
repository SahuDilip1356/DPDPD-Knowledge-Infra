import { describe, it, expect } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const { meta, provisions } = JSON.parse(fs.readFileSync(path.join(root, "src/data/law/provisions.json"), "utf8"));
const glossary = JSON.parse(fs.readFileSync(path.join(root, "src/data/law/glossary.json"), "utf8"));
const by = Object.fromEntries(provisions.map((p) => [p.label, p]));

describe("provisions.json (T2)", () => {
  it("has exactly 75 provision records with the expected labels", () => {
    expect(provisions).toHaveLength(75);
    const labels = provisions.map((p) => p.label);
    for (let n = 1; n <= 44; n++) expect(labels).toContain(`S${n}`);
    for (let n = 1; n <= 23; n++) expect(labels).toContain(`R${n}`);
    expect(labels).toContain("ACT-SCHEDULE");
    for (const s of ["FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH"]) expect(labels).toContain(`SCH-${s}`);
    expect(new Set(labels).size).toBe(75);
  });

  it("every record has verbatim text, a title, a URN, a hashed source and a module", () => {
    for (const p of provisions) {
      expect(p.text.length, p.label).toBeGreaterThan(20);
      expect(p.title, p.label).toBeTruthy();
      expect(p.urn, p.label).toMatch(/^urn:ki:in:dpdp:(act:2023|rules:2025):/);
      expect(p.source.sha256, p.label).toMatch(/^[0-9a-f]{64}$/);
      expect(p.source.document, p.label).toBeTruthy();
      expect(p.source.notification, p.label).toBeTruthy();
      expect(p.module, p.label).toMatch(/^(what-is-dpdpa|core-rules|peoples-rights|special-cases|enforcement)$/);
      expect(p.note).toBeNull();
      expect(Array.isArray(p.note_cites)).toBe(true);
    }
  });

  it("carries the Rules' commencement dates from Rule 1", () => {
    for (const n of [1, 2, 17, 18, 19, 20, 21]) expect(by[`R${n}`].in_force_from, `R${n}`).toBe("2025-11-13");
    expect(by.R4.in_force_from).toBe("2026-11-13");
    for (const n of [3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 22, 23]) expect(by[`R${n}`].in_force_from, `R${n}`).toBe("2027-05-13");
    expect(by["SCH-FIRST"].in_force_from).toBe("2026-11-13");
    expect(by["SCH-FIFTH"].in_force_from).toBe("2025-11-13");
  });

  it("does not invent an Act commencement date", () => {
    for (let n = 1; n <= 44; n++) expect(by[`S${n}`].in_force_from).toBeNull();
    expect(meta.note).toMatch(/commencement/i);
  });

  it("Section 6 carries the consent standard verbatim and the Schedule has 7 rows", () => {
    expect(by.S6.text).toContain("free, specific, informed, unconditional and unambiguous");
    expect(by.S5.title).toBe("Notice");
    expect(by.S6.title).toBe("Consent");
    expect(by["ACT-SCHEDULE"].rows).toHaveLength(7);
    expect(by["ACT-SCHEDULE"].rows[0].penalty).toMatch(/two hundred and fifty crore/);
    expect(by["ACT-SCHEDULE"].rows[4].penalty).toMatch(/ten thousand rupees/);
  });

  it("Rules use the notified numbering, not the draft", () => {
    expect(by.R7.title).toMatch(/breach/i);
    expect(by.R10.title).toMatch(/child/i);
    expect(by.R13.title).toMatch(/Significant Data Fiduciary/);
    expect(by.R15.title).toMatch(/outside the territory of India/);
    expect(by.R4.title).toMatch(/Consent Manager/);
  });
});

describe("questions attached to provisions (T3)", () => {
  it("Section 6 has at least 5 canonical questions, none more than 8", () => {
    expect(by.S6.questions.length).toBeGreaterThanOrEqual(5);
    for (const p of provisions) {
      expect(p.questions.length, p.label).toBeLessThanOrEqual(8);
      for (const q of p.questions) {
        expect(q.id).toMatch(/^Q-\d+$/);
        expect(q.question.length).toBeGreaterThan(10);
      }
    }
  });
});

describe("glossary.json (T7 data)", () => {
  it("every definition is a verbatim substring of Section 2 or Rule 2 and slugs are unique", () => {
    expect(glossary.length).toBeGreaterThanOrEqual(25);
    const slugs = new Set();
    for (const g of glossary) {
      expect(["S2", "R2"]).toContain(g.provision);
      expect(by[g.provision].text).toContain(g.definition);
      expect(g.definition).toContain(g.term);
      expect(slugs.has(g.slug), g.slug).toBe(false);
      slugs.add(g.slug);
    }
    expect(glossary.map((g) => g.slug)).toContain("data-fiduciary");
    expect(glossary.map((g) => g.slug)).toContain("data-principal");
  });
});
