import React, { Suspense, lazy, use } from "react";
import { BrowserRouter, Navigate, matchRoutes, useParams, useRoutes } from "react-router-dom";
import { getByRoute, loadProvision } from "./lib/law";
import { getModule, loadModule } from "./lib/modules";
import "./styles/design-tokens.css";
import "./styles/global.css";
import "./styles/components.css";

/* Public screens. Each is a chunk of its own, so a page loads its screen and
   not the others. */
const SCREENS = import.meta.glob(
  "./components/screens/{Home,GuideIndex,Guide,Provision,ProvisionIndex,Glossary,NotFound,LearnIndex,Module,Quiz,DecisionAid}.jsx"
);
const ALL_SCREENS = [];

/**
 * A lazily loaded screen that renders synchronously once `preload()` has
 * resolved. main.jsx preloads the first page's screen before hydrating, so
 * hydration never suspends and the prerendered HTML is adopted as it stands;
 * a screen reached later by navigation suspends until its chunk arrives.
 *
 * `chunk.id` is the source path, which is how Vite's manifest names the chunk;
 * scripts/prerender.mjs uses it to preload each page's own chunks.
 */
function screen(name, exportName = "default") {
  const id = `src/components/screens/${name}.jsx`;
  const load = SCREENS[`./components/screens/${name}.jsx`];
  let mod = null;
  let promise = null;
  const preload = () => (promise ??= load().then((m) => (mod = m)));
  function Screen(props) {
    const Component = (mod ?? use(preload()))[exportName];
    return <Component {...props} />;
  }
  Screen.displayName = exportName === "default" ? name : exportName;
  Screen.chunk = { id, preload };
  ALL_SCREENS.push(Screen);
  return Screen;
}

const Home = screen("Home");
const GuideIndex = screen("GuideIndex");
const Guide = screen("Guide");
const Provision = screen("Provision");
const ProvisionIndex = screen("ProvisionIndex");
const GlossaryIndex = screen("Glossary", "GlossaryIndex");
const GlossaryEntry = screen("Glossary");
const NotFound = screen("NotFound");
const LearnIndex = screen("LearnIndex");
const Module = screen("Module");
const Quiz = screen("Quiz");
const DecisionAid = screen("DecisionAid");

// The founder's workspace is a separate bundle, loaded only under /workspace.
const Workspace = lazy(() => import("./Workspace"));

function LegacyChange() {
  const { id } = useParams();
  return <Navigate to={`/workspace/changes/${id}`} replace />;
}

/* What a page needs besides its screen: one provision's text, or one module's
   lessons. Ids name the chunks as the build does (scripts/vite-content.mjs). */
const provisionData = ({ pathname }) => {
  const p = getByRoute(pathname);
  return p ? [{ id: `virtual:law/${p.label}`, preload: () => loadProvision(p.label) }] : [];
};
const moduleData = ({ params }) =>
  getModule(params.slug) ? [{ id: `virtual:course/${params.slug}`, preload: () => loadModule(params.slug) }] : [];

const page = (path, Screen, element, data) => ({
  path,
  element,
  needs: (match) => [Screen.chunk, ...(data ? data(match) : [])]
});

export const routes = [
  // Public, indexable
  page("/", Home, <Home />),
  page("/guide", GuideIndex, <GuideIndex />),
  page("/guide/:slug", Guide, <Guide />),
  page("/act", ProvisionIndex, <ProvisionIndex doc="act" />),
  page("/act/:slug", Provision, <Provision />, provisionData),
  page("/rules", ProvisionIndex, <ProvisionIndex doc="rules" />),
  page("/rules/:slug", Provision, <Provision />, provisionData),
  page("/glossary", GlossaryIndex, <GlossaryIndex />),
  page("/glossary/:slug", GlossaryEntry, <GlossaryEntry />),
  page("/learn", LearnIndex, <LearnIndex />),
  page("/learn/:slug", Module, <Module />, moduleData),
  page("/learn/:slug/quiz", Quiz, <Quiz />, moduleData),
  page("/tools/:slug", DecisionAid, <DecisionAid />),

  // Workspace — reached by URL only, never from public navigation,
  // served with noindex (spec AC9, AC14).
  {
    path: "/workspace/*",
    element: (
      <Suspense fallback={<p style={{ padding: 40 }}>Loading the workspace…</p>}>
        <Workspace />
      </Suspense>
    )
  },

  // Old workspace paths keep working for anyone who bookmarked them.
  ...["today", "course", "infographic", "changes", "knowledge", "actions", "factory", "ask", "admin"].map((p) => ({
    path: `/${p}`,
    element: <Navigate to={`/workspace/${p}`} replace />
  })),
  { path: "/changes/:id", element: <LegacyChange /> },
  { path: "/bible", element: <Navigate to="/act" replace /> },

  // A real not-found page. The host serves dist/404.html with status 404 for
  // unknown paths; these routes cover client-side navigation and the
  // prerender of that file.
  page("/404", NotFound, <NotFound />),
  page("*", NotFound, <NotFound />)
];

/** The chunks a path renders from: its screen, and its provision or module when it has one. */
export function routeChunks(pathname) {
  return (matchRoutes(routes, pathname) || []).flatMap((m) => m.route.needs?.(m) ?? []);
}

/** Loads a path's chunks, so its first render does not suspend. */
export function preloadRoute(pathname) {
  return Promise.all(routeChunks(pathname).map((c) => c.preload()));
}

/** Loads every public screen; the prerender renders them all synchronously. */
export function preloadScreens() {
  return Promise.all(ALL_SCREENS.map((s) => s.chunk.preload()));
}

function AppRoutes() {
  return useRoutes(routes);
}

/**
 * `Router` is injectable so the prerender step can pass StaticRouter. In the
 * browser it stays BrowserRouter and nothing about the app changes.
 *
 * Navigation runs in a transition, so while the next page's chunk loads the
 * current page stays on screen; the boundary's fallback is never painted.
 */
export default function App({ Router = BrowserRouter, routerProps = {} }) {
  return (
    <Router {...routerProps}>
      <Suspense fallback={null}>
        <AppRoutes />
      </Suspense>
    </Router>
  );
}
