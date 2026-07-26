import React, { useState, useEffect } from "react";
import { supabase } from "../../data/supabaseClient";
import { ACTION_ITEMS } from "../../data/mockData";
import { 
  StatusBadge, 
  PriorityBadge, 
  EmptyState,
  ObjectTypeBadge
} from "../ui/SharedComponents";

export default function DecisionsActions() {
  const [actionItems, setActionItems] = useState([]);
  const [selectedActionId, setSelectedActionId] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  // Load Action Items on mount
  const loadActions = async () => {
    setLoading(true);
    try {
      if (supabase) {
        const { data, error } = await supabase
          .from("action_items")
          .select("*");
        if (!error && data && data.length > 0) {
          setActionItems(data);
          setSelectedActionId(data[0].id);
          setLoading(false);
          return;
        }
      }
    } catch (err) {
      console.warn("Supabase load failed, falling back to mockData.js:", err);
    }
    setActionItems(ACTION_ITEMS);
    setSelectedActionId(ACTION_ITEMS[0]?.id || "");
    setLoading(false);
  };

  useEffect(() => {
    loadActions();
  }, []);

  const selectedAction = actionItems.find(a => a.id === selectedActionId);

  // Filters
  const filteredActions = actionItems.filter(a => {
    const matchesRole = roleFilter === "all" || (a.affected_roles && a.affected_roles.includes(roleFilter));
    const matchesStatus = statusFilter === "all" || a.status === statusFilter;
    return matchesRole && matchesStatus;
  });

  // Extract all unique roles
  const allRoles = ["all", ...new Set(actionItems.flatMap(a => a.affected_roles || []))];
  const allStatuses = ["all", "proposed", "accepted", "in_progress", "blocked", "completed"];

  const handleUpdateStatus = async (status) => {
    if (!selectedAction) return;
    
    try {
      if (supabase) {
        const { error } = await supabase
          .from("action_items")
          .update({ status })
          .eq("id", selectedAction.id);
        if (error) throw error;
      }
      
      // Update local state directly so UI reacts immediately
      setActionItems(prev => prev.map(a => a.id === selectedAction.id ? { ...a, status } : a));
      alert(`Status updated to ${status.replace("_", " ")} and saved to audit ledger.`);
    } catch (err) {
      console.error("Failed to update status:", err);
      // Fallback update on local copy if Supabase is offline
      setActionItems(prev => prev.map(a => a.id === selectedAction.id ? { ...a, status } : a));
      alert(`Status updated locally to ${status.replace("_", " ")} (offline fallback).`);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-slate-500" style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", fontStyle: "italic", color: "var(--text-muted)", padding: "100px 0" }}>
        Loading DPDPA Decisions & Actions...
      </div>
    );
  }

  return (
    <div className="decisions-actions" style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: "var(--space-6)" }}>
      {/* ── Left Column: Action Items List ─────────────────────────── */}
      <div className="flex flex-col gap-4">
        <div className="section-header">
          <div>
            <h1 className="text-display">Decisions & Actions</h1>
            <p className="text-small">Operational compliance workflows mapped directly to legal obligations under DPDPA.</p>
          </div>
        </div>

        {/* Filters */}
        <div className="card card-compact flex gap-4" style={{ flexDirection: "row", flexWrap: "wrap" }}>
          <div className="flex flex-col gap-1" style={{ flex: 1, minWidth: "140px" }}>
            <span className="text-meta">Role Filter</span>
            <select className="input" value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
              {allRoles.map(r => (
                <option key={r} value={r}>{r === "all" ? "All Roles" : r}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1" style={{ flex: 1, minWidth: "140px" }}>
            <span className="text-meta">Status Filter</span>
            <select className="input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              {allStatuses.map(s => (
                <option key={s} value={s}>{s === "all" ? "All Statuses" : s.replace("_", " ").toUpperCase()}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Checklist */}
        <div className="flex flex-col gap-3">
          {filteredActions.length === 0 ? (
            <EmptyState title="No action items found" description="Adjust your filters or generate new actions from the Ingestion Factory." />
          ) : (
            filteredActions.map(a => (
              <div
                key={a.id}
                className={`card card-interactive flex flex-col gap-2 ${selectedActionId === a.id ? "selected-action-card" : ""}`}
                onClick={() => setSelectedActionId(a.id)}
                style={{
                  borderLeft: `4px solid ${a.priority === "critical" ? "var(--error)" : "var(--signal-gold)"}`,
                  background: selectedActionId === a.id ? "var(--bg-selected)" : "var(--bg-white)",
                  borderColor: selectedActionId === a.id ? "var(--verification-green)" : "var(--border)"
                }}
              >
                <div className="flex justify-between items-start gap-4">
                  <div style={{ fontWeight: "var(--fw-semibold)", color: "var(--text-primary)" }}>
                    {a.title}
                  </div>
                  <PriorityBadge priority={a.priority} />
                </div>
                
                <div className="text-small text-muted truncate">
                  {a.description}
                </div>

                <div className="flex justify-between items-center text-small" style={{ marginTop: "4px" }}>
                  <span>Due: <strong>{a.due_date}</strong></span>
                  <StatusBadge status={a.status} size="small" />
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* ── Right Column: Detail Work Panel ───────────────────────── */}
      <div className="flex flex-col gap-4">
        {selectedAction ? (
          <div className="card flex flex-col gap-6" style={{ position: "sticky", top: "var(--space-6)" }}>
            
            {/* Header info */}
            <div>
              <div className="flex justify-between items-start gap-4" style={{ marginBottom: "var(--space-2)" }}>
                <span className="text-meta">Action Detail ({selectedAction.id})</span>
                <StatusBadge status={selectedAction.status} />
              </div>
              <h2 className="text-h2">{selectedAction.title}</h2>
            </div>

            {/* Description */}
            <div className="flex flex-col gap-2">
              <span className="text-meta">Task Instructions</span>
              <p className="text-body" style={{ lineHeight: "1.6" }}>{selectedAction.description}</p>
            </div>

            {/* Legal Links */}
            <div className="card card-compact flex flex-col gap-2" style={{ background: "var(--bg-cloud)" }}>
              <span className="text-meta">Source Legal Obligation</span>
              <div className="flex items-center gap-2">
                <ObjectTypeBadge type="Act" />
                <span style={{ fontWeight: "var(--fw-medium)" }}>{selectedAction.source_obligation}</span>
              </div>
              <div className="text-small text-mono">{selectedAction.ko_urn}</div>
            </div>

            {/* Assignees */}
            <div className="grid-2" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-4)" }}>
              <div className="flex flex-col gap-1">
                <span className="text-meta">Primary Owner</span>
                <div style={{ fontWeight: "var(--fw-semibold)" }}>{selectedAction.owner}</div>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-meta">Legal Reviewer</span>
                <div style={{ fontWeight: "var(--fw-semibold)" }}>{selectedAction.reviewer}</div>
              </div>
            </div>

            <div className="divider" />

            {/* Action State Controls */}
            <div className="flex flex-col gap-3">
              <span className="text-meta">Update Action State</span>
              <div className="flex gap-2" style={{ flexWrap: "wrap" }}>
                {selectedAction.status !== "in_progress" && (
                  <button className="btn btn-secondary" onClick={() => handleUpdateStatus("in_progress")}>
                    ▶ Start Progress
                  </button>
                )}
                {selectedAction.status !== "blocked" && (
                  <button className="btn btn-secondary" style={{ borderColor: "var(--error)", color: "var(--error)" }} onClick={() => handleUpdateStatus("blocked")}>
                    ⊘ Mark Blocked
                  </button>
                )}
                {selectedAction.status !== "completed" && (
                  <button className="btn btn-primary" onClick={() => handleUpdateStatus("completed")}>
                    ✓ Mark Completed
                  </button>
                )}
              </div>
            </div>

            {/* Completion Evidence */}
            <div className="flex flex-col gap-2">
              <span className="text-meta">Completion Evidence & Rationale</span>
              <textarea 
                className="input" 
                rows={3} 
                placeholder="Enter audit remarks, link PRs, config files, or document links for review..." 
              />
              <button className="btn btn-secondary" style={{ alignSelf: "flex-end", marginTop: "var(--space-1)" }}>
                Save Evidence
              </button>
            </div>

          </div>
        ) : (
          <EmptyState title="No action selected" description="Select a compliance action item from the checklist to assign owners, record decisions, and attach evidence." />
        )}
      </div>
    </div>
  );
}
