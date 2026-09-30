import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { SaralPrivacyLogo, SaralPrivacyMark } from "./ui/SaralPrivacyLogo";
import NavIcon from "./ui/NavIcon";
import "../styles/global.css";
import "../styles/components.css";

export default function AppShell({ children, apiOnline, loadingHealth, onSearchClick, user, onSignInClick, onSignOutClick }) {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  const navSections = [
    {
      label: "Operations",
      items: [
        { path: "/workspace/today", label: "Today", icon: "today", description: "Command Center" },
        { path: "/workspace/changes", label: "Changes", icon: "changes", description: "Regulatory tracker" },
        { path: "/workspace/actions", label: "Decisions", icon: "actions", description: "Operational response" },
      ],
    },
    {
      label: "Knowledge",
      items: [
        { path: "/workspace/acts", label: "Acts", icon: "knowledge", description: "Statutory law" },
        { path: "/workspace/rules", label: "Rules", icon: "knowledge", description: "Regulatory rules" },
        { path: "/workspace/interpretations", label: "Interpretations", icon: "ask", description: "Opinion and commentary" },
        { path: "/workspace/discussions", label: "Discussions", icon: "bible", description: "Circulars and notes" },
        { path: "/workspace/bible", label: "DPDPA Bible", icon: "bible", description: "Legal reference" },
      ],
    },
    {
      label: "Intelligence",
      items: [
        { path: "/workspace/knowledge", label: "Knowledge Graph", icon: "knowledge", description: "Object explorer" },
        { path: "/workspace/ask", label: "Ask Intelligence", icon: "ask", description: "Grounded Q&A" },
        { path: "/workspace/infographic", label: "Architecture", icon: "architecture", description: "Visual blueprint" },
        { path: "/workspace/factory", label: "Research Factory", icon: "factory", description: "Ingestion pipeline" },
      ],
    },
    {
      label: "Programs",
      items: [
        { path: "/workspace/course", label: "DPDPA Certification", icon: "certification", description: "Masterclass & Exam", external: true },
        ...(user ? [{ path: "/workspace/admin", label: "Admin Audit", icon: "admin", description: "Audit & analytics" }] : []),
      ],
    },
  ];

  const isActivePath = (path) => location.pathname === path || location.pathname.startsWith(`${path}/`);

  return (
    <div className={`app-shell ${collapsed ? "nav-collapsed" : ""}`}>
      {/* ── Left Navigation Drawer ─────────────────────────────────── */}
      <aside className="app-nav">
        <div className="nav-brand" style={{ padding: collapsed ? "12px 0" : "12px 16px", justifyContent: collapsed ? "center" : "flex-start" }}>
          {!collapsed ? (
            <SaralPrivacyLogo
              lockup="horizontal"
              theme="dark"
              size={36}
              showTagline={false}
              onClick={() => setCollapsed(!collapsed)}
            />
          ) : (
            <div
              title="Expand Sidebar"
              onClick={() => setCollapsed(!collapsed)}
              style={{ cursor: "pointer", display: "flex", justifyContent: "center", width: "100%" }}
            >
              <SaralPrivacyMark size={32} theme="dark" />
            </div>
          )}
        </div>

        <nav className="nav-menu">
          {navSections.map((section) => (
            <div className="nav-section" key={section.label}>
              {!collapsed && <p className="nav-section-title">{section.label}</p>}
              {section.items.map((item) => {
                const externalUrl = item.external
                  ? import.meta.env.VITE_SHIKSHA_URL || "https://dpdpa.shiksha"
                  : null;

                if (externalUrl) {
                  return (
                    <a
                      key={item.path}
                      href={externalUrl}
                      className="nav-link-item"
                      title={collapsed ? item.label : ""}
                    >
                      <span className="nav-icon"><NavIcon name={item.icon} /></span>
                      {!collapsed && (
                        <div className="nav-label-group">
                          <span className="nav-label">{item.label}</span>
                          <span className="nav-desc">{item.description}</span>
                        </div>
                      )}
                    </a>
                  );
                }

                const isActive = isActivePath(item.path);

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`nav-link-item ${isActive ? "active" : ""}`}
                    title={collapsed ? item.label : ""}
                  >
                    <span className="nav-icon"><NavIcon name={item.icon} /></span>
                    {!collapsed && (
                      <div className="nav-label-group">
                        <span className="nav-label">{item.label}</span>
                        <span className="nav-desc">{item.description}</span>
                      </div>
                    )}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        <div className="nav-footer">
          {!collapsed ? (
            <div className="nav-version" style={{ flexDirection: "column", gap: "2px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "var(--text-muted)" }}>
                <span>DPDPA Knowledge Infra</span>
                <span>v1.0.0</span>
              </div>
              <div style={{ fontSize: "9px", color: "rgba(255,255,255,0.4)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                India Privacy Engine
              </div>
              <div style={{ fontSize: "9px", color: "rgba(255,255,255,0.55)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 600, marginTop: "4px" }}>
                A SaralPrivacy Initiative
              </div>
            </div>
          ) : (
            <div style={{ textAlign: "center" }}>
              <span className="text-meta" style={{ fontSize: "10px", color: "var(--text-muted)" }}>v1.0</span>
            </div>
          )}
        </div>
      </aside>

      {/* ── Main Content Area ─────────────────────────────────────── */}
      <div className="app-main-container">
        {/* ── Top Bar ─────────────────────────────────────────────── */}
        <header className="app-topbar">
          <div className="topbar-left">
            <button
              className="btn-icon"
              onClick={() => setCollapsed(!collapsed)}
              aria-label="Toggle sidebar"
            >
              ☰
            </button>
            <button className="topbar-search-trigger" onClick={onSearchClick}>
              <span>🔍 Search Knowledge, URNs, Actions...</span>
              <kbd>⌘K</kbd>
            </button>
          </div>

          <div className="topbar-right" style={{ display: "flex", gap: "var(--space-md)", alignItems: "center" }}>
            <div className={`api-indicator-badge ${apiOnline ? "online" : ""}`}>
              <span className="api-dot"></span>
              <span>{loadingHealth ? "Checking status..." : apiOnline ? "Live API Online" : "API Unavailable"}</span>
            </div>

            {user ? (
              <div style={{ display: "flex", gap: "var(--space-sm)", alignItems: "center" }}>
                <span className="text-meta" style={{ display: "flex", alignItems: "center", gap: "var(--space-xs)", padding: "4px 8px", background: "rgba(16, 185, 129, 0.1)", color: "var(--color-success)", borderRadius: "var(--radius-sm)", fontWeight: 600 }}>
                  👤 {user.email.split("@")[0]}
                </span>
                <button 
                  className="btn-secondary" 
                  onClick={onSignOutClick}
                  style={{ padding: "4px 8px", fontSize: "12px", border: "1px solid rgba(255, 74, 74, 0.3)", color: "#ff4a4a" }}
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <button 
                className="btn-primary" 
                onClick={onSignInClick}
                style={{ padding: "6px 12px", fontSize: "12px", gap: "6px" }}
              >
                🔐 Admin Login
              </button>
            )}

            <button className="btn-icon" aria-label="Notifications">
              🔔
            </button>
          </div>
        </header>

        {/* ── Content View ─────────────────────────────────────────── */}
        <main className="app-content-body">
          <div className="content-max-wrapper">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
