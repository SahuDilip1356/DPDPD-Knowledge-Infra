/**
 * Citation extraction and checking.
 *
 * A plain-language note or a lesson may only cite provisions it has declared.
 * These helpers turn prose references — "Section 6(4)", "Rules 3 and 6",
 * "First Schedule", "the Schedule" — into the wiki's labels (S6, R3, R6,
 * SCH-FIRST, ACT-SCHEDULE) so a build step can compare them against an
 * allow-list and refuse to ship a page that cites what it should not.
 *
 * Pure functions, no I/O, so they run in the browser bundle and in Node.
 */

const ORDINALS = { first: "FIRST", second: "SECOND", third: "THIRD", fourth: "FOURTH", fifth: "FIFTH", sixth: "SIXTH", seventh: "SEVENTH" };

export const KNOWN_LABELS = new Set([
  ...Array.from({ length: 44 }, (_, i) => `S${i + 1}`),
  "ACT-SCHEDULE",
  ...Array.from({ length: 23 }, (_, i) => `R${i + 1}`),
  ...Object.values(ORDINALS).map((o) => `SCH-${o}`)
]);

/** "6(4)", "8", "3 and 6", "4, 5 and 7", "17 to 19" → [6] [8] [3,6] [4,5,7] [17,18,19] */
function numbers(list) {
  const out = [];
  const items = list.split(/\s*(?:,|and|&|or)\s*/i).map((s) => s.trim()).filter(Boolean);
  for (const item of items) {
    const range = /^(\d+)\s*(?:to|-|–)\s*(\d+)/.exec(item);
    if (range) {
      const [a, b] = [Number(range[1]), Number(range[2])];
      if (b >= a && b - a < 50) for (let n = a; n <= b; n++) out.push(n);
      continue;
    }
    const m = /^(\d+)/.exec(item);
    if (m) out.push(Number(m[1]));
  }
  return out;
}

// A list of numbers with optional sub-clauses: "6(1)", "8(5) and 8(6)", "17 to 19", "4, 5 and 7"
const LIST = String.raw`\d+(?:\s*\([^)]{1,4}\))*(?:\s*(?:,|and|&|or|to|-|–)\s*\d+(?:\s*\([^)]{1,4}\))*)*`;
const SECTION = new RegExp(String.raw`\b(?:sections?|ss?\.)\s*(${LIST})`, "gi");
const RULE = new RegExp(String.raw`\b(?:rules?|rr?\.)\s*(${LIST})`, "gi");
const RULES_SCHEDULE = /\b(first|second|third|fourth|fifth|sixth|seventh)\s+schedule\b/gi;
const ACT_SCHEDULE = /\b(?:the\s+schedule(?:\s+to\s+the\s+act)?|schedule\s+to\s+the\s+act|act'?s\s+schedule)\b/gi;

/** Labels cited in a piece of text, in order of first appearance, de-duplicated. */
export function extractCitations(text) {
  const found = [];
  const add = (l) => { if (!found.includes(l)) found.push(l); };
  const src = String(text ?? "");
  for (const m of src.matchAll(SECTION)) numbers(m[1]).forEach((n) => add(`S${n}`));
  for (const m of src.matchAll(RULE)) numbers(m[1]).forEach((n) => add(`R${n}`));
  for (const m of src.matchAll(RULES_SCHEDULE)) add(`SCH-${ORDINALS[m[1].toLowerCase()]}`);
  // "Third Schedule" also matches the bare "Schedule" pattern's neighbourhood; only
  // count the Act's Schedule when no ordinal precedes the word.
  for (const m of src.matchAll(ACT_SCHEDULE)) {
    const before = src.slice(Math.max(0, m.index - 12), m.index);
    if (!/(first|second|third|fourth|fifth|sixth|seventh)\s*$/i.test(before)) add("ACT-SCHEDULE");
  }
  return found;
}

/**
 * Citations in `text` that are not in `allowed`.
 * `allowed` is any iterable of labels; unknown labels in `allowed` are reported too,
 * because an allow-list that names a provision that does not exist is itself a defect.
 */
export function checkCitations(text, allowed) {
  const allow = new Set(allowed);
  const offenders = extractCitations(text).filter((l) => !allow.has(l));
  const unknownAllowed = [...allow].filter((l) => !KNOWN_LABELS.has(l));
  return { offenders, unknownAllowed, ok: offenders.length === 0 && unknownAllowed.length === 0 };
}

/** Route for a label, or null. */
export function routeForLabel(label) {
  let m;
  if ((m = /^S(\d+)$/.exec(label))) return `/act/section-${m[1]}`;
  if (label === "ACT-SCHEDULE") return "/act/schedule";
  if ((m = /^R(\d+)$/.exec(label))) return `/rules/rule-${m[1]}`;
  if ((m = /^SCH-([A-Z]+)$/.exec(label))) return `/rules/schedule-${m[1].toLowerCase()}`;
  return null;
}
