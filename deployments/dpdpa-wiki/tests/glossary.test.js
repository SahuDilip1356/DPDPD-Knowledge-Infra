import { describe, it, expect } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { readPage, bodyText, jsonLd, title, canonical, ROOT } from "./helpers/dist.js";
import { listGlossary, glossaryRoutes, getTerm } from "../src/lib/law.js";

const collapse = (s) => String(s).replace(/\s+/g, " ").trim();
const raw = JSON.parse(fs.readFileSync(path.join(ROOT, "src/data/law/glossary.json"), "utf8"));

describe("glossary pages (T7)", () => {
  it("every entry route exists and carries its definition verbatim", () => {
    expect(glossaryRoutes()).toHaveLength(raw.length);
    for (const t of listGlossary()) {
      const route = `/glossary/${t.slug}`;
      const html = readPage(route);
      expect(html, `${route} — run \`npm run build\` first`).toBeTruthy();
      const text = bodyText(html);
      expect(text, route).toContain(collapse(t.definition));
      expect(text, route).toContain(t.clause);
      expect(html, route).toContain(t.provision === "S2" ? 'href="/act/section-2"' : 'href="/rules/rule-2"');
      expect(canonical(html), route).toBe(`https://dpdpa.wiki${route}`);
      expect(title(html), route).toContain(t.term);
    }
  });

  it("/glossary/data-fiduciary emits DefinedTerm JSON-LD", () => {
    const html = readPage("/glossary/data-fiduciary");
    expect(html).toBeTruthy();
    const term = getTerm("data-fiduciary");
    const block = jsonLd(html).find((b) => b["@type"] === "DefinedTerm");
    expect(block).toBeTruthy();
    expect(block.name).toBe("Data Fiduciary");
    expect(block.description).toBe(term.definition);
    expect(block.inDefinedTermSet).toEqual({
      "@type": "DefinedTermSet",
      name: "DPDPA 2023 definitions",
      url: "https://dpdpa.wiki/glossary"
    });
    expect(block.url).toBe("https://dpdpa.wiki/glossary/data-fiduciary");
    expect(jsonLd(html).map((b) => b["@type"])).toContain("BreadcrumbList");
  });

  it("/glossary lists every term, alphabetically grouped", () => {
    const html = readPage("/glossary");
    expect(html).toBeTruthy();
    const links = [...html.matchAll(/href="\/glossary\/([^"]+)"/g)].map((m) => m[1]);
    expect(new Set(links).size).toBe(raw.length);
    for (const t of raw) expect(links, t.slug).toContain(t.slug);
    // Letters appear in order.
    const text = bodyText(html);
    const idx = ["Appellate Tribunal", "Board", "Consent Manager", "Data Fiduciary", "verifiable consent"].map((s) => text.indexOf(s));
    expect(idx.every((n) => n >= 0)).toBe(true);
    expect([...idx].sort((a, b) => a - b)).toEqual(idx);
  });
});
