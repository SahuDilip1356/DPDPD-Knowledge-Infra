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
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const dist = path.join(root, "dist");
const template = fs.readFileSync(path.join(dist, "index.html"), "utf8");

const { render, publicRoutes, headFor } = await import(
  path.join(root, "dist-ssr", "entry-server.js")
);

const routes = publicRoutes();
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
  let doc = template.replace('<div id="root"></div>', `<div id="root">${html}</div>`);

  if (head) {
    // Replace the template's own title and description so they are not
    // duplicated, then insert the route's tags before </head>.
    doc = doc
      .replace(/\n?\s*<title>[\s\S]*?<\/title>/, "")
      .replace(/\n?\s*<meta name="description"[^>]*>/, "")
      .replace(/\n?\s*<link rel="canonical"[^>]*>/, "")
      .replace(/\n?\s*<meta property="og:(type|title|description|url)"[^>]*>/g, "")
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

console.log(`\n  ${written}/${routes.length} routes prerendered`);
