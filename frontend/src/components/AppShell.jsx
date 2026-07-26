import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import "../styles/global.css";
import "../styles/components.css";


export default function AppShell({ children, apiOnline, loadingHealth, onSearchClick }) {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: "/today", label: "Today", icon: "📅", description: "Command Center" },
    { path: "/changes", label: "Changes", icon: "🔄", description: "Regulatory Changes" },
    { path: "/knowledge", label: "Knowledge", icon: "📚", description: "Explorer & Graph" },
    { path: "/actions", label: "Decisions & Actions", icon: "💼", description: "Operational Response" },
    { path: "/factory", label: "Research Factory", icon: "🏗️", description: "Ingestion Pipeline" },
    { path: "/ask", label: "Ask Intelligence", icon: "🧠", description: "Grounded Q&A" },
  ];

  return (
    <div className={`app-shell ${collapsed ? "nav-collapsed" : ""}`}>
      {/* ── Left Navigation Drawer ─────────────────────────────────── */}
      <aside className="app-nav">
        <div className="nav-brand">
          <span className="brand-logo" onClick={() => setCollapsed(!collapsed)} style={{ cursor: "pointer" }}>🛡️</span>
          {!collapsed && (
            <div className="brand-text">
              <div className="brand-title">SaralPrivacy</div>
              <div className="brand-subtitle">Knowledge Infra</div>
            </div>
          )}
        </div>

        <nav className="nav-menu">
          {navItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link-item ${isActive ? "active" : ""}`}
                title={collapsed ? item.label : ""}
              >
                <span className="nav-icon">{item.icon}</span>
                {!collapsed && (
                  <div className="nav-label-group">
                    <span className="nav-label">{item.label}</span>
                    <span className="nav-desc">{item.description}</span>
                  </div>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="nav-footer">
          {!collapsed ? (
            <div className="nav-version">
              <span>DPDPA Core</span>
              <span>v1.0.0</span>
            </div>
          ) : (
            <span className="text-meta">v1</span>
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

          <div className="topbar-right">
            <div className={`api-indicator-badge ${apiOnline ? "online" : ""}`}>
              <span className="api-dot"></span>
              <span>{loadingHealth ? "Checking status..." : apiOnline ? "Live API Online" : "Sandbox Mode"}</span>
            </div>

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
