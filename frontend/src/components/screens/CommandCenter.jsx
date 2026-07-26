import React from "react";
import { useNavigate } from "react-router-dom";
import { REGULATORY_EVENTS, ACTION_ITEMS, PIPELINE_ITEMS, getTrustLabel } from "../../data/mockData";
import { MetricCard, StatusBadge, PriorityBadge, ImpactBadge } from "../ui/SharedComponents";

export default function CommandCenter() {
  const navigate = useNavigate();

  // Compute metrics
  const activeEventsCount = REGULATORY_EVENTS.filter(e => e.status === "active").length;
  const criticalActionsCount = ACTION_ITEMS.filter(a => a.priority === "critical" && a.status !== "completed").length;
  const pendingReviewCount = PIPELINE_ITEMS.length; // items in factory pipeline
  const unresolvedConflictsCount = 1; // mock conflict count

  const handleMetricClick = (path) => {
    navigate(path);
  };

  return (
    <div className="command-center flex flex-col gap-6">
      {/* ── Page Header ───────────────────────────────────────────── */}
      <div className="section-header">
        <div>
          <h1 className="text-display">Command Center</h1>
          <p className="text-small">Real-time overview of regulatory changes, compliance tasks, and data factory pipeline health.</p>
        </div>
        <div className="text-meta">Updated just now</div>
      </div>

      {/* ── Metric Grid ───────────────────────────────────────────── */}
      <div className="metric-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "var(--space-4)" }}>
        <MetricCard
          label="Material Changes"
          value={activeEventsCount}
          icon="🔄"
          onClick={() => handleMetricClick("/changes")}
        />
        <MetricCard
          label="Critical Action Items"
          value={criticalActionsCount}
          icon="💼"
          onClick={() => handleMetricClick("/actions")}
        />
        <MetricCard
          label="Pending Review"
          value={pendingReviewCount}
          icon="🏗️"
          onClick={() => handleMetricClick("/factory")}
        />
        <MetricCard
          label="Unresolved Conflicts"
          value={unresolvedConflictsCount}
          icon="⚠️"
          onClick={() => handleMetricClick("/changes")} // or specific workspace
        />
      </div>

      {/* ── Main Dashboard Layout ─────────────────────────────────── */}
      <div className="dashboard-grid" style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "var(--space-6)" }}>
        
        {/* Left Column: Material Changes & Attention Required */}
        <div className="flex flex-col gap-6">
          {/* Section: Material Changes */}
          <div className="card">
            <div className="section-header" style={{ marginBottom: "var(--space-4)" }}>
              <h3>Material Changes</h3>
              <button className="btn btn-secondary" onClick={() => navigate("/changes")}>View All Changes</button>
            </div>
            
            <div className="table-wrapper" style={{ overflowX: "auto" }}>
              <table className="data-table" style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid var(--border)", paddingBottom: "var(--space-2)" }}>
                    <th style={{ padding: "var(--space-2) 0", fontWeight: "var(--fw-semibold)" }}>Event</th>
                    <th style={{ padding: "var(--space-2)", fontWeight: "var(--fw-semibold)" }}>Authority</th>
                    <th style={{ padding: "var(--space-2)", fontWeight: "var(--fw-semibold)" }}>Effective Date</th>
                    <th style={{ padding: "var(--space-2)", fontWeight: "var(--fw-semibold)" }}>Impact</th>
                  </tr>
                </thead>
                <tbody>
                  {REGULATORY_EVENTS.slice(0, 3).map((event) => (
                    <tr 
                      key={event.id} 
                      className="table-row-interactive" 
                      onClick={() => navigate(`/changes/${event.id}`)}
                      style={{ borderBottom: "1px solid var(--border)", cursor: "pointer" }}
                    >
                      <td style={{ padding: "var(--space-3) 0", maxWidth: "320px" }}>
                        <div style={{ fontWeight: "var(--fw-medium)", color: "var(--text-primary)" }}>{event.title}</div>
                        <div className="text-small" style={{ marginTop: "2px" }}>{event.type}</div>
                      </td>
                      <td style={{ padding: "var(--space-3)" }}>{event.authority}</td>
                      <td style={{ padding: "var(--space-3)" }}>{event.date_effective}</td>
                      <td style={{ padding: "var(--space-3)" }}>
                        <ImpactBadge level={event.impact_level} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Section: Attention Required */}
          <div className="card">
            <div className="section-header" style={{ marginBottom: "var(--space-4)" }}>
              <h3>Attention Required</h3>
            </div>
            
            <div className="attention-list flex flex-col gap-3">
              {ACTION_ITEMS.filter(a => a.status === "proposed" || a.priority === "critical").map((action) => (
                <div 
                  key={action.id} 
                  className="attention-item card card-compact card-interactive flex items-center justify-between"
                  onClick={() => navigate("/actions")}
                  style={{ borderLeft: "4px solid var(--error)" }}
                >
                  <div style={{ minWidth: 0, flex: 1, paddingRight: "var(--space-4)" }}>
                    <div style={{ fontWeight: "var(--fw-semibold)", color: "var(--text-primary)" }} className="truncate">
                      {action.title}
                    </div>
                    <div className="text-small flex gap-2 items-center" style={{ marginTop: "2px" }}>
                      <span>Due: {action.due_date}</span>
                      <span>•</span>
                      <span>Owner: {action.owner}</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
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
          <div className="card flex flex-col gap-4">
            <h3>Factory Pipeline Health</h3>
            <p className="text-small">Status of ongoing data ingestion, schema parsing, and verification checks.</p>
            
            <div className="pipeline-stats flex flex-col gap-3">
              {PIPELINE_ITEMS.map((item) => (
                <div key={item.id} className="pipeline-mini-card" style={{ padding: "var(--space-2) 0", borderBottom: "1px solid var(--border)" }}>
                  <div className="flex justify-between" style={{ marginBottom: "2px" }}>
                    <span style={{ fontWeight: "var(--fw-medium)", fontSize: "var(--text-small)" }} className="truncate">{item.title}</span>
                    <PriorityBadge priority={item.priority} />
                  </div>
                  <div className="flex justify-between text-small">
                    <span>{item.stage_name}</span>
                    <span style={{ color: "var(--text-muted)" }}>{item.time_in_stage}</span>
                  </div>
                </div>
              ))}
            </div>

            <button className="btn btn-primary" onClick={() => navigate("/factory")} style={{ width: "100%", justifyContent: "center" }}>
              Open Research Factory Board
            </button>
          </div>

          <div className="card flex flex-col gap-3" style={{ background: "var(--status-review-bg)", borderColor: "var(--warning-border)" }}>
            <h4 style={{ color: "#92400E" }}>💡 Compliance Tips</h4>
            <ul className="flex flex-col gap-2 text-small" style={{ color: "#78350F" }}>
              <li>• Ensure all consent notices offer translation options before <strong>June 15, 2024</strong>.</li>
              <li>• Set up automated alerts for security breaches to comply with the 72-hour reporting rule.</li>
              <li>• Perform a bi-annual audit of third-party vendor data contracts.</li>
            </ul>
          </div>
        </div>

      </div>
    </div>
  );
}
