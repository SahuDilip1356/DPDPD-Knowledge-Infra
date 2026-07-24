import React, { useState } from "react";

export default function BusinessActions({ actionItems }) {
  const [selectedRole, setSelectedRole] = useState("All");
  const [selectedPriority, setSelectedPriority] = useState("All");
  const [checkedIds, setCheckedIds] = useState({});

  // Gather unique roles
  const allRoles = ["All", ...new Set(actionItems.flatMap((item) => item.affected_roles))];
  const allPriorities = ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"];

  const toggleCheck = (id) => {
    setCheckedIds((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const filteredActions = actionItems.filter((action) => {
    const roleMatch = selectedRole === "All" || action.affected_roles.includes(selectedRole);
    const priorityMatch = selectedPriority === "All" || action.priority === selectedPriority;
    return roleMatch && priorityMatch;
  });

  return (
    <div className="glass-panel" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div style={{ textAlign: "left" }}>
        <h2 style={{ fontFamily: "var(--font-heading)" }}>Compliance Business Actions</h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "1rem" }}>
          Legal obligations parsed by Department 7 (Business Translation) and mapped directly to organizational roles.
        </p>
      </div>

      {/* Filters */}
      <div className="checklist-filters">
        <select
          className="filter-select"
          value={selectedRole}
          onChange={(e) => setSelectedRole(e.target.value)}
        >
          {allRoles.map((role) => (
            <option key={role} value={role}>
              Role: {role}
            </option>
          ))}
        </select>

        <select
          className="filter-select"
          value={selectedPriority}
          onChange={(e) => setSelectedPriority(e.target.value)}
        >
          {allPriorities.map((pri) => (
            <option key={pri} value={pri}>
              Priority: {pri}
            </option>
          ))}
        </select>
      </div>

      {/* Checklist List */}
      <div className="action-items-list">
        {filteredActions.length > 0 ? (
          filteredActions.map((action, idx) => {
            const key = `${action.urn}-${idx}`;
            const isCompleted = !!checkedIds[key];
            return (
              <div key={key} className={`action-item-row ${isCompleted ? "completed" : ""}`} style={{ opacity: isCompleted ? 0.6 : 1 }}>
                <input
                  type="checkbox"
                  className="action-checkbox"
                  checked={isCompleted}
                  onChange={() => toggleCheck(key)}
                />
                <div className="action-content">
                  <div className="action-title-row">
                    <div style={{ fontWeight: 600, fontSize: "0.95rem", textDecoration: isCompleted ? "line-through" : "none" }}>
                      {action.ko_title}
                    </div>
                    <div className="action-label-tags">
                      <span className={`priority-tag ${action.priority.toLowerCase()}`}>
                        {action.priority}
                      </span>
                      <span className="priority-tag" style={{ background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-color)", color: "var(--text-secondary)" }}>
                        {action.deadline_category.split(" ")[0]}
                      </span>
                    </div>
                  </div>
                  <div className="action-desc" style={{ textDecoration: isCompleted ? "line-through" : "none" }}>
                    {action.action_description}
                  </div>
                  <div className="action-roles">
                    {action.affected_roles.map((role) => (
                      <span key={role} className="role-badge">
                        {role}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div style={{ padding: "4rem", color: "var(--text-muted)", textAlign: "center" }}>
            No compliance actions match the selected filters.
          </div>
        )}
      </div>
    </div>
  );
}
