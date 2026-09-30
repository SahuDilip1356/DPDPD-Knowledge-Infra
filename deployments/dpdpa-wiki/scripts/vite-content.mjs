/**
 * Serves the law corpus and the course as modules sized for the page that
 * needs them.
 *
 *   virtual:law              every provision's label, title, dates and route;
 *                            in the browser, a loader per provision for the rest
 *   virtual:law/<label>      one provision's text, source, questions and notes
 *   virtual:course           every module's summary; in the browser, a loader
 *                            per module for the rest
 *   virtual:course/<slug>    one module's finished record: lessons as HTML,
 *                            figures, self-test
 *
 * Server builds and tests get complete records from virtual:law and
 * virtual:course, so the prerender and the tests read everything
 * synchronously. The browser gets the light lists up front and one chunk per
 * provision or module, fetched for the page that shows it: a provision page
 * does not carry the other 74, and no browser parses Markdown.
 *
 * Module records are built here, in Node, by src/lib/module-build.js — the
 * code that used to run in the browser — so `marked` and the raw Markdown stay
 * out of the client bundle. The sources stay the only truth: provisions.json
 * as sync-law.mjs writes it, and src/content/modules/*.md.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = fileURLToPath(new URL("../", import.meta.url));
const LAW_FILE = path.join(ROOT, "src/data/law/provisions.json");
const MODULES_DIR = path.join(ROOT, "src/content/modules");
const MODULE_BUILD = pathToFileURL(path.join(ROOT, "src/lib/module-build.js")).href;

/** Fields of a provision that only its own page shows. */
const BODY_FIELDS = ["text", "source", "questions", "note", "note_cites", "rows"];

/**
 * The day the build judges commencement on: "applies from" badges in lessons,
 * and the first render of anything dated (see src/lib/useToday.js).
 */
export const BUILD_DAY = new Date().toISOString().slice(0, 10);

const IDS = /^virtual:(law|course)(?:\/(.+))?$/;
const js = (value) => JSON.stringify(value);

export default function content() {
  let law = null;
  let course = null;

  const readLaw = () => (law ??= JSON.parse(fs.readFileSync(LAW_FILE, "utf8")));

  async function readCourse() {
    if (course) return course;
    const { buildModule, moduleSummary } = await import(MODULE_BUILD);
    const byLabel = Object.fromEntries(readLaw().provisions.map((p) => [p.label, p]));
    const lawApi = { getProvision: (l) => byLabel[l] || null, onDate: new Date(`${BUILD_DAY}T00:00:00Z`) };
    const records = fs
      .readdirSync(MODULES_DIR)
      .filter((f) => /^\d\d-.+\.md$/.test(f))
      .map((f) => buildModule(fs.readFileSync(path.join(MODULES_DIR, f), "utf8"), f, lawApi))
      .sort((a, b) => a.order - b.order);
    course = { records, summaries: records.map(moduleSummary) };
    return course;
  }

  return {
    name: "dpdpa-content",

    resolveId(id) {
      return IDS.test(id) ? `\0${id}` : undefined;
    },

    async load(id, options) {
      const match = id.startsWith("\0") && IDS.exec(id.slice(1));
      if (!match) return undefined;
      const [, kind, key] = match;
      const server = Boolean(options?.ssr) || this.environment?.config?.consumer === "server";
      this.addWatchFile(LAW_FILE);

      if (kind === "law") {
        const { meta, provisions } = readLaw();
        if (key) {
          const p = provisions.find((x) => x.label === key);
          if (!p) this.error(`virtual:law/${key} names no provision`);
          return `export default ${js(Object.fromEntries(BODY_FIELDS.filter((f) => f in p).map((f) => [f, p[f]])))};`;
        }
        if (server) return `export const meta = ${js(meta)};\nexport const provisions = ${js(provisions)};\nexport const bodies = null;\n`;
        const light = provisions.map((p) => Object.fromEntries(Object.entries(p).filter(([f]) => !BODY_FIELDS.includes(f))));
        const loaders = provisions.map((p) => `  ${js(p.label)}: () => import(${js(`virtual:law/${p.label}`)})`);
        return `export const meta = ${js(meta)};\nexport const provisions = ${js(light)};\nexport const bodies = {\n${loaders.join(",\n")}\n};\n`;
      }

      for (const f of fs.readdirSync(MODULES_DIR)) this.addWatchFile(path.join(MODULES_DIR, f));
      const { records, summaries } = await readCourse();
      if (key) {
        const m = records.find((r) => r.slug === key);
        if (!m) this.error(`virtual:course/${key} names no module`);
        return `export default ${js(m)};`;
      }
      if (server) return `export const modules = ${js(records)};\nexport const loaders = null;\n`;
      const loaders = records.map((m) => `  ${js(m.slug)}: () => import(${js(`virtual:course/${m.slug}`)})`);
      return `export const modules = ${js(summaries)};\nexport const loaders = {\n${loaders.join(",\n")}\n};\n`;
    },

    watchChange(file) {
      if (file === LAW_FILE) law = null;
      if (file === LAW_FILE || file.startsWith(MODULES_DIR)) course = null;
    }
  };
}
