import { describe, it, expect } from "vitest";
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { readPage, builtRoutes, DIST, ROOT } from "./helpers/dist.js";

// Spec, non-functional: no page loads more than 200 KB gzipped of JS for first render.
const BUDGET = 200 * 1000;

const gz = new Map();
const gzipSize = (file) => {
  if (!gz.has(file)) gz.set(file, zlib.gzipSync(fs.readFileSync(path.join(DIST, file)), { level: 9 }).length);
  return gz.get(file);
};

/** Static imports of a built chunk ("./x.js" → "assets/x.js"); dynamic import() is not followed. */
function staticImports(file) {
  const code = fs.readFileSync(path.join(DIST, file), "utf8");
  const out = [];
  for (const m of code.matchAll(/\bfrom\s*["'](\.\/[^"']+\.js)["']|\bimport\s*["'](\.\/[^"']+\.js)["']/g)) {
    out.push(path.posix.join(path.posix.dirname(file), m[1] || m[2]));
  }
  return out;
}

/** Every JS file a document loads before its first render: its entry and preloads, with their static imports. */
function pageScripts(html) {
  const roots = [
    ...[...html.matchAll(/<script type="module"[^>]*src="\/([^"]+)"/g)].map((m) => m[1]),
    ...[...html.matchAll(/<link rel="modulepreload"[^>]*href="\/([^"]+)"/g)].map((m) => m[1])
  ];
  const seen = new Set();
  const walk = (f) => {
    if (seen.has(f)) return;
    seen.add(f);
    staticImports(f).forEach(walk);
  };
  roots.forEach(walk);
  return seen;
}

const kb = (n) => `${(n / 1000).toFixed(1)} KB`;
const total = (files) => [...files].reduce((n, f) => n + gzipSize(f), 0);

describe("JS budget (spec: ≤ 200 KB gzipped per page)", () => {
  const routes = builtRoutes().filter((r) => !r.startsWith("/workspace"));

  it("has pages to measure", () => {
    expect(routes.length).toBeGreaterThan(100);
  });

  it("keeps every public page, and 404.html, within budget", () => {
    const pages = [...routes.map((r) => [r, readPage(r)]), ["404.html", fs.readFileSync(path.join(DIST, "404.html"), "utf8")]];
    const over = [];
    for (const [route, html] of pages) {
      const size = total(pageScripts(html));
      if (size > BUDGET) over.push(`${route}: ${kb(size)}`);
    }
    expect(over, "pages over budget").toEqual([]);
  });

  it("preloads each page's own screen, and its provision or module when it has one", () => {
    const expectations = [
      ["/", /\/Home-/],
      ["/act/section-6", /\/Provision-/],
      ["/act/section-6", /\/S6-/],
      ["/rules/schedule-first", /\/SCH-FIRST-/],
      ["/learn/core-rules", /\/Module-/],
      ["/learn/core-rules", /\/core-rules-/],
      ["/learn/core-rules/quiz", /\/Quiz-/],
      ["/glossary", /\/Glossary-/]
    ];
    for (const [route, chunk] of expectations) {
      const preloads = [...readPage(route).matchAll(/<link rel="modulepreload"[^>]*href="([^"]+)"/g)].map((m) => m[1]);
      expect(preloads.some((f) => chunk.test(f)), `${route} preloads ${chunk}`).toBe(true);
    }
  });

  it("stays within budget whichever screen and data chunk a page combines", () => {
    // Independent of the route table: the entry, plus the heaviest screen,
    // plus the heaviest provision or module chunk, still fits.
    const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, "dist-ssr", "client-manifest.json"), "utf8"));
    const closure = (key, into = new Set()) => {
      const e = manifest[key];
      if (!into.has(e.file)) {
        into.add(e.file);
        (e.imports || []).forEach((k) => closure(k, into));
      }
      return into;
    };
    const entry = closure("index.html");
    const extra = (key) => total([...closure(key)].filter((f) => !entry.has(f)));
    const keys = Object.keys(manifest);
    const heaviest = (keysOf) => Math.max(0, ...keysOf.map(extra));
    const worst =
      total(entry) +
      heaviest(keys.filter((k) => k.startsWith("src/components/screens/"))) +
      heaviest(keys.filter((k) => k.startsWith("virtual:")));
    expect(worst, `worst case ${kb(worst)}`).toBeLessThanOrEqual(BUDGET);
  });

  it("ships no Markdown parser and no gazette text in the entry", () => {
    const entry = [...pageScripts(readPage("/"))].map((f) => fs.readFileSync(path.join(DIST, f), "utf8")).join("\n");
    expect(entry).not.toContain("marked(): input parameter");
    expect(entry).not.toContain("free, specific, informed, unconditional and unambiguous");
  });
});
