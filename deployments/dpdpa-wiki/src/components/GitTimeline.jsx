import React from "react";

export default function GitTimeline({ timelineEvents }) {
  return (
    <div className="glass-panel" style={{ textAlign: "left" }}>
      <h2 style={{ fontFamily: "var(--font-heading)", marginBottom: "0.5rem" }}>Git Ledger Commits</h2>
      <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "2rem" }}>
        Chronological audit log of all updates made to the canonical Git Ledger.
        Each commit is cryptographic, signed, and maps directly to a version change in the database.
      </p>

      <div className="timeline">
        {timelineEvents.map((evt, idx) => (
          <div key={idx} className="timeline-event">
            <div className="timeline-icon">
              <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--accent-color)" }}></div>
            </div>
            <div className="timeline-card">
              <div className="timeline-meta">
                <span style={{ color: "var(--accent-color)" }}>COMMIT {evt.commit_hash || `f8b9e${idx}d`}</span>
                <span>{evt.system_time}</span>
              </div>
              <div className="timeline-msg">
                <div style={{ fontWeight: 600, marginBottom: "0.25rem" }}>
                  {evt.commit_message}
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", display: "flex", gap: "1rem" }}>
                  <span>Author ID: <code style={{ fontSize: "0.7rem", padding: "1px 4px" }}>{evt.author_id}</code></span>
                  <span>Version: <code style={{ fontSize: "0.7rem", padding: "1px 4px" }}>v{evt.version}</code></span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
