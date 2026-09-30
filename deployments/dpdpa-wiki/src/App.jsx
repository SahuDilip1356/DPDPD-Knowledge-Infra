import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";
import "./styles/design-tokens.css";
import "./styles/global.css";
import "./styles/components.css";

// Public, prerendered screens: imported eagerly so the prerender renders them.
import Home from "./components/screens/Home";
import GuideIndex from "./components/screens/GuideIndex";
import Guide from "./components/screens/Guide";
import Provision from "./components/screens/Provision";
import ProvisionIndex from "./components/screens/ProvisionIndex";
import GlossaryEntry, { GlossaryIndex } from "./components/screens/Glossary";
import NotFound from "./components/screens/NotFound";
import LearnIndex from "./components/screens/LearnIndex";
import Module from "./components/screens/Module";
import Quiz from "./components/screens/Quiz";
import DecisionAid from "./components/screens/DecisionAid";

// The founder's workspace is a separate bundle, loaded only under /workspace.
const Workspace = lazy(() => import("./Workspace"));

function LegacyChange() {
  const { id } = useParams();
  return <Navigate to={`/workspace/changes/${id}`} replace />;
}

/**
 * `Router` is injectable so the prerender step can pass StaticRouter. In the
 * browser it stays BrowserRouter and nothing about the app changes.
 */
export default function App({ Router = BrowserRouter, routerProps = {} }) {
  return (
    <Router {...routerProps}>
      <Routes>
        {/* Public, indexable */}
        <Route path="/" element={<Home />} />
        <Route path="/guide" element={<GuideIndex />} />
        <Route path="/guide/:slug" element={<Guide />} />
        <Route path="/act" element={<ProvisionIndex doc="act" />} />
        <Route path="/act/:slug" element={<Provision />} />
        <Route path="/rules" element={<ProvisionIndex doc="rules" />} />
        <Route path="/rules/:slug" element={<Provision />} />
        <Route path="/glossary" element={<GlossaryIndex />} />
        <Route path="/glossary/:slug" element={<GlossaryEntry />} />
        <Route path="/learn" element={<LearnIndex />} />
        <Route path="/learn/:slug" element={<Module />} />
        <Route path="/learn/:slug/quiz" element={<Quiz />} />
        <Route path="/tools/:slug" element={<DecisionAid />} />

        {/* Workspace — reached by URL only, never from public navigation,
            served with noindex (spec AC9, AC14). */}
        <Route
          path="/workspace/*"
          element={
            <Suspense fallback={<p style={{ padding: 40 }}>Loading the workspace…</p>}>
              <Workspace />
            </Suspense>
          }
        />

        {/* Old workspace paths keep working for anyone who bookmarked them. */}
        {["today", "course", "infographic", "changes", "knowledge", "actions", "factory", "ask", "admin"].map((p) => (
          <Route key={p} path={`/${p}`} element={<Navigate to={`/workspace/${p}`} replace />} />
        ))}
        <Route path="/changes/:id" element={<LegacyChange />} />
        <Route path="/bible" element={<Navigate to="/act" replace />} />

        {/* A real not-found page. The host serves dist/404.html with status 404
            for unknown paths; this route covers client-side navigation and the
            prerender of that file. */}
        <Route path="/404" element={<NotFound />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}
