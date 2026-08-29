import { listGuides, getGuide } from "./guides";
import { FAQ } from "../data/homeContent";

export const SITE = "https://dpdpa.wiki";

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

  return "";
}

function tags({ title, description, canonical, ogType, jsonld }) {
  const out = [
    `<title>${esc(title)}</title>`,
    `<meta name="description" content="${esc(description)}" />`,
    `<link rel="canonical" href="${esc(canonical)}" />`,
    `<meta property="og:type" content="${esc(ogType)}" />`,
    `<meta property="og:title" content="${esc(title)}" />`,
    `<meta property="og:description" content="${esc(description)}" />`,
    `<meta property="og:url" content="${esc(canonical)}" />`
  ];
  if (jsonld) {
    // Only "</script" needs neutralising inside a JSON-LD block.
    const json = JSON.stringify(jsonld).replace(/<\/script/gi, "<\\/script");
    out.push(`<script type="application/ld+json">${json}</script>`);
  }
  return out.join("\n    ");
}

/** Every public path the prerender step should emit HTML for. */
export function publicRoutes() {
  return ["/", "/guide", ...listGuides().map((g) => `/guide/${g.slug}`)];
}
