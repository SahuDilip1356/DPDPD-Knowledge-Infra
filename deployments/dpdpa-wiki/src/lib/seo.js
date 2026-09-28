import { listGuides, getGuide } from "./guides";
import { FAQ } from "../data/homeContent";
import {
  DOCS, CHAPTERS, listProvisions, getByRoute, provisionRoutes, documentOf, displayLabel,
  isInForce, pageTitle, heading, excerpt, routeFor,
  listGlossary, getTerm, glossaryRoutes, glossaryTitle,
  ACT_INDEX_TITLE, RULES_INDEX_TITLE, GLOSSARY_TITLE
} from "./law";

export const SITE = "https://dpdpa.wiki";
/* One image for every page until per-page cards exist. The file itself is
   produced by a separate task; the tag is emitted regardless so unfurlers
   never see a page with no image at all. */
export const OG_IMAGE = `${SITE}/og-default.png`;

const esc = (s) =>
  String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

/**
 * Head tags for a public route, as an HTML string.
 *
 * These are produced here rather than only in a React effect because an effect
 * runs after JavaScript loads — too late for a crawler reading the response.
 * The prerender step writes this into the document it emits, so the title,
 * description, canonical and structured data are present in the HTML itself.
 */
export function headFor(path) {
  const clean = path.replace(/\/+$/, "") || "/";

  if (clean === "/") {
    return tags({
      title: "DPDP Act 2023 — Understand and implement India's data protection law | dpdpa.wiki",
      description:
        "A citation-grounded reference for India's Digital Personal Data Protection Act, 2023. Obligations, rights, penalties, consent and breach response — every claim traced to its section, rule or gazette notification.",
      canonical: `${SITE}/`,
      ogType: "website",
      // The FAQ answers are the homepage's most search-visible content, so the
      // structured data has to be in the document rather than added by script.
      jsonld: {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        mainEntity: FAQ.map(({ q, a }) => ({
          "@type": "Question",
          name: q,
          acceptedAnswer: { "@type": "Answer", text: a }
        }))
      }
    });
  }

  if (clean === "/guide") {
    return tags({
      title: "Guides to the DPDP Act | dpdpa.wiki",
      description:
        "Long-form guides to India's Digital Personal Data Protection Act, in plain language, with worked examples from Indian businesses and the sections cited throughout.",
      canonical: `${SITE}/guide`,
      ogType: "website",
      jsonld: {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        name: "Guides to the DPDP Act",
        url: `${SITE}/guide`,
        inLanguage: "en-IN",
        hasPart: listGuides().map((g) => ({
          "@type": "Article",
          headline: g.title,
          url: `${SITE}/guide/${g.slug}`,
          datePublished: g.published
        }))
      }
    });
  }

  const m = /^\/guide\/([^/]+)$/.exec(clean);
  if (m) {
    const g = getGuide(m[1]);
    if (!g) return "";
    const canonical = g.canonical || `${SITE}/guide/${g.slug}`;
    return tags({
      title: g.meta_title || g.title,
      description: g.meta_description || "",
      canonical,
      ogType: "article",
      jsonld: {
        "@context": "https://schema.org",
        "@type": "Article",
        headline: g.title,
        description: g.meta_description,
        datePublished: g.published,
        inLanguage: "en-IN",
        author: { "@type": "Organization", name: g.author || "SaralPrivacy" },
        publisher: { "@type": "Organization", name: "SaralPrivacy" },
        mainEntityOfPage: { "@type": "WebPage", "@id": canonical },
        keywords: [g.primary_keyword, ...(g.secondary_keywords || [])].filter(Boolean).join(", ")
      }
    });
  }

  if (clean === "/act" || clean === "/rules") return indexHead(clean === "/act" ? DOCS.act : DOCS.rules);

  const p = getByRoute(clean);
  if (p) return provisionHead(p);

  if (clean === "/glossary") return glossaryIndexHead();

  const g = /^\/glossary\/([^/]+)$/.exec(clean);
  if (g) {
    const term = getTerm(g[1]);
    return term ? glossaryEntryHead(term) : "";
  }

  return "";
}

function breadcrumbs(items) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map(([name, path], i) => ({
      "@type": "ListItem",
      position: i + 1,
      name,
      item: `${SITE}${path}`
    }))
  };
}

/* A provision page: the Legislation object describes the provision itself,
   with the whole Act or Rules as its parent. Legal force is stated only for
   the Rules, whose commencement dates are in the record; the Act's are not
   verified, so nothing is claimed. */
function provisionHead(p) {
  const doc = documentOf(p);
  const url = `${SITE}${routeFor(p)}`;
  const legislation = {
    "@context": "https://schema.org",
    "@type": "Legislation",
    name: heading(p),
    legislationIdentifier: displayLabel(p),
    legislationType: doc.legislationType,
    inLanguage: "en-IN",
    isPartOf: { "@type": "Legislation", name: doc.name },
    legislationDate: doc.legislationDate,
    url
  };
  if (doc === DOCS.rules) {
    legislation.legislationLegalForce = isInForce(p) ? "InForce" : "NotInForce";
  }
  return tags({
    title: pageTitle(p),
    description: excerpt(p.text),
    canonical: url,
    ogType: "article",
    jsonld: [legislation, breadcrumbs([["Home", "/"], [doc.short, doc.route], [displayLabel(p), routeFor(p)]])]
  });
}

function indexHead(doc) {
  const isAct = doc === DOCS.act;
  const parts = listProvisions().filter((p) => documentOf(p) === doc);
  return tags({
    title: isAct ? ACT_INDEX_TITLE : RULES_INDEX_TITLE,
    description: isAct
      ? `Every section of the ${doc.name}, in ${CHAPTERS.length} chapters, plus the Schedule of penalties. Each page carries the gazette text as printed.`
      : `Every rule and schedule of the ${doc.name}, with the date each one applies from. Each page carries the gazette text as printed.`,
    canonical: `${SITE}${doc.route}`,
    ogType: "website",
    jsonld: [
      {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        name: doc.name,
        url: `${SITE}${doc.route}`,
        inLanguage: "en-IN",
        hasPart: parts.map((p) => ({ "@type": "Legislation", name: heading(p), url: `${SITE}${routeFor(p)}` }))
      },
      breadcrumbs([["Home", "/"], [doc.short, doc.route]])
    ]
  });
}

const TERM_SET = { "@type": "DefinedTermSet", name: "DPDPA 2023 definitions", url: `${SITE}/glossary` };

function glossaryIndexHead() {
  return tags({
    title: GLOSSARY_TITLE,
    description: `${listGlossary().length} terms defined in Section 2 of the Digital Personal Data Protection Act, 2023 and Rule 2 of the DPDP Rules, 2025, each in the words of the gazette.`,
    canonical: `${SITE}/glossary`,
    ogType: "website",
    jsonld: [
      {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        name: "DPDPA 2023 definitions",
        url: `${SITE}/glossary`,
        inLanguage: "en-IN",
        hasPart: listGlossary().map((t) => ({ "@type": "DefinedTerm", name: t.term, url: `${SITE}/glossary/${t.slug}` }))
      },
      breadcrumbs([["Home", "/"], ["Glossary", "/glossary"]])
    ]
  });
}

function glossaryEntryHead(t) {
  const url = `${SITE}/glossary/${t.slug}`;
  return tags({
    title: glossaryTitle(t),
    description: excerpt(t.definition),
    canonical: url,
    ogType: "article",
    jsonld: [
      {
        "@context": "https://schema.org",
        "@type": "DefinedTerm",
        name: t.term,
        description: t.definition,
        inDefinedTermSet: TERM_SET,
        url
      },
      breadcrumbs([["Home", "/"], ["Glossary", "/glossary"], [t.term, `/glossary/${t.slug}`]])
    ]
  });
}

function tags({ title, description, canonical, ogType, ogImage = OG_IMAGE, jsonld }) {
  const out = [
    `<title>${esc(title)}</title>`,
    `<meta name="description" content="${esc(description)}" />`,
    `<link rel="canonical" href="${esc(canonical)}" />`,
    `<meta property="og:type" content="${esc(ogType)}" />`,
    `<meta property="og:title" content="${esc(title)}" />`,
    `<meta property="og:description" content="${esc(description)}" />`,
    `<meta property="og:url" content="${esc(canonical)}" />`,
    `<meta property="og:image" content="${esc(ogImage)}" />`,
    `<meta name="twitter:card" content="summary_large_image" />`
  ];
  for (const block of [].concat(jsonld || [])) {
    // Only "</script" needs neutralising inside a JSON-LD block.
    const json = JSON.stringify(block).replace(/<\/script/gi, "<\\/script");
    out.push(`<script type="application/ld+json">${json}</script>`);
  }
  return out.join("\n    ");
}

/** Every public path the prerender step should emit HTML for. */
export function publicRoutes() {
  return [
    "/",
    "/guide",
    ...listGuides().map((g) => `/guide/${g.slug}`),
    "/act",
    "/rules",
    ...provisionRoutes(),
    "/glossary",
    ...glossaryRoutes()
  ];
}
