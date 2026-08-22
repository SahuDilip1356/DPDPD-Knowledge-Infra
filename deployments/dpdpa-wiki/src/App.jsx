import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./styles/design-tokens.css";
import "./styles/global.css";
import "./styles/components.css";

import AppShell from "./components/AppShell";
import SearchOverlay from "./components/ui/SearchOverlay";
import AuthModal from "./components/ui/AuthModal";
import { supabase } from "./data/supabaseClient";

// Screens
import Home from "./components/screens/Home";
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

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

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

export default function App() {
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
    <BrowserRouter>
      <Routes>
        {/* Public, indexable */}
        <Route path="/" element={<Home />} />

        {/* Workspace */}
        <Route path="/today" element={workspace(<CommandCenter />)} />
        <Route path="/course" element={<CourseRedirect />} />
        <Route path="/infographic" element={workspace(<InfographicDashboard />)} />
        <Route path="/changes" element={workspace(<ChangesFeed />)} />
        <Route path="/changes/:id" element={workspace(<ChangeWorkspace />)} />
        <Route path="/knowledge" element={workspace(<KnowledgeExplorer />)} />
        <Route path="/actions" element={workspace(<DecisionsActions user={user} />)} />
        <Route path="/factory" element={workspace(
          <FactoryBoard user={user} onSignInClick={() => setAuthModalOpen(true)} />
        )} />
        <Route path="/ask" element={workspace(
          <AskIntelligence apiOnline={apiOnline} apiBaseUrl={API_BASE_URL} />
        )} />
        <Route path="/bible" element={workspace(<Bible />)} />
        <Route path="/admin" element={workspace(<AdminAudit />)} />

        {/* Unknown paths land on the homepage rather than the workspace, so a
            stale inbound link still gives a stranger somewhere to start. */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      <SearchOverlay isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={(u) => setUser(u)}
      />
    </BrowserRouter>
  );
}
