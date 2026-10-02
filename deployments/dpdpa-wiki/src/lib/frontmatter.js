/**
 * Front-matter parsing for the Markdown content (guides and course modules).
 *
 * We parse front-matter ourselves rather than pulling in gray-matter, which
 * expects Node's Buffer and needs a polyfill in the browser. The subset used
 * by these documents is small and fixed: scalars, string lists, and lists of
 * objects one level deep.
 *
 * No imports, so it runs in the browser bundle, the prerender and the Vite
 * plugin that builds the course records in Node.
 */

/** Strips matching surrounding quotes, which YAML treats as delimiters. */
function unquote(value) {
  const v = value.trim();
  if (v.length >= 2 && ((v[0] === '"' && v.at(-1) === '"') || (v[0] === "'" && v.at(-1) === "'"))) {
    return v.slice(1, -1);
  }
  return v;
}

export function parseFrontmatter(source) {
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
