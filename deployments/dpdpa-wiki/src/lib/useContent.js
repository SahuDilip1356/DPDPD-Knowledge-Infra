import { use } from "react";
import { isLoaded, loadProvision } from "./law";
import { getModule, isModuleLoaded, loadModule } from "./modules";

/*
 * A page's own data, read during render. In the browser a provision's text or
 * a module's lessons are chunks of their own: when they are already loaded
 * (main.jsx loads the first page's before hydrating) these return at once;
 * otherwise the render suspends until they arrive.
 */

/** The provision record with its text, or null. */
export function useProvision(p) {
  return !p || isLoaded(p) ? p : use(loadProvision(p.label));
}

/** The full module record for a slug, or null when the slug names no module. */
export function useModule(slug) {
  const m = getModule(slug);
  return !m || isModuleLoaded(m) ? m : use(loadModule(slug));
}
