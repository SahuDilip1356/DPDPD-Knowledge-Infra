import { describe, it, expect } from "vitest";
import { readPage, title, meta, canonical, jsonLd } from "./helpers/dist.js";
import { listProvisions, routeFor, glossaryRoutes } from "../src/lib/law.js";

const SITE = "https://dpdpa.wiki";
const types = (html) => jsonLd(html).map((b) => b["@type"]);

describe("provision head tags (T5)", () => {
  it.each([
    ["/act/section-6", /^Section 6 — Consent \| DPDPA 2023 \| DPDPA Wiki$/],
    ["/rules/rule-7", /^Rule 7 — Intimation of personal data breach \| DPDP Rules 2025 \| DPDPA Wiki$/]
  ])("%s has a title, description, canonical, og:image and Legislation + BreadcrumbList", (route, pattern) => {
    const html = readPage(route);
    expect(html, "run `npm run build` first").toBeTruthy();
    expect(title(html)).toMatch(pattern);
    const d = meta(html, "description");
    expect(d).toBeTruthy();
    expect(d.length).toBeLessThanOrEqual(160);
    expect(canonical(html)).toBe(`${SITE}${route}`);
    expect(meta(html, "og:url")).toBe(`${SITE}${route}`);
    expect(meta(html, "og:type")).toBe("article");
    expect(meta(html, "og:image")).toBe(`${SITE}/og-default.png`);
    expect(meta(html, "twitter:card")).toBe("summary_large_image");
    expect(types(html)).toContain("Legislation");
    expect(types(html)).toContain("BreadcrumbList");
  });

  it("the Schedule and a rules schedule follow the title pattern", () => {
    expect(title(readPage("/act/schedule"))).toBe("The Schedule — Penalties | DPDPA 2023 | DPDPA Wiki");
    expect(title(readPage("/rules/schedule-first"))).toMatch(/^First Schedule — .+ \| DPDP Rules 2025 \| DPDPA Wiki$/);
  });

  it("Legislation objects carry identifier, parent, date and (for Rules) legal force", () => {
    const s6 = jsonLd(readPage("/act/section-6")).find((b) => b["@type"] === "Legislation");
    expect(s6.legislationIdentifier).toBe("Section 6");
    expect(s6.inLanguage).toBe("en-IN");
    expect(s6.isPartOf.name).toMatch(/Digital Personal Data Protection Act, 2023/);
    expect(s6.legislationDate).toBe("2023-08-11");
    expect(s6.url).toBe(`${SITE}/act/section-6`);
    expect(s6.legislationLegalForce).toBeUndefined();

    const r7 = jsonLd(readPage("/rules/rule-7")).find((b) => b["@type"] === "Legislation");
    expect(r7.legislationIdentifier).toBe("Rule 7");
    expect(r7.legislationDate).toBe("2025-11-13");
    expect(r7.isPartOf.name).toMatch(/Rules, 2025/);
    expect(r7.legislationLegalForce).toBe(new Date("2027-05-13") <= new Date() ? "InForce" : "NotInForce");
    const r1 = jsonLd(readPage("/rules/rule-1")).find((b) => b["@type"] === "Legislation");
    expect(r1.legislationLegalForce).toBe("InForce");

    const crumbs = jsonLd(readPage("/act/section-6")).find((b) => b["@type"] === "BreadcrumbList");
    expect(crumbs.itemListElement.map((i) => i.name)).toEqual(["Home", "The Act", "Section 6"]);
  });

  it("every provision route has a unique title and a self canonical", () => {
    const seen = new Map();
    for (const p of listProvisions()) {
      const route = routeFor(p);
      const html = readPage(route);
      expect(html, route).toBeTruthy();
      const t = title(html);
      expect(t, route).toBeTruthy();
      expect(seen.has(t), `${route} shares its title with ${seen.get(t)}`).toBe(false);
      seen.set(t, route);
      expect(canonical(html), route).toBe(`${SITE}${route}`);
      expect(meta(html, "og:image"), route).toBeTruthy();
      expect(types(html), route).toContain("Legislation");
    }
  });

  it("index pages emit CollectionPage + BreadcrumbList", () => {
    for (const route of ["/act", "/rules", "/glossary"]) {
      const html = readPage(route);
      expect(html, route).toBeTruthy();
      expect(canonical(html)).toBe(`${SITE}${route}`);
      expect(types(html)).toContain("CollectionPage");
      expect(types(html)).toContain("BreadcrumbList");
    }
  });

  it("existing routes now carry og:image and twitter:card exactly once", () => {
    for (const route of ["/"]) {
      const html = readPage(route);
      expect(meta(html, "og:image"), route).toBe(`${SITE}/og-default.png`);
      expect((html.match(/name="twitter:card"/g) || []).length, route).toBe(1);
      expect((html.match(/property="og:image"/g) || []).length, route).toBe(1);
    }
  });

  it("the home page's WebSite block no longer advertises a SearchAction", () => {
    const html = readPage("/");
    expect(html).not.toContain("SearchAction");
    expect(html).not.toContain("/ask?q=");
  });

  it("all glossary routes are prerendered", () => {
    for (const route of glossaryRoutes()) expect(readPage(route), route).toBeTruthy();
  });
});
