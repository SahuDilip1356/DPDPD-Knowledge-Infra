import React, { useState } from "react";
import { FACTORY_DEPARTMENTS, PIPELINE_ITEMS } from "../../data/mockData";
import { PriorityBadge, EmptyState } from "../ui/SharedComponents";

export default function FactoryBoard({ user, onSignInClick }) {
  const [selectedItemId, setSelectedItemId] = useState(PIPELINE_ITEMS[0]?.id || "");
  const [selectedPriority, setSelectedPriority] = useState("all");
  const selectedItem = PIPELINE_ITEMS.find(i => i.id === selectedItemId);

  const handleApproveStage = () => {
    if (!selectedItem) return;
    if (!user) {
      alert("⚠️ Access Denied: You must be logged in as an administrator to approve and advance stages in the Ingestion pipeline.");
      onSignInClick();
      return;
    }
    if (selectedItem.current_stage >= 8) {
      alert(`Published! Committed to database and Git Ledger: ${selectedItem.title}`);
      return;
    }
    selectedItem.current_stage += 1;
    const nextDept = FACTORY_DEPARTMENTS.find(d => d.id === selectedItem.current_stage);
    selectedItem.stage_name = nextDept.name;
    alert(`Approved! Moved to next stage: ${nextDept.name}`);
    setSelectedItemId(selectedItem.id);
  };

  // Filter items by priority if selected
  const filteredPipelineItems = PIPELINE_ITEMS.filter(item => {
    if (selectedPriority !== "all" && item.priority !== selectedPriority) return false;
    return true;
  });

  // Stage theme configurations
  const STAGE_THEMES = [
    { id: 1, color: "#14213D", lightBg: "#F0F4F8", border: "#CBD5E1", icon: "🔍" },
    { id: 2, color: "#1A4FA3", lightBg: "#EFF6FF", border: "#BFDBFE", icon: "✅" },
    { id: 3, color: "#0D9488", lightBg: "#F0FDFA", border: "#99F6E4", icon: "🏗️" },
    { id: 4, color: "#4F46E5", lightBg: "#EEF2FF", border: "#C7D2FE", icon: "📚" },
    { id: 5, color: "#7C3AED", lightBg: "#F5F3FF", border: "#DDD6FE", icon: "🔗" },
    { id: 6, color: "#059669", lightBg: "#ECFDF5", border: "#A7F3D0", icon: "🧠" },
    { id: 7, color: "#D97706", lightBg: "#FFFBEB", border: "#FDE68A", icon: "🔬" },
    { id: 8, color: "#138808", lightBg: "#E6F4E8", border: "#86EFAC", icon: "⚡" },
  ];

  return (
    <div className="factory-board flex flex-col gap-6" style={{ paddingBottom: "var(--space-8)" }}>
      {/* ── Page Header & Pipeline Telemetry ─────────────────────────── */}
      <div className="card flex flex-col gap-4" style={{ background: "linear-gradient(135deg, #14213D 0%, #0F172A 100%)", borderRadius: "16px", padding: "24px 28px", color: "#FFFFFF" }}>
        <div className="flex justify-between items-center" style={{ flexWrap: "wrap", gap: "16px" }}>
          <div>
            <div style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "4px" }}>
              <span style={{ background: "rgba(19, 136, 8, 0.25)", border: "1px solid #138808", color: "#34D399", padding: "2px 10px", borderRadius: "9999px", fontSize: "11px", fontWeight: 700, textTransform: "uppercase" }}>
                ⚡ Automated Ingestion Pipeline
              </span>
              <span style={{ background: "rgba(255, 255, 255, 0.1)", color: "rgba(255, 255, 255, 0.8)", padding: "2px 10px", borderRadius: "9999px", fontSize: "11px", fontWeight: 600 }}>
                8 Stage Legal Validation
              </span>
            </div>
            <h1 style={{ fontSize: "26px", fontWeight: 800, color: "#FFFFFF", margin: 0 }}>
              Research Ingestion Factory
            </h1>
            <p style={{ fontSize: "13px", color: "rgba(255, 255, 255, 0.75)", margin: "4px 0 0 0" }}>
              Track statutory DPDPA documents, gazette notifications, and court judgements flowing through programmatic verification.
            </p>
          </div>

          {/* Telemetry Metrics */}
          <div style={{ display: "flex", gap: "16px", background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.12)", padding: "12px 20px", borderRadius: "12px" }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "20px", fontWeight: 800, color: "#34D399" }}>{PIPELINE_ITEMS.length}</div>
              <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.6)", textTransform: "uppercase" }}>Active Docs</div>
            </div>
            <div style={{ width: "1px", background: "rgba(255,255,255,0.15)" }}></div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "20px", fontWeight: 800, color: "#60A5FA" }}>98.4%</div>
              <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.6)", textTransform: "uppercase" }}>Validation Rate</div>
            </div>
            <div style={{ width: "1px", background: "rgba(255,255,255,0.15)" }}></div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "20px", fontWeight: 800, color: "#FF9933" }}>18m</div>
              <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.6)", textTransform: "uppercase" }}>Avg Stage Time</div>
            </div>
          </div>
        </div>

        {/* Priority Filter Bar */}
        <div style={{ display: "flex", alignItems: "center", justifyBetween: "space-between", paddingTop: "12px", borderTop: "1px solid rgba(255,255,255,0.1)", marginTop: "4px" }}>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <span style={{ fontSize: "12px", color: "rgba(255,255,255,0.7)", fontWeight: 600 }}>Filter Priority:</span>
            {["all", "critical", "high", "medium", "low"].map(p => (
              <button
                key={p}
                onClick={() => setSelectedPriority(p)}
                style={{
                  padding: "3px 10px",
                  borderRadius: "9999px",
                  fontSize: "11px",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  background: selectedPriority === p ? "var(--brand-green)" : "rgba(255,255,255,0.1)",
                  color: "#FFFFFF",
                  border: selectedPriority === p ? "1px solid #34D399" : "1px solid transparent",
                  cursor: "pointer"
                }}
              >
                {p}
              </button>
            ))}
          </div>
          <span style={{ fontSize: "11px", color: "rgba(255,255,255,0.5)" }}>
            Showing {filteredPipelineItems.length} of {PIPELINE_ITEMS.length} pipeline items
          </span>
        </div>
      </div>

      {/* ── High-Contrast Kanban Pipeline ──────────────────────────── */}
      <div className="kanban-scroll-wrapper" style={{ overflowX: "auto", paddingBottom: "12px" }}>
        <div className="kanban-grid" style={{ display: "flex", gap: "16px", minWidth: "1720px" }}>
          {FACTORY_DEPARTMENTS.map(dept => {
            const itemsInDept = filteredPipelineItems.filter(i => i.current_stage === dept.id);
            const theme = STAGE_THEMES.find(t => t.id === dept.id) || STAGE_THEMES[0];

            return (
              <div 
                key={dept.id} 
                className="kanban-column flex flex-col gap-3"
                style={{
                  width: "215px",
                  background: "#FFFFFF",
                  border: `1px solid ${theme.border}`,
                  borderRadius: "14px",
                  padding: "12px",
                  minHeight: "480px",
                  boxShadow: "0 4px 14px rgba(20, 33, 61, 0.04)"
                }}
              >
                {/* Column Stage Header */}
                <div 
                  className="column-header" 
                  style={{
                    background: theme.lightBg,
                    border: `1px solid ${theme.border}`,
                    borderRadius: "10px",
                    padding: "10px 12px"
                  }}
                >
                  <div className="flex justify-between items-center">
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <span style={{ fontSize: "14px" }}>{theme.icon}</span>
                      <span style={{ fontWeight: 800, fontSize: "13px", color: theme.color }}>
                        {dept.short}
                      </span>
                    </div>
                    <span 
                      style={{ 
                        fontSize: "11px", 
                        fontWeight: 800, 
                        background: theme.color, 
                        color: "#FFFFFF", 
                        padding: "2px 7px", 
                        borderRadius: "9999px" 
                      }}
                    >
                      {itemsInDept.length}
                    </span>
                  </div>
                  <div style={{ fontSize: "10px", fontWeight: 600, color: "var(--text-muted)", marginTop: "4px" }}>
                    Stage {dept.id} of 8
                  </div>
                </div>

                {/* Column Pipeline Cards */}
                <div className="column-items flex flex-col gap-3" style={{ flex: 1 }}>
                  {itemsInDept.length === 0 ? (
                    <div 
                      style={{ 
                        flex: 1, 
                        display: "flex", 
                        flexDirection: "column",
                        alignItems: "center", 
                        justify: "center", 
                        border: "2px dashed #E2E8F0", 
                        borderRadius: "10px", 
                        background: "#F8FAFC",
                        opacity: 0.7,
                        minHeight: "120px"
                      }}
                    >
                      <span style={{ fontSize: "18px", opacity: 0.5 }}>📥</span>
                      <span style={{ fontSize: "11px", fontWeight: 600, color: "#64748B", marginTop: "4px" }}>Stage Clear</span>
                    </div>
                  ) : (
                    itemsInDept.map(item => {
                      const isSelected = selectedItemId === item.id;

                      return (
                        <div
                          key={item.id}
                          className="kanban-card card card-compact card-interactive flex flex-col gap-2"
                          onClick={() => setSelectedItemId(item.id)}
                          style={{
                            background: isSelected ? "#F0FDF4" : "#FFFFFF",
                            border: isSelected ? "2px solid #138808" : "1px solid #E2E8F0",
                            borderRadius: "10px",
                            padding: "12px",
                            boxShadow: isSelected ? "0 0 12px rgba(19, 136, 8, 0.2)" : "0 2px 6px rgba(0,0,0,0.03)",
                            transition: "all 150ms ease"
                          }}
                        >
                          {/* Item Category Badge & Priority */}
                          <div className="flex justify-between items-center" style={{ width: "100%" }}>
                            <span 
                              style={{ 
                                fontSize: "10px", 
                                fontWeight: 700, 
                                background: "#F1F5F9", 
                                color: "#334155", 
                                padding: "2px 6px", 
                                borderRadius: "4px",
                                border: "1px solid #CBD5E1"
                              }}
                            >
                              {item.authority.includes("MeitY") ? "MeitY" : item.authority.includes("Parliament") ? "Statute" : "Judicial"}
                            </span>
                            <PriorityBadge priority={item.priority} />
                          </div>

                          {/* Item Title */}
                          <div 
                            style={{ 
                              fontSize: "12px", 
                              fontWeight: 700, 
                              color: "var(--brand-navy)", 
                              lineHeight: 1.35,
                              marginTop: "2px"
                            }}
                          >
                            {item.title}
                          </div>

                          {/* Footer Info */}
                          <div className="flex justify-between items-center text-small" style={{ marginTop: "6px", paddingTop: "6px", borderTop: "1px solid #F1F5F9" }}>
                            <span style={{ fontSize: "10px", color: "var(--brand-slate)", fontWeight: 600, display: "flex", alignItems: "center", gap: "3px" }}>
                              <span>⏱</span> {item.time_in_stage}
                            </span>
                            <span style={{ fontSize: "10px", fontWeight: 700, color: item.auto_checks?.schema_valid ? "#138808" : "#DC2626" }}>
                              {item.auto_checks?.schema_valid ? "✓ Validated" : "⚠ Pending"}
                            </span>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Detail Inspection & Operational Queue Split ───────────── */}
      <div className="factory-detail-split" style={{ display: "grid", gridTemplateColumns: "1.1fr 2fr", gap: "var(--space-6)" }}>
        
        {/* Left pane: Ingestion Exceptions Panel */}
        <div className="card flex flex-col gap-4" style={{ background: "#FFFFFF", borderRadius: "14px", border: "1px solid var(--border)", boxShadow: "var(--shadow-card)" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>Ingestion Exceptions</h3>
            <span style={{ background: "#FEF2F2", border: "1px solid #FCA5A5", color: "#DC2626", fontSize: "11px", fontWeight: 700, padding: "2px 8px", borderRadius: "9999px" }}>
              2 Active Alerts
            </span>
          </div>
          <p className="text-small" style={{ margin: 0, color: "var(--brand-slate)" }}>
            Parser errors, translation timeouts, or ontology mapping mismatches requiring human intervention.
          </p>
          
          <div className="exceptions-list flex flex-col gap-3">
            <div className="card card-compact flex flex-col gap-2" style={{ borderLeft: "4px solid #DC2626", background: "#FEF2F2", borderRadius: "10px", padding: "14px" }}>
              <div className="flex justify-between items-center">
                <span style={{ fontWeight: 700, color: "#991B1B", fontSize: "13px" }}>Malayalam Parser Timeout</span>
                <span style={{ background: "#DC2626", color: "#FFFFFF", fontSize: "9px", fontWeight: 800, padding: "1px 6px", borderRadius: "4px" }}>CRITICAL</span>
              </div>
              <p className="text-small" style={{ color: "#7F1D1D", margin: 0, fontSize: "12px", lineHeight: 1.4 }}>
                Regex parser timed out on Section 14 Malayalam gazette font encoding. OCR fallback required.
              </p>
              <div className="flex justify-between items-center text-small" style={{ marginTop: "6px", paddingTop: "6px", borderTop: "1px solid rgba(220, 38, 38, 0.2)" }}>
                <span style={{ fontSize: "11px", color: "#991B1B", fontWeight: 600 }}>File: gazette-ml-14.pdf</span>
                <button className="btn btn-tertiary" style={{ fontSize: "11px", color: "#DC2626", fontWeight: 700 }}>Run Manual OCR →</button>
              </div>
            </div>

            <div className="card card-compact flex flex-col gap-2" style={{ borderLeft: "4px solid #EA580C", background: "#FFF7ED", borderRadius: "10px", padding: "14px" }}>
              <div className="flex justify-between items-center">
                <span style={{ fontWeight: 700, color: "#92400E", fontSize: "13px" }}>Ontology Noun Mapping Mismatch</span>
                <span style={{ background: "#EA580C", color: "#FFFFFF", fontSize: "9px", fontWeight: 800, padding: "1px 6px", borderRadius: "4px" }}>WARNING</span>
              </div>
              <p className="text-small" style={{ color: "#78350F", margin: 0, fontSize: "12px", lineHeight: 1.4 }}>
                Unresolved term: "Subordinate Fiduciary" extracted but missing in Constitutional Noun vocabulary.
              </p>
              <div className="flex justify-between items-center text-small" style={{ marginTop: "6px", paddingTop: "6px", borderTop: "1px solid rgba(234, 88, 12, 0.2)" }}>
                <span style={{ fontSize: "11px", color: "#92400E", fontWeight: 600 }}>URN: urn:ki:in:dpdp:act...</span>
                <button className="btn btn-tertiary" style={{ fontSize: "11px", color: "#EA580C", fontWeight: 700 }}>Map Synonym →</button>
              </div>
            </div>
          </div>
        </div>

        {/* Right pane: Review & Action Panel */}
        <div className="card flex flex-col gap-4" style={{ background: "#FFFFFF", borderRadius: "14px", border: "1px solid var(--border)", boxShadow: "var(--shadow-card)" }}>
          {selectedItem ? (
            <div className="flex flex-col gap-4">
              <div className="flex justify-between items-start">
                <div>
                  <span style={{ background: "#EFF6FF", border: "1px solid #BFDBFE", color: "#1A4FA3", padding: "3px 10px", borderRadius: "9999px", fontSize: "11px", fontWeight: 700 }}>
                    Reviewing Stage {selectedItem.current_stage} of 8: {selectedItem.stage_name}
                  </span>
                  <h3 style={{ marginTop: "8px", fontSize: "18px", fontWeight: 800, color: "var(--brand-navy)", margin: "8px 0 0 0" }}>
                    {selectedItem.title}
                  </h3>
                </div>
                <PriorityBadge priority={selectedItem.priority} />
              </div>

              <div style={{ height: "1px", background: "var(--border)" }} />

              <div className="grid-2" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div style={{ background: "#F8FAFC", padding: "12px", borderRadius: "8px", border: "1px solid #E2E8F0" }}>
                  <span className="text-meta" style={{ fontSize: "10px" }}>Source Document URN</span>
                  <div style={{ fontWeight: 700, color: "var(--brand-navy)", fontSize: "13px", marginTop: "2px" }}>{selectedItem.source}</div>
                </div>
                <div style={{ background: "#F8FAFC", padding: "12px", borderRadius: "8px", border: "1px solid #E2E8F0" }}>
                  <span className="text-meta" style={{ fontSize: "10px" }}>Originating Authority</span>
                  <div style={{ fontWeight: 700, color: "var(--brand-navy)", fontSize: "13px", marginTop: "2px" }}>{selectedItem.authority}</div>
                </div>
              </div>

              {/* Extraction Auto Checks */}
              <div className="card card-compact" style={{ background: "#F0FDF4", border: "1px solid #86EFAC", borderRadius: "10px", padding: "14px" }}>
                <span className="text-meta" style={{ color: "#166534", fontSize: "11px", fontWeight: 700 }}>Programmatic Validation Audit</span>
                <div className="flex gap-4" style={{ marginTop: "8px", flexWrap: "wrap" }}>
                  <div className="flex items-center gap-2 text-small" style={{ fontSize: "12px", color: "#14532D", fontWeight: 600 }}>
                    <span>{selectedItem.auto_checks.schema_valid ? "🟢" : "🔴"}</span>
                    <span>JSON-LD Schema Valid</span>
                  </div>
                  <div className="flex items-center gap-2 text-small" style={{ fontSize: "12px", color: "#14532D", fontWeight: 600 }}>
                    <span>{selectedItem.auto_checks.entities_resolved ? "🟢" : "🟡"}</span>
                    <span>Constitutional Nouns Mapped</span>
                  </div>
                  <div className="flex items-center gap-2 text-small" style={{ fontSize: "12px", color: "#14532D", fontWeight: 600 }}>
                    <span>{selectedItem.auto_checks.duplicates_checked ? "🟢" : "🟡"}</span>
                    <span>De-duplication Clear</span>
                  </div>
                </div>
              </div>

              {/* Workspace Action Buttons */}
              <div className="flex justify-between items-center" style={{ marginTop: "12px", paddingTop: "12px", borderTop: "1px solid var(--border)" }}>
                <button className="btn btn-secondary" style={{ borderColor: "#DC2626", color: "#DC2626", fontWeight: 700 }}>
                  ✕ Return / Reject Stage
                </button>
                <button className="btn btn-primary" onClick={handleApproveStage} style={{ padding: "10px 20px", fontSize: "13px", fontWeight: 800 }}>
                  ✓ Approve & Advance Stage →
                </button>
              </div>
            </div>
          ) : (
            <EmptyState title="Select a pipeline item" description="Select an active ingestion task from the board above to inspect auto-validation status, perform stage reviews, or approve publication." />
          )}
        </div>

      </div>
    </div>
  );
}

