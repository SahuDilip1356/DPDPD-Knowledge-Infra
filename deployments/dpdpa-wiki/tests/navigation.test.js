import { describe, it, expect } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { readPage, builtRoutes, meta, canonical, DIST, ROOT } from "./helpers/dist.js";

const WORKSPACE = ["/today", "/knowledge", "/actions", "/factory", "/ask", "/admin", "/bible", "/changes", "/infographic", "/workspace"];
const linkRe = /(?:href|to)="([^"]*)"/g;

describe("public navigation (T10, AC9)", () => {
  const routes = builtRoutes().filter((r) => r !== "/workspace");

  it("built the public routes", () => {
    expect(routes.length).toBeGreaterThanOrEqual(110);
  });

  it("no public page links to a workspace path", () => {
    for (const route of routes) {
      const html = readPage(route);
      for (const m of html.matchAll(linkRe)) {
        const href = m[1].split("?")[0].split("#")[0];
        for (const w of WORKSPACE) {
          expect(href === w || href.startsWith(w + "/"), `${route} links to ${href}`).toBe(false);
        }
      }
    }
  });

  it("the primary navigation lists the law, the rules and the glossary", () => {
    const html = readPage("/");
    expect(html).toContain('href="/act"');
    expect(html).toContain('href="/rules"');
    expect(html).toContain('href="/glossary"');
    expect(html).toContain('aria-expanded="false"');
  });

  it("the workspace document is noindex", () => {
    const ws = fs.readFileSync(path.join(DIST, "workspace", "index.html"), "utf8");
    expect(ws).toMatch(/<meta name="robots" content="noindex, nofollow" \/>/);
  });
});

describe("site files (T11, AC14, AC15)", () => {
  it("404.html exists, is not the home page, and is noindex", () => {
    const p = path.join(DIST, "404.html");
    expect(fs.existsSync(p)).toBe(true);
    const html = fs.readFileSync(p, "utf8");
    expect(html).toContain("There is no page at this address.");
    expect(canonical(html)).not.toBe("https://dpdpa.wiki/");
    expect(html).toMatch(/name="robots" content="noindex/);
  });

  it("sitemap.xml lists every public route with lastmod", () => {
    const xml = fs.readFileSync(path.join(DIST, "sitemap.xml"), "utf8");
    expect(xml.startsWith('<?xml version="1.0" encoding="UTF-8"?>')).toBe(true);
    const locs = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
    expect(locs.length).toBeGreaterThanOrEqual(90);
    expect(locs).toContain("https://dpdpa.wiki/");
    expect(locs).toContain("https://dpdpa.wiki/act/section-6");
    expect(locs).toContain("https://dpdpa.wiki/rules/rule-7");
    expect(locs.some((l) => l.includes("/workspace"))).toBe(false);
    expect((xml.match(/<lastmod>\d{4}-\d{2}-\d{2}<\/lastmod>/g) || []).length).toBe(locs.length);
    const opens = (xml.match(/<url>/g) || []).length, closes = (xml.match(/<\/url>/g) || []).length;
    expect(opens).toBe(closes);
  });

  it("robots.txt allows the site, blocks the workspace and names the sitemap", () => {
    const txt = fs.readFileSync(path.join(DIST, "robots.txt"), "utf8");
    expect(txt).toMatch(/^Allow: \/$/m);
    expect(txt).toMatch(/^Disallow: \/workspace\/$/m);
    expect(txt).toContain("Sitemap: https://dpdpa.wiki/sitemap.xml");
  });

  it("every public page carries og:image and a self canonical", () => {
    for (const route of builtRoutes().filter((r) => r !== "/workspace")) {
      const html = readPage(route);
      expect(meta(html, "og:image"), route).toMatch(/^https:\/\/dpdpa\.wiki\/.+\.png$/);
      expect(canonical(html), route).toBe(`https://dpdpa.wiki${route === "/" ? "/" : route}`);
    }
    expect(fs.existsSync(path.join(DIST, "og-default.png"))).toBe(true);
  });

  it("vercel.json serves the workspace as an app, redirects old paths, and has no catch-all", () => {
    const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, "vercel.json"), "utf8"));
    expect(cfg.rewrites.some((r) => r.source === "/(.*)")).toBe(false);
    const ws = cfg.rewrites.find((r) => r.source === "/workspace/:path*");
    expect(ws, "workspace rewrite").toBeTruthy();
    // With cleanUrls on, "/workspace/index.html" is itself redirected, so a rewrite to it
    // serves the 404 page. The destination must be the clean path.
    if (cfg.cleanUrls) expect(ws.destination).not.toMatch(/\.html$/);
    expect(ws.destination).toBe("/workspace");
    for (const old of ["/today", "/ask", "/admin"]) expect(cfg.redirects.some((r) => r.source === old && r.permanent)).toBe(true);
  });
});

describe("mobile and motion (T17, AC16, AC18 presence checks)", () => {
  it("the public shell has a menu control with aria-expanded and 44px targets in CSS", () => {
    const shell = fs.readFileSync(path.join(ROOT, "src/components/marketing/PublicShell.jsx"), "utf8");
    expect(shell).toContain("aria-expanded={open}");
    const css = fs.readFileSync(path.join(ROOT, "src/styles/home.css"), "utf8");
    expect(css).toMatch(/\.pub-menu-btn[\s\S]*min-height: 44px/);
    expect(css).toMatch(/\.pub \{[\s\S]*?font-size: 16px/);
  });

  it("reduced motion is honoured in the stylesheets", () => {
    const dir = path.join(ROOT, "src/styles");
    const all = fs.readdirSync(dir).map((f) => fs.readFileSync(path.join(dir, f), "utf8")).join("\n");
    expect(all).toContain("prefers-reduced-motion: reduce");
  });
});
