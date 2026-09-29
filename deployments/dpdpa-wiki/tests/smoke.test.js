import { describe, it, expect } from "vitest";
import { readPage, title, builtRoutes } from "./helpers/dist.js";

describe("build output", () => {
  it("prerendered the home page with a title", () => {
    const html = readPage("/");
    expect(html, "run `npm run build` first").toBeTruthy();
    expect(title(html)).toMatch(/DPDPA Wiki/);
  });

  it("wrote at least one route", () => {
    expect(builtRoutes().length).toBeGreaterThan(0);
  });
});
