import React, { useState } from "react";
import { supabase } from "../../data/supabaseClient";

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  if (!isOpen) return null;

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setErrorMsg("");

    if (!supabase) {
      // Mock Auth Fallback Mode (offline)
      setTimeout(() => {
        setLoading(false);
        const mockUser = { email, id: "mock-user-uuid-12345" };
        onAuthSuccess(mockUser);
        onClose();
      }, 500);
      return;
    }

    try {
      if (isSignUp) {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        setMessage("Verification email sent! Check your inbox.");
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        if (data?.user) {
          onAuthSuccess(data.user);
          onClose();
        }
      }
    } catch (err) {
      setErrorMsg(err.message || "An authentication error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-overlay" style={{ display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1100 }}>
      <div className="search-modal-container" style={{ maxWidth: "420px", width: "100%", padding: "var(--space-xl)", gap: "var(--space-md)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
          <h3 className="section-title" style={{ margin: 0 }}>
            {isSignUp ? "🛡️ Register Admin" : "🛡️ Admin Authorization"}
          </h3>
          <button className="btn-icon" onClick={onClose} style={{ fontSize: "18px" }}>×</button>
        </div>

        <p className="text-meta" style={{ margin: 0 }}>
          {supabase 
            ? "Sign in using your Supabase credentials to manage compliance and ingestion settings."
            : "Sandbox Mode active: Enter any email/password to authenticate as a mock administrator."}
        </p>

        <form onSubmit={handleAuth} style={{ display: "flex", flexDirection: "column", gap: "var(--space-md)", width: "100%", marginTop: "var(--space-sm)" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-xs)" }}>
            <label className="text-meta" style={{ fontWeight: 600 }}>Email Address</label>
            <input
              type="email"
              placeholder="admin@saralprivacy.in"
              className="topbar-search-trigger"
              style={{ width: "100%", padding: "var(--space-sm)", background: "rgba(255, 255, 255, 0.03)", color: "var(--color-text-primary)", border: "1px solid rgba(255, 255, 255, 0.1)", borderRadius: "var(--radius-md)" }}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-xs)" }}>
            <label className="text-meta" style={{ fontWeight: 600 }}>Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className="topbar-search-trigger"
              style={{ width: "100%", padding: "var(--space-sm)", background: "rgba(255, 255, 255, 0.03)", color: "var(--color-text-primary)", border: "1px solid rgba(255, 255, 255, 0.1)", borderRadius: "var(--radius-md)" }}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {errorMsg && (
            <div className="card" style={{ borderLeft: "3px solid #ff4a4a", background: "rgba(255, 74, 74, 0.05)", padding: "var(--space-sm)" }}>
              <span className="text-body" style={{ color: "#ff4a4a", fontSize: "13px" }}>{errorMsg}</span>
            </div>
          )}

          {message && (
            <div className="card" style={{ borderLeft: "3px solid var(--color-success)", background: "rgba(16, 185, 129, 0.05)", padding: "var(--space-sm)" }}>
              <span className="text-body" style={{ color: "var(--color-success)", fontSize: "13px" }}>{message}</span>
            </div>
          )}

          <button className="btn-primary" type="submit" disabled={loading} style={{ width: "100%", justifyContent: "center", marginTop: "var(--space-xs)" }}>
            {loading ? "Authenticating..." : isSignUp ? "Create Admin Account" : "Authorize Session"}
          </button>
        </form>

        <div style={{ display: "flex", justifyContent: "center", marginTop: "var(--space-sm)" }}>
          <button 
            className="text-link-btn" 
            onClick={() => {
              setIsSignUp(!isSignUp);
              setMessage("");
              setErrorMsg("");
            }}
            style={{ background: "none", border: "none", color: "var(--color-accent-blue)", cursor: "pointer", fontSize: "13px" }}
          >
            {isSignUp ? "Already have an account? Sign In" : "Need an account? Register as Admin"}
          </button>
        </div>
      </div>
    </div>
  );
}
