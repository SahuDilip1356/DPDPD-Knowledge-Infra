import React, { useState } from "react";
import { SaralPrivacyLogo, SaralPrivacyMark } from "./ui/SaralPrivacyLogo";
import { MODULES_DATA } from "../data/certificationData";
import { useCourseProgress } from "./CourseProgressContext";
import "../styles/global.css";
import "../styles/components.css";

const WIKI_URL = import.meta.env.VITE_WIKI_URL || "https://dpdpa.wiki";

// Module 0 is the baseline diagnostic, 1–10 are the taught modules,
// 11 is the sector capstone and 12 is the certification exam.
const LEARNING_MODULES = MODULES_DATA.filter((m) => m.id >= 0 && m.id <= 10);
const CAPSTONE = MODULES_DATA.find((m) => m.id === 11);
const EXAM = MODULES_DATA.find((m) => m.id === 12);
const TOTAL_GRADED = 12;

/** Strips the "Module N: " prefix — the rail already shows the number. */
function shortTitle(title) {
  return title.replace(/^Module\s+\d+:\s*/, "");
}

function ModuleRow({ module, state, collapsed, onClick }) {
  const icon = { done: "✓", active: "●", locked: "○", open: "○" }[state];
  const isLocked = state === "locked";

  return (
    <button
      type="button"
      onClick={isLocked ? undefined : onClick}
      disabled={isLocked}
      title={collapsed ? shortTitle(module.title) : ""}
      className={`course-module-row ${state === "active" ? "active" : ""}`}
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: "10px",
        width: "100%",
        padding: collapsed ? "8px 0" : "8px 12px",
        justifyContent: collapsed ? "center" : "flex-start",
        background: state === "active" ? "rgba(96, 165, 250, 0.14)" : "transparent",
        borderLeft: state === "active" ? "2px solid #60A5FA" : "2px solid transparent",
        border: "none",
        borderRadius: "var(--radius-sm)",
        cursor: isLocked ? "not-allowed" : "pointer",
        opacity: isLocked ? 0.4 : 1,
        textAlign: "left",
        font: "inherit"
      }}
    >
      <span
        style={{
          fontSize: "12px",
          lineHeight: "18px",
          color: state === "done" ? "#22C55E" : state === "active" ? "#60A5FA" : "rgba(255,255,255,0.45)",
          flexShrink: 0
        }}
      >
        {icon}
      </span>
      {!collapsed && (
        <span style={{ display: "flex", flexDirection: "column", gap: "1px", minWidth: 0 }}>
          <span
            style={{
              fontSize: "12px",
              fontWeight: state === "active" ? 700 : 500,
              color: state === "active" ? "#FFFFFF" : "rgba(255,255,255,0.82)",
              lineHeight: 1.3
            }}
          >
            {module.id}. {shortTitle(module.title)}
          </span>
          <span style={{ fontSize: "10px", color: "rgba(255,255,255,0.4)" }}>{module.duration}</span>
        </span>
      )}
    </button>
  );
}

export default function CourseShell({
  children,
  apiOnline,
  loadingHealth,
  user,
  onSignInClick,
  onSignOutClick
}) {
  const [collapsed, setCollapsed] = useState(false);
  const { progress, goToModule } = useCourseProgress();
  const { phase, currentModuleId, completedModules, certIssued } = progress;

  const isDone = (id) => completedModules.includes(id);
  const gradedDone = completedModules.filter((id) => id >= 1).length;
  const percent = Math.round((gradedDone / TOTAL_GRADED) * 100);

  const stateFor = (id) => {
    if (isDone(id)) return "done";
    if (phase === "learning" && id === currentModuleId) return "active";
    if (id === 0 || isDone(id - 1)) return "open";
    return "locked";
  };

  return (
    <div className={`app-shell ${collapsed ? "nav-collapsed" : ""}`}>
      {/* ── Course Progress Rail ───────────────────────────────────── */}
      <aside className="app-nav">
        <div
          className="nav-brand"
          style={{ padding: collapsed ? "12px 0" : "12px 16px", justifyContent: collapsed ? "center" : "flex-start" }}
        >
          {!collapsed ? (
            <SaralPrivacyLogo
              lockup="horizontal"
              theme="dark"
              size={36}
              showTagline={false}
              onClick={() => setCollapsed(true)}
            />
          ) : (
            <div
              title="Expand Sidebar"
              onClick={() => setCollapsed(false)}
              style={{ cursor: "pointer", display: "flex", justifyContent: "center", width: "100%" }}
            >
              <SaralPrivacyMark size={32} theme="dark" />
            </div>
          )}
        </div>

        {/* ── Progress Meter ──────────────────────────────────────── */}
        <div style={{ padding: collapsed ? "8px 10px 12px" : "4px 16px 14px" }}>
          {!collapsed && (
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "baseline",
                marginBottom: "6px"
              }}
            >
              <span
                style={{
                  fontSize: "10px",
                  fontWeight: 700,
                  color: "rgba(255,255,255,0.55)",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em"
                }}
              >
                DPDPA Certification
              </span>
              <span style={{ fontSize: "11px", fontWeight: 700, color: "#60A5FA" }}>
                {gradedDone}/{TOTAL_GRADED}
              </span>
            </div>
          )}
          <div
            title={collapsed ? `${gradedDone}/${TOTAL_GRADED} complete` : ""}
            style={{ height: "4px", width: "100%", background: "rgba(255,255,255,0.12)", borderRadius: "2px" }}
          >
            <div
              style={{
                height: "100%",
                width: `${percent}%`,
                background: "linear-gradient(90deg, #1A4FA3 0%, #22C55E 100%)",
                borderRadius: "2px",
                transition: "width 240ms ease"
              }}
            />
          </div>
        </div>

        {/* ── Module List ─────────────────────────────────────────── */}
        <nav className="nav-menu" style={{ gap: "2px" }}>
          {LEARNING_MODULES.map((module) => (
            <ModuleRow
              key={module.id}
              module={module}
              state={stateFor(module.id)}
              collapsed={collapsed}
              onClick={() => goToModule(module.id)}
            />
          ))}

          <div style={{ height: "1px", background: "rgba(255,255,255,0.1)", margin: "10px 12px" }} />

          {CAPSTONE && (
            <ModuleRow
              module={{ ...CAPSTONE, title: "🎯 Sector Capstone Simulation" }}
              state={stateFor(CAPSTONE.id)}
              collapsed={collapsed}
              onClick={() => goToModule(CAPSTONE.id)}
            />
          )}
          {EXAM && (
            <ModuleRow
              module={{ ...EXAM, title: "🏆 Certification Exam" }}
              state={stateFor(EXAM.id)}
              collapsed={collapsed}
              onClick={() => goToModule(EXAM.id)}
            />
          )}
        </nav>

        {/* ── Footer: cross-domain hand-off + attribution ──────────── */}
        <div className="nav-footer">
          <a
            href={WIKI_URL}
            className="nav-link-item"
            title={collapsed ? "DPDPA Knowledge Base" : ""}
            style={{ marginBottom: collapsed ? "6px" : "10px" }}
          >
            <span className="nav-icon">📚</span>
            {!collapsed && (
              <div className="nav-label-group">
                <span className="nav-label">Knowledge Base ↗</span>
                <span className="nav-desc">dpdpa.wiki</span>
              </div>
            )}
          </a>

          {!collapsed ? (
            <div className="nav-version" style={{ flexDirection: "column", gap: "2px" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: "11px",
                  color: "var(--text-muted)"
                }}
              >
                <span>DPDPA Certification</span>
                <span>v1.0.0</span>
              </div>
              <div
                style={{
                  fontSize: "9px",
                  color: "rgba(255,255,255,0.55)",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  fontWeight: 600,
                  marginTop: "2px"
                }}
              >
                A SaralPrivacy Initiative
              </div>
            </div>
          ) : (
            <div style={{ textAlign: "center" }}>
              <span className="text-meta" style={{ fontSize: "10px", color: "var(--text-muted)" }}>
                v1.0
              </span>
            </div>
          )}
        </div>
      </aside>

      {/* ── Main Content Area ──────────────────────────────────────── */}
      <div className="app-main-container">
        <header className="app-topbar">
          <div className="topbar-left">
            <button className="btn-icon" onClick={() => setCollapsed(!collapsed)} aria-label="Toggle sidebar">
              ☰
            </button>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--brand-navy)" }}>
              {certIssued
                ? "📜 Verified Credential Issued"
                : phase === "learning" && LEARNING_MODULES.some((m) => m.id === currentModuleId)
                  ? shortTitle(MODULES_DATA.find((m) => m.id === currentModuleId)?.title || "")
                  : "DPDPA Business Practitioner Masterclass"}
            </span>
          </div>

          <div className="topbar-right" style={{ display: "flex", gap: "var(--space-md)", alignItems: "center" }}>
            <div className={`api-indicator-badge ${apiOnline ? "online" : ""}`}>
              <span className="api-dot"></span>
              <span>{loadingHealth ? "Checking status..." : apiOnline ? "Live API Online" : "Sandbox Mode"}</span>
            </div>

            {user ? (
              <div style={{ display: "flex", gap: "var(--space-sm)", alignItems: "center" }}>
                <span
                  className="text-meta"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "var(--space-xs)",
                    padding: "4px 8px",
                    background: "rgba(16, 185, 129, 0.1)",
                    color: "var(--color-success)",
                    borderRadius: "var(--radius-sm)",
                    fontWeight: 600
                  }}
                >
                  👤 {user.email.split("@")[0]}
                </span>
                <button
                  className="btn-secondary"
                  onClick={onSignOutClick}
                  style={{
                    padding: "4px 8px",
                    fontSize: "12px",
                    border: "1px solid rgba(255, 74, 74, 0.3)",
                    color: "#ff4a4a"
                  }}
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
                🔐 Sign In
              </button>
            )}
          </div>
        </header>

        <main className="app-content-body">
          <div className="content-max-wrapper">{children}</div>
        </main>
      </div>
    </div>
  );
}
