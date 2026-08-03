import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./styles/design-tokens.css";
import "./styles/global.css";
import "./styles/components.css";

import CourseShell from "./components/CourseShell";
import { CourseProgressProvider } from "./components/CourseProgressContext";
import AuthModal from "./components/ui/AuthModal";
import { supabase } from "./data/supabaseClient";

import CertificationCourse from "./components/screens/CertificationCourse";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WIKI_URL = import.meta.env.VITE_WIKI_URL || "https://dpdpa.wiki";

/**
 * dpdpa.shiksha serves exactly one thing: the certification course.
 * Every knowledge-infrastructure surface lives on dpdpa.wiki — the course's
 * "Tool Bridge" CTAs hand off there.
 */
function CertificationCourseWrapper() {
  return (
    <CertificationCourse
      onNavigate={(screen) => {
        window.location.assign(`${WIKI_URL}/${screen}`);
      }}
    />
  );
}

export default function App() {
  const [apiOnline, setApiOnline] = useState(false);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [user, setUser] = useState(null);

  // Check API health status
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`, { method: "GET" });
        setApiOnline(response.ok);
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

    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setUser(session.user);
      }
    });

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

  return (
    <BrowserRouter>
      <CourseProgressProvider>
        <CourseShell
          apiOnline={apiOnline}
          loadingHealth={loadingHealth}
          user={user}
          onSignInClick={() => setAuthModalOpen(true)}
          onSignOutClick={handleSignOut}
        >
          <Routes>
            <Route path="/" element={<CertificationCourseWrapper />} />
            {/* Legacy in-app path from the pre-split single-domain build. */}
            <Route path="/course" element={<Navigate to="/" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </CourseShell>
      </CourseProgressProvider>

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={(u) => setUser(u)}
      />
    </BrowserRouter>
  );
}
