import React from "react";

/* ═══════════════════════════════════════════════════════════════════
   SHARED UI COMPONENTS
   Regulatory Knowledge Infrastructure — Design System §28
   ═══════════════════════════════════════════════════════════════════ */

/* ── Status Badge (§24 + §28.2) ───────────────────────────────── */
const STATUS_CONFIG = {
  active:       { label: "Active",       icon: "●", className: "badge-active" },
  draft:        { label: "Draft",        icon: "◌", className: "badge-draft" },
  under_review: { label: "Under Review", icon: "◎", className: "badge-review" },
  qualified:    { label: "Qualified",    icon: "◉", className: "badge-review" },
  conflicted:   { label: "Conflicted",   icon: "⚠", className: "badge-conflict" },
  superseded:   { label: "Superseded",   icon: "⊘", className: "badge-superseded" },
  obsolete:     { label: "Obsolete",     icon: "⊗", className: "badge-superseded" },
  rejected:     { label: "Rejected",     icon: "✕", className: "badge-conflict" },
  // Evidence statuses
  verified:                { label: "Verified",             icon: "✓", className: "badge-active" },
  pending_verification:    { label: "Pending Verification", icon: "◎", className: "badge-review" },
  extraction_incomplete:   { label: "Extraction Incomplete",icon: "◌", className: "badge-draft" },
  source_unavailable:      { label: "Source Unavailable",   icon: "✕", className: "badge-conflict" },
  integrity_mismatch:      { label: "Integrity Mismatch",   icon: "⚠", className: "badge-conflict" },
  // Review statuses
  approved:                    { label: "Approved",                  icon: "✓", className: "badge-active" },
  approved_with_qualification: { label: "Approved with Qualification", icon: "◉", className: "badge-review" },
  pending:                     { label: "Pending Review",            icon: "◎", className: "badge-review" },
  changes_requested:           { label: "Changes Requested",        icon: "↻", className: "badge-review" },
  // Action statuses
  proposed:           { label: "Proposed",         icon: "◌", className: "badge-draft" },
  applicability_review: { label: "Applicability Review", icon: "◎", className: "badge-review" },
  accepted:           { label: "Accepted",         icon: "●", className: "badge-active" },
  in_progress:        { label: "In Progress",      icon: "▶", className: "badge-active" },
  blocked:            { label: "Blocked",          icon: "⊘", className: "badge-conflict" },
  ready_for_review:   { label: "Ready for Review", icon: "◉", className: "badge-review" },
  completed:          { label: "Completed",        icon: "✓", className: "badge-active" },
  not_applicable:     { label: "Not Applicable",   icon: "—", className: "badge-superseded" },
};

export function StatusBadge({ status, size = "default" }) {
  const config = STATUS_CONFIG[status] || { label: status, icon: "?", className: "badge-draft" };
  return (
    <span className={`status-badge ${config.className} ${size === "small" ? "badge-sm" : ""}`}>
      <span className="badge-icon" aria-hidden="true">{config.icon}</span>
      {config.label}
    </span>
  );
}

/* ── Priority Badge ───────────────────────────────────────────── */
export function PriorityBadge({ priority, showDot = true }) {
  const configs = {
    critical: { label: "CRITICAL", bg: "#FEF2F2", text: "#991B1B", border: "#FCA5A5", dot: "#DC2626" },
    high:     { label: "HIGH",     bg: "#FFF7ED", text: "#92400E", border: "#FDBA74", dot: "#EA580C" },
    medium:   { label: "MEDIUM",   bg: "#EFF6FF", text: "#1E40AF", border: "#93C5FD", dot: "#2563EB" },
    low:      { label: "LOW",      bg: "#F8FAFC", text: "#475569", border: "#CBD5E1", dot: "#64748B" },
  };
  const config = configs[priority] || configs.low;

  return (
    <span
      className="priority-badge"
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "5px",
        padding: "3px 9px",
        borderRadius: "9999px",
        fontSize: "10px",
        fontWeight: 800,
        letterSpacing: "0.06em",
        background: config.bg,
        color: config.text,
        border: `1px solid ${config.border}`,
        whiteSpace: "nowrap",
        boxShadow: "0 1px 2px rgba(0,0,0,0.03)"
      }}
    >
      {showDot && (
        <span
          style={{
            width: "5px",
            height: "5px",
            borderRadius: "50%",
            background: config.dot,
            boxShadow: priority === "critical" ? "0 0 6px rgba(220, 38, 38, 0.6)" : "none"
          }}
        />
      )}
      <span>{config.label}</span>
    </span>
  );
}

/* ── Object Type Icon (§7 — Constitutional Nouns) ─────────────── */
const TYPE_ICONS = {
  Act:           { icon: "📜", color: "#121A2E" },
  Rule:          { icon: "📋", color: "#07B981" },
  Notification:  { icon: "📢", color: "#E8AB42" },
  Circular:      { icon: "📄", color: "#35B6AE" },
  Case:          { icon: "⚖️", color: "#7C3AED" },
  Judgement:     { icon: "🔨", color: "#7C3AED" },
  Opinion:       { icon: "💬", color: "#64748B" },
  Template:      { icon: "📝", color: "#0EA5E9" },
  Control:       { icon: "🛡️", color: "#F59E0B" },
  Risk:          { icon: "⚠️", color: "#EF4444" },
  Organization:  { icon: "🏢", color: "#6366F1" },
  Authority:     { icon: "🏛️", color: "#121A2E" },
};

export function ObjectTypeIcon({ type, size = 20 }) {
  const config = TYPE_ICONS[type] || { icon: "📎", color: "#64748B" };
  return (
    <span
      className="object-type-icon"
      style={{ fontSize: size, lineHeight: 1 }}
      title={type}
      aria-label={type}
    >
      {config.icon}
    </span>
  );
}

export function ObjectTypeBadge({ type }) {
  return (
    <span className="object-type-badge">
      <ObjectTypeIcon type={type} size={14} />
      <span>{type}</span>
    </span>
  );
}

/* ── Trust Indicator (§25 — Multi-dimensional) ────────────────── */
export function TrustIndicator({ trust, compact = false }) {
  if (!trust) return <span className="text-small" style={{ color: "var(--text-muted)" }}>No trust data</span>;

  const dimensions = [
    { key: "source_authority",           label: "Source Authority",  value: trust.source_authority },
    { key: "citation_integrity",         label: "Citation Integrity", value: trust.citation_integrity },
    { key: "extraction_quality",         label: "Extraction Quality", value: trust.extraction_quality },
    { key: "interpretation_confidence",  label: "Interpretation",    value: trust.interpretation_confidence },
    { key: "freshness",                  label: "Freshness",         value: trust.freshness },
  ];

  const reviewLabel = trust.human_review === "approved" ? "Approved"
    : trust.human_review === "approved_with_qualification" ? "Qualified"
    : trust.human_review === "pending" ? "Pending"
    : trust.human_review || "Unknown";

  if (compact) {
    const avg = dimensions.reduce((s, d) => s + d.value, 0) / dimensions.length;
    return (
      <span className="trust-compact" title={`Trust: ${(avg * 100).toFixed(0)}% — Review: ${reviewLabel}`}>
        <span className={`trust-dot trust-${avg >= 0.85 ? "high" : avg >= 0.6 ? "med" : "low"}`} />
        <span className="text-small">{reviewLabel}</span>
      </span>
    );
  }

  return (
    <div className="trust-indicator">
      <div className="trust-dimensions">
        {dimensions.map(d => (
          <div key={d.key} className="trust-row">
            <span className="trust-label">{d.label}</span>
            <div className="trust-bar-track">
              <div
                className={`trust-bar-fill trust-${d.value >= 0.85 ? "high" : d.value >= 0.6 ? "med" : "low"}`}
                style={{ width: `${d.value * 100}%` }}
              />
            </div>
            <span className="trust-value">{(d.value * 100).toFixed(0)}%</span>
          </div>
        ))}
      </div>
      <div className="trust-review-row">
        <span className="trust-label">Human Review</span>
        <StatusBadge status={trust.human_review} size="small" />
      </div>
    </div>
  );
}

/* ── Citation Card (§28.5) ────────────────────────────────────── */
export function CitationCard({ evidence, expanded = false }) {
  const [isExpanded, setIsExpanded] = React.useState(expanded);

  if (!evidence) return null;

  const locationText = evidence.coordinates?.page 
    ? `Page ${evidence.coordinates.page}${evidence.coordinates.section ? `, Sec ${evidence.coordinates.section}` : ""}`
    : evidence.coordinates?.section 
      ? `Section: ${evidence.coordinates.section}`
      : "Primary Source";

  return (
    <div className={`citation-card ${isExpanded ? "citation-expanded" : ""}`} style={{ border: "1px solid var(--border)", borderRadius: "10px", overflow: "hidden", background: "#FFFFFF", boxShadow: "0 2px 6px rgba(0,0,0,0.02)" }}>
      <button 
        className="citation-header" 
        onClick={() => setIsExpanded(!isExpanded)}
        style={{ width: "100%", padding: "12px 14px", background: "#F8FAFC", display: "flex", justifyContent: "space-between", alignItems: "center", border: "none", cursor: "pointer" }}
      >
        <div className="citation-source" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <StatusBadge status={evidence.verification_status || "verified"} size="small" />
          <span style={{ fontWeight: 700, color: "var(--brand-navy)", fontSize: "13px" }}>
            {evidence.source_name || evidence.source_urn || "Verified Evidence Citation"}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--brand-slate)", background: "#FFFFFF", padding: "2px 8px", borderRadius: "4px", border: "1px solid #CBD5E1" }}>
            {locationText}
          </span>
          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>{isExpanded ? "▲" : "▼"}</span>
        </div>
      </button>
      {isExpanded && (
        <div className="citation-body" style={{ padding: "16px", background: "#FFFFFF", borderTop: "1px solid #E2E8F0" }}>
          <blockquote className="citation-text" style={{ fontStyle: "italic", fontSize: "13px", color: "var(--brand-navy)", lineHeight: 1.6, paddingLeft: "12px", borderLeft: "3px solid var(--brand-blue)", margin: "0 0 12px 0" }}>
            "{evidence.citation_text || "Full citation text registered in statutory ledger."}"
          </blockquote>
          <div className="citation-meta" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "11px", color: "var(--text-muted)", paddingTop: "8px", borderTop: "1px stroke #F1F5F9" }}>
            <span style={{ fontWeight: 600 }}>Source Tier: <span style={{ textTransform: "capitalize", color: "var(--brand-navy)" }}>{evidence.source_tier || "primary"}</span></span>
            {evidence.hash && (
              <span className="text-mono" title={evidence.hash} style={{ fontSize: "10px", color: "var(--text-muted)" }}>
                Ledger Hash: {evidence.hash.substring(0, 14)}…
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Time Display (§4.7) ──────────────────────────────────────── */
export function TimeDisplay({ label, date, type = "legal" }) {
  if (!date) return null;
  const typeLabels = {
    legal: "Legal effective",
    detected: "Detected",
    published: "Published to graph",
    system: "System recorded"
  };
  const formatted = new Date(date).toLocaleDateString("en-IN", {
    day: "numeric", month: "short", year: "numeric"
  });
  return (
    <div className="time-display">
      <span className="text-meta">{label || typeLabels[type] || type}</span>
      <span className="time-value">{formatted}</span>
    </div>
  );
}

/* ── Impact Level Badge ───────────────────────────────────────── */
export function ImpactBadge({ level, showDot = true }) {
  const configs = {
    critical: { label: "Critical Impact", bg: "#FEF2F2", text: "#991B1B", border: "#FCA5A5", dot: "#DC2626" },
    high:     { label: "High Impact",     bg: "#FFF7ED", text: "#92400E", border: "#FDBA74", dot: "#EA580C" },
    medium:   { label: "Medium Impact",   bg: "#EFF6FF", text: "#1E40AF", border: "#93C5FD", dot: "#2563EB" },
    low:      { label: "Low Impact",      bg: "#F8FAFC", text: "#475569", border: "#CBD5E1", dot: "#64748B" },
  };
  const config = configs[level] || configs.low;

  return (
    <span
      className="impact-badge"
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "6px",
        padding: "4px 11px",
        borderRadius: "9999px",
        fontSize: "11px",
        fontWeight: 700,
        letterSpacing: "0.02em",
        background: config.bg,
        color: config.text,
        border: `1px solid ${config.border}`,
        whiteSpace: "nowrap",
        boxShadow: "0 1px 2px rgba(0,0,0,0.03)"
      }}
    >
      {showDot && (
        <span
          style={{
            width: "6px",
            height: "6px",
            borderRadius: "50%",
            background: config.dot,
            boxShadow: level === "critical" ? "0 0 6px rgba(220, 38, 38, 0.5)" : "none"
          }}
        />
      )}
      <span>{config.label}</span>
    </span>
  );
}

/* ── Empty State (§28.7) ──────────────────────────────────────── */
export function EmptyState({ icon = "📭", title, description, action }) {
  return (
    <div className="empty-state">
      <span className="empty-icon">{icon}</span>
      <h3 className="empty-title">{title}</h3>
      {description && <p className="empty-desc">{description}</p>}
      {action && <div className="empty-action">{action}</div>}
    </div>
  );
}

/* ── Metric Card (for Command Center) ─────────────────────────── */
export function MetricCard({ label, value, change, trendLabel, icon, color = "blue", onClick }) {
  const colorMap = {
    navy:    { iconBg: "#14213D", iconColor: "#FFFFFF" },
    blue:    { iconBg: "#1A4FA3", iconColor: "#FFFFFF" },
    green:   { iconBg: "#138808", iconColor: "#FFFFFF" },
    saffron: { iconBg: "#FF9933", iconColor: "#FFFFFF" },
  };
  const theme = colorMap[color] || colorMap.blue;

  return (
    <button className="metric-card card card-compact card-interactive" onClick={onClick}>
      <div className="metric-header" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
        <span className="text-meta" style={{ fontSize: "11px", letterSpacing: "0.05em" }}>{label}</span>
        <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: theme.iconBg, color: theme.iconColor, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
          {icon}
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: "8px", marginTop: "8px" }}>
        <div className="metric-value" style={{ fontSize: "28px", fontWeight: 800, color: "var(--brand-navy)" }}>{value}</div>
        {change && (
          <span className={`metric-change ${change > 0 ? "change-up" : "change-down"}`}>
            {change > 0 ? "↑" : "↓"} {Math.abs(change)}
          </span>
        )}
      </div>
      {trendLabel && (
        <div style={{ marginTop: "6px", fontSize: "11px", color: "var(--text-muted)" }}>
          {trendLabel}
        </div>
      )}
    </button>
  );
}

/* ── Section Header ───────────────────────────────────────────── */
export function SectionHeader({ title, subtitle, action }) {
  return (
    <div className="section-header">
      <div>
        <h2>{title}</h2>
        {subtitle && <p className="text-small">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

/* ── Filter Pill ──────────────────────────────────────────────── */
export function FilterPill({ label, active, onClick }) {
  return (
    <button
      className={`filter-pill ${active ? "filter-active" : ""}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
}
