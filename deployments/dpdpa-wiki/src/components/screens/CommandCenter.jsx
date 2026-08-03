import React from "react";
import { useNavigate } from "react-router-dom";
import { REGULATORY_EVENTS, ACTION_ITEMS, PIPELINE_ITEMS } from "../../data/mockData";
import { MetricCard, StatusBadge, PriorityBadge, ImpactBadge } from "../ui/SharedComponents";

export default function CommandCenter() {
  const navigate = useNavigate();

  // Compute metrics
  const activeEventsCount = REGULATORY_EVENTS.filter(e => e.status === "active").length;
  const criticalActionsCount = ACTION_ITEMS.filter(a => a.priority === "critical" && a.status !== "completed").length;
  const pendingReviewCount = PIPELINE_ITEMS.length;
  const unresolvedConflictsCount = 1;

  const handleMetricClick = (path) => {
    navigate(path);
  };

  return (
    <div className="command-center flex flex-col gap-6" style={{ paddingBottom: "var(--space-8)" }}>
      {/* ── Enterprise Hero Banner ──────────────────────────────────── */}
      <div className="hero-banner flex items-center justify-between gap-6" style={{ background: "linear-gradient(135deg, #14213D 0%, #0F172A 100%)", borderRadius: "16px", padding: "28px 32px", color: "#FFFFFF", boxShadow: "0 10px 25px -5px rgba(20, 33, 61, 0.3)" }}>
        <div className="flex flex-col gap-2" style={{ maxWidth: "780px" }}>
          <div style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "4px" }}>
            <span style={{ background: "rgba(19, 136, 8, 0.2)", border: "1px solid #138808", color: "#34D399", padding: "3px 10px", borderRadius: "9999px", fontSize: "11px", fontWeight: 700, letterSpacing: "0.05em", textTransform: "uppercase" }}>
              🇮🇳 India DPDPA Framework
            </span>
            <span style={{ background: "rgba(26, 79, 163, 0.2)", stroke: "#1A4FA3", color: "#93C5FD", padding: "3px 10px", borderRadius: "9999px", fontSize: "11px", fontWeight: 600 }}>
              Live Knowledge Graph v1.0
            </span>
          </div>

          <h1 style={{ fontSize: "28px", fontWeight: 800, color: "#FFFFFF", lineHeight: 1.2, margin: 0 }}>
            SaralPrivacy Knowledge Infra
          </h1>
          <p style={{ fontSize: "14px", color: "rgba(255, 255, 255, 0.8)", lineHeight: 1.5, margin: 0 }}>
            India’s authoritative, real-time Privacy Knowledge Engine — tracking statutory DPDPA rules, MeitY notifications, judicial precedents & operational playbooks.
          </p>

          <div style={{ display: "flex", gap: "16px", marginTop: "12px", fontSize: "12px", color: "rgba(255,255,255,0.7)" }}>
            <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#34D399", boxShadow: "0 0 8px #34D399" }}></span>
              Statutory Graph Online
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#60A5FA" }}></span>
              MeitY & Judicial Feeds Active
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#FF9933" }}></span>
              Zero Unmapped Obligations
            </span>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "10px", minWidth: "200px" }}>
          <button 
            className="btn btn-primary" 
            onClick={() => navigate("/knowledge")}
            style={{ padding: "10px 18px", fontSize: "13px", background: "#138808", color: "#FFFFFF", borderRadius: "8px", fontWeight: 700, boxShadow: "0 4px 12px rgba(19, 136, 8, 0.3)" }}
          >
            Explore Knowledge Graph →
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={() => navigate("/ask")}
            style={{ padding: "10px 18px", fontSize: "13px", background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.2)", color: "#FFFFFF", borderRadius: "8px" }}
          >
            🧠 Ask Intelligence Q&A
          </button>
        </div>
      </div>

      {/* ── Metric Grid ───────────────────────────────────────────── */}
      <div className="metric-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "var(--space-4)" }}>
        <MetricCard
          label="Material Changes"
          value={activeEventsCount}
          change={2}
          trendLabel="Active Legislation & Amendments"
          icon="🔄"
          color="blue"
          onClick={() => handleMetricClick("/changes")}
        />
        <MetricCard
          label="Critical Action Items"
          value={criticalActionsCount}
          trendLabel="Operational Responses Due"
          icon="💼"
          color="saffron"
          onClick={() => handleMetricClick("/actions")}
        />
        <MetricCard
          label="Pending Review"
          value={pendingReviewCount}
          trendLabel="Research Factory Pipeline"
          icon="🏗️"
          color="green"
          onClick={() => handleMetricClick("/factory")}
        />
        <MetricCard
          label="Unresolved Conflicts"
          value={unresolvedConflictsCount}
          trendLabel="Automated Conflict Engine"
          icon="⚖️"
          color="navy"
          onClick={() => handleMetricClick("/changes")}
        />
      </div>

      {/* ── Main Dashboard Layout ─────────────────────────────────── */}
      <div className="dashboard-grid" style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "var(--space-6)" }}>
        
        {/* Left Column: Material Changes & Attention Required */}
        <div className="flex flex-col gap-6">
          {/* Section: Material Changes */}
          <div className="card" style={{ background: "#FFFFFF", borderRadius: "16px", border: "1px solid var(--border)", boxShadow: "0 4px 20px -2px rgba(20, 33, 61, 0.05)" }}>
            <div className="section-header" style={{ marginBottom: "16px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <h3 style={{ fontSize: "17px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>Material Regulatory Changes</h3>
                  <span style={{ background: "#EFF6FF", border: "1px solid #BFDBFE", color: "#1E40AF", fontSize: "11px", fontWeight: 700, padding: "2px 8px", borderRadius: "9999px" }}>
                    {activeEventsCount} Active
                  </span>
                </div>
                <p className="text-small" style={{ margin: "3px 0 0 0", color: "var(--brand-slate)" }}>
                  Latest statutory amendments, gazetted DPDP rules, and judicial notifications.
                </p>
              </div>
              <button 
                className="btn btn-secondary" 
                onClick={() => navigate("/changes")} 
                style={{ fontSize: "12px", padding: "7px 14px", fontWeight: 600, color: "var(--brand-blue)", borderColor: "var(--brand-blue)" }}
              >
                View All Changes →
              </button>
            </div>
            
            <div className="table-wrapper" style={{ overflowX: "auto", borderRadius: "10px", border: "1px solid #E2E8F0" }}>
              <table className="data-table" style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
                <thead>
                  <tr style={{ background: "linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%)", borderBottom: "2px solid #CBD5E1" }}>
                    <th style={{ padding: "12px 14px", fontSize: "11px", fontWeight: 800, color: "#334155", textTransform: "uppercase", letterSpacing: "0.06em" }}>Event Title & Category</th>
                    <th style={{ padding: "12px 14px", fontSize: "11px", fontWeight: 800, color: "#334155", textTransform: "uppercase", letterSpacing: "0.06em" }}>Issuing Authority</th>
                    <th style={{ padding: "12px 14px", fontSize: "11px", fontWeight: 800, color: "#334155", textTransform: "uppercase", letterSpacing: "0.06em" }}>Effective Date</th>
                    <th style={{ padding: "12px 14px", fontSize: "11px", fontWeight: 800, color: "#334155", textTransform: "uppercase", letterSpacing: "0.06em" }}>Impact Assessment</th>
                    <th style={{ padding: "12px 14px", fontSize: "11px", fontWeight: 800, color: "#334155", textTransform: "uppercase", letterSpacing: "0.06em", textAlign: "right" }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {REGULATORY_EVENTS.slice(0, 3).map((event) => {
                    const formattedDate = event.date_effective 
                      ? new Date(event.date_effective).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })
                      : null;

                    return (
                      <tr 
                        key={event.id} 
                        className="table-row-interactive" 
                        onClick={() => navigate(`/changes/${event.id}`)}
                        style={{ 
                          borderBottom: "1px solid #E2E8F0", 
                          cursor: "pointer", 
                          transition: "all 150ms ease",
                          background: "#FFFFFF" 
                        }}
                      >
                        <td style={{ padding: "16px 14px", maxWidth: "340px" }}>
                          <div style={{ fontWeight: 700, color: "var(--brand-navy)", fontSize: "14px", lineHeight: 1.3 }}>
                            {event.title}
                          </div>
                          <div style={{ marginTop: "6px", display: "inline-flex", alignItems: "center", gap: "4px", background: "#F1F5F9", border: "1px solid #CBD5E1", padding: "2px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: 600, color: "#475569" }}>
                            <span>{event.type.includes("Legislation") ? "📜 Statute" : event.type.includes("Draft") ? "📋 Draft Rule" : event.type.includes("Consultation") ? "💬 Public Consultation" : "⚖️ Gazetted Rule"}</span>
                          </div>
                        </td>

                        <td style={{ padding: "16px 14px", fontSize: "13px", color: "var(--brand-slate)" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                            <span style={{ width: "26px", height: "26px", borderRadius: "6px", background: "#F0F4F8", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "13px" }}>
                              {event.authority.includes("Parliament") ? "🏛️" : "💻"}
                            </span>
                            <span style={{ fontWeight: 600, color: "var(--brand-navy)" }}>{event.authority}</span>
                          </div>
                        </td>

                        <td style={{ padding: "16px 14px", fontSize: "13px" }}>
                          {formattedDate ? (
                            <span style={{ fontWeight: 700, color: "var(--brand-navy)", display: "flex", alignItems: "center", gap: "4px" }}>
                              <span>📅</span> {formattedDate}
                            </span>
                          ) : (
                            <span style={{ background: "#F8FAFC", border: "1px solid #E2E8F0", color: "#64748B", padding: "3px 10px", borderRadius: "9999px", fontSize: "11px", fontWeight: 600 }}>
                              Draft Phase
                            </span>
                          )}
                        </td>

                        <td style={{ padding: "16px 14px" }}>
                          <ImpactBadge level={event.impact_level} />
                        </td>

                        <td style={{ padding: "16px 14px", textAlign: "right" }}>
                          <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--brand-blue)", display: "inline-flex", alignItems: "center", gap: "2px" }}>
                            Details →
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Section: Attention Required */}
          <div className="card" style={{ background: "#FFFFFF", borderRadius: "14px", border: "1px solid var(--border)", boxShadow: "var(--shadow-card)" }}>
            <div className="section-header" style={{ marginBottom: "var(--space-4)" }}>
              <div>
                <h3 style={{ fontSize: "16px", fontWeight: 700, color: "var(--brand-navy)", margin: 0 }}>Attention Required</h3>
                <p className="text-small" style={{ margin: "2px 0 0 0" }}>High-priority compliance responses & DPO task deadlines.</p>
              </div>
            </div>
            
            <div className="attention-list flex flex-col gap-3">
              {ACTION_ITEMS.filter(a => a.status === "proposed" || a.priority === "critical").map((action) => (
                <div 
                  key={action.id} 
                  className="attention-item card card-compact card-interactive flex items-center justify-between"
                  onClick={() => navigate("/actions")}
                  style={{ borderLeft: "4px solid #DC2626", background: "#FAFBFD", padding: "14px 16px" }}
                >
                  <div style={{ minWidth: 0, flex: 1, paddingRight: "var(--space-4)" }}>
                    <div style={{ fontWeight: 700, color: "var(--brand-navy)", fontSize: "14px" }} className="truncate">
                      {action.title}
                    </div>
                    <div className="text-small flex gap-3 items-center" style={{ marginTop: "4px", color: "var(--text-muted)", fontSize: "12px" }}>
                      <span style={{ fontWeight: 600, color: "#DC2626" }}>📅 Due: {action.due_date}</span>
                      <span>•</span>
                      <span>👤 Owner: {action.owner}</span>
                    </div>
                  </div>
                  <div className="flex gap-2 items-center">
                    <PriorityBadge priority={action.priority} />
                    <StatusBadge status={action.status} size="small" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Ingestion Factory Health & Summary */}
        <div className="flex flex-col gap-6">
          <div className="card flex flex-col gap-4" style={{ background: "#FFFFFF", borderRadius: "14px", border: "1px solid var(--border)", boxShadow: "var(--shadow-card)" }}>
            <div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, color: "var(--brand-navy)", margin: 0 }}>Factory Pipeline Health</h3>
              <p className="text-small" style={{ margin: "2px 0 0 0" }}>Real-time data ingestion & citation verification status.</p>
            </div>
            
            <div className="pipeline-stats flex flex-col gap-3">
              {PIPELINE_ITEMS.map((item) => (
                <div key={item.id} className="pipeline-mini-card" style={{ padding: "10px 0", borderBottom: "1px solid var(--border)" }}>
                  <div className="flex justify-between items-center" style={{ marginBottom: "4px" }}>
                    <span style={{ fontWeight: 600, fontSize: "13px", color: "var(--brand-navy)" }} className="truncate">{item.title}</span>
                    <PriorityBadge priority={item.priority} />
                  </div>
                  <div className="flex justify-between text-small" style={{ fontSize: "12px", color: "var(--brand-slate)" }}>
                    <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#138808" }}></span>
                      {item.stage_name}
                    </span>
                    <span style={{ color: "var(--text-muted)", fontWeight: 500 }}>{item.time_in_stage}</span>
                  </div>
                </div>
              ))}
            </div>

            <button className="btn btn-primary" onClick={() => navigate("/factory")} style={{ width: "100%", justifyContent: "center", padding: "10px", fontSize: "13px" }}>
              Open Research Factory Board →
            </button>
          </div>

          {/* DPDPA Knowledge Tip Card */}
          <div className="card flex flex-col gap-3" style={{ background: "#FFF7ED", borderColor: "#FDBA74", borderRadius: "14px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "16px" }}>💡</span>
              <h4 style={{ color: "#92400E", margin: 0, fontSize: "14px", fontWeight: 700 }}>DPDPA Compliance Insight</h4>
            </div>
            <ul className="flex flex-col gap-2 text-small" style={{ color: "#78350F", fontSize: "12px", lineHeight: 1.5 }}>
              <li>• All consent notices must provide multi-lingual support under DPDPA Rule guidelines.</li>
              <li>• Data Fiduciaries must configure automated 72-hour breach reporting protocols to CERT-In & DPBI.</li>
              <li>• Conduct quarterly verifications of Data Processor contracts against primary statutory rules.</li>
            </ul>
          </div>
        </div>

      </div>
    </div>
  );
}

