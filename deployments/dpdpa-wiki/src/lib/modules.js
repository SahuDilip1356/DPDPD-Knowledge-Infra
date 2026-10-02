import { modules, loaders } from "virtual:course";
import { getProvision } from "./law";
import { routeForLabel } from "./citations";
import { SITE } from "./site";

/**
 * Course modules: lookup, loading and head tags.
 *
 * One Markdown file per module under src/content/modules/NN-slug.md (see the
 * README there). src/lib/module-build.js turns them into records at build
 * time, served through virtual:course (scripts/vite-content.mjs), so the same
 * records feed the prerender, the client and the tests.
 *
 * On the server every record is complete. In the browser the list holds each
 * module's summary — enough for the course index, the home page and the
 * course track — and loadModule() fetches one module's lessons and self-test
 * for the page that shows them.
 */

export const TOTAL_MODULES = 6;
export const SITE_NAME = "DPDPA Wiki";
export const PROVIDER = { "@type": "Organization", name: "SaralPrivacy Knowledge Infra", url: SITE };
export const LEARN_TITLE = "Learn the DPDPA — a six-module course | DPDPA Wiki";
export const LEARN_DESCRIPTION =
  "Six short modules on India's Digital Personal Data Protection Act, 2023 and the DPDP Rules, 2025, in order from what the Act is to what it asks of your business. Every statement cites its section or rule; every module ends in a self-test.";

const MODULES = [...modules].sort((a, b) => a.order - b.order);
const loading = new Map();

export function listModules() {
  return MODULES;
}

/** A module's record: complete once loaded (always, outside the browser), its summary before. */
export function getModule(slug) {
  return MODULES.find((m) => m.slug === slug) || null;
}

/** True when the record carries its lessons and self-test. */
export function isModuleLoaded(m) {
  return !loaders || "lessons" in m;
}

/**
 * Fetches one module's lessons and self-test into its record. Resolves to the
 * record, or null for a slug that names no module; repeat calls share a promise.
 */
export function loadModule(slug) {
  const m = getModule(slug);
  if (!m || isModuleLoaded(m)) return Promise.resolve(m);
  if (!loading.has(slug)) {
    loading.set(slug, loaders[slug]().then((mod) => Object.assign(m, mod.default)));
  }
  return loading.get(slug);
}

/** Questions readers ask about this module's provisions, most-asked first, one per provision. */
export function moduleQuestions(m, limit = 5) {
  return m.questions.slice(0, limit);
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
