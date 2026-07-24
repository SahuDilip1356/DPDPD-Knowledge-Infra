import React, { useState } from "react";

export default function GraphExplorer({ knowledgeObjects }) {
  const [selectedUrn, setSelectedUrn] = useState(
    knowledgeObjects.length > 0 ? knowledgeObjects[0].urn : null
  );
  const [searchTerm, setSearchTerm] = useState("");

  const selectedKo = knowledgeObjects.find((ko) => ko.urn === selectedUrn);

  const filteredKos = knowledgeObjects.filter(
    (ko) =>
      ko.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ko.urn.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="glass-panel explorer-grid">
      {/* Sidebar List */}
      <div className="explorer-sidebar">
        <input
          type="text"
          placeholder="Search objects..."
          className="search-bar"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <div className="node-list">
          {filteredKos.map((ko) => (
            <div
              key={ko.urn}
              className={`node-card ${selectedUrn === ko.urn ? "active" : ""}`}
              onClick={() => setSelectedUrn(ko.urn)}
            >
              <div className="node-title">{ko.title}</div>
              <div className="node-meta">
                <span className="node-type-tag">{ko.urn.split(":")[4].toUpperCase()}</span>
                <span>v{ko.version}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Detail Area */}
      <div className="explorer-detail">
        {selectedKo ? (
          <div>
            <div className="detail-header">
              <div className="detail-title">{selectedKo.title}</div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem", color: "var(--info-color)" }}>
                {selectedKo.urn}
              </div>
            </div>

            <div className="detail-grid">
              <div className="detail-stat">
                <div className="stat-label">Version</div>
                <div className="stat-value">v{selectedKo.version}</div>
              </div>
              <div className="stat-stat detail-stat">
                <div className="stat-label">Legal Time Start</div>
                <div className="stat-value">{selectedKo.date}</div>
              </div>
              <div className="stat-stat detail-stat">
                <div className="stat-label">Confidence Score</div>
                <div className="stat-value" style={{ color: "var(--accent-color)" }}>
                  {selectedKo.confidence_score * 100}%
                </div>
              </div>
            </div>

            <div className="detail-section">
              <div className="section-title">Summary</div>
              <p style={{ lineHeight: "1.5", color: "var(--text-secondary)", fontSize: "0.95rem" }}>
                {selectedKo.summary}
              </p>
            </div>

            {selectedKo.entities && selectedKo.entities.length > 0 && (
              <div className="detail-section">
                <div className="section-title">Constitutional Nouns</div>
                <div className="action-roles">
                  {selectedKo.entities.map((ent, idx) => (
                    <span key={idx} className="role-badge" style={{ borderColor: "var(--accent-border)", color: "var(--accent-color)" }}>
                      {ent}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {selectedKo.relations && selectedKo.relations.length > 0 && (
              <div className="detail-section">
                <div className="section-title">Graph Edge Connections (Relations)</div>
                <div>
                  {selectedKo.relations.map((rel, idx) => (
                    <div key={idx} className="relation-badge">
                      <span style={{ color: "var(--info-color)" }}>{selectedKo.urn.split(":")[5]}</span>
                      <span className="relation-arrow">──[{rel.edge_type}]──&gt;</span>
                      <span>{rel.target_urn.split(":")[5] || rel.target_urn}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedKo.evidence && selectedKo.evidence.length > 0 && (
              <div className="detail-section">
                <div className="section-title">Evidence coordinate index</div>
                <div>
                  {selectedKo.evidence.map((ev, idx) => (
                    <div key={idx} className="citation-item" style={{ background: "rgba(255,255,255,0.01)" }}>
                      <div className="citation-meta">
                        <span style={{ color: "var(--text-primary)" }}>{ev.source_urn}</span>
                        <span style={{ color: "var(--text-muted)" }}>Page {ev.coordinates?.page}, Sec {ev.coordinates?.section}</span>
                      </div>
                      <div className="citation-text">"{ev.citation_text}"</div>
                      <div style={{ fontSize: "0.7rem", fontFamily: "var(--font-mono)", color: "var(--text-muted)", marginTop: "0.25rem" }}>
                        SHA-256 Checksum: {ev.coordinates?.hash}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedKo.business_impact && (
              <div className="detail-section" style={{ borderTop: "1px solid var(--border-color)", paddingTop: "1.5rem" }}>
                <div className="section-title" style={{ color: "var(--warning-color)" }}>Translated Business Impact</div>
                <div className="citation-item" style={{ background: "rgba(245, 158, 11, 0.02)", borderColor: "rgba(245, 158, 11, 0.2)" }}>
                  <div style={{ fontWeight: 600, marginBottom: "0.5rem", color: "var(--text-primary)" }}>
                    {selectedKo.business_impact.impact_summary}
                  </div>
                  <div style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}>
                    <span style={{ fontWeight: 600, color: "var(--warning-color)" }}>Action Required: </span>
                    {selectedKo.business_impact.action_required}
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ padding: "4rem", color: "var(--text-muted)", textAlign: "center" }}>
            Select a Knowledge Object to view details.
          </div>
        )}
      </div>
    </div>
  );
}
