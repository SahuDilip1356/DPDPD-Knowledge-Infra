/**
 * Build gate: no note and no lesson may cite a provision it is not allowed to.
 *
 * Runs before the client build. Exits 1 naming every offending page and label.
 *
 *   provision.note     may cite only provision.note_cites ∪ { its own label }
 *   module lesson      may cite only the module's `provisions`
 *   module quiz item   may cite only labels in its `cites`, all within `provisions`
 *
 * Modules are Markdown under src/content/modules/*.md with front-matter; lessons
 * are the `## ` sections of the body. Absent modules are fine (none authored yet).
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { extractCitations, checkCitations, KNOWN_LABELS } from "../src/lib/citations.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const problems = [];

// ── Provision notes ──
const { provisions } = JSON.parse(fs.readFileSync(path.join(root, "src/data/law/provisions.json"), "utf8"));
for (const p of provisions) {
  if (!p.note) continue;
  const { offenders, unknownAllowed } = checkCitations(p.note, [...(p.note_cites || []), p.label]);
  for (const l of offenders) problems.push(`${p.label} note cites ${l}, not in note_cites`);
  for (const l of unknownAllowed) problems.push(`${p.label} note_cites names unknown label ${l}`);
}

// ── Modules ──
const modDir = path.join(root, "src/content/modules");
const files = fs.existsSync(modDir) ? fs.readdirSync(modDir).filter((f) => /^\d\d-.*\.md$/.test(f)).sort() : [];
for (const f of files) {
  const src = fs.readFileSync(path.join(modDir, f), "utf8");
  const fm = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(src);
  if (!fm) { problems.push(`${f}: no front-matter`); continue; }
  const body = src.slice(fm[0].length);
  const provMatch = /^provisions:\s*\[([^\]]*)\]/m.exec(fm[1]);
  const listed = provMatch ? provMatch[1].split(",").map((s) => s.trim().replace(/^["']|["']$/g, "")).filter(Boolean) : [];
  if (!listed.length) {
    // block-style list
    const block = /^provisions:\s*\n((?:\s+-\s+.*\n?)+)/m.exec(fm[1]);
    if (block) listed.push(...block[1].split("\n").map((l) => l.replace(/^\s+-\s+/, "").trim().replace(/^["']|["']$/g, "")).filter(Boolean));
  }
  if (!listed.length) { problems.push(`${f}: front-matter has no provisions list`); continue; }
  for (const l of listed) if (!KNOWN_LABELS.has(l)) problems.push(`${f}: provisions names unknown label ${l}`);

  const sections = body.split(/^(?=##\s)/m);
  for (const sec of sections) {
    const heading = (/^##\s+(.+)$/m.exec(sec)?.[1] || "(intro)").trim();
    for (const l of extractCitations(sec)) {
      if (!listed.includes(l)) problems.push(`${f} › "${heading}" cites ${l}, outside the module's provisions`);
    }
  }
  // quiz items: each "cites:" line inside the front-matter quiz block
  // both "cites: [S4, R7]" and "cites: S4, R7"
  for (const m of fm[1].matchAll(/^\s+cites:\s*\[?([^\]\n]*)\]?\s*$/gm)) {
    for (const l of m[1].split(",").map((s) => s.trim().replace(/^["']|["']$/g, "")).filter(Boolean)) {
      if (!listed.includes(l)) problems.push(`${f} quiz cites ${l}, outside the module's provisions`);
    }
  }
}

if (problems.length) {
  console.error(`check-citations: ${problems.length} problem(s)`);
  for (const p of problems) console.error(`  ✗ ${p}`);
  process.exit(1);
}
const notes = provisions.filter((p) => p.note).length;
console.log(`check-citations: ok — ${notes} note(s), ${files.length} module(s) checked`);
