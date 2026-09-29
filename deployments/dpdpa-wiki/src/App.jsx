import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";
import "./styles/design-tokens.css";
import "./styles/global.css";
import "./styles/components.css";

import AppShell from "./components/AppShell";
import SearchOverlay from "./components/ui/SearchOverlay";
import AuthModal from "./components/ui/AuthModal";
import { supabase } from "./data/supabaseClient";

// Screens
import Home from "./components/screens/Home";
import GuideIndex from "./components/screens/GuideIndex";
import Guide from "./components/screens/Guide";
import Provision from "./components/screens/Provision";
import ProvisionIndex from "./components/screens/ProvisionIndex";
import GlossaryEntry, { GlossaryIndex } from "./components/screens/Glossary";
import CommandCenter from "./components/screens/CommandCenter";
import InfographicDashboard from "./components/screens/InfographicDashboard";
import ChangesFeed from "./components/screens/ChangesFeed";
import ChangeWorkspace from "./components/screens/ChangeWorkspace";
import KnowledgeExplorer from "./components/screens/KnowledgeExplorer";
import DecisionsActions from "./components/screens/DecisionsActions";
import FactoryBoard from "./components/screens/FactoryBoard";
import AskIntelligence from "./components/screens/AskIntelligence";
import AdminAudit from "./components/screens/AdminAudit";
import Bible from "./components/screens/Bible";
import NotFound from "./components/screens/NotFound";
import LearnIndex from "./components/screens/LearnIndex";
import Module from "./components/screens/Module";
import Quiz from "./components/screens/Quiz";
import DecisionAid from "./components/screens/DecisionAid";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function LegacyChange() {
  const { id } = useParams();
  return <Navigate to={`/workspace/changes/${id}`} replace />;
}

function CourseRedirect() {
  React.useEffect(() => {
    window.location.replace(import.meta.env.VITE_SHIKSHA_URL || "https://dpdpa.shiksha");
  }, []);
  return (
    <div style={{ padding: "40px", textAlign: "center", color: "var(--brand-navy)" }}>
      <h2>Redirecting to DPDPA Certification...</h2>
      <p className="text-muted">If you are not redirected automatically, <a href={import.meta.env.VITE_SHIKSHA_URL || "https://dpdpa.shiksha"}>click here</a>.</p>
    </div>
  );
}

/**
 * `Router` is injectable so the prerender step can pass StaticRouter. In the
 * browser it stays BrowserRouter and nothing about the app changes.
 */
export default function App({ Router = BrowserRouter, routerProps = {} }) {
  const [apiOnline, setApiOnline] = useState(false);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [searchOpen, setSearchOpen] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [user, setUser] = useState(null);

  // Check API health status
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`, { method: "GET" });
        if (response.ok) {
          setApiOnline(true);
        } else {
          setApiOnline(false);
        }
      } catch (err) {
        setApiOnline(false);
      } finally {
        setLoadingHealth(false);
      }
    };
    checkHealth();
  }, []);

  // Supabase Auth Listener
  useEffect(() => {
    if (!supabase) return;
    
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setUser(session.user);
      }
    });

    // Listen for state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleSignOut = async () => {
    if (supabase) {
      await supabase.auth.signOut();
    }
    setUser(null);
  };

  // Listen for Cmd+K to trigger global search
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  /* Working surfaces share the sidebar shell. The public homepage does not —
     it carries its own header and footer, because a visitor arriving from a
     search result needs a way in, not a way around. */
  const workspace = (element) => (
    <AppShell
      apiOnline={apiOnline}
      loadingHealth={loadingHealth}
      onSearchClick={() => setSearchOpen(true)}
      user={user}
      onSignInClick={() => setAuthModalOpen(true)}
      onSignOutClick={handleSignOut}
    >
      {element}
    </AppShell>
  );

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

        {/* Workspace — the founder's working surface. Reached by URL only,
            never from public navigation, and served with noindex (spec AC9, AC14). */}
        <Route path="/workspace" element={<Navigate to="/workspace/today" replace />} />
        <Route path="/workspace/today" element={workspace(<CommandCenter />)} />
        <Route path="/workspace/course" element={<CourseRedirect />} />
        <Route path="/workspace/infographic" element={workspace(<InfographicDashboard />)} />
        <Route path="/workspace/changes" element={workspace(<ChangesFeed />)} />
        <Route path="/workspace/changes/:id" element={workspace(<ChangeWorkspace />)} />
        <Route path="/workspace/knowledge" element={workspace(<KnowledgeExplorer />)} />
        <Route path="/workspace/actions" element={workspace(<DecisionsActions user={user} />)} />
        <Route path="/workspace/factory" element={workspace(
          <FactoryBoard user={user} onSignInClick={() => setAuthModalOpen(true)} />
        )} />
        <Route path="/workspace/ask" element={workspace(
          <AskIntelligence apiOnline={apiOnline} apiBaseUrl={API_BASE_URL} />
        )} />
        <Route path="/workspace/bible" element={workspace(<Bible />)} />
        <Route path="/workspace/admin" element={workspace(<AdminAudit />)} />

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

      <SearchOverlay isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={(u) => setUser(u)}
      />
    </Router>
  );
}
