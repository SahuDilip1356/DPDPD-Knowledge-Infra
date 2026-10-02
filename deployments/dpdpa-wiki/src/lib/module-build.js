import { Marked } from "marked";
import { parseFrontmatter } from "./frontmatter.js";
import { extractCitations, routeForLabel } from "./citations.js";
import { formatDate, isInForce } from "./dates.js";

/**
 * Builds course Module records from their Markdown sources.
 *
 * This runs at build time, in Node, inside the Vite plugin in
 * scripts/vite-content.mjs: the browser receives finished records and never
 * parses Markdown. So nothing here needs Vite, and every relative import
 * carries its extension.
 *
 * The builder is tolerant — a half-written module still produces a record —
 * and tests/modules.test.js is strict about the shape, so an author sees a
 * failing test rather than a build that will not start.
 */

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
    String.raw`\b(?<ord>${ORDINALS.map((o) => `[${o[0].toUpperCase()}${o[0]}]${o.slice(1)}`).join("|")})\s+[Ss]chedule\b`,
    // Capital S only: "build the schedule" in prose is not the Act's penalty Schedule.
    String.raw`\b(?<act>[Tt]he\s+Schedule(?:\s+to\s+the\s+Act)?)\b`
  ].join("|"),
  "g"
);
const NUM_TOKEN = new RegExp(`(${NUM})`, "g");

function anchor(getProvision, label, text) {
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
 * when the lesson is rendered in several pieces. `getProvision` looks a label
 * up in the law corpus.
 */
export function linkCitations(html, { getProvision, badged = new Set(), onDate = new Date() }) {
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
      return anchor(getProvision, label, text) + badge(label);
    });
    return linked; // the first link already carries the word ("Section 3(a)")
  };
  const replaceText = (text) =>
    text.replace(CITE, (m, ...rest) => {
      const g = rest.at(-1);
      if (g.secword) return linkList(g.secword, g.seclist, "S");
      if (g.ruleword) return linkList(g.ruleword, g.rulelist, "R");
      if (g.ord) {
        const label = `SCH-${g.ord.toUpperCase()}`; // ord may be "First" or "first"
        return anchor(getProvision, label, m) + badge(label);
      }
      if (g.act) return anchor(getProvision, "ACT-SCHEDULE", m);
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

/**
 * A lesson body as ordered blocks. Container directives mark the visual
 * pieces; everything else is prose.
 *
 *   ::: short            the lesson in two sentences, shown first
 *   ::: figure           a JSON figure spec (components/learn/Figure.jsx)
 *   ::: example <title>  a worked example from a business
 *
 * Malformed figure JSON throws, naming the lesson, so a broken figure fails
 * the build instead of disappearing from the page.
 */
export function lessonBlocks(markdown, where = "") {
  const blocks = [];
  let prose = [];
  let open = null;
  const flush = () => {
    const text = prose.join("\n").trim();
    if (text) blocks.push({ type: "prose", markdown: text });
    prose = [];
  };
  for (const line of String(markdown).split(/\r?\n/)) {
    const start = /^:::\s*(short|figure|example)\b\s*(.*)$/.exec(line.trim());
    if (!open && start) {
      flush();
      open = { name: start[1], arg: start[2].trim(), lines: [] };
      continue;
    }
    if (open && line.trim() === ":::") {
      const body = open.lines.join("\n").trim();
      if (open.name === "figure") {
        let spec;
        try {
          spec = JSON.parse(body);
        } catch (err) {
          throw new Error(`Figure in ${where} is not valid JSON: ${err.message}`);
        }
        blocks.push({ type: "figure", spec });
      } else {
        blocks.push({ type: open.name, title: open.arg, markdown: body });
      }
      open = null;
      continue;
    }
    (open ? open.lines : prose).push(line);
  }
  if (open) throw new Error(`Unclosed ::: ${open.name} in ${where}`);
  flush();
  return blocks;
}

/**
 * One Module record from a Markdown source. `law.getProvision` resolves cited
 * labels; `law.onDate` is the day "applies from" badges are judged on.
 */
export function buildModule(source, path, law) {
  const { getProvision, onDate } = law;
  const { data, body } = parseFrontmatter(source);
  const file = path.split("/").pop() || "";
  const slug = String(data.slug || file.replace(/^\d\d-/, "").replace(/\.md$/, "")).trim();
  const order = Number(data.order ?? /^(\d\d)-/.exec(file)?.[1] ?? 0);
  const { intro, lessons } = splitLessons(body);
  const handoff = data.handoff_url ? { label: String(data.handoff_label || "Continue"), url: String(data.handoff_url) } : null;

  const introBadged = new Set();
  const provisions = labelList(data.provisions);
  const quiz = Array.isArray(data.quiz) ? data.quiz.filter((q) => q && typeof q === "object").map(quizItem) : [];
  return {
    slug,
    order,
    title: String(data.title || "").trim(),
    summary: String(data.summary || "").trim(),
    minutes: Number(data.minutes) || Math.max(1, Math.ceil(body.split(/\s+/).filter(Boolean).length / 200)),
    provisions,
    next: nullable(data.next),
    handoff,
    quiz,
    quizCount: quiz.length,
    lessonCount: lessons.length,
    questions: topQuestions(provisions, getProvision),
    intro_html: intro ? linkCitations(md.parse(intro), { getProvision, badged: introBadged, onDate }) : "",
    intro_cites: extractCitations(intro),
    lessons: lessons.map(({ heading, id, markdown, cites }) => {
      const badged = new Set();
      const blocks = lessonBlocks(markdown, `${file} › ${heading}`).map((b) =>
        b.type === "figure" ? b : { ...b, html: linkCitations(md.parse(b.markdown), { getProvision, badged, onDate }) }
      );
      return {
        heading,
        id,
        cites,
        blocks,
        short: blocks.find((b) => b.type === "short")?.html || "",
        html: blocks.filter((b) => b.type === "prose").map((b) => b.html).join("\n")
      };
    })
  };
}

/**
 * The top question readers ask about each provision the module covers, in the
 * module's order, deduplicated. The page shows the first few.
 */
function topQuestions(labels, getProvision) {
  const seen = new Set();
  const out = [];
  for (const label of labels) {
    for (const q of getProvision(label)?.questions || []) {
      if (seen.has(q.id)) continue;
      seen.add(q.id);
      out.push({ ...q, label });
      break; // the top question per provision keeps the list spread across the module
    }
  }
  return out;
}

/** What the course index, the home page and the course track need: everything but the lessons and self-test. */
export function moduleSummary(m) {
  const { slug, order, title, summary, minutes, provisions, next, handoff, quizCount, lessonCount } = m;
  return { slug, order, title, summary, minutes, provisions, next, handoff, quizCount, lessonCount };
}
