import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = fileURLToPath(new URL("../../", import.meta.url));
export const DIST = path.join(ROOT, "dist");

/** Path of the prerendered HTML file for a public route. */
export function distPath(route) {
  const clean = route.replace(/\/+$/, "") || "/";
  return clean === "/"
    ? path.join(DIST, "index.html")
    : path.join(DIST, clean.replace(/^\//, ""), "index.html");
}

/** The prerendered HTML for a public route, or null when it was not built. */
export function readPage(route) {
  const p = distPath(route);
  return fs.existsSync(p) ? fs.readFileSync(p, "utf8") : null;
}

/** Every prerendered route in dist/, as "/a/b" paths. */
export function builtRoutes() {
  if (!fs.existsSync(DIST)) return [];
  const out = [];
  const walk = (dir, rel) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (entry.isDirectory()) {
        if (entry.name === "assets") continue;
        walk(path.join(dir, entry.name), `${rel}/${entry.name}`);
      } else if (entry.name === "index.html") {
        out.push(rel || "/");
      }
    }
  };
  walk(DIST, "");
  return out.sort();
}

/** The text between <body> and </body>, with tags stripped and whitespace collapsed. */
export function bodyText(html) {
  const body = /<body[^>]*>([\s\S]*?)<\/body>/.exec(html)?.[1] || "";
  return body
    .replace(/<script[\s\S]*?<\/script>/g, "")
    .replace(/<style[\s\S]*?<\/style>/g, "")
    .replace(/<[^>]+>/g, " ")
    .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#x27;|&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

/** Parsed JSON-LD blocks found in the document head or body. */
export function jsonLd(html) {
  const out = [];
  const re = /<script type="application\/ld\+json">([\s\S]*?)<\/script>/g;
  let m;
  while ((m = re.exec(html))) {
    try { out.push(JSON.parse(m[1])); } catch { /* malformed block: leave it to the test */ }
  }
  return out;
}

/** Content of a <meta name|property="..."> tag, or null. */
export function meta(html, key) {
  const re = new RegExp(`<meta (?:name|property)="${key}" content="([^"]*)"`);
  return re.exec(html)?.[1] ?? null;
}

export function title(html) {
  return /<title>([\s\S]*?)<\/title>/.exec(html)?.[1] ?? null;
}

export function canonical(html) {
  return /<link rel="canonical" href="([^"]*)"/.exec(html)?.[1] ?? null;
}
