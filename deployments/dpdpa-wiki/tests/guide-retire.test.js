import { describe, it, expect } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { readPage, ROOT, DIST } from "./helpers/dist.js";

describe("MSME guide retired (T19 branch A, AC12)", () => {
  it("301s to the first module and is gone from the sitemap and nav", () => {
    const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, "vercel.json"), "utf8"));
    const r = cfg.redirects.find((x) => x.source === "/guide/dpdp-act-explained-indian-msmes");
    expect(r?.destination).toBe("/learn/what-is-dpdpa");
    expect(r?.permanent).toBe(true);
    expect(cfg.redirects.find((x) => x.source === "/guide")?.destination).toBe("/learn");
    const xml = fs.readFileSync(path.join(DIST, "sitemap.xml"), "utf8");
    expect(xml).not.toContain("/guide");
    expect(fs.existsSync(path.join(DIST, "guide"))).toBe(false);
    const home = readPage("/");
    expect(home).not.toMatch(/href="\/guide(\/|")/);
  });
});
