import React, { useState, useEffect, useMemo } from "react";
import {
  EmptyState,
  ObjectTypeBadge,
  StatusBadge,
  TimeDisplay
} from "../ui/SharedComponents";
import { supabase } from "../../data/supabaseClient";
import { apiFetch, API_CONFIGURED } from "../../lib/api";
import { KNOWLEDGE_OBJECTS, OPINIONS, CONSTITUTIONAL_NOUNS } from "../../data/mockData";
import { MOCKS_ENABLED } from "../../data/runtimeMode";

const MOCK_BACKUP = [...KNOWLEDGE_OBJECTS, ...OPINIONS];

function normalizeKnowledgeRecord(row) {
  const body = (row.body && typeof row.body === "object") ? row.body : {};
  const title = row.title || body.title || "";
  const summary = row.summary || body.summary || "No summary available.";
  const confidence = Number(
    row.confidence_score ?? row.confidence ?? body.confidence_score ?? body.confidence ?? 0
  );
  const systemTimeStart = row.system_time_start || row.system_time || row.published_at || row.date_published || null;
  const systemTimeEnd = row.system_time_end || row.system_end || null;
  const legalTimeStart = row.legal_time_start || row.date_legal || body.date_legal || row.legal_date || null;
  const legalTimeEnd = row.legal_time_end || row.legal_end || body.legal_end || null;
  const relations = Array.isArray(row.relations) ? row.relations : Array.isArray(body.relations) ? body.relations : [];
  const evidence = Array.isArray(row.evidence) ? row.evidence : Array.isArray(body.evidence) ? body.evidence : [];
  const businessImpact = row.business_impact || body.business_impact || {};

  return {
    urn: row.urn || "",
    version: Number(row.version || 1),
    type: row.type || body.type || "Unknown",
    title,
    summary,
    confidence,
    status: systemTimeEnd ? "superseded" : "active",
    system_time_start: systemTimeStart,
    system_time_end: systemTimeEnd,
    legal_time_start: legalTimeStart,
    legal_time_end: legalTimeEnd,
    authority: row.authority || body.authority || "Unknown",
    jurisdiction: row.jurisdiction || body.jurisdiction || "India",
    relations,
    evidence,
    business_impact: businessImpact,
    linked_objects: row.linked_objects || body.linked_objects || []
  };
}

function matchesSearchText(item, query) {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  return (
    item.title.toLowerCase().includes(q) ||
    item.summary.toLowerCase().includes(q) ||
    item.urn.toLowerCase().includes(q)
  );
}

function applyTypeFilter(list, allowedTypes) {
  if (!allowedTypes || allowedTypes.length === 0) {
    return list;
  }
  const normalized = allowedTypes.map((v) => v.toLowerCase());
  return list.filter((item) => normalized.includes((item.type || "").toLowerCase()));
}

export default function KnowledgeCategory({
  title = "Knowledge",
  description = "Regulatory knowledge objects grouped by category.",
  allowedTypes = []
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [allItems, setAllItems] = useState([]);
  const [selectedUrn, setSelectedUrn] = useState("");
  const [historyOpen, setHistoryOpen] = useState(false);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const typeFilterSignature = useMemo(() => allowedTypes.join("|"), [allowedTypes]);

  useEffect(() => {
    let alive = true;

    const loadKnowledge = async () => {
      setLoading(true);
      setError("");
      let records = [];

      try {
        if (API_CONFIGURED) {
          try {
            const res = await apiFetch("/knowledge/search?limit=200&order_by=legal");
            if (res.ok) {
              const payload = await res.json();
              records = (payload.items || []).map(normalizeKnowledgeRecord);
            } else {
              throw new Error(`Knowledge search returned ${res.status}`);
            }
          } catch (err) {
            records = [];
            console.warn("API knowledge search failed, falling back:", err);
          }
        }

        if (!records.length && supabase) {
          try {
            const { data, error: supabaseErr } = await supabase
              .from("knowledge_objects")
              .select("*");
            if (supabaseErr) throw supabaseErr;
            records = (data || []).map(normalizeKnowledgeRecord);
          } catch (supabaseErr) {
            console.warn("Supabase knowledge load failed:", supabaseErr);
            records = [];
          }
        }

        if (!records.length && MOCKS_ENABLED) {
          records = MOCK_BACKUP.map(normalizeKnowledgeRecord);
        }

        records = applyTypeFilter(records, allowedTypes);
        records.sort((a, b) => {
          const aDate = new Date(a.legal_time_start || a.system_time_start || 0).getTime();
          const bDate = new Date(b.legal_time_start || b.system_time_start || 0).getTime();
          return bDate - aDate;
        });

        if (!alive) return;
        setAllItems(records);
        setSelectedUrn(records[0]?.urn || "");
      } catch (fatal) {
        console.error("Failed to load category knowledge:", fatal);
        if (alive) {
          setError("Could not load this category right now.");
          setAllItems([]);
        }
      } finally {
        if (alive) setLoading(false);
      }
    };

    loadKnowledge();
    return () => {
      alive = false;
    };
  }, [typeFilterSignature]);

  const filteredItems = useMemo(() => {
    const base = applyTypeFilter(allItems, allowedTypes);
    return base.filter((item) => matchesSearchText(item, searchTerm));
  }, [allItems, allowedTypes, searchTerm, typeFilterSignature]);

  useEffect(() => {
    if (!selectedUrn && filteredItems.length > 0) {
      setSelectedUrn(filteredItems[0].urn);
    } else if (selectedUrn && !filteredItems.find((item) => item.urn === selectedUrn)) {
      setSelectedUrn(filteredItems[0]?.urn || "");
      setHistory([]);
      setHistoryOpen(false);
    }
  }, [filteredItems, selectedUrn]);

  const selected = filteredItems.find((item) => item.urn === selectedUrn);

  const visibleNouns = CONSTITUTIONAL_NOUNS.slice(0, 12);
  const typeLabel = allowedTypes.length > 0 ? allowedTypes.join(" / ") : "All";

  const loadHistory = async (urn) => {
    if (!urn || !API_CONFIGURED) {
      setHistory([]);
      setHistoryOpen(false);
      return;
    }

    setHistoryLoading(true);
    setHistoryOpen(true);
    try {
      const res = await apiFetch(`/knowledge/sections/${urn}/history`);
      if (!res.ok) {
        throw new Error(`History endpoint returned ${res.status}`);
      }
      const payload = await res.json();
      setHistory(payload.versions || []);
    } catch (err) {
      console.warn("Could not load history:", err);
      setHistory([]);
      setError("History could not be loaded for this object.");
    } finally {
      setHistoryLoading(false);
    }
  };

  const evidenceSamples = selected ? (selected.evidence || []).slice(0, 2) : [];

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center text-sm" style={{ paddingTop: "100px", color: "var(--text-muted)" }}>
        Loading {title.toLowerCase()}...
      </div>
    );
  }

  if (!loading && filteredItems.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center">
        <EmptyState
          title={`No ${title.toLowerCase()} yet`}
          subtitle={error || "Try expanding scope or removing the search filter."}
        />
      </div>
    );
  }

  return (
    <div className="knowledge-category">
      <header className="section-header">
        <div>
          <p className="text-meta" style={{ marginBottom: "4px" }}>{typeLabel}</p>
          <h2>{title}</h2>
          <p className="text-small" style={{ maxWidth: "680px", marginTop: "8px" }}>
            {description}
          </p>
        </div>
        <div className="text-small" style={{ textAlign: "right" }}>
          <p style={{ marginBottom: "2px", color: "var(--text-muted)" }}>Surface taxonomy</p>
          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "flex-end", gap: "6px" }}>
            {visibleNouns.slice(0, 6).map((noun) => (
              <span key={noun} className="filter-pill filter-active">
                {noun}
              </span>
            ))}
          </div>
        </div>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: "var(--space-4)" }}>
        <section className="card card-compact" style={{ padding: "var(--space-4)", overflowY: "auto", maxHeight: "calc(100vh - 170px)" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <input
              className="input"
              type="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={`Search ${title.toLowerCase()} by title, urn, or summary`}
            />
            <span className="text-meta">Chronology ({filteredItems.length})</span>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {filteredItems.map((item) => (
                <button
                  key={item.urn}
                  className={`card card-compact card-interactive`}
                  style={{
                    textAlign: "left",
                    background: selectedUrn === item.urn ? "var(--bg-selected)" : "var(--bg-white)"
                  }}
                  onClick={() => {
                    setSelectedUrn(item.urn);
                    setHistory([]);
                    setHistoryOpen(false);
                    setError("");
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "var(--space-2)", alignItems: "center", marginBottom: "6px" }}>
                    <ObjectTypeBadge type={item.type} />
                    <StatusBadge size="small" status={item.status === "active" ? "active" : "obsolete"} />
                  </div>
                  <p style={{ fontWeight: 700, color: "var(--text-primary)", marginBottom: "6px" }}>{item.title}</p>
                  <p className="text-small" style={{ color: "var(--text-muted)", marginBottom: "6px" }}>{item.summary}</p>
                  <span className="text-mono" style={{ fontSize: "10px", color: "var(--text-muted)" }}>{item.urn}</span>
                  <div style={{ marginTop: "8px", display: "flex", gap: "6px", justifyContent: "space-between" }}>
                    <TimeDisplay label="Legal" date={item.legal_time_start || item.system_time_start} type="legal" />
                    <span className="text-meta" style={{ whiteSpace: "nowrap" }}>v{item.version}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="card" style={{ padding: "var(--space-6)", overflowY: "auto", maxHeight: "calc(100vh - 170px)" }}>
          {!selected ? (
            <EmptyState
              title="Select a record"
              subtitle="Choose a knowledge object from the left to view its obligations and version details."
            />
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
              <div className="flex" style={{ justifyContent: "space-between", alignItems: "center", gap: "var(--space-3)" }}>
                <div>
                  <p className="text-meta" style={{ marginBottom: "6px" }}>{selected.type} • {selected.jurisdiction}</p>
                  <h3 style={{ fontSize: "var(--text-h3)", margin: 0 }}>{selected.title}</h3>
                  <p className="text-small" style={{ marginTop: "8px", color: "var(--text-muted)" }}>{selected.summary}</p>
                </div>
                <div style={{ textAlign: "right" }}>
                  <StatusBadge status={selected.status} />
                  <div className="text-meta" style={{ marginTop: "6px" }}>Version {selected.version}</div>
                </div>
              </div>

              <div className="card card-compact" style={{ background: "#F8FAFC" }}>
                <p className="text-meta" style={{ marginBottom: "6px" }}>Chronological Context</p>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-3)" }}>
                  <TimeDisplay label="Legal effective from" date={selected.legal_time_start} type="legal" />
                  <TimeDisplay label="Published to platform" date={selected.system_time_start} type="system" />
                  <TimeDisplay label="Authority or source" date={null} type="detected" />
                  <TimeDisplay label="Trust score" date={null} type="published" />
                </div>
              </div>

              <div className="card card-compact">
                <p className="text-meta" style={{ marginBottom: "8px" }}>Business obligations</p>
                <p className="text-small" style={{ lineHeight: 1.6 }}>
                  {(selected.business_impact && selected.business_impact.impact_summary) ||
                    "No mapped business impact available in this version."}
                </p>
                {selected.business_impact?.affected_roles?.length > 0 && (
                  <p className="text-small" style={{ marginTop: "8px", color: "var(--text-muted)" }}>
                    <strong>Roles:</strong> {selected.business_impact.affected_roles.join(", ")}
                  </p>
                )}
                {selected.business_impact?.affected_processes?.length > 0 && (
                  <p className="text-small" style={{ marginTop: "8px", color: "var(--text-muted)" }}>
                    <strong>Processes:</strong> {selected.business_impact.affected_processes.join(", ")}
                  </p>
                )}
              </div>

              {selected.linked_objects?.length > 0 && (
                <div className="card card-compact">
                  <p className="text-meta" style={{ marginBottom: "8px" }}>Linked objects</p>
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    {selected.linked_objects.slice(0, 8).map((linked, index) => (
                      <code key={`${linked}-${index}`} className="text-mono" style={{ fontSize: "11px" }}>
                        {linked}
                      </code>
                    ))}
                  </div>
                </div>
              )}

              {selected.relations.length > 0 && (
                <div className="card card-compact">
                  <p className="text-meta" style={{ marginBottom: "8px" }}>Relations ({selected.relations.length})</p>
                  <ul style={{ paddingLeft: "16px" }}>
                    {selected.relations.slice(0, 12).map((edge, idx) => (
                      <li key={`${edge.target_urn}-${idx}`} className="text-small" style={{ marginBottom: "6px", color: "var(--text-muted)" }}>
                        <strong>{edge.edge_type}</strong> → {edge.target_urn}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {evidenceSamples.length > 0 && (
                <div className="card card-compact">
                  <p className="text-meta" style={{ marginBottom: "8px" }}>Evidence snippets</p>
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    {evidenceSamples.map((e) => (
                      <blockquote key={e.id || e.source_urn || e.hash} className="text-small" style={{ margin: 0, paddingLeft: "10px", borderLeft: "3px solid var(--brand-blue)", color: "var(--brand-navy)" }}>
                        {`“${e.citation_text || e.text || "Evidence exists in this version."}”`}
                      </blockquote>
                    ))}
                  </div>
                </div>
              )}

              <button
                className="btn btn-secondary"
                onClick={() => loadHistory(selected.urn)}
                disabled={historyLoading}
                style={{ width: "fit-content" }}
              >
                {historyLoading ? "Loading history..." : "Show section history"}
              </button>

              {historyOpen && (
                <div className="card card-compact">
                  <p className="text-meta" style={{ marginBottom: "8px" }}>Version history</p>
                  {history.length === 0 ? (
                    <p className="text-small" style={{ color: "var(--text-muted)" }}>No historical versions available for this item.</p>
                  ) : (
                    <ul style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                      {history.map((row) => (
                        <li key={`${row.version}`} className="card card-compact" style={{ padding: "10px 12px", borderLeft: `4px solid ${row.status === "active" ? "var(--verification-green)" : "var(--brand-blue)"}` }}>
                          <p style={{ fontWeight: 700, marginBottom: "4px" }}>{row.version === selected.version ? <strong>Current:</strong> : ""} v{row.version}</p>
                          <div className="text-small" style={{ color: "var(--text-muted)" }}>
                            System: {row.system_time_start || "—"} | Legal: {row.legal_time_start || "—"}
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
