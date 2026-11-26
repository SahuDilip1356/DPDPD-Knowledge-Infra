import scenarios from "virtual:scenarios";
import { SITE } from "./site";

/**
 * The six napkin scenarios at /learn/scenarios.
 *
 * One record in the course-module format, built from
 * src/content/scenarios.md by scripts/vite-content.mjs. It is small, so the
 * whole record ships with the page's own chunk.
 */
export const SCENARIOS_PATH = "/learn/scenarios";
export const SCENARIOS_TITLE = "Six napkins: the DPDP Act in six pictures | DPDPA Wiki";

export function getScenarios() {
  return scenarios;
}

/** The `tags()` input for /learn/scenarios (see seo.js). */
export function headForScenarios() {
  const s = scenarios;
  const url = `${SITE}${SCENARIOS_PATH}`;
  return {
    title: SCENARIOS_TITLE,
    description: s.summary,
    canonical: url,
    ogType: "article",
    jsonld: [
      {
        "@context": "https://schema.org",
        "@type": "LearningResource",
        name: s.title,
        description: s.summary,
        url,
        inLanguage: "en-IN",
        isAccessibleForFree: true,
        educationalLevel: "Beginner",
        learningResourceType: "Worked examples",
        teaches: s.lessons.map((l) => l.heading),
        provider: { "@type": "Organization", name: "SaralPrivacy Knowledge Infra", url: SITE },
        isPartOf: { "@type": "CollectionPage", name: "Learn the DPDPA", url: `${SITE}/learn` }
      },
      {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        itemListElement: [["Home", "/"], ["Learn", "/learn"], ["Six napkins", SCENARIOS_PATH]].map(([name, path], i) => ({
          "@type": "ListItem", position: i + 1, name, item: `${SITE}${path}`
        }))
      }
    ]
  };
}
