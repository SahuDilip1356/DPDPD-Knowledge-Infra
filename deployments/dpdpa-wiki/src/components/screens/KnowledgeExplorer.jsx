import React, { useMemo, useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { supabase } from "../../data/supabaseClient";
import CometCascadeHeroBackground from "../marketing/CometCascadeHeroBackground";
import {
  KNOWLEDGE_OBJECTS,
  OPINIONS,
} from "../../data/mockData";
import { MOCKS_ENABLED } from "../../data/runtimeMode";
import {
  EmptyState,
  ObjectTypeBadge,
  StatusBadge,
  TimeDisplay
} from "../ui/SharedComponents";
import "../../styles/knowledge.css";

const LANDING_PANELS = [
  { path: "/acts", title: "Acts", description: "Statutory base text" },
  { path: "/rules", title: "Rules", description: "Implementing regulations" },
  { path: "/interpretations", title: "Interpretations", description: "Opinion & commentary" },
  { path: "/discussions", title: "Discussions", description: "Circulars and notes" },
  { path: "/bible", title: "DPDPA Bible", description: "Reference index and schedule" },
  { path: "/changes", title: "Change Engine", description: "Current legal amendments" }
];

function normalizeRow(row) {
  return {
    urn: row.urn || "",
    title: row.title || "Untitled",
    type: row.type || "Unknown",
    version: Number(row.version || 1),
    status: row.status || "active",
    summary: row.summary || "No summary available.",
    legalDate: row.date_legal || row.legal_time_start || row.published_at || row.date_published || "",
    systemDate: row.date_detected || row.system_time_start || row.system_published || row.date_published || "",
    authority: row.authority || "Unknown authority",
    evidence: Array.isArray(row.evidence) ? row.evidence : [],
    relations: Array.isArray(row.relations) ? row.relations : [],
    linkedObjects: row.linked_objects || [],
    businessImpact: row.business_impact || row.businessImpact || {}
  };
}

export default function KnowledgeExplorer() {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeType, setActiveType] = useState("all");
  const [selectedUrn, setSelectedUrn] = useState("");
  const [loading, setLoading] = useState(true);
  const [objects, setObjects] = useState([]);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      try {
        if (supabase) {
          const { data, error } = await supabase
            .from("knowledge_objects")
            .select("*")
            .order("legal_time_start", { ascending: false });

          if (!cancelled && !error && Array.isArray(data) && data.length > 0) {
            setObjects(data.map(normalizeRow));
            setSelectedUrn(data[0]?.urn || "");
            setLoading(false);
            return;
          }
        }
      } catch {
        // fall back to fixtures below
      }

      if (!cancelled) {
        const fixture = MOCKS_ENABLED ? [...KNOWLEDGE_OBJECTS, ...OPINIONS] : [];
        const normalized = fixture.map(normalizeRow);
        setObjects(normalized);
        setSelectedUrn(normalized[0]?.urn || "");
      }
      if (!cancelled) {
        setLoading(false);
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const selected = objects.find((o) => o.urn === selectedUrn);

  const allTypes = useMemo(() => {
    const set = new Set(["all"]);
    objects.forEach((o) => {
      if (o.type) set.add(o.type);
    });
    const ordered = Array.from(set);
    ordered.sort((a, b) => {
      if (a === "all") return -1;
      if (b === "all") return 1;
      return a.localeCompare(b);
    });
    return ordered;
  }, [objects]);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    return objects.filter((o) => {
      const inText =
        q.length === 0 ||
        o.title.toLowerCase().includes(q) ||
        o.summary.toLowerCase().includes(q) ||
        o.urn.toLowerCase().includes(q) ||
        o.authority.toLowerCase().includes(q);
      const inType = activeType === "all" || o.type === activeType;
      return inText && inType;
    });
  }, [objects, activeType, searchTerm]);

  const groups = useMemo(() => {
    const core = filtered.filter((o) => ["Act", "Rule", "Case", "Notification"].includes(o.type));
    const guidance = filtered.filter((o) => o.type === "Circular");
    const opinions = filtered.filter((o) => o.type === "Opinion");
    return { core, guidance, opinions, other: [] };
  }, [filtered]);

  useEffect(() => {
    if (filtered.length === 0) {
      setSelectedUrn("");
      return;
    }

    if (!filtered.some((o) => o.urn === selectedUrn)) {
      setSelectedUrn(filtered[0].urn);
    }
  }, [filtered, selectedUrn]);

  const kpis = useMemo(() => {
    const all = objects.length;
    const active = objects.filter((o) => o.status !== "superseded").length;
    const latestTs = objects.reduce((acc, o) => {
      const t = new Date(o.legalDate || 0).getTime();
      if (Number.isNaN(t)) return acc;
      return Math.max(acc, t);
    }, 0);
    return {
      all,
      active,
      updates: all > 0 ? Math.min(all, Math.max(1, Math.round((all * 0.42)))) : 0,
      latestLabel: latestTs ? new Date(latestTs).toLocaleDateString("en-IN") : "—"
    };
  }, [objects]);

  if (loading) {
    return <div className="knowledge-empty">Loading DPDPA knowledge index...</div>;
  }

  return (
    <div className="knowledge-page">
      <section className="knowledge-hero" role="banner">
        <CometCascadeHeroBackground />
        <div className="knowledge-hero-overlay" aria-hidden="true" />
        <div className="knowledge-hero-content">
          <div className="knowledge-hero-meta">
            <span className="knowledge-pill">Knowledge Infrastructure</span>
            <span className="knowledge-pill">Layered URN Registry</span>
            <span className="knowledge-pill">Statute-First</span>
          </div>
          <h1>DPDPA Knowledge Hub</h1>
          <p style={{ maxWidth: "680px", color: "rgba(226, 232, 240, 0.94)" }}>
            Browse Acts, Rules, Interpretations, and sector discussions from one place.
            Every object is versioned and traceable through URN, source date, and relation graph.
          </p>

          <form
            className="knowledge-search"
            onSubmit={(e) => {
              e.preventDefault();
            }}
          >
            <input
              className="input"
              type="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by title, URN, authority, or section"
              aria-label="Search knowledge objects"
            />
          </form>

          <div className="knowledge-kpis" style={{ marginTop: "var(--space-5)" }}>
            <div className="knowledge-kpi">
              <p className="knowledge-kpi-value">{kpis.all}</p>
              <p className="knowledge-kpi-label">Total knowledge objects</p>
            </div>
            <div className="knowledge-kpi">
              <p className="knowledge-kpi-value">{kpis.active}</p>
              <p className="knowledge-kpi-label">Active versions</p>
            </div>
            <div className="knowledge-kpi">
              <p className="knowledge-kpi-value">{kpis.updates}</p>
              <p className="knowledge-kpi-label">Update cadence (rolling)</p>
            </div>
            <div className="knowledge-kpi">
              <p className="knowledge-kpi-value">{kpis.latestLabel}</p>
              <p className="knowledge-kpi-label">Latest legal date</p>
            </div>
          </div>

          <div className="knowledge-chip-row">
            {LANDING_PANELS.map((panel) => (
              <Link key={panel.path} to={panel.path} className="knowledge-chip">
                <span style={{ fontWeight: 700 }}>{panel.title}</span>
                <span style={{ opacity: 0.75 }}>· {panel.description}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="knowledge-layout">
        <aside className="knowledge-filters">
          <div className="knowledge-list-group">
            <p className="knowledge-layer-title">Object type</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "10px" }}>
              {allTypes.map((type) => {
                const active = activeType === type;
                return (
                  <button
                    key={type}
                    type="button"
                    className={`knowledge-chip ${active ? "is-active" : ""}`}
                    onClick={() => setActiveType(type)}
                    style={{
                      borderColor: active ? "rgba(255, 255, 255, 0.6)" : "var(--border)",
                      background: active ? "rgba(30, 64, 175, 0.15)" : "rgba(15, 23, 42, 0.06)",
                      color: active ? "var(--text-inverse)" : "var(--text-body)"
                    }}
                  >
                    {type}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="knowledge-list">
            {["core", "guidance", "opinions"].map((bucket) => {
              const items = {
                core: groups.core,
                guidance: groups.guidance,
                opinions: groups.opinions
              }[bucket];

              if (!items.length) return null;

              const labels = {
                core: "Core law layer",
                guidance: "Sector guidance",
                opinions: "Opinion layer"
              };

              return (
                <div key={bucket} className="knowledge-list-group">
                  <p className="knowledge-layer-title">{labels[bucket]}</p>
                  <div style={{ marginTop: "10px", display: "grid", gap: "10px" }}>
                    {items.map((item) => (
                      <button
                        key={item.urn}
                        type="button"
                        className={`card card-compact card-interactive knowledge-object-card ${selectedUrn === item.urn ? "is-selected" : ""}`}
                        onClick={() => setSelectedUrn(item.urn)}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", gap: "8px", alignItems: "center" }}>
                          <ObjectTypeBadge type={item.type} />
                          <span className="text-mono" style={{ fontSize: "10px" }}>v{item.version}</span>
                        </div>
                        <div style={{ fontWeight: 700, color: "var(--text-primary)", marginTop: "6px" }}>
                          {item.title}
                        </div>
                        <p className="text-small" style={{ color: "var(--text-muted)", marginTop: "6px" }}>
                          {item.summary}
                        </p>
                        <div style={{ display: "flex", justifyContent: "space-between", gap: "8px", marginTop: "8px", alignItems: "center" }}>
                          <StatusBadge size="small" status={item.status} />
                          <span className="text-meta" style={{ fontSize: "10px", textAlign: "right" }}>{item.legalDate || "—"}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}

            {filtered.length === 0 && (
              <div className="knowledge-list-group">
                <EmptyState
                  title="No knowledge objects"
                  subtitle="Change the search text or widen the filter and try again."
                />
              </div>
            )}
          </div>
        </aside>

        <div className="knowledge-detail-shell">
          {!selected ? (
            <EmptyState
              title="Choose a knowledge object"
              subtitle="Pick one from the left panel to inspect versions, relations, and evidence"
            />
          ) : (
            <>
              <div className="card">
                <div className="knowledge-detail-head">
                  <div style={{ maxWidth: "78%" }}>
                    <p className="knowledge-detail-urn">{selected.urn}</p>
                    <h2 className="knowledge-detail-title">{selected.title}</h2>
                    <div style={{ marginTop: "8px", color: "var(--text-muted)", fontSize: "13px" }}>
                      {selected.authority} · version {selected.version}
                    </div>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px", alignItems: "flex-end" }}>
                    <ObjectTypeBadge type={selected.type} />
                    <StatusBadge status={selected.status} />
                  </div>
                </div>

                <p style={{ marginTop: "14px", color: "var(--text-muted)", lineHeight: 1.6 }}>
                  {selected.summary}
                </p>

                <div className="knowledge-relation-row" style={{ marginTop: "16px" }}>
                  <TimeDisplay label="Legal effective" date={selected.legalDate} type="legal" />
                  <TimeDisplay label="Published on platform" date={selected.systemDate} type="system" />
                </div>
              </div>

              <div className="card">
                <p className="knowledge-layer-title" style={{ marginBottom: "10px" }}>Linked objects</p>
                <div style={{ display: "grid", gap: "8px" }}>
                  {selected.relations.length === 0 && selected.linkedObjects.length === 0 ? (
                    <p className="text-small" style={{ color: "var(--text-muted)" }}>No linked objects for this version.</p>
                  ) : (
                    [...selected.relations, ...selected.linkedObjects.map((urn) => ({ target_urn: urn, edge_type: "RELATED" }))]
                      .slice(0, 10)
                      .map((rel, idx) => (
                        <div key={`${rel.target_urn}-${idx}`} className="card card-compact" style={{ borderColor: "var(--border)" }}>
                          <span className="text-small" style={{ color: "var(--text-muted)" }}>{rel.edge_type}</span>
                          <p className="text-mono" style={{ fontSize: "11px" }}>{rel.target_urn}</p>
                        </div>
                      ))
                  )}
                </div>
              </div>

              <div className="card">
                <p className="knowledge-layer-title" style={{ marginBottom: "10px" }}>Evidence snippets</p>
                <div style={{ display: "grid", gap: "10px" }}>
                  {selected.evidence.length === 0 ? (
                    <p className="text-small" style={{ color: "var(--text-muted)" }}>No evidence attached to this version yet.</p>
                  ) : (
                    selected.evidence.slice(0, 4).map((e) => (
                      <blockquote
                        key={e.id || e.hash || e.source_urn}
                        className="citation"
                        data-layer={selected.type?.toLowerCase?.()}
                      >
                        <span className="citation-urn">{selected.title}</span>
                        <p className="text-small" style={{ marginTop: "4px" }}>“{e.citation_text || e.text || "Evidence exists for this version."}”</p>
                        <div className="citation-provenance">
                          <span>{e.source_name || e.source_urn || "Source unavailable"}</span>
                          <span>{e.hash ? `#${e.hash.slice(0, 12)}…` : "No hash"}</span>
                          <span>{e.coordinates?.section ? e.coordinates.section : ""}</span>
                        </div>
                      </blockquote>
                    ))
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
}
