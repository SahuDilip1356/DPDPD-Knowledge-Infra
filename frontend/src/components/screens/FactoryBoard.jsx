import React, { useState } from "react";
import { FACTORY_DEPARTMENTS, PIPELINE_ITEMS } from "../../data/mockData";
import { PriorityBadge, EmptyState, StatusBadge } from "../ui/SharedComponents";

export default function FactoryBoard() {
  const [selectedItemId, setSelectedItemId] = useState(PIPELINE_ITEMS[0]?.id || "");
  const selectedItem = PIPELINE_ITEMS.find(i => i.id === selectedItemId);

  const handleApproveStage = () => {
    if (!selectedItem) return;
    if (selectedItem.current_stage >= 8) {
      alert(`Published! Committed to database and Git Ledger: ${selectedItem.title}`);
      return;
    }
    selectedItem.current_stage += 1;
    const nextDept = FACTORY_DEPARTMENTS.find(d => d.id === selectedItem.current_stage);
    selectedItem.stage_name = nextDept.name;
    alert(`Approved! Moved to next stage: ${nextDept.name}`);
    setSelectedItemId(selectedItem.id); // trigger rerender
  };

  return (
    <div className="factory-board flex flex-col gap-6">
      {/* ── Page Header ───────────────────────────────────────────── */}
      <div className="section-header">
        <div>
          <h1 className="text-display">Research Ingestion Factory</h1>
          <p className="text-small">Track regulatory documents flowing through the 8-department validation pipeline.</p>
        </div>
      </div>

      {/* ── Kanban Board Board ──────────────────────────────────────── */}
      <div className="kanban-scroll-wrapper" style={{ overflowX: "auto", paddingBottom: "var(--space-4)" }}>
        <div className="kanban-grid" style={{ display: "flex", gap: "var(--space-4)", minWidth: "1600px" }}>
          {FACTORY_DEPARTMENTS.map(dept => {
            const itemsInDept = PIPELINE_ITEMS.filter(i => i.current_stage === dept.id);
            return (
              <div 
                key={dept.id} 
                className="kanban-column flex flex-col gap-3"
                style={{
                  width: "200px",
                  background: "var(--bg-white)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-lg)",
                  padding: "var(--space-3)",
                  minHeight: "450px"
                }}
              >
                {/* Column Header */}
                <div className="column-header flex justify-between items-center" style={{ borderBottom: "1px solid var(--border)", paddingBottom: "var(--space-2)" }}>
                  <div className="flex items-center gap-2">
                    <span>{dept.icon}</span>
                    <span style={{ fontWeight: "var(--fw-semibold)", fontSize: "13px", color: "var(--text-primary)" }}>{dept.short}</span>
                  </div>
                  <span className="text-meta" style={{ fontSize: "10px", background: "var(--bg-subtle)", padding: "2px 6px", borderRadius: "var(--radius-pill)" }}>
                    {itemsInDept.length}
                  </span>
                </div>

                {/* Column Items */}
                <div className="column-items flex flex-col gap-3" style={{ flex: 1 }}>
                  {itemsInDept.length === 0 ? (
                    <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", border: "1px dashed var(--border)", borderRadius: "var(--radius-md)", opacity: 0.4 }}>
                      <span className="text-meta" style={{ fontSize: "10px" }}>Empty</span>
                    </div>
                  ) : (
                    itemsInDept.map(item => (
                      <div
                        key={item.id}
                        className={`card card-compact card-interactive flex flex-col gap-2 ${selectedItemId === item.id ? "selected-kanban-card" : ""}`}
                        onClick={() => setSelectedItemId(item.id)}
                        style={{
                          background: selectedItemId === item.id ? "var(--bg-selected)" : "var(--bg-cloud)",
                          borderColor: selectedItemId === item.id ? "var(--verification-green)" : "var(--border)",
                          padding: "var(--space-3)"
                        }}
                      >
                        <div style={{ fontSize: "11px", fontWeight: "var(--fw-medium)", color: "var(--text-primary)", lineHeight: "1.4" }} className="truncate">
                          {item.title}
                        </div>
                        <div className="flex justify-between items-center text-small" style={{ marginTop: "var(--space-2)" }}>
                          <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>{item.time_in_stage}</span>
                          <PriorityBadge priority={item.priority} />
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Detail Panel & Work Queues Split ───────────────────────── */}
      <div className="factory-detail-split" style={{ display: "grid", gridTemplateColumns: "1.2fr 2fr", gap: "var(--space-6)" }}>
        
        {/* Left pane: Ingestion Exceptions Sidebar */}
        <div className="card flex flex-col gap-4">
          <h3>Ingestion Exceptions</h3>
          <p className="text-small">Parser errors, translation failures, or network fetch issues requiring operational intervention.</p>
          
          <div className="exceptions-list flex flex-col gap-3">
            <div className="card card-compact flex flex-col gap-2" style={{ borderLeft: "4px solid var(--error)", background: "var(--status-conflict-bg)" }}>
              <div className="flex justify-between items-center">
                <span style={{ fontWeight: "var(--fw-semibold)", color: "var(--text-primary)", fontSize: "var(--text-small)" }}>Malayalam Parser Timeout</span>
                <span className="text-meta" style={{ color: "var(--error)", fontSize: "10px" }}>CRITICAL</span>
              </div>
              <p className="text-small" style={{ color: "var(--text-body)" }}>
                Failed to parse Section 14 text block. Regex parser timed out on Malayalam gazette font.
              </p>
              <div className="flex justify-between items-center text-small" style={{ marginTop: "4px" }}>
                <span>File: gazette-ml-14.pdf</span>
                <button className="btn btn-tertiary" style={{ fontSize: "11px", color: "var(--error)" }}>Manual Parse</button>
              </div>
            </div>

            <div className="card card-compact flex flex-col gap-2" style={{ borderLeft: "4px solid var(--status-review)", background: "var(--status-review-bg)" }}>
              <div className="flex justify-between items-center">
                <span style={{ fontWeight: "var(--fw-semibold)", color: "var(--text-primary)", fontSize: "var(--text-small)" }}>Ontology Mapping Exception</span>
                <span className="text-meta" style={{ color: "var(--status-review)", fontSize: "10px" }}>WARNING</span>
              </div>
              <p className="text-small" style={{ color: "var(--text-body)" }}>
                Unresolved noun match: "Subordinate Fiduciary" proposed but not found in Constitution.
              </p>
              <div className="flex justify-between items-center text-small" style={{ marginTop: "4px" }}>
                <span>Object URN: urn:ki:in:dpdp:act...</span>
                <button className="btn btn-tertiary" style={{ fontSize: "11px", color: "var(--assurance-teal)" }}>Map Synonym</button>
              </div>
            </div>
          </div>
        </div>

        {/* Right pane: Review & Action Panel */}
        <div className="card flex flex-col gap-4">
          {selectedItem ? (
            <div className="flex flex-col gap-4">
              <div className="flex justify-between items-center">
                <div>
                  <span className="text-meta">Reviewing Department: {selectedItem.stage_name}</span>
                  <h3 style={{ marginTop: "4px" }}>{selectedItem.title}</h3>
                </div>
                <PriorityBadge priority={selectedItem.priority} />
              </div>

              <div className="divider" />

              <div className="grid-2" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-4)" }}>
                <div>
                  <span className="text-meta">Source Document</span>
                  <div style={{ fontWeight: "var(--fw-medium)" }}>{selectedItem.source}</div>
                </div>
                <div>
                  <span className="text-meta">Origin Authority</span>
                  <div style={{ fontWeight: "var(--fw-medium)" }}>{selectedItem.authority}</div>
                </div>
              </div>

              {/* Extraction Auto Checks */}
              <div className="card card-compact" style={{ background: "var(--bg-cloud)" }}>
                <span className="text-meta">Programmatic Auto-Validation Checks</span>
                <div className="flex gap-4" style={{ marginTop: "var(--space-2)", flexWrap: "wrap" }}>
                  <div className="flex items-center gap-1 text-small">
                    <span>{selectedItem.auto_checks.schema_valid ? "🟢" : "🔴"}</span>
                    <span>Schema Validation</span>
                  </div>
                  <div className="flex items-center gap-1 text-small">
                    <span>{selectedItem.auto_checks.entities_resolved ? "🟢" : "🟡"}</span>
                    <span>Ontology Nouns Resolved</span>
                  </div>
                  <div className="flex items-center gap-1 text-small">
                    <span>{selectedItem.auto_checks.duplicates_checked ? "🟢" : "🟡"}</span>
                    <span>De-duplication Scanned</span>
                  </div>
                </div>
              </div>

              {/* Workspace Action Buttons */}
              <div className="flex justify-between items-center" style={{ marginTop: "var(--space-4)" }}>
                <button className="btn btn-secondary" style={{ borderColor: "var(--error)", color: "var(--error)" }}>
                  ✕ Return / Reject Stage
                </button>
                <button className="btn btn-primary" onClick={handleApproveStage}>
                  ✓ Approve & Advance Stage
                </button>
              </div>
            </div>
          ) : (
            <EmptyState title="Select a pipeline item" description="Select an active ingestion task from the board to perform validation checks, assign ontology synonyms, or approve publication." />
          )}
        </div>

      </div>
    </div>
  );
}
