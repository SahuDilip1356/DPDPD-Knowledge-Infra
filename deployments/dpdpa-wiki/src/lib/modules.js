import { Marked } from "marked";
import { parseFrontmatter } from "./guides";
import { extractCitations, routeForLabel } from "./citations";
import { getProvision, formatDate, isInForce } from "./law";
import { SITE } from "./site";

/**
 * Course modules: loader, citation linker and head-tag builder.
 *
 * One Markdown file per module under src/content/modules/NN-slug.md (see the
 * README there). The front-matter is the Module record from the spec; the body
 * is the intro followed by one `## ` section per lesson. Vite inlines the files
 * at build time, so the same records feed the prerender, the client and the
 * tests.
 *
 * The loader is tolerant — a half-written module still produces a record — and
 * tests/modules.test.js is strict about the shape, so an author sees a failing
 * test rather than a build that will not start.
 */

export const TOTAL_MODULES = 6;
export const SITE_NAME = "DPDPA Wiki";
export const PROVIDER = { "@type": "Organization", name: "SaralPrivacy Knowledge Infra", url: SITE };
export const LEARN_TITLE = "Learn the DPDPA — a six-module course | DPDPA Wiki";
export const LEARN_DESCRIPTION =
  "Six short modules on India's Digital Personal Data Protection Act, 2023 and the DPDP Rules, 2025, in order from what the Act is to what it asks of your business. Every statement cites its section or rule; every module ends in a self-test.";

const RAW = import.meta.glob("../content/modules/*.md", {
  query: "?raw",
  import: "default",
  eager: true
});

/* ── Front-matter helpers ────────────────────────────────────────── */

/** "[S1, S2]" or "S2, R2" or ["S1"] → ["S1", "S2"]. */
export function labelList(value) {
  if (Array.isArray(value)) return value.map((v) => String(v).trim()).filter(Boolean);
  return String(value ?? "")
    .replace(/^\s*\[|\]\s*$/g, "")
    .split(",")
    .map((s) => s.trim().replace(/^["']|["']$/g, ""))
    .filter(Boolean);
}

/** "b" → 1, "2" → 2, "B" → 1; anything else → -1. */
function answerIndex(value) {
  const v = String(value ?? "").trim().toLowerCase();
  if (/^[a-d]$/.test(v)) return v.charCodeAt(0) - 97;
  if (/^[0-3]$/.test(v)) return Number(v);
  return -1;
}

function quizItem(raw) {
  const options = ["a", "b", "c", "d"].every((k) => raw[k] != null)
    ? ["a", "b", "c", "d"].map((k) => String(raw[k]))
    : labelList(raw.options);
  return {
    q: String(raw.q ?? "").trim(),
    options,
    answer: answerIndex(raw.answer),
    cites: labelList(raw.cites)
  };
}

function nullable(value) {
  const v = String(value ?? "").trim();
  return v === "" || v.toLowerCase() === "null" || v === "~" ? null : v;
}

/* ── Markdown ────────────────────────────────────────────────────── */

function slugify(text) {
  return text.toLowerCase().trim().replace(/[^\w\s-]/g, "").replace(/\s+/g, "-");
}

const md = new Marked();

/* ── Citation linking ────────────────────────────────────────────── */

// A number with optional sub-clauses: "6", "6(4)", "8(5)(a)".
const NUM = String.raw`\d{1,2}(?:\s?\([^)\s]{1,4}\))*`;
// A list of them: "4, 5 and 7", "8(5) and 8(6)", "17 to 19", "3, 5, or 6".
const CONJ = String.raw`\s*(?:,\s*(?:and|or)?|and|&|or|to|–|-)\s*`;
const LIST = `${NUM}(?:${CONJ}${NUM})*`;
const ORDINALS = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh"];

const CITE = new RegExp(
  [
    String.raw`\b(?<secword>[Ss]ections?)\s+(?<seclist>${LIST})`,
    String.raw`\b(?<ruleword>[Rr]ules?)\s+(?<rulelist>${LIST})`,
    String.raw`\b(?<ord>${ORDINALS.join("|")})\s+[Ss]chedule\b`,
    String.raw`\b(?<act>[Tt]he\s+[Ss]chedule(?:\s+to\s+the\s+Act)?)\b`
  ].join("|"),
  "gi"
);
const NUM_TOKEN = new RegExp(`(${NUM})`, "g");

function anchor(label, text) {
  const route = routeForLabel(label);
  return getProvision(label) && route ? `<a class="cite" href="${route}">${text}</a>` : text;
}

/**
 * Turns inline references in rendered HTML into links to provision pages,
 * leaving the wording as it stands. Only text is touched: nothing inside an
 * existing <a>, <code> or <pre> is rewritten. A cited Rule (or Rules Schedule)
 * that is not yet in force gets an "applies from" badge after its first link.
 *
 * `badged` is shared across calls so the badge appears once per lesson even
 * when the lesson is rendered in several pieces.
 */
export function linkCitations(html, { badged = new Set(), onDate = new Date() } = {}) {
  const badge = (label) => {
    const p = getProvision(label);
    if (!p || badged.has(label) || isInForce(p, onDate) !== false) return "";
    badged.add(label);
    return `<span class="cite-badge">applies from ${formatDate(p.in_force_from)}</span>`;
  };
  const linkList = (word, list, prefix) => {
    let first = true;
    const linked = list.replace(NUM_TOKEN, (token) => {
      const n = /^\d+/.exec(token)[0];
      const label = `${prefix}${Number(n)}`;
      const text = first ? `${word} ${token}` : token;
      first = false;
      return anchor(label, text) + badge(label);
    });
    return linked.startsWith(word) ? linked : `${word} ${linked}`;
  };
  const replaceText = (text) =>
    text.replace(CITE, (m, ...rest) => {
      const g = rest.at(-1);
      if (g.secword) return linkList(g.secword, g.seclist, "S");
      if (g.ruleword) return linkList(g.ruleword, g.rulelist, "R");
      if (g.ord) {
        const label = `SCH-${g.ord.toUpperCase()}`;
        return anchor(label, m) + badge(label);
      }
      if (g.act) return anchor("ACT-SCHEDULE", m);
      return m;
    });

  // Walk tags and text separately so markup is never matched as prose.
  const parts = String(html).split(/(<[^>]+>)/);
  let skip = 0;
  return parts
    .map((part) => {
      if (part.startsWith("<")) {
        if (/^<(a|code|pre)\b/i.test(part)) skip++;
        else if (/^<\/(a|code|pre)\b/i.test(part)) skip = Math.max(0, skip - 1);
        return part;
      }
      return skip > 0 || !part ? part : replaceText(part);
    })
    .join("");
}

/* ── Module records ──────────────────────────────────────────────── */

function splitLessons(body) {
  const sections = body.replace(/^\s*#\s+.+?(\r?\n|$)/, "").split(/^(?=##\s)/m);
  const intro = sections[0] && !/^##\s/.test(sections[0]) ? sections.shift() : "";
  const seen = new Map();
  const lessons = sections.map((sec) => {
    const m = /^##\s+(.+?)\s*$/m.exec(sec);
    const heading = (m?.[1] || "").replace(/[*_`]/g, "").trim();
    let id = slugify(heading) || "lesson";
    const n = seen.get(id) ?? 0;
    seen.set(id, n + 1);
    if (n > 0) id = `${id}-${n}`;
    const text = sec.slice(m ? m.index + m[0].length : 0);
    return { heading, id, markdown: text.trim(), cites: extractCitations(sec) };
  });
  return { intro: intro.trim(), lessons };
}

/** One Module record from a Markdown source. Exported for the tests' fixtures. */
export function buildModule(source, path = "") {
  const { data, body } = parseFrontmatter(source);
  const file = path.split("/").pop() || "";
  const slug = String(data.slug || file.replace(/^\d\d-/, "").replace(/\.md$/, "")).trim();
  const order = Number(data.order ?? /^(\d\d)-/.exec(file)?.[1] ?? 0);
  const { intro, lessons } = splitLessons(body);
  const handoff = data.handoff_url ? { label: String(data.handoff_label || "Continue"), url: String(data.handoff_url) } : null;

  const introBadged = new Set();
  return {
    slug,
    order,
    title: String(data.title || "").trim(),
    summary: String(data.summary || "").trim(),
    minutes: Number(data.minutes) || Math.max(1, Math.ceil(body.split(/\s+/).filter(Boolean).length / 200)),
    provisions: labelList(data.provisions),
    next: nullable(data.next),
    handoff,
    quiz: Array.isArray(data.quiz) ? data.quiz.filter((q) => q && typeof q === "object").map(quizItem) : [],
    intro_html: intro ? linkCitations(md.parse(intro), { badged: introBadged }) : "",
    intro_cites: extractCitations(intro),
    lessons: lessons.map(({ heading, id, markdown, cites }) => ({
      heading,
      id,
      cites,
      html: linkCitations(md.parse(markdown), { badged: new Set() })
    }))
  };
}

const MODULES = Object.entries(RAW)
  .filter(([path]) => /\d\d-.+\.md$/.test(path))
  .map(([path, source]) => buildModule(source, path))
  .sort((a, b) => a.order - b.order);

export function listModules() {
  return MODULES;
}

export function getModule(slug) {
  return MODULES.find((m) => m.slug === slug) || null;
}

/** The module after / before this one in the course, by declared `next` or by order. */
export function nextModule(m) {
  return (m.next && getModule(m.next)) || MODULES.find((x) => x.order === m.order + 1) || null;
}
export function prevModule(m) {
  return MODULES.find((x) => x.next === m.slug) || MODULES.find((x) => x.order === m.order - 1) || null;
}

export function modulePath(m) {
  return `/learn/${m.slug}`;
}
export function quizPath(m) {
  return `/learn/${m.slug}/quiz`;
}

export function moduleRoutes() {
  return ["/learn", ...MODULES.flatMap((m) => [modulePath(m), quizPath(m)])];
}

/* ── Head tags ───────────────────────────────────────────────────── */

export function moduleTitleTag(m) {
  return `${m.title} — Module ${m.order} of ${TOTAL_MODULES} | ${SITE_NAME}`;
}
export function quizTitleTag(m) {
  return `${m.title} — self-test | ${SITE_NAME}`;
}
export function quizDescription(m) {
  return `${m.quiz.length} questions on ${m.title.replace(/[.?!]$/, "")}. Mark yourself; every answer links to the provision it rests on.`;
}

function breadcrumbs(items) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map(([name, path], i) => ({ "@type": "ListItem", position: i + 1, name, item: `${SITE}${path}` }))
  };
}

function courseOf(m) {
  return {
    "@context": "https://schema.org",
    "@type": "Course",
    name: m.title,
    description: m.summary,
    url: `${SITE}${modulePath(m)}`,
    provider: PROVIDER,
    hasCourseInstance: { "@type": "CourseInstance", courseMode: "online", courseWorkload: `PT${m.minutes}M` },
    isAccessibleForFree: true,
    inLanguage: "en-IN",
    learningResourceType: "Lesson",
    educationalLevel: "Beginner",
    timeRequired: `PT${m.minutes}M`,
    teaches: m.lessons.map((l) => l.heading),
    about: m.provisions
      .map((label) => ({ label, p: getProvision(label) }))
      .filter(({ p }) => p)
      .map(({ label, p }) => ({ "@type": "Legislation", name: p.title, legislationIdentifier: label, url: `${SITE}${routeForLabel(label)}` })),
    position: m.order,
    isPartOf: { "@type": "CollectionPage", name: "Learn the DPDPA", url: `${SITE}/learn` }
  };
}

/**
 * The `tags()` input for a /learn path, or null when the path names nothing.
 * seo.js spreads this into its head builder; the shape is its contract.
 */
export function headForModule(path) {
  const clean = String(path || "").replace(/\/+$/, "") || "/";

  if (clean === "/learn") {
    return {
      title: LEARN_TITLE,
      description: LEARN_DESCRIPTION,
      canonical: `${SITE}/learn`,
      ogType: "website",
      jsonld: [
        {
          "@context": "https://schema.org",
          "@type": "CollectionPage",
          name: "Learn the DPDPA",
          description: LEARN_DESCRIPTION,
          url: `${SITE}/learn`,
          inLanguage: "en-IN",
          hasPart: MODULES.map((m) => ({ "@type": "Course", name: m.title, description: m.summary, url: `${SITE}${modulePath(m)}`, position: m.order }))
        },
        breadcrumbs([["Home", "/"], ["Learn", "/learn"]])
      ]
    };
  }

  const match = /^\/learn\/([^/]+)(\/quiz)?$/.exec(clean);
  if (!match) return null;
  const m = getModule(match[1]);
  if (!m) return null;

  if (match[2]) {
    return {
      title: quizTitleTag(m),
      description: quizDescription(m),
      canonical: `${SITE}${quizPath(m)}`,
      ogType: "website",
      jsonld: [
        {
          "@context": "https://schema.org",
          "@type": "Quiz",
          name: `${m.title} — self-test`,
          url: `${SITE}${quizPath(m)}`,
          inLanguage: "en-IN",
          about: { "@type": "Course", name: m.title, url: `${SITE}${modulePath(m)}` },
          educationalAlignment: { "@type": "AlignmentObject", alignmentType: "assesses", targetName: m.title },
          // The question text only. Answers stay out of the document (spec AC7).
          hasPart: m.quiz.map((q, i) => ({ "@type": "Question", name: q.q, position: i + 1, eduQuestionType: "Multiple choice" }))
        },
        breadcrumbs([["Home", "/"], ["Learn", "/learn"], [m.title, modulePath(m)], ["Self-test", quizPath(m)]])
      ]
    };
  }

  return {
    title: moduleTitleTag(m),
    description: m.summary,
    canonical: `${SITE}${modulePath(m)}`,
    ogType: "article",
    jsonld: [courseOf(m), breadcrumbs([["Home", "/"], ["Learn", "/learn"], [`Module ${m.order}`, modulePath(m)]])]
  };
}
