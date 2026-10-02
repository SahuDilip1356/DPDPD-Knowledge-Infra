import React from "react";
import { renderToString } from "react-dom/server";
import { StaticRouter } from "react-router";
import App, { preloadScreens, routeChunks } from "./App";

export { publicRoutes, headFor } from "./lib/seo";

// Every screen is a lazy chunk in the browser; here they are all loaded once,
// up front, so render() stays synchronous. Law and course records are
// complete on the server (scripts/vite-content.mjs).
await preloadScreens();

/**
 * Renders a route to HTML at build time.
 *
 * The app is safe to render this way because every browser API it touches sits
 * inside an effect or an event handler, neither of which runs here.
 */
export function render(url) {
  return renderToString(
    <StaticRouter location={url}>
      <App Router={React.Fragment} routerProps={{}} />
    </StaticRouter>
  );
}

/** Source ids of the chunks a route renders from, as Vite's client manifest names them. */
export function chunksFor(url) {
  return routeChunks(url).map((c) => c.id);
}
