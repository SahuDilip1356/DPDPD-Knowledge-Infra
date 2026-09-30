import fs from "node:fs";
import path from "node:path";
import { describe, it, expect } from "vitest";
import { ROOT } from "./helpers/dist.js";

// mockData.js is plain ESM with no browser globals, so it loads directly.
const mod = await import("../src/data/mockData.js");
const text = fs.readFileSync(path.join(ROOT, "src/data/mockData.js"), "utf8");

const DELETED_TITLES = [
  "WP(C) 177/2026",
  "Bombay HC Judgement",
  "Constitution Bench",
  "Consent Notice Rules 2024",
  "Rule 5: Verifiable Consent",
  "Rule 14: Consent Manager",
  "AZB & Partners",
  "Trilegal",
  "Shardul Amarchand"
];

const DRAFT_URN_FRAGMENTS = [":rules:2025:r23", ":rules:2025:r5", "consent-manager-net-worth"];

const records = Object.entries(mod)
  .filter(([, v]) => Array.isArray(v))
  .flatMap(([name, arr]) => arr.filter((x) => x && typeof x === "object").map((x) => ({ name, x })));

describe("sample data is sourced", () => {
  it("has records to check", () => {
    expect(records.length).toBeGreaterThan(0);
  });

  it("every record with a title or urn carries an https source_url", () => {
    const legal = records.filter(({ x }) => "title" in x || "urn" in x);
    expect(legal.length).toBeGreaterThan(0);
    const bad = legal
      .filter(({ x }) => !/^https:\/\//.test(x.source_url ?? ""))
      .map(({ name, x }) => `${name}:${x.id ?? x.urn ?? x.title}`);
    expect(bad).toEqual([]);
  });

  it("only cites the MeitY publications of the Act and the Rules", () => {
    const urls = new Set(records.map(({ x }) => x.source_url).filter(Boolean));
    for (const u of urls) expect(u).toMatch(/^https:\/\/www\.meity\.gov\.in\//);
  });
});

describe("fabricated items are gone", () => {
  for (const title of DELETED_TITLES) {
    it(`no longer mentions "${title}"`, () => {
      expect(text).not.toContain(title);
    });
  }

  it("no urn uses the draft (January 2025) rule numbering", () => {
    const urns = records.map(({ x }) => x.urn).filter(Boolean);
    for (const urn of urns) {
      for (const frag of DRAFT_URN_FRAGMENTS) expect(urn).not.toContain(frag);
    }
  });

  it("nothing still points at a deleted record", () => {
    const koUrns = new Set(mod.KNOWLEDGE_OBJECTS.map((k) => k.urn));
    const eventIds = new Set(mod.REGULATORY_EVENTS.map((e) => e.id));
    for (const ko of mod.KNOWLEDGE_OBJECTS) for (const r of ko.relations) expect(koUrns.has(r.target_urn), r.target_urn).toBe(true);
    for (const e of mod.REGULATORY_EVENTS) for (const u of e.affected_ko_urns) expect(koUrns.has(u), `${e.id} -> ${u}`).toBe(true);
    for (const a of mod.ACTION_ITEMS) {
      expect(koUrns.has(a.ko_urn), `${a.id} -> ${a.ko_urn}`).toBe(true);
      expect(eventIds.has(a.triggering_event_id), `${a.id} -> ${a.triggering_event_id}`).toBe(true);
    }
    for (const t of mod.TIMELINE_EVENTS) expect(koUrns.has(t.ko_urn), `${t.commit_hash} -> ${t.ko_urn}`).toBe(true);
  });

  it("helpers still work with the shorter arrays", () => {
    expect(mod.getOpinionsForKO("urn:ki:in:dpdp:act:dpdpa-2023")).toEqual([]);
    expect(mod.getKOByUrn("urn:ki:in:dpdp:act:dpdpa-2023")?.title).toBe("Digital Personal Data Protection Act 2023");
    expect(mod.getRelatedKOs("urn:ki:in:dpdp:rule:dpdp-rules-2025").length).toBeGreaterThan(0);
  });
});
