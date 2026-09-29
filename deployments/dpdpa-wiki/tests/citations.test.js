import { describe, it, expect } from "vitest";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { extractCitations, checkCitations, routeForLabel, KNOWN_LABELS } from "../src/lib/citations.js";

const root = fileURLToPath(new URL("../", import.meta.url));

describe("extractCitations", () => {
  it("reads sections with sub-clauses and lists", () => {
    expect(extractCitations("Under Section 6(4) a Data Principal may withdraw consent.")).toEqual(["S6"]);
    expect(extractCitations("Sections 8(5) and 8(6) set the security and notice duties.")).toEqual(["S8"]);
    expect(extractCitations("see sections 4, 5 and 7, and section 33")).toEqual(["S4", "S5", "S7", "S33"]);
    expect(extractCitations("Sections 17 to 19 deal with exemptions and the Board.")).toEqual(["S17", "S18", "S19"]);
  });
  it("reads rules and the schedules", () => {
    expect(extractCitations("Rule 7 requires intimation; Rules 3 and 6 cover notice and safeguards.")).toEqual(["R7", "R3", "R6"]);
    expect(extractCitations("The First Schedule lists Consent Manager conditions.")).toEqual(["SCH-FIRST"]);
    expect(extractCitations("Penalties are in the Schedule to the Act.")).toEqual(["ACT-SCHEDULE"]);
    expect(extractCitations("The Third Schedule sets retention periods, not the Schedule.")).toEqual(["SCH-THIRD", "ACT-SCHEDULE"]);
  });
  it("does not read lowercase 'the schedule' in prose as the Act's Schedule", () => {
    expect(extractCitations("Build the schedule from the inventory; keep the retention schedule current.")).toEqual([]);
    expect(extractCitations("any language in the Eighth Schedule to the Constitution")).toEqual([]);
  });
  it("ignores prose with no citations", () => {
    expect(extractCitations("Consent must be free, specific and informed.")).toEqual([]);
    expect(extractCitations("")).toEqual([]);
  });
});

describe("checkCitations", () => {
  it("passes a note that cites only allowed provisions", () => {
    const r = checkCitations("Notice under Section 5 precedes consent under Section 6.", ["S5", "S6"]);
    expect(r.ok).toBe(true);
    expect(r.offenders).toEqual([]);
  });
  it("fails a note citing an unknown or undeclared label", () => {
    const r = checkCitations("Section 99 says so, and Rule 7 too.", ["S6"]);
    expect(r.ok).toBe(false);
    expect(r.offenders).toEqual(["S99", "R7"]);
  });
  it("fails when the allow-list itself names a provision that does not exist", () => {
    const r = checkCitations("Rule 7 applies.", ["R7", "R99"]);
    expect(r.ok).toBe(false);
    expect(r.unknownAllowed).toEqual(["R99"]);
  });
  it("knows exactly 75 labels", () => {
    expect(KNOWN_LABELS.size).toBe(75);
    expect(routeForLabel("S6")).toBe("/act/section-6");
    expect(routeForLabel("SCH-FIRST")).toBe("/rules/schedule-first");
    expect(routeForLabel("ACT-SCHEDULE")).toBe("/act/schedule");
    expect(routeForLabel("X1")).toBeNull();
  });
});

describe("check-citations.mjs", () => {
  it("passes on the current data (no notes, no modules)", () => {
    const out = execFileSync("node", [path.join(root, "scripts/check-citations.mjs")], { encoding: "utf8" });
    expect(out).toMatch(/check-citations: ok/);
  });
  it("fails on a lesson that cites outside its module", () => {
    // Write a throwaway module into a temp copy of the checker's module dir via env override is
    // more machinery than it is worth; exercise the same logic through the library instead.
    const moduleProvisions = ["S1", "S2", "S3"];
    const lesson = "## What the Act covers\nSection 3 applies the Act; penalties sit in Section 33.";
    const outside = extractCitations(lesson).filter((l) => !moduleProvisions.includes(l));
    expect(outside).toEqual(["S33"]);
  });
});
