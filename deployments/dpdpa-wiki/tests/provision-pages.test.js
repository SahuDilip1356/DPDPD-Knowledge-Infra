import { describe, it, expect } from "vitest";
import { readPage, bodyText } from "./helpers/dist.js";
import {
  listProvisions, getProvision, provisionRoutes, routeFor, getByRoute, labelFor,
  formatDate, isInForce, clauseLines, commencement
} from "../src/lib/law.js";

const collapse = (s) => String(s).replace(/\s+/g, " ").trim();
const by = Object.fromEntries(listProvisions().map((p) => [p.label, p]));

describe("law.js helpers (T4)", () => {
  it("knows all 75 provisions and their routes", () => {
    expect(listProvisions()).toHaveLength(75);
    expect(provisionRoutes()).toHaveLength(75);
    expect(new Set(provisionRoutes()).size).toBe(75);
    expect(routeFor("S6")).toBe("/act/section-6");
    expect(routeFor("ACT-SCHEDULE")).toBe("/act/schedule");
    expect(routeFor("R7")).toBe("/rules/rule-7");
    expect(routeFor("SCH-FIRST")).toBe("/rules/schedule-first");
    expect(getByRoute("/act/section-6/")).toBe(getProvision("S6"));
    expect(getByRoute("/rules/schedule-seventh").label).toBe("SCH-SEVENTH");
    expect(getByRoute("/act/section-99")).toBeNull();
  });

  it("maps display text back to labels", () => {
    expect(labelFor("Section 6")).toBe("S6");
    expect(labelFor("Section 6(4)")).toBe("S6");
    expect(labelFor("Rule 7")).toBe("R7");
    expect(labelFor("the Schedule")).toBe("ACT-SCHEDULE");
    expect(labelFor("First Schedule")).toBe("SCH-FIRST");
    expect(labelFor("Section 99")).toBeNull();
  });

  it("formats dates and judges legal force by date", () => {
    expect(formatDate("2027-05-13")).toBe("13 May 2027");
    expect(formatDate("2025-11-13")).toBe("13 November 2025");
    expect(isInForce(by.R7, new Date("2026-09-28"))).toBe(false);
    expect(isInForce(by.R7, new Date("2027-05-13T00:00:00Z"))).toBe(true);
    expect(isInForce(by.R1, new Date("2026-09-28"))).toBe(true);
    expect(isInForce(by.S6)).toBeNull();
    expect(commencement(by.R7, new Date("2026-09-28")).label).toBe("Applies from 13 May 2027");
    expect(commencement(by.R1, new Date("2026-09-28")).label).toBe("In force since 13 November 2025");
    expect(commencement(by.S6)).toBeNull();
  });

  it("splits sub-clauses onto their own lines without changing a character", () => {
    for (const p of listProvisions()) {
      const lines = clauseLines(p.text);
      expect(lines.map((l) => l.text).join(""), p.label).toBe(p.text);
    }
    const r7 = clauseLines(by.R7.text).map((l) => l.text.trim());
    expect(r7.some((l) => l.startsWith("(1) On becoming aware"))).toBe(true);
    expect(r7.some((l) => l.startsWith("(a) a description of the breach"))).toBe(true);
    expect(r7.some((l) => l.startsWith("(ii) the broad facts"))).toBe(true);
    // Cross-references inside a sentence stay inline.
    const s6 = clauseLines(by.S6.text).map((l) => l.text);
    expect(s6.some((l) => l.includes("referred in sub-section (1) which"))).toBe(true);
  });
});

describe("provision pages (T4)", () => {
  it("/act/section-6 carries the Section 6 text verbatim", () => {
    const html = readPage("/act/section-6");
    expect(html, "run `npm run build` first").toBeTruthy();
    const text = bodyText(html);
    expect(text).toContain(collapse(by.S6.text));
    expect(text).toContain("Section 6 — Consent");
    expect(text).toContain("Home › The Act › Section 6");
    expect(text).toContain(`Source: ${by.S6.source.document}, ${by.S6.source.notification}`);
    expect(text).toContain(`SHA-256 ${by.S6.source.sha256.slice(0, 12)}… — verified copy`);
    expect(html).toContain(`href="${by.S6.source.url}"`);
    expect(text).not.toMatch(/Applies from|In force since/);
    expect(text).toContain("Taught in Core Rules");
    expect(html).toContain('href="/act/section-5"');
    expect(html).toContain('href="/act/section-7"');
  });

  it("/rules/rule-7 says when it applies from", () => {
    const text = bodyText(readPage("/rules/rule-7"));
    expect(text).toContain("Applies from 13 May 2027");
    expect(text).toContain(collapse(by.R7.text));
    expect(text).toContain("Questions people ask about this provision");
    for (const q of by.R7.questions) expect(text).toContain(q.question);
  });

  it("a rule already in force says so", () => {
    expect(bodyText(readPage("/rules/rule-1"))).toContain("In force since 13 November 2025");
  });

  it("/act/schedule lists the 7 penalty rows", () => {
    const html = readPage("/act/schedule");
    const text = bodyText(html);
    expect((html.match(/<tr>/g) || []).length).toBe(8); // header + 7 rows
    expect(text).toContain("two hundred and fifty crore");
    for (const r of by["ACT-SCHEDULE"].rows) {
      expect(text).toContain(collapse(r.breach));
      expect(text).toContain(collapse(r.penalty));
    }
    expect(text).toContain(collapse(by["ACT-SCHEDULE"].text));
  });

  it("every one of the 75 routes is built with its gazette text", () => {
    for (const p of listProvisions()) {
      const html = readPage(routeFor(p));
      expect(html, routeFor(p)).toBeTruthy();
      const text = bodyText(html);
      expect(text, p.label).toContain(collapse(p.text));
      expect(text, p.label).toContain(p.title);
      expect(text, p.label).toContain(p.source.document);
      expect(text, p.label).toContain(p.source.notification);
      if (p.in_force_from) expect(text, p.label).toMatch(new RegExp(`(Applies from|In force since) ${formatDate(p.in_force_from)}`));
    }
  });

  it("a provision without a note shows the pending marker", () => {
    for (const p of listProvisions()) {
      if (p.note !== null) continue;
      expect(bodyText(readPage(routeFor(p))), p.label).toContain("Plain-language note pending");
    }
  });

  it("/act and /rules link to every child route", () => {
    const act = readPage("/act");
    const rules = readPage("/rules");
    expect(act).toBeTruthy();
    expect(rules).toBeTruthy();
    for (const p of listProvisions()) {
      const index = p.kind === "section" || p.kind === "act-schedule" ? act : rules;
      expect(index, routeFor(p)).toContain(`href="${routeFor(p)}"`);
    }
    const actText = bodyText(act);
    for (const ch of ["Preliminary", "Obligations of Data Fiduciary", "Penalties and adjudication", "Miscellaneous"]) expect(actText).toContain(ch);
    expect(bodyText(rules)).toContain("Applies from 13 May 2027");
  });
});
