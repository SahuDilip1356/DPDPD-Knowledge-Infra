/**
 * The only writer of src/data/law/*.json.
 *
 * Copies the verified law from the competitive-intelligence ground truth into
 * the wiki as data. Provision text is never edited here or anywhere in the
 * wiki: if the gazette text is wrong, fix the ground-truth builder and re-run.
 *
 *   staging/competitive_intel/ground_truth/act_sections.json     44 sections + Schedule
 *   staging/competitive_intel/ground_truth/rules_sections.json   23 rules + 7 schedules
 *   staging/competitive_intel/questions/question_graph.jsonl     canonical questions
 *        │
 *        ▼
 *   src/data/law/provisions.json   75 Provision records (spec: Contracts)
 *   src/data/law/glossary.json     defined terms from Section 2 and Rule 2
 *
 * Fails loudly when anything is missing or malformed, because a silent gap
 * here becomes a wrong page.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const wiki = path.resolve(here, "..");
const repo = path.resolve(wiki, "..", "..");
const truth = path.join(repo, "staging", "competitive_intel", "ground_truth");
const graphPath = path.join(repo, "staging", "competitive_intel", "questions", "question_graph.jsonl");
const outDir = path.join(wiki, "src", "data", "law");

const fail = (msg) => { console.error(`sync-law: ${msg}`); process.exit(1); };
const read = (p) => {
  if (!fs.existsSync(p)) fail(`missing ${p}`);
  return JSON.parse(fs.readFileSync(p, "utf8"));
};

const act = read(path.join(truth, "act_sections.json"));
const rules = read(path.join(truth, "rules_sections.json"));

// ── Which module teaches each provision (spec: module slugs, plan: T12/T23–T26) ──
const MODULE = {};
const assign = (slug, labels) => labels.forEach((l) => { MODULE[l] = slug; });
assign("what-is-dpdpa", ["S1", "S2", "S3", "S40", "S41", "S42", "S43", "S44", "R1", "R2"]);
assign("core-rules", ["S4", "S5", "S6", "S7", "S8", "R3", "R6", "R7", "R8", "SCH-THIRD"]);
assign("peoples-rights", ["S9", "S11", "S12", "S13", "S14", "S15", "R9", "R10", "R11", "R12", "R14", "SCH-FOURTH"]);
assign("special-cases", ["S10", "S16", "S17", "R4", "R5", "R13", "R15", "R16", "SCH-FIRST", "SCH-SECOND"]);
assign("enforcement", [
  ...Array.from({ length: 22 }, (_, i) => `S${18 + i}`), "ACT-SCHEDULE",
  "R17", "R18", "R19", "R20", "R21", "R22", "R23", "SCH-FIFTH", "SCH-SIXTH", "SCH-SEVENTH"
]);

// ── Commencement ──
// Rules: from the notified Rule 1, carried in the ground truth as
// {"in_force_from_YYYY-MM-DD": [rule numbers]}.
const ruleInForce = {};
for (const [k, nums] of Object.entries(rules.commencement)) {
  const date = k.replace("in_force_from_", "");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) fail(`bad commencement key ${k}`);
  nums.forEach((n) => { ruleInForce[n] = date; });
}
// A Schedule to the Rules applies from the date of the rule that invokes it.
const SCHEDULE_RULE = { First: 4, Second: 5, Third: 8, Fourth: 12, Fifth: 18, Sixth: 21, Seventh: 23 };
// The Act's own commencement is by separate S.O. notification(s) that are not
// yet part of the verified ground truth, so Act provisions carry null here and
// the page shows no "applies from" date rather than a guessed one.
const ACT_IN_FORCE = null;

const actSource = {
  document: act.document,
  notification: "Act No. 22 of 2023, Gazette of India Extraordinary, 11 August 2023",
  sha256: act.pdf_sha256,
  url: act.source_url
};
const rulesSource = {
  document: rules.document,
  notification: rules.notification,
  corrigendum: rules.corrigendum,
  sha256: rules.rules_pdf_sha256,
  url: rules.rules_pdf_url
};

const provisions = [];
const push = (rec) => {
  for (const k of ["label", "urn", "title", "text", "source"]) if (!rec[k]) fail(`${rec.label || "?"} lacks ${k}`);
  if (!(rec.label in MODULE)) fail(`${rec.label} has no module`);
  provisions.push({ ...rec, note: null, note_cites: [], questions: [], module: MODULE[rec.label] });
};

// Act sections 1..44
const sections = Object.values(act.sections).sort((a, b) => a.section - b.section);
if (sections.length !== 44) fail(`expected 44 sections, got ${sections.length}`);
sections.forEach((s, i) => {
  if (s.section !== i + 1) fail(`section numbering gap at ${s.section}`);
  push({
    label: `S${s.section}`, kind: "section", number: s.section,
    urn: `urn:ki:in:dpdp:act:2023:sec:${s.section}`,
    title: s.title, text: s.text.trim(), source: actSource, in_force_from: ACT_IN_FORCE
  });
});

// The Act's Schedule (penalties)
if (!act.schedule?.rows || act.schedule.rows.length !== 7) fail("Act Schedule must have 7 rows");
push({
  label: "ACT-SCHEDULE", kind: "act-schedule", number: null,
  urn: "urn:ki:in:dpdp:act:2023:schedule",
  title: "The Schedule — Penalties (see section 33)", text: act.schedule.text.trim(),
  rows: act.schedule.rows, source: actSource, in_force_from: ACT_IN_FORCE
});

// Rules 1..23
const ruleList = Object.values(rules.rules).sort((a, b) => a.rule - b.rule);
if (ruleList.length !== 23) fail(`expected 23 rules, got ${ruleList.length}`);
ruleList.forEach((r, i) => {
  if (r.rule !== i + 1) fail(`rule numbering gap at ${r.rule}`);
  if (!ruleInForce[r.rule]) fail(`rule ${r.rule} has no commencement date`);
  push({
    label: `R${r.rule}`, kind: "rule", number: r.rule,
    urn: `urn:ki:in:dpdp:rules:2025:rule:${r.rule}`,
    title: r.title, text: r.text.trim(), source: rulesSource, in_force_from: ruleInForce[r.rule]
  });
});

// Schedules to the Rules
const ORDER = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh"];
for (const name of ORDER) {
  const s = rules.schedules[name];
  if (!s) fail(`missing ${name} Schedule`);
  const heading = new RegExp(`^${name.toUpperCase()} SCHEDULE\\s*\\[See ([^\\]]+)\\]`).exec(s.text);
  push({
    label: `SCH-${name.toUpperCase()}`, kind: "rules-schedule", number: null,
    urn: `urn:ki:in:dpdp:rules:2025:schedule:${name.toLowerCase()}`,
    title: `${name} Schedule${heading ? ` (see ${heading[1]})` : ""}`,
    text: s.text.trim(), source: rulesSource, in_force_from: ruleInForce[SCHEDULE_RULE[name]]
  });
}

if (provisions.length !== 75) fail(`expected 75 provisions, got ${provisions.length}`);
const known = new Set(provisions.map((p) => p.label));

// ── Canonical questions → provisions (top 8 per provision by demand) ──
if (fs.existsSync(graphPath)) {
  const byLabel = new Map();
  for (const line of fs.readFileSync(graphPath, "utf8").split("\n")) {
    if (!line.trim()) continue;
    const q = JSON.parse(line);
    for (const raw of q.provisions || []) {
      const label = String(typeof raw === "string" ? raw : raw.label || "").replace(/\(.*$/, "").trim();
      if (!known.has(label)) continue;
      if (!byLabel.has(label)) byLabel.set(label, []);
      byLabel.get(label).push({ id: q.question_id, question: q.question, demand: q.demand_sites || 0 });
    }
  }
  for (const p of provisions) {
    const qs = (byLabel.get(p.label) || []).sort((a, b) => b.demand - a.demand || a.id.localeCompare(b.id));
    const seen = new Set();
    p.questions = qs.filter((q) => !seen.has(q.id) && seen.add(q.id)).slice(0, 8).map(({ id, question }) => ({ id, question }));
  }
} else {
  console.warn("sync-law: question graph not found; provisions carry no questions");
}

// ── Glossary: defined terms in Section 2 and Rule 2 ──
// Pattern in the gazette text: (a) “Appellate Tribunal” means …; the clause
// runs to the next lettered marker or the end of the provision.
const glossary = [];
const slugify = (t) => t.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
for (const label of ["S2", "R2"]) {
  const p = provisions.find((x) => x.label === label);
  const text = p.text;
  // "means" or "includes", possibly after a qualifier such as "in relation to personal data,".
  const re = /\(([a-z]{1,2})\)\s+[“"]([^”"]+)[”"][^“”;]{0,80}?\b(?:means|includes)\b/g;
  const hits = [...text.matchAll(re)];
  hits.forEach((m, i) => {
    const start = m.index;
    const end = i + 1 < hits.length ? hits[i + 1].index : text.length;
    const definition = text.slice(start, end).trim().replace(/;\s*$/, ";");
    glossary.push({ term: m[2].trim(), slug: slugify(m[2]), clause: `${label === "S2" ? "Section 2" : "Rule 2"}(${m[1]})`, definition, provision: label });
  });
}
// Same slug can appear in both provisions (e.g. "Act" in Rule 2); keep both, disambiguated.
const slugCount = new Map();
for (const g of glossary) {
  const n = (slugCount.get(g.slug) || 0) + 1;
  slugCount.set(g.slug, n);
  if (n > 1) g.slug = `${g.slug}-${g.provision.toLowerCase()}`;
}
for (const g of glossary) {
  const p = provisions.find((x) => x.label === g.provision);
  if (!p.text.includes(g.definition)) fail(`glossary ${g.term} is not verbatim`);
}

fs.mkdirSync(outDir, { recursive: true });
const meta = {
  generated_at: new Date().toISOString().slice(0, 10),
  act: actSource, rules: rulesSource,
  note: "Act commencement dates are not in the verified ground truth; Act provisions carry in_force_from: null."
};
fs.writeFileSync(path.join(outDir, "provisions.json"), JSON.stringify({ meta, provisions }, null, 1) + "\n");
fs.writeFileSync(path.join(outDir, "glossary.json"), JSON.stringify(glossary, null, 1) + "\n");

const withQ = provisions.filter((p) => p.questions.length).length;
console.log(`sync-law: ${provisions.length} provisions (${withQ} with questions), ${glossary.length} glossary terms → ${path.relative(wiki, outDir)}/`);
