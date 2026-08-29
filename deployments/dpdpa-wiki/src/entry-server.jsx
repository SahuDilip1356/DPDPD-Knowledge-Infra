import React from "react";
import { renderToString } from "react-dom/server";
import { StaticRouter } from "react-router";
import App from "./App";

export { publicRoutes, headFor } from "./lib/seo";

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
