import React, { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import AppShell from "./components/AppShell";
import SearchOverlay from "./components/ui/SearchOverlay";
import AuthModal from "./components/ui/AuthModal";
import { supabase } from "./data/supabaseClient";

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
import Acts from "./components/screens/Acts";
import Rules from "./components/screens/Rules";
import Interpretations from "./components/screens/Interpretations";
import Discussions from "./components/screens/Discussions";
import { API_BASE_URL, API_CONFIGURED, apiFetch } from "./lib/api";

const SHIKSHA_URL = import.meta.env.VITE_SHIKSHA_URL || "https://dpdpa.shiksha";

function CourseRedirect() {
  useEffect(() => { window.location.replace(SHIKSHA_URL); }, []);
  return (
    <div style={{ padding: "40px", textAlign: "center", color: "var(--brand-navy)" }}>
      <h2>Redirecting to DPDPA Certification…</h2>
      <p className="text-muted">If nothing happens, <a href={SHIKSHA_URL}>open the certification site</a>.</p>
    </div>
  );
}

/**
 * The founder's workspace, as its own bundle.
 *
 * Everything here (Supabase auth, the API health check, sample data, the
 * sidebar screens) used to load on every public page. It is now fetched only
 * when someone opens /workspace/*, which the prerender never renders and
 * search engines are told not to index.
 */
export default function Workspace() {
  const [apiOnline, setApiOnline] = useState(false);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [searchOpen, setSearchOpen] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [user, setUser] = useState(null);

  // No backend configured (as on the public preview): report offline without a request.
  useEffect(() => {
    if (!API_CONFIGURED) {
      setApiOnline(false);
      setLoadingHealth(false);
      return;
    }
    apiFetch("/health/ready", { method: "GET" })
      .then((r) => setApiOnline(r.ok))
      .catch(() => setApiOnline(false))
      .finally(() => setLoadingHealth(false));
  }, []);

  useEffect(() => {
    if (!supabase) return undefined;
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) setUser(session.user);
    });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });
    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    const onKey = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const signOut = async () => {
    if (supabase) await supabase.auth.signOut();
    setUser(null);
  };

  const shell = (element) => (
    <AppShell
      apiOnline={apiOnline}
      loadingHealth={loadingHealth}
      onSearchClick={() => setSearchOpen(true)}
      user={user}
      onSignInClick={() => setAuthModalOpen(true)}
      onSignOutClick={signOut}
    >
      {element}
    </AppShell>
  );

  return (
    <>
      <Routes>
        <Route index element={<Navigate to="today" replace />} />
        <Route path="today" element={shell(<CommandCenter />)} />
        <Route path="course" element={<CourseRedirect />} />
        <Route path="infographic" element={shell(<InfographicDashboard />)} />
        <Route path="changes" element={shell(<ChangesFeed />)} />
        <Route path="changes/:id" element={shell(<ChangeWorkspace />)} />
        <Route path="knowledge" element={shell(<KnowledgeExplorer />)} />
        <Route path="actions" element={shell(<DecisionsActions user={user} />)} />
        <Route path="factory" element={shell(<FactoryBoard user={user} onSignInClick={() => setAuthModalOpen(true)} />)} />
        <Route path="ask" element={shell(<AskIntelligence apiOnline={apiOnline} apiBaseUrl={API_BASE_URL} />)} />
        <Route path="bible" element={shell(<Bible />)} />
        <Route path="acts" element={shell(<Acts />)} />
        <Route path="rules" element={shell(<Rules />)} />
        <Route path="interpretations" element={shell(<Interpretations />)} />
        <Route path="discussions" element={shell(<Discussions />)} />
        <Route path="admin" element={shell(<AdminAudit />)} />
        <Route path="*" element={<Navigate to="today" replace />} />
      </Routes>
      <SearchOverlay isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
      <AuthModal isOpen={authModalOpen} onClose={() => setAuthModalOpen(false)} onAuthSuccess={(u) => setUser(u)} />
    </>
  );
}
