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
const PRIORITY_CONFIG = {
  critical: { label: "Critical", className: "priority-critical" },
  high:     { label: "High",     className: "priority-high" },
  medium:   { label: "Medium",   className: "priority-medium" },
  low:      { label: "Low",      className: "priority-low" },
};

export function PriorityBadge({ priority }) {
  const config = PRIORITY_CONFIG[priority] || { label: priority, className: "priority-low" };
  return <span className={`priority-badge ${config.className}`}>{config.label}</span>;
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

  return (
    <div className={`citation-card ${isExpanded ? "citation-expanded" : ""}`}>
      <button className="citation-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="citation-source">
          <StatusBadge status={evidence.verification_status} size="small" />
          <span className="text-small">{evidence.source_name || evidence.source_urn}</span>
        </div>
        <span className="text-meta">
          p.{evidence.coordinates?.page}, {evidence.coordinates?.section}
        </span>
      </button>
      {isExpanded && (
        <div className="citation-body">
          <blockquote className="citation-text">"{evidence.citation_text}"</blockquote>
          <div className="citation-meta">
            <span className="text-meta">Source Tier: {evidence.source_tier || "primary"}</span>
            <span className="text-mono citation-hash" title={evidence.hash}>
              Hash: {evidence.hash?.substring(0, 12)}…
            </span>
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
const IMPACT_CONFIG = {
  critical: { label: "Critical Impact", className: "impact-critical" },
  high:     { label: "High Impact",     className: "impact-high" },
  medium:   { label: "Medium Impact",   className: "impact-medium" },
  low:      { label: "Low Impact",      className: "impact-low" },
};

export function ImpactBadge({ level }) {
  const config = IMPACT_CONFIG[level] || { label: level, className: "impact-low" };
  return <span className={`impact-badge ${config.className}`}>{config.label}</span>;
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
export function MetricCard({ label, value, change, icon, onClick }) {
  return (
    <button className="metric-card card card-compact card-interactive" onClick={onClick}>
      <div className="metric-header">
        <span className="metric-icon">{icon}</span>
        <span className="text-meta">{label}</span>
      </div>
      <div className="metric-value">{value}</div>
      {change && <span className={`metric-change ${change > 0 ? "change-up" : "change-down"}`}>
        {change > 0 ? "↑" : "↓"} {Math.abs(change)}
      </span>}
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
