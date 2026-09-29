import { describe, it, expect } from "vitest";
import { readPage, jsonLd } from "./helpers/dist.js";

const WORKSPACE = ["/today", "/knowledge", "/actions", "/factory", "/ask", "/admin", "/bible", "/workspace"];

describe("home page (T18, AC9)", () => {
  const html = readPage("/");

  it("leads with the course", () => {
    expect(html).toContain('href="/learn/what-is-dpdpa"');
    const hero = /<section class="hero">([\s\S]*?)<\/section>/.exec(html)?.[1] || "";
    expect(hero).toContain('href="/learn/what-is-dpdpa"');
    expect(hero).toContain('href="/act"');
    for (const slug of ["what-is-dpdpa", "core-rules", "peoples-rights", "special-cases", "enforcement", "in-your-business"]) {
      expect(html).toContain(`href="/learn/${slug}"`);
    }
  });

  it("links only to public destinations", () => {
    for (const m of html.matchAll(/(?:href|to)="([^"]*)"/g)) {
      const href = m[1].split("#")[0];
      for (const w of WORKSPACE) expect(href === w || href.startsWith(w + "/"), href).toBe(false);
    }
    expect(html).not.toContain("assess-opt");
    expect(html).toContain('href="https://saralprivacy.com/assessment"');
    expect(html).toContain('id="assessment"');
  });

  it("every FAQ answer cites a provision page", () => {
    const items = [...html.matchAll(/<article class="faq-item">([\s\S]*?)<\/article>/g)];
    expect(items.length).toBeGreaterThanOrEqual(6);
    for (const [, body] of items) expect(body).toMatch(/href="\/(act|rules)\//);
    const faq = jsonLd(html).find((j) => j["@type"] === "FAQPage");
    expect(faq.mainEntity.length).toBe(items.length);
  });

  it("has no SearchAction while Ask is hidden", () => {
    expect(html).not.toContain("SearchAction");
  });
});
