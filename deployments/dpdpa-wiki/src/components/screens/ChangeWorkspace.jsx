import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getEventById, getKOByUrn, getActionsForEvent, CONFLICTS } from "../../data/mockData";
import { 
  StatusBadge, 
  PriorityBadge, 
  ImpactBadge, 
  TrustIndicator, 
  CitationCard, 
  TimeDisplay, 
  ObjectTypeBadge 
} from "../ui/SharedComponents";

export default function ChangeWorkspace() {
  const { id } = useParams();
  const navigate = useNavigate();
  const event = getEventById(id);

  const [activeTab, setActiveTab] = useState("overview");
  const [applicability, setApplicability] = useState("unknown");
  const [rationale, setRationale] = useState("");
  const [savingApplicability, setSavingApplicability] = useState(false);

  if (!event) {
    return (
      <div className="card text-center" style={{ padding: "var(--space-12)" }}>
        <h3>Event not found</h3>
        <button className="btn btn-primary" onClick={() => navigate("/changes")} style={{ marginTop: "var(--space-4)" }}>
          Back to Changes
        </button>
      </div>
    );
  }

  // Get related objects & actions
  const relatedKOs = event.affected_ko_urns.map(urn => getKOByUrn(urn)).filter(Boolean);
  const eventActions = getActionsForEvent(event.id);
  
  // Find associated conflicts if event has any
  const eventConflicts = event.has_conflicts 
    ? CONFLICTS.filter(c => c.claim_a.ko_urn === event.affected_ko_urns[0] || c.claim_b.ko_urn === event.affected_ko_urns[0])
    : [];

  const handleSaveApplicability = () => {
    setSavingApplicability(true);
    setTimeout(() => {
      setSavingApplicability(false);
      alert("Applicability decision saved to Git audit ledger successfully!");
    }, 800);
  };

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "evidence", label: "Evidence" },
    { id: "changed", label: "What Changed" },
    { id: "impact", label: "Impact Radius" },
    { id: "conflicts", label: `Conflicts (${eventConflicts.length})` },
    { id: "actions", label: `Decisions & Actions (${eventActions.length})` },
    { id: "history", label: "History" },
  ];

  return (
    <div className="change-workspace flex flex-col gap-6">
      {/* ── Breadcrumb ── */}
      <div className="text-small">
        <span style={{ cursor: "pointer", color: "var(--text-link)" }} onClick={() => navigate("/changes")}>
          Regulatory Changes
        </span>{" "}
        / {event.title.substring(0, 40)}...
      </div>

      {/* ── Workspace Header ───────────────────────────────────────── */}
      <div className="card flex flex-col gap-4" style={{ borderLeft: "6px solid var(--assurance-teal)" }}>
        <div className="flex justify-between items-start gap-4">
          <div>
            <span className="text-meta">{event.authority} • {event.jurisdiction}</span>
            <h1 className="text-h1" style={{ marginTop: "4px" }}>{event.title}</h1>
          </div>
          <div className="flex gap-2">
            <ImpactBadge level={event.impact_level} />
            <StatusBadge status={event.status} />
          </div>
        </div>

        <div className="flex gap-6 text-small" style={{ flexWrap: "wrap" }}>
          <TimeDisplay label="Published" date={event.date_published} />
          <TimeDisplay label="Effective Date" date={event.date_effective} />
          <TimeDisplay label="Detected By Scout" date={event.date_detected} />
        </div>
      </div>

      {/* ── Three-Panel Workspace Layout ───────────────────────────── */}
      <div className="workspace-layout" style={{ display: "grid", gridTemplateColumns: "3fr 1fr", gap: "var(--space-6)" }}>
        
        {/* Left Column: Tabbed Workspace */}
        <div className="flex flex-col gap-4">
          {/* Tab Navigation */}
          <nav className="nav-tabs" style={{ background: "var(--bg-white)", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)", padding: "4px" }}>
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`nav-tab ${activeTab === tab.id ? "active" : ""}`}
                onClick={() => setActiveTab(tab.id)}
                style={{ padding: "var(--space-2) var(--space-4)", borderRadius: "var(--radius-md)" }}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          {/* Tab Content Panel */}
          <div className="card" style={{ minHeight: "400px" }}>
            {/* Overview Tab */}
            {activeTab === "overview" && (
              <div className="flex flex-col gap-4">
                <h3>Executive Summary</h3>
                <p className="text-body" style={{ fontSize: "16px", lineHeight: "1.6" }}>{event.summary}</p>
                
                <div className="divider" />
                
                <h3>Key Changes</h3>
                <p className="text-body">{event.change_description}</p>
                
                <div className="divider" />
                
                <h3>Scope of Impact</h3>
                <div className="flex gap-2" style={{ flexWrap: "wrap" }}>
                  {event.affected_industries.map(ind => (
                    <span key={ind} className="object-type-badge">{ind}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Evidence Tab */}
            {activeTab === "evidence" && (
              <div className="flex flex-col gap-4">
                <h3>Authoritative Evidence</h3>
                <p className="text-small">Direct source documents and coordinate citations verifying this change.</p>
                
                <div className="flex flex-col gap-4">
                  {relatedKOs.flatMap(ko => ko.evidence).map((ev, index) => (
                    <CitationCard key={ev.id || index} evidence={ev} expanded={index === 0} />
                  ))}
                </div>
              </div>
            )}

            {/* What Changed Tab */}
            {activeTab === "changed" && (
              <div className="flex flex-col gap-4">
                <h3>Regulatory Shift Analysis</h3>
                <p className="text-small">Comparison of the legal position before and after this event.</p>
                
                <div className="diff-box card" style={{ background: "var(--bg-cloud)", border: "1px dashed var(--border-strong)" }}>
                  <div style={{ display: "flex", gap: "var(--space-6)" }}>
                    <div style={{ flex: 1 }}>
                      <span className="text-meta" style={{ color: "var(--error)" }}>Previous Standard</span>
                      <p className="text-body" style={{ marginTop: "8px", textDecoration: "line-through", opacity: 0.6 }}>
                        No binding guidelines. Consent notices followed non-binding industry advisories recommending simplified three-line consent format.
                      </p>
                    </div>
                    <div style={{ width: "1px", background: "var(--border)" }} />
                    <div style={{ flex: 1 }}>
                      <span className="text-meta" style={{ color: "var(--verification-green)" }}>Current Mandate (New Standard)</span>
                      <p className="text-body" style={{ marginTop: "8px", fontWeight: "var(--fw-medium)" }}>
                        Structured consent notice listing specific items of personal data, withdrawal channels, grievance officers, and translated in 8th Schedule languages.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Impact Radius Tab */}
            {activeTab === "impact" && (
              <div className="flex flex-col gap-4">
                <h3>Impact Radius</h3>
                <p className="text-small">Systems, roles, and Knowledge Objects affected by this change.</p>
                
                <div className="flex flex-col gap-3">
                  <h4>Affected Knowledge Objects</h4>
                  {relatedKOs.map(ko => (
                    <div key={ko.urn} className="card card-compact flex items-center justify-between" style={{ flexDirection: "row" }}>
                      <div className="flex items-center gap-3">
                        <ObjectTypeBadge type={ko.type} />
                        <span style={{ fontWeight: "var(--fw-medium)" }}>{ko.title}</span>
                      </div>
                      <span className="text-meta text-mono">{ko.urn}</span>
                    </div>
                  ))}
                </div>

                <div className="divider" style={{ margin: "var(--space-2) 0" }} />

                <div className="flex gap-6">
                  <div style={{ flex: 1 }}>
                    <h4>Affected Roles</h4>
                    <ul className="flex flex-col gap-1" style={{ marginTop: "var(--space-2)" }}>
                      {event.affected_processes.map(p => (
                        <li key={p} className="text-body">• {p}</li>
                      ))}
                    </ul>
                  </div>
                  <div style={{ flex: 1 }}>
                    <h4>Operational Controls</h4>
                    <ul className="flex flex-col gap-1" style={{ marginTop: "var(--space-2)" }}>
                      <li className="text-body">• Multilingual notices (CTRL-NOTICE-002)</li>
                      <li className="text-body">• Consent management portal (CTRL-CONSENT-001)</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Conflicts Tab */}
            {activeTab === "conflicts" && (
              <div className="flex flex-col gap-4">
                <h3>Interpretive Conflicts</h3>
                <p className="text-small">Active legal disputes, deviations, or uncertainties regarding this change.</p>
                
                {eventConflicts.length === 0 ? (
                  <EmptyState title="No conflicts detected" description="There are no active legal conflicts or contradictory rules associated with this event." />
                ) : (
                  eventConflicts.map(c => (
                    <div key={c.id} className="card" style={{ borderLeft: "4px solid var(--status-conflict)" }}>
                      <div className="flex justify-between items-start" style={{ marginBottom: "var(--space-3)" }}>
                        <h4>{c.title}</h4>
                        <StatusBadge status={c.status} size="small" />
                      </div>
                      
                      <div className="grid-2" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-4)", marginBottom: "var(--space-4)" }}>
                        <div className="card card-compact" style={{ background: "var(--bg-cloud)" }}>
                          <span className="text-meta">Claim A ({c.claim_a.authority})</span>
                          <p className="text-small" style={{ fontWeight: "var(--fw-medium)", marginTop: "4px" }}>"{c.claim_a.statement}"</p>
                        </div>
                        <div className="card card-compact" style={{ background: "var(--bg-cloud)" }}>
                          <span className="text-meta">Claim B ({c.claim_b.authority})</span>
                          <p className="text-small" style={{ fontWeight: "var(--fw-medium)", marginTop: "4px" }}>"{c.claim_b.statement}"</p>
                        </div>
                      </div>

                      <p className="text-body" style={{ marginBottom: "var(--space-3)" }}>{c.explanation}</p>
                      
                      <div className="divider" style={{ marginBottom: "var(--space-3)" }} />
                      
                      <div className="text-small flex gap-4">
                        <span>Scope: <strong>{c.scope}</strong></span>
                        <span>Auditor Review: <strong>{c.reviewer} ({c.reviewer_notes})</strong></span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Decisions & Actions Tab */}
            {activeTab === "actions" && (
              <div className="flex flex-col gap-4">
                <h3>Compliance Decisions</h3>
                <p className="text-small">Decide organization applicability and assign operational responses.</p>
                
                <div className="card card-compact flex flex-col gap-4" style={{ background: "var(--bg-cloud)" }}>
                  <div className="flex justify-between items-center">
                    <span style={{ fontWeight: "var(--fw-medium)" }}>Organizational Applicability Status:</span>
                    <select 
                      className="input" 
                      value={applicability} 
                      onChange={(e) => setApplicability(e.target.value)}
                      style={{ width: "200px" }}
                    >
                      <option value="unknown">Unknown / Under Review</option>
                      <option value="applies">Applies in Full</option>
                      <option value="partial">Partially Applies</option>
                      <option value="no">Does Not Apply</option>
                    </select>
                  </div>
                  
                  <div className="flex flex-col gap-2">
                    <span className="text-meta">Decision Rationale & Assessment Notes</span>
                    <textarea 
                      className="input" 
                      rows={3} 
                      placeholder="Describe why this applies or doesn't apply to our systems, products, and services..."
                      value={rationale}
                      onChange={(e) => setRationale(e.target.value)}
                    />
                  </div>

                  <button className="btn btn-primary" onClick={handleSaveApplicability} disabled={savingApplicability} style={{ alignSelf: "flex-end" }}>
                    {savingApplicability ? "Saving to Git Ledger..." : "Commit Decision & Rationale"}
                  </button>
                </div>

                <div className="divider" style={{ margin: "var(--space-2) 0" }} />

                <h3>Assigned Response Actions</h3>
                <div className="flex flex-col gap-3">
                  {eventActions.map(action => (
                    <div key={action.id} className="card card-compact flex items-center justify-between" style={{ flexDirection: "row" }}>
                      <div>
                        <div style={{ fontWeight: "var(--fw-medium)" }}>{action.title}</div>
                        <span className="text-small">Owner: {action.owner} • Due: {action.due_date}</span>
                      </div>
                      <div className="flex gap-2">
                        <PriorityBadge priority={action.priority} />
                        <StatusBadge status={action.status} size="small" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* History Tab */}
            {activeTab === "history" && (
              <div className="flex flex-col gap-4">
                <h3>Event Lifecycle & Audit History</h3>
                <p className="text-small">Immutable timeline tracking how this change was indexed, verified, and published.</p>
                
                <div className="timeline-mini" style={{ paddingLeft: "var(--space-4)", borderLeft: "2px solid var(--border)" }}>
                  <div className="timeline-mini-item" style={{ marginBottom: "var(--space-4)", position: "relative" }}>
                    <div style={{ position: "absolute", left: "-21px", top: "4px", width: "10px", height: "10px", borderRadius: "50%", background: "var(--verification-green)" }} />
                    <div className="text-meta">Stage 8: Published to Graph</div>
                    <div className="text-body" style={{ fontWeight: "var(--fw-medium)" }}>Committed to database and Git Ledger ledger index</div>
                    <div className="text-small">By: Publishing Agent • Date: {event.date_published}</div>
                  </div>
                  <div className="timeline-mini-item" style={{ marginBottom: "var(--space-4)", position: "relative" }}>
                    <div style={{ position: "absolute", left: "-21px", top: "4px", width: "10px", height: "10px", borderRadius: "50%", background: "var(--assurance-teal)" }} />
                    <div className="text-meta">Stage 2: Verification & Citation</div>
                    <div className="text-body">Evidence citation coordinate packets created and signed</div>
                    <div className="text-small">By: Citation Agent • Date: {event.date_detected}</div>
                  </div>
                  <div className="timeline-mini-item" style={{ position: "relative" }}>
                    <div style={{ position: "absolute", left: "-21px", top: "4px", width: "10px", height: "10px", borderRadius: "50%", background: "var(--signal-gold)" }} />
                    <div className="text-meta">Stage 1: Scout / Ingestion</div>
                    <div className="text-body">Regulatory signal discovered and registered in incoming queue</div>
                    <div className="text-small">By: Scout Agent • Date: {event.date_detected}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Sticky Panel */}
        <div className="flex flex-col gap-6" style={{ position: "sticky", top: "var(--space-6)" }}>
          <div className="card flex flex-col gap-4">
            <h4>Workspace Metrics</h4>
            
            <div className="flex flex-col gap-3">
              <div>
                <span className="text-meta">Effective Countdown</span>
                <div style={{ fontSize: "24px", fontWeight: "var(--fw-semibold)", color: "var(--text-primary)", marginTop: "4px" }}>
                  Active
                </div>
              </div>

              <div className="divider" />

              <div>
                <span className="text-meta">Multi-Dimensional Trust</span>
                <div style={{ marginTop: "8px" }}>
                  <TrustIndicator trust={{
                    source_authority: 0.95,
                    source_integrity: 0.92,
                    citation_integrity: 0.90,
                    extraction_quality: 0.88,
                    interpretation_confidence: 0.85,
                    human_review: "approved",
                    freshness: 0.90
                  }} />
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
