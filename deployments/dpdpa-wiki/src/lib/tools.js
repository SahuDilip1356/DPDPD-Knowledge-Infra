/**
 * Decision aids: read access to src/data/tools/decision-trees.json.
 *
 * A tree is data — questions, options, results — and every node names the
 * provisions it rests on, so the page can link each step to the gazette text
 * and a build check can refuse a tree that cites nothing or cites what does
 * not exist. `validateTree` is pure so tests can run it on fixtures.
 *
 * seo.js imports this file; this file must not import seo.js.
 */
import trees from "../data/tools/decision-trees.json";
import { getProvision, listProvisions, routeFor, heading } from "./law";

const SITE = "https://dpdpa.wiki";
const SITE_NAME = "DPDPA Wiki";

const TOOLS = trees;
const BY_SLUG = Object.fromEntries(TOOLS.map((t) => [t.slug, t]));

export function listTools() {
  return TOOLS;
}

export function getTool(slug) {
  return BY_SLUG[slug] || null;
}

export function toolRoutes() {
  return TOOLS.map((t) => `/tools/${t.slug}`);
}

/** Every label a tree cites, once each, in document order. */
export function treeLabels(tree) {
  const seen = new Set();
  for (const node of Object.values(tree.nodes || {})) {
    for (const l of node.cites || []) seen.add(l);
    for (const l of node.result?.cites || []) seen.add(l);
  }
  return listProvisions().map((p) => p.label).filter((l) => seen.has(l));
}

export function toolTitle(tree) {
  return `${tree.title} | ${SITE_NAME}`;
}

/**
 * Head tags for a tool route, in the shape seo.js's `tags()` accepts, or null
 * for a path that is not a tool. The WebPage's `about` lists the provisions
 * the tree draws on, so the structured data says what the page is about in
 * the same terms as the provision pages themselves.
 */
export function headForTool(path) {
  const clean = String(path || "").replace(/\/+$/, "");
  const m = /^\/tools\/([^/]+)$/.exec(clean);
  const tree = m ? getTool(m[1]) : null;
  if (!tree) return null;
  const route = `/tools/${tree.slug}`;
  const url = `${SITE}${route}`;
  return {
    title: toolTitle(tree),
    description: tree.summary,
    canonical: url,
    ogType: "website",
    jsonld: [
      {
        "@context": "https://schema.org",
        "@type": "WebPage",
        name: tree.title,
        description: tree.summary,
        url,
        inLanguage: "en-IN",
        isPartOf: { "@type": "WebSite", name: SITE_NAME, url: SITE },
        about: treeLabels(tree).map((label) => {
          const p = getProvision(label);
          return { "@type": "Legislation", name: heading(p), url: `${SITE}${routeFor(p)}` };
        })
      },
      {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: `${SITE}/` },
          { "@type": "ListItem", position: 2, name: tree.title, item: url }
        ]
      }
    ]
  };
}

/**
 * Problems with a tree, as strings; an empty array means the tree is sound.
 *
 * Checks: the start node exists; every node has a known type and non-empty,
 * known `cites`; every question has at least two options, each pointing at a
 * node that exists; every result carries a verdict, an explanation and its own
 * known `cites`; every node is reachable from the start; there are no cycles,
 * so every path ends in a result.
 */
export function validateTree(tree, knownLabels) {
  const problems = [];
  const known = knownLabels instanceof Set ? knownLabels : new Set(knownLabels || []);
  const nodes = tree?.nodes || {};
  const ids = Object.keys(nodes);
  const name = tree?.slug || "(tree)";

  if (!tree?.slug) problems.push(`${name}: missing slug`);
  if (!tree?.title) problems.push(`${name}: missing title`);
  if (!tree?.summary) problems.push(`${name}: missing summary`);
  if (!tree?.start) problems.push(`${name}: missing start`);
  else if (!nodes[tree.start]) problems.push(`${name}: start node "${tree.start}" does not exist`);
  if (ids.length === 0) problems.push(`${name}: no nodes`);

  const checkCites = (where, cites) => {
    if (!Array.isArray(cites) || cites.length === 0) {
      problems.push(`${name}/${where}: cites is empty`);
      return;
    }
    for (const l of cites) if (!known.has(l)) problems.push(`${name}/${where}: unknown label ${l}`);
  };

  for (const id of ids) {
    const n = nodes[id];
    if (!n.text) problems.push(`${name}/${id}: missing text`);
    checkCites(id, n.cites);
    if (n.type === "question") {
      if (!Array.isArray(n.options) || n.options.length < 2) {
        problems.push(`${name}/${id}: a question needs at least two options`);
      }
      for (const [i, o] of (n.options || []).entries()) {
        if (!o.label) problems.push(`${name}/${id}: option ${i} has no label`);
        if (!o.next) problems.push(`${name}/${id}: option ${i} has no next`);
        else if (!nodes[o.next]) problems.push(`${name}/${id}: option ${i} points at missing node "${o.next}"`);
      }
    } else if (n.type === "result") {
      if (!n.result?.verdict) problems.push(`${name}/${id}: result has no verdict`);
      if (!n.result?.explanation) problems.push(`${name}/${id}: result has no explanation`);
      checkCites(`${id}.result`, n.result?.cites);
      if (n.options) problems.push(`${name}/${id}: a result cannot have options`);
    } else {
      problems.push(`${name}/${id}: unknown type "${n.type}"`);
    }
  }

  // Reachability and cycles: a depth-first walk from the start, colouring
  // nodes grey while on the stack. Reaching a grey node is a cycle.
  const colour = new Map();
  const walk = (id, path) => {
    if (!nodes[id]) return;
    const c = colour.get(id);
    if (c === "grey") { problems.push(`${name}: cycle ${[...path, id].join(" → ")}`); return; }
    if (c === "black") return;
    colour.set(id, "grey");
    for (const o of nodes[id].options || []) if (o.next) walk(o.next, [...path, id]);
    colour.set(id, "black");
  };
  if (tree?.start && nodes[tree.start]) walk(tree.start, []);
  for (const id of ids) if (!colour.has(id)) problems.push(`${name}/${id}: unreachable from start`);

  return problems;
}
