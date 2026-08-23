import { marked } from "marked";

/**
 * Guide loading and parsing.
 *
 * Guides are markdown files with YAML-ish frontmatter, authored outside this
 * repo and dropped into src/content/guides/. Vite inlines them at build time,
 * so there is no fetch at runtime and the whole set is available for
 * prerendering.
 *
 * We parse frontmatter ourselves rather than pulling in gray-matter, which
 * expects Node's Buffer and needs a polyfill in the browser. The subset used
 * by these documents is small and fixed: scalars, string lists, and lists of
 * objects one level deep.
 */

const RAW = import.meta.glob("../content/guides/*.md", {
  query: "?raw",
  import: "default",
  eager: true
});

/** Strips matching surrounding quotes, which YAML treats as delimiters. */
function unquote(value) {
  const v = value.trim();
  if (v.length >= 2 && ((v[0] === '"' && v.at(-1) === '"') || (v[0] === "'" && v.at(-1) === "'"))) {
    return v.slice(1, -1);
  }
  return v;
}

function parseFrontmatter(source) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(source);
  if (!match) return { data: {}, body: source };

  const data = {};
  const lines = match[1].split(/\r?\n/);

  let key = null;      // current top-level key collecting a list
  let list = null;     // the array being built
  let item = null;     // current object inside that array

  for (const line of lines) {
    if (!line.trim() || line.trim().startsWith("#")) continue;

    const indent = line.length - line.trimStart().length;
    const trimmed = line.trim();

    // "- foo" or "- key: value" — a list entry
    if (trimmed.startsWith("- ")) {
      const rest = trimmed.slice(2);
      const kv = /^([A-Za-z0-9_]+):\s*(.*)$/.exec(rest);
      if (kv) {
        item = { [kv[1]]: unquote(kv[2]) };
        list?.push(item);
      } else {
        item = null;
        list?.push(unquote(rest));
      }
      continue;
    }

    // Indented "key: value" continues the current list item
    if (indent > 0 && item) {
      const kv = /^([A-Za-z0-9_]+):\s*(.*)$/.exec(trimmed);
      if (kv) item[kv[1]] = unquote(kv[2]);
      continue;
    }

    // Top-level "key: value" — or "key:" opening a list
    const kv = /^([A-Za-z0-9_]+):\s*(.*)$/.exec(trimmed);
    if (!kv) continue;

    if (kv[2] === "") {
      key = kv[1];
      list = [];
      item = null;
      data[key] = list;
    } else {
      data[kv[1]] = unquote(kv[2]);
      key = null;
      list = null;
      item = null;
    }
  }

  return { data, body: source.slice(match[0].length) };
}

/**
 * Splits the body into an ordered list of blocks.
 *
 * Prose becomes {type:'html'}. Container directives — `::: name` … `:::` —
 * become {type:'directive'} so a React component can render them, which is
 * how infographics and callouts stay components rather than dead markup.
 *
 * Directive bodies use `key: value` lines when they carry fields (the cta
 * block), otherwise the raw text is passed through as markdown.
 */
function parseBlocks(body) {
  const blocks = [];
  const lines = body.split(/\r?\n/);
  let prose = [];
  let directive = null;

  const flushProse = () => {
    const text = prose.join("\n").trim();
    if (text) blocks.push({ type: "html", html: marked.parse(text) });
    prose = [];
  };

  for (const line of lines) {
    const open = /^:::\s*([a-z0-9-]+)\s*$/i.exec(line.trim());
    const close = line.trim() === ":::";

    if (open && !directive) {
      flushProse();
      directive = { name: open[1].toLowerCase(), lines: [] };
      continue;
    }
    if (close && directive) {
      const raw = directive.lines.join("\n").trim();
      const fields = {};
      let hasFields = false;
      for (const l of directive.lines) {
        const kv = /^([a-z_]+):\s*(.+)$/i.exec(l.trim());
        if (kv) { fields[kv[1]] = kv[2].trim(); hasFields = true; }
      }
      blocks.push({
        type: "directive",
        name: directive.name,
        fields: hasFields ? fields : null,
        html: marked.parse(raw)
      });
      directive = null;
      continue;
    }
    if (directive) { directive.lines.push(line); continue; }
    prose.push(line);
  }

  if (directive) prose.push(...directive.lines); // unterminated block: treat as prose
  flushProse();
  return blocks;
}

/** Heading list for the table of contents, with ids matching what marked emits. */
function parseHeadings(body) {
  const headings = [];
  const seen = new Map();
  for (const line of body.split(/\r?\n/)) {
    const m = /^(#{2,3})\s+(.+?)\s*$/.exec(line);
    if (!m) continue;
    const text = m[2].replace(/[*_`]/g, "");
    let id = text.toLowerCase().trim()
      .replace(/[^\w\s-]/g, "")
      .replace(/\s+/g, "-");
    // marked appends -1, -2 … to repeated slugs; mirror that so links resolve.
    const n = seen.get(id) ?? 0;
    seen.set(id, n + 1);
    if (n > 0) id = `${id}-${n}`;
    headings.push({ depth: m[1].length, text, id });
  }
  return headings;
}

function build(path, source) {
  const { data, body } = parseFrontmatter(source);
  const slug = data.slug || path.split("/").pop().replace(/\.md$/, "");
  // The H1 is rendered from frontmatter, so drop it from the body to avoid two.
  const withoutH1 = body.replace(/^\s*#\s+.+?(\r?\n|$)/, "");

  return {
    slug,
    ...data,
    blocks: parseBlocks(withoutH1),
    headings: parseHeadings(withoutH1),
    wordCount: withoutH1.split(/\s+/).filter(Boolean).length
  };
}

const GUIDES = Object.entries(RAW)
  .map(([path, source]) => build(path, source))
  .sort((a, b) => String(b.published || "").localeCompare(String(a.published || "")));

export function listGuides() {
  return GUIDES;
}

export function getGuide(slug) {
  return GUIDES.find((g) => g.slug === slug) || null;
}

/** Slugs a prerender step can enumerate to emit one HTML file per guide. */
export function guideSlugs() {
  return GUIDES.map((g) => g.slug);
}
