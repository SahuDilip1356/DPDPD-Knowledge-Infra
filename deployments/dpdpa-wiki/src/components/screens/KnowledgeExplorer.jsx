import React, { useState, useEffect } from "react";
import { supabase } from "../../data/supabaseClient";
import { 
  KNOWLEDGE_OBJECTS, 
  OPINIONS, 
  CONSTITUTIONAL_NOUNS, 
  getKOByUrn, 
  getOpinionsForKO 
} from "../../data/mockData";
import { 
  StatusBadge, 
  ObjectTypeBadge, 
  TrustIndicator, 
  CitationCard, 
  TimeDisplay,
  EmptyState
} from "../ui/SharedComponents";

export default function KnowledgeExplorer() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [selectedUrn, setSelectedUrn] = useState("");
  const [rightPanelTab, setRightPanelTab] = useState("relations"); // relations, trust
  const [middleTab, setMiddleTab] = useState("content"); // content, opinions
  
  // Asynchronous state for all objects loaded from DB/mock
  const [allObjects, setAllObjects] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load objects on component mount
  useEffect(() => {
    const loadObjects = async () => {
      setLoading(true);
      try {
        if (supabase) {
          const { data, error } = await supabase
            .from("knowledge_objects")
            .select("*");
          if (!error && data && data.length > 0) {
            setAllObjects(data);
            setSelectedUrn(data[0].urn);
            setLoading(false);
            return;
          }
        }
      } catch (err) {
        console.warn("Supabase load failed, falling back to mockData.js:", err);
      }
      
      // Fallback
      const combined = [...KNOWLEDGE_OBJECTS, ...OPINIONS];
      setAllObjects(combined);
      setSelectedUrn(combined[0]?.urn || "");
      setLoading(false);
    };
    
    loadObjects();
  }, []);

  const selectedKO = allObjects.find(ko => ko.urn === selectedUrn);

  const filteredKOs = allObjects.filter(ko => {
    const matchesSearch = ko.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          ko.urn.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === "all" || ko.type === filterType;
    return matchesSearch && matchesType;
  });

  // Local helper functions operating on active state objects
  const getKOByUrnLocal = (urn) => {
    return allObjects.find(k => k.urn === urn);
  };

  const getOpinionsForKOLocal = (urn) => {
    return allObjects.filter(o => o.type === "Opinion" && o.relations && o.relations.some(r => r.target_urn === urn));
  };

  // Group items by category layer
  const coreLaw = filteredKOs.filter(ko => ["Act", "Rule", "Case", "Notification"].includes(ko.type));
  const sectoralGuidance = filteredKOs.filter(ko => ["Circular"].includes(ko.type));
  const opinionLayer = filteredKOs.filter(ko => ["Opinion"].includes(ko.type));

  const uniqueTypes = ["all", ...CONSTITUTIONAL_NOUNS.filter(n => allObjects.some(ko => ko.type === n))];

  // Helper to render an item card in left list
  const renderItemCard = (ko) => (
    <button
      key={ko.urn}
      className={`card card-compact card-interactive flex flex-col gap-2 ${selectedUrn === ko.urn ? "selected-ko-card" : ""}`}
      onClick={() => {
        setSelectedUrn(ko.urn);
        setMiddleTab("content"); // Reset middle tab
      }}
      style={{
        textAlign: "left",
        background: selectedUrn === ko.urn ? "var(--bg-selected)" : "var(--bg-white)",
        borderColor: selectedUrn === ko.urn ? "var(--verification-green)" : "var(--border)"
      }}
    >
      <div className="flex justify-between items-center" style={{ width: "100%" }}>
        <ObjectTypeBadge type={ko.type} />
        {ko.type === "Opinion" && ko.source_credibility && (
          <span className="priority-badge priority-low" style={{ fontSize: "9px", padding: "1px 6px" }}>
            {ko.source_credibility === "tier-1" ? "Tier 1: High Credibility" : "Tier 2: Persuasive"}
          </span>
        )}
        <span className="text-meta" style={{ fontSize: "10px" }}>v{ko.version}</span>
      </div>
      <div style={{ fontWeight: "var(--fw-semibold)", color: "var(--text-primary)", fontSize: "var(--text-small)" }}>
        {ko.title}
      </div>
      <div className="flex justify-between items-center text-small">
        <span>{ko.date_legal}</span>
        <StatusBadge status={ko.status} size="small" />
      </div>
    </button>
  );

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-slate-500" style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", fontStyle: "italic", color: "var(--text-muted)" }}>
        Loading DPDPA Knowledge Base...
      </div>
    );
  }

  return (
    <div className="knowledge-explorer" style={{ display: "grid", gridTemplateColumns: "300px 1fr 340px", gap: "var(--space-4)", height: "calc(100vh - var(--topbar-height) - 2 * var(--space-6))" }}>
      
      {/* ── Left panel: List & Search ──────────────────────────────── */}
      <div className="flex flex-col gap-3" style={{ borderRight: "1px solid var(--border)", paddingRight: "var(--space-3)", overflowY: "auto" }}>
        <input 
          className="input" 
          type="text" 
          placeholder="Search objects, URNs..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        <div className="flex flex-col gap-1">
          <span className="text-meta">Object Type</span>
          <select 
            className="input" 
            value={filterType} 
            onChange={(e) => setFilterType(e.target.value)}
          >
            {uniqueTypes.map(t => (
              <option key={t} value={t}>{t === "all" ? "All Types" : t}</option>
            ))}
          </select>
        </div>

        <div className="divider" style={{ margin: "var(--space-2) 0" }} />

        {/* Scrollable list grouped by layers */}
        <div className="flex flex-col gap-4">
          
          {/* Core Law Layer */}
          {coreLaw.length > 0 && (
            <div className="flex flex-col gap-2">
              <span className="text-meta" style={{ fontSize: "10px", fontWeight: "var(--fw-bold)", letterSpacing: "0.5px" }}>🏛️ CORE LAW LAYER</span>
              <div className="flex flex-col gap-2">
                {coreLaw.map(renderItemCard)}
              </div>
            </div>
          )}

          {/* Sectoral Guidance Layer */}
          {sectoralGuidance.length > 0 && (
            <div className="flex flex-col gap-2">
              <span className="text-meta" style={{ fontSize: "10px", fontWeight: "var(--fw-bold)", letterSpacing: "0.5px" }}>📋 SECTORAL GUIDANCE</span>
              <div className="flex flex-col gap-2">
                {sectoralGuidance.map(renderItemCard)}
              </div>
            </div>
          )}

          {/* Opinion & Commentary Layer */}
          {opinionLayer.length > 0 && (
            <div className="flex flex-col gap-2">
              <span className="text-meta" style={{ fontSize: "10px", fontWeight: "var(--fw-bold)", letterSpacing: "0.5px" }}>💡 OPINION & COMMENTARY</span>
              <div className="flex flex-col gap-2">
                {opinionLayer.map(renderItemCard)}
              </div>
            </div>
          )}

          {filteredKOs.length === 0 && (
            <div className="text-muted text-small text-center" style={{ padding: "var(--space-6) 0" }}>
              No matches found
            </div>
          )}
        </div>
      </div>

      {/* ── Center panel: Object details (Progressive disclosure) ───── */}
      <div className="flex flex-col gap-4" style={{ overflowY: "auto", padding: "0 var(--space-4)" }}>
        {selectedKO ? (
          <div className="flex flex-col gap-4">
            {/* Identity Header */}
            <div className="card flex flex-col gap-3" style={{ background: "#FFFFFF", borderRadius: "14px", border: "1px solid var(--border)", boxShadow: "0 4px 16px rgba(20, 33, 61, 0.04)", padding: "20px 24px" }}>
              <div className="flex justify-between items-center" style={{ flexWrap: "wrap", gap: "10px" }}>
                <div className="flex items-center gap-2 flex-wrap">
                  <span 
                    className="text-mono" 
                    style={{ 
                      fontSize: "11px", 
                      fontWeight: 700, 
                      background: "#F1F5F9", 
                      color: "var(--brand-navy)", 
                      padding: "3px 10px", 
                      borderRadius: "6px",
                      border: "1px solid #CBD5E1"
                    }}
                  >
                    {selectedKO.urn}
                  </span>
                  
                  {selectedKO.relations?.some(r => ["Conflicts With", "Harmonizes With", "Overrides"].includes(r.edge_type)) && (
                    <span 
                      style={{ 
                        fontSize: "11px", 
                        fontWeight: 700, 
                        background: "#FEF2F2", 
                        color: "#991B1B", 
                        border: "1px solid #FCA5A5",
                        padding: "3px 10px", 
                        borderRadius: "9999px",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px"
                      }}
                    >
                      <span>⚡ Inter-Statutory Link Active ({selectedKO.relations.find(r => ["Conflicts With", "Harmonizes With", "Overrides"].includes(r.edge_type)).edge_type})</span>
                    </span>
                  )}

                  {selectedKO.source_credibility && (
                    <span 
                      style={{ 
                        fontSize: "11px", 
                        fontWeight: 700, 
                        background: selectedKO.source_credibility === "tier-1" ? "#EEF2FF" : "#F8FAFC", 
                        color: selectedKO.source_credibility === "tier-1" ? "#312E81" : "#475569", 
                        border: selectedKO.source_credibility === "tier-1" ? "1px solid #C7D2FE" : "1px solid #CBD5E1",
                        padding: "3px 10px", 
                        borderRadius: "9999px",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px"
                      }}
                    >
                      <span>{selectedKO.source_credibility === "tier-1" ? "🛡️ Tier 1 Publisher (High Authority)" : "📄 Tier 2 Publisher (Persuasive)"}</span>
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <ObjectTypeBadge type={selectedKO.type} />
                  <StatusBadge status={selectedKO.status} />
                </div>
              </div>

              <h1 style={{ fontSize: "22px", fontWeight: 800, color: "var(--brand-navy)", margin: "4px 0 0 0", lineHeight: 1.3 }}>
                {selectedKO.title}
              </h1>
            </div>

            {/* Middle navigation tabs for the selected object */}
            {selectedKO.type !== "Opinion" && (
              <div className="flex gap-2" style={{ borderBottom: "2px solid var(--border)", paddingBottom: "0" }}>
                <button 
                  className={`btn-clean text-small ${middleTab === "content" ? "text-primary border-active" : "text-muted"}`} 
                  onClick={() => setMiddleTab("content")}
                  style={{ 
                    padding: "8px 16px", 
                    fontWeight: 700,
                    fontSize: "13px",
                    color: middleTab === "content" ? "var(--brand-navy)" : "var(--text-muted)",
                    borderBottom: middleTab === "content" ? "3px solid var(--brand-green)" : "3px solid transparent",
                    transition: "all 150ms ease"
                  }}
                >
                  📄 Statutory Summary & Citations
                </button>
                <button 
                  className={`btn-clean text-small flex items-center gap-1 ${middleTab === "opinions" ? "text-primary border-active" : "text-muted"}`} 
                  onClick={() => setMiddleTab("opinions")}
                  style={{ 
                    padding: "8px 16px", 
                    fontWeight: 700,
                    fontSize: "13px",
                    color: middleTab === "opinions" ? "var(--brand-navy)" : "var(--text-muted)",
                    borderBottom: middleTab === "opinions" ? "3px solid var(--brand-green)" : "3px solid transparent",
                    transition: "all 150ms ease"
                  }}
                >
                  💡 Linked Opinions & Commentary ({getOpinionsForKOLocal(selectedKO.urn).length})
                </button>
              </div>
            )}

            {middleTab === "content" ? (
              <div className="flex flex-col gap-5">
                {/* Meaning & Definition Section */}
                <div className="card" style={{ background: "#FFFFFF", borderRadius: "14px", border: "1px solid var(--border)", boxShadow: "var(--shadow-card)", padding: "20px" }}>
                  <h3 style={{ fontSize: "16px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>Definition & Statutory Summary</h3>
                  <p className="text-body" style={{ marginTop: "10px", lineHeight: "1.65", color: "var(--brand-slate)", fontSize: "14px" }}>
                    {selectedKO.summary}
                  </p>
                  
                  {(selectedKO.forum_published || selectedKO.interpretation_stance) && (
                    <div style={{ display: "flex", gap: "12px", marginTop: "14px", paddingTop: "12px", borderTop: "1px solid #F1F5F9", flexWrap: "wrap" }}>
                      {selectedKO.forum_published && (
                        <div style={{ fontSize: "12px", background: "#F8FAFC", padding: "4px 10px", borderRadius: "6px", border: "1px solid #E2E8F0" }}>
                          <strong style={{ color: "var(--brand-navy)" }}>Published In:</strong> <span style={{ color: "var(--brand-slate)", fontWeight: 600 }}>{selectedKO.forum_published}</span>
                        </div>
                      )}
                      {selectedKO.interpretation_stance && (
                        <div style={{ fontSize: "12px", background: "#F8FAFC", padding: "4px 10px", borderRadius: "6px", border: "1px solid #E2E8F0" }}>
                          <strong style={{ color: "var(--brand-navy)" }}>Stance:</strong> <span style={{ color: "var(--brand-blue)", fontWeight: 700, textTransform: "capitalize" }}>{selectedKO.interpretation_stance.replace("_", " ")}</span>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="flex gap-2" style={{ marginTop: "14px", flexWrap: "wrap" }}>
                    {(selectedKO.entities || []).map(ent => (
                      <span key={ent} style={{ background: "#F1F5F9", border: "1px solid #CBD5E1", color: "#334155", padding: "3px 10px", borderRadius: "6px", fontSize: "11px", fontWeight: 700 }}>
                        {ent}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Business Obligation Mapping Section */}
                {selectedKO.business_impact && (
                  <div className="card" style={{ background: "#FFFFFF", borderRadius: "14px", border: "1px solid var(--border)", borderLeft: "5px solid var(--brand-blue)", boxShadow: "var(--shadow-card)", padding: "20px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
                      <span style={{ fontSize: "18px" }}>💼</span>
                      <h3 style={{ fontSize: "16px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>Business Obligation & Compliance Action</h3>
                    </div>
                    
                    <div className="flex flex-col gap-3">
                      <div style={{ background: "#EFF6FF", border: "1px solid #BFDBFE", borderRadius: "10px", padding: "12px 14px" }}>
                        <span style={{ fontSize: "11px", fontWeight: 800, color: "#1E40AF", textTransform: "uppercase", letterSpacing: "0.05em" }}>Impact Summary</span>
                        <p style={{ fontSize: "13px", color: "#1E3A8A", margin: "4px 0 0 0", lineHeight: 1.5, fontWeight: 500 }}>
                          {selectedKO.business_impact.impact_summary}
                        </p>
                      </div>

                      <div style={{ background: "#F0FDF4", border: "1px solid #86EFAC", borderRadius: "10px", padding: "12px 14px" }}>
                        <span style={{ fontSize: "11px", fontWeight: 800, color: "#14532D", textTransform: "uppercase", letterSpacing: "0.05em" }}>Required Operational Action</span>
                        <p style={{ fontSize: "13px", color: "#14532D", margin: "4px 0 0 0", lineHeight: 1.5, fontWeight: 600 }}>
                          ⚡ {selectedKO.business_impact.action_required}
                        </p>
                      </div>
                      
                      {selectedKO.business_impact.affected_roles && (
                        <div style={{ marginTop: "4px" }}>
                          <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--brand-slate)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Target Operational Roles</span>
                          <div className="flex gap-2" style={{ marginTop: "6px", flexWrap: "wrap" }}>
                            {selectedKO.business_impact.affected_roles.map(r => (
                              <span key={r} style={{ background: "#F8FAFC", border: "1px solid #CBD5E1", color: "var(--brand-navy)", padding: "3px 10px", borderRadius: "9999px", fontSize: "11px", fontWeight: 700 }}>
                                👤 {r}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Evidence section */}
                <div className="flex flex-col gap-3">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <h3 style={{ fontSize: "16px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>Citations & Evidence Ledger</h3>
                    <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--brand-green)", background: "#E6F4E8", padding: "2px 8px", borderRadius: "9999px" }}>
                      ✓ Verified Gazette Record
                    </span>
                  </div>

                  <div className="flex flex-col gap-3">
                    {selectedKO.evidence && selectedKO.evidence.map(ev => (
                      <CitationCard key={ev.id} evidence={ev} />
                    ))}
                  </div>
                </div>

                {/* Temporal section */}
                <div className="card" style={{ background: "#FFFFFF", borderRadius: "14px", border: "1px solid var(--border)", padding: "20px" }}>
                  <h3 style={{ fontSize: "16px", fontWeight: 800, color: "var(--brand-navy)", margin: "0 0 12px 0" }}>Timeline & System Ledger</h3>
                  <div className="flex gap-6" style={{ marginTop: "4px", flexWrap: "wrap" }}>
                    <TimeDisplay label="Legal Effective Date" date={selectedKO.date_legal} />
                    <TimeDisplay label="Detected by Factory" date={selectedKO.date_detected} />
                    {selectedKO.date_published && <TimeDisplay label="Published to Graph" date={selectedKO.date_published} />}
                  </div>
                </div>
              </div>
            ) : (
              // opinions tab
              <div className="flex flex-col gap-3">
                <h3>Credible Interpretations & Editorial Discussions</h3>
                <p className="text-small text-muted">
                  These materials represent legal commentary and stakeholder analyses discussing this Core Law element.
                </p>

                {getOpinionsForKOLocal(selectedKO.urn).length === 0 ? (
                  <EmptyState 
                    title="No Linked Opinions" 
                    description="No top-tier law firm briefings or consensus position papers reference this URN yet." 
                  />
                ) : (
                  <div className="flex flex-col gap-4">
                    {getOpinionsForKOLocal(selectedKO.urn).map(op => (
                      <div key={op.urn} className="card card-interactive flex flex-col gap-2" onClick={() => setSelectedUrn(op.urn)}>
                        <div className="flex justify-between items-center">
                          <span className="text-meta text-mono" style={{ fontSize: "10px" }}>{op.urn}</span>
                          <span className="priority-badge priority-low" style={{ fontSize: "9px" }}>
                            {op.authority}
                          </span>
                        </div>
                        <h4 style={{ margin: "2px 0 6px 0", color: "var(--text-link)", cursor: "pointer" }}>{op.title}</h4>
                        <p className="text-body text-small" style={{ lineClamp: 2, overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" }}>
                          {op.summary}
                        </p>
                        <div className="flex justify-between items-center text-meta text-small" style={{ marginTop: "4px" }}>
                          <span>Stance: <span style={{ textTransform: "capitalize" }}>{op.interpretation_stance.replace("_", " ")}</span></span>
                          <span>Published: {op.date_published}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <EmptyState title="Select a Knowledge Object" description="Select an object from the left pane to explore its full details, citations, and relationships." />
        )}
      </div>

      {/* ── Right panel: Relations Explorer / Visual Graph ───────── */}
      <div className="flex flex-col gap-4" style={{ borderLeft: "1px solid var(--border)", paddingLeft: "var(--space-4)", overflowY: "auto" }}>
        <div className="flex gap-2" style={{ background: "var(--bg-cloud)", padding: "4px", borderRadius: "var(--radius-md)" }}>
          <button 
            className={`btn ${rightPanelTab === "relations" ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setRightPanelTab("relations")}
            style={{ flex: 1, justifyContent: "center" }}
          >
            🔗 Connections
          </button>
          <button 
            className={`btn ${rightPanelTab === "trust" ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setRightPanelTab("trust")}
            style={{ flex: 1, justifyContent: "center" }}
          >
            🛡️ Trust Breakdown
          </button>
        </div>

        {selectedKO && rightPanelTab === "relations" && (
          <div className="flex flex-col gap-4">
            <h4>Graph Neighborhood</h4>
            
            {/* Visual Mini Graph mock */}
            <div className="visual-graph-box card flex flex-col items-center justify-center gap-4" style={{ height: "180px", background: "var(--bg-cloud)" }}>
              {/* Primary Node */}
              <div className="graph-node graph-primary" style={{ padding: "8px 12px", background: "var(--trust-navy)", color: "var(--text-inverse)", borderRadius: "var(--radius-md)", fontSize: "11px", fontWeight: "var(--fw-medium)", textAlign: "center" }}>
                {selectedKO.title.substring(0, 20)}...
              </div>

              {/* Edge line */}
              <div className="graph-edge-line" style={{ width: "2px", height: "24px", background: "var(--border-strong)", position: "relative" }}>
                <span style={{ position: "absolute", left: "6px", top: "2px", fontSize: "10px", color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                  {selectedKO.relations[0]?.edge_type || "Relates To"}
                </span>
              </div>

              {/* Connected Node */}
              {selectedKO.relations[0] ? (
                <div className="graph-node graph-secondary" style={{ padding: "8px 12px", background: "var(--bg-white)", border: "1px solid var(--border-strong)", borderRadius: "var(--radius-md)", fontSize: "11px", textAlign: "center" }}>
                  {getKOByUrnLocal(selectedKO.relations[0].target_urn)?.title.substring(0, 20)}...
                </div>
              ) : (
                <div className="text-small text-muted">No external connections</div>
              )}
            </div>

            <div className="divider" />

            <h4>Semantic Sentences</h4>
            <div className="flex flex-col gap-2">
              {(!selectedKO.relations || selectedKO.relations.length === 0) ? (
                <p className="text-small text-muted">No explicit graph relationships registered.</p>
              ) : (
                selectedKO.relations.map((rel, idx) => {
                  const target = getKOByUrnLocal(rel.target_urn);
                  return (
                    <div key={idx} className="relationship-sentence text-small">
                      This <strong>{selectedKO.type}</strong> <u>{rel.edge_type}</u> target <strong>{target?.type || "Object"}</strong>:{" "}
                      <span style={{ color: "var(--text-link)", cursor: "pointer" }} onClick={() => setSelectedUrn(rel.target_urn)}>
                        {target?.title}
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        )}

        {selectedKO && rightPanelTab === "trust" && (
          <div className="flex flex-col gap-4">
            <h4>Trust & Verification Audit</h4>
            <p className="text-small">Detailed multi-dimensional confidence breakdown from programmatic metrics and human approval states.</p>
            <TrustIndicator trust={selectedKO.trust} />
          </div>
        )}
      </div>

    </div>
  );
}
