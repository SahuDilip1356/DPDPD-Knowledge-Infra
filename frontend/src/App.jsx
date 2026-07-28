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
import CommandCenter from "./components/screens/CommandCenter";
import ChangesFeed from "./components/screens/ChangesFeed";
import ChangeWorkspace from "./components/screens/ChangeWorkspace";
import KnowledgeExplorer from "./components/screens/KnowledgeExplorer";
import DecisionsActions from "./components/screens/DecisionsActions";
import FactoryBoard from "./components/screens/FactoryBoard";
import AskIntelligence from "./components/screens/AskIntelligence";
import AdminAudit from "./components/screens/AdminAudit";

const API_BASE_URL = "http://localhost:8000";

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
        setSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <BrowserRouter>
      <AppShell 
        apiOnline={apiOnline} 
        loadingHealth={loadingHealth} 
        onSearchClick={() => setSearchOpen(true)}
        user={user}
        onSignInClick={() => setAuthModalOpen(true)}
        onSignOutClick={handleSignOut}
      >
        <Routes>
          <Route path="/" element={<Navigate to="/today" replace />} />
          <Route path="/today" element={<CommandCenter />} />
          <Route path="/changes" element={<ChangesFeed />} />
          <Route path="/changes/:id" element={<ChangeWorkspace />} />
          <Route path="/knowledge" element={<KnowledgeExplorer />} />
          <Route path="/actions" element={<DecisionsActions user={user} />} />
          <Route path="/factory" element={<FactoryBoard user={user} onSignInClick={() => setAuthModalOpen(true)} />} />
          <Route path="/ask" element={
            <AskIntelligence apiOnline={apiOnline} apiBaseUrl={API_BASE_URL} />
          } />
          <Route path="/admin" element={<AdminAudit />} />
          <Route path="*" element={<Navigate to="/today" replace />} />
        </Routes>
      </AppShell>

      <SearchOverlay isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
      <AuthModal 
        isOpen={authModalOpen} 
        onClose={() => setAuthModalOpen(false)} 
        onAuthSuccess={(u) => setUser(u)} 
      />
    </BrowserRouter>
  );
}
