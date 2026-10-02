/**
 * Writes real HTML for the public routes.
 *
 * A single-page app serves the same near-empty document for every URL, so the
 * content only exists once JavaScript has run. Crawlers that do not run it —
 * and answer engines and social unfurlers largely do not — see nothing. For a
 * site whose whole point is being found by search, that is self-defeating.
 *
 * This renders each public route to markup at build time and writes it into
 * the shipped index.html, head tags included. The client still hydrates on
 * load, so the app behaves exactly as before; the difference is only what a
 * request receives before any script runs.
 *
 * Workspace routes are left alone. They sit behind interaction and live data,
 * and nobody should be finding /admin in a search result.
 *
 * Each page's root carries data-route, so main.jsx hydrates only HTML rendered
 * for the URL it is on, and modulepreload links for the page's own screen and
 * data chunks, so they download alongside the entry script instead of after it.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const dist = path.join(root, "dist");
const template = fs.readFileSync(path.join(dist, "index.html"), "utf8");

const { render, publicRoutes, headFor, chunksFor } = await import(
  path.join(root, "dist-ssr", "entry-server.js")
);

// Vite's client manifest maps source ids to built chunks. It is a build
// artefact, not something to serve: moved out of dist/ into dist-ssr/, where
// tests/bundle-budget.test.js reads it.
const manifestPath = path.join(dist, ".vite", "manifest.json");
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
fs.renameSync(manifestPath, path.join(root, "dist-ssr", "client-manifest.json"));
fs.rmSync(path.join(dist, ".vite"), { recursive: true, force: true });

// The entry and its static imports are already in the template.
const inTemplate = new Set();
const closure = (key, into) => {
  const entry = manifest[key];
  if (!entry) throw new Error(`no chunk for ${key} in the client manifest`);
  if (into.has(entry.file)) return;
  into.add(entry.file);
  for (const dep of entry.imports || []) closure(dep, into);
};
closure("index.html", inTemplate);

/** <link rel=modulepreload> tags for the chunks a route renders from, beyond the entry's. */
function preloadsFor(route) {
  const files = new Set();
  for (const id of chunksFor(route)) closure(id, files);
  return [...files]
    .filter((f) => !inTemplate.has(f))
    .map((f) => `<link rel="modulepreload" crossorigin href="/${f}">`)
    .join("\n    ");
}

/** The template with a route's markup in the root and its chunks preloaded. */
function withRoute(route, html) {
  const preloads = preloadsFor(route);
  const doc = template.replace('<div id="root"></div>', `<div id="root" data-route="${route}">${html}</div>`);
  return preloads ? doc.replace("</head>", `  ${preloads}\n  </head>`) : doc;
}

const routes = publicRoutes();
const SITE = "https://dpdpa.wiki";
const today = new Date().toISOString().slice(0, 10);
let written = 0;

for (const route of routes) {
  let html;
  try {
    html = render(route);
  } catch (err) {
    console.error(`  ✗ ${route} — ${err.message}`);
    process.exitCode = 1;
    continue;
  }

  const head = headFor(route);
  let doc = withRoute(route, html);

  if (head) {
    // Replace the template's own title and description so they are not
    // duplicated, then insert the route's tags before </head>.
    doc = doc
      .replace(/\n?\s*<title>[\s\S]*?<\/title>/, "")
      .replace(/\n?\s*<meta name="description"[^>]*>/, "")
      .replace(/\n?\s*<link rel="canonical"[^>]*>/, "")
      .replace(/\n?\s*<meta property="og:(type|title|description|url|image)"[^>]*>/g, "")
      .replace(/\n?\s*<meta name="twitter:card"[^>]*>/, "")
      .replace("</head>", `  ${head}\n  </head>`);
  }

  const outPath =
    route === "/"
      ? path.join(dist, "index.html")
      : path.join(dist, route.replace(/^\//, ""), "index.html");

  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, doc);

  const bodyBytes = (/<body[^>]*>([\s\S]*?)<\/body>/.exec(doc)?.[1] || "").length;
  console.log(`  ✓ ${route.padEnd(42)} ${String(bodyBytes).padStart(7)} bytes`);
  written++;
}

// ── sitemap.xml: every public route, lastmod = build date ──
const sitemap = [
  '<?xml version="1.0" encoding="UTF-8"?>',
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
  ...routes.map((r) => `  <url><loc>${SITE}${r === "/" ? "/" : r}</loc><lastmod>${today}</lastmod></url>`),
  "</urlset>",
  ""
].join("\n");
fs.writeFileSync(path.join(dist, "sitemap.xml"), sitemap);

// ── 404.html: a real not-found page with a 404 status from the host ──
// Rendered from the /404 route (App maps it and the catch-all to NotFound).
try {
  const html404 = render("/404");
  const head404 = headFor("/404") || [
    "<title>Page not found | dpdpa.wiki</title>",
    '<meta name="robots" content="noindex" />',
    `<link rel="canonical" href="${SITE}/404" />`
  ].join("\n    ");
  let doc = withRoute("/404", html404);
  doc = doc
    .replace(/\n?\s*<title>[\s\S]*?<\/title>/, "")
    .replace(/\n?\s*<meta name="description"[^>]*>/, "")
    .replace(/\n?\s*<link rel="canonical"[^>]*>/, "")
    .replace(/\n?\s*<meta name="robots"[^>]*>/, "")
    .replace(/\n?\s*<meta property="og:(type|title|description|url)"[^>]*>/g, "")
    .replace("</head>", `  ${head404}\n  </head>`);
  fs.writeFileSync(path.join(dist, "404.html"), doc);
  console.log(`  ✓ ${"/404 → 404.html".padEnd(42)} ${String(html404.length).padStart(7)} bytes`);
} catch (err) {
  console.warn(`  ! 404.html not written — ${err.message}`);
}

// ── /workspace/index.html: the SPA document for the founder's workspace, noindex ──
{
  const wsDir = path.join(dist, "workspace");
  fs.mkdirSync(wsDir, { recursive: true });
  const ws = template.replace("</head>", '  <meta name="robots" content="noindex, nofollow" />\n  </head>');
  fs.writeFileSync(path.join(wsDir, "index.html"), ws);
}

console.log(`\n  ${written}/${routes.length} routes prerendered · sitemap.xml (${routes.length} urls) · 404.html · workspace/index.html`);
