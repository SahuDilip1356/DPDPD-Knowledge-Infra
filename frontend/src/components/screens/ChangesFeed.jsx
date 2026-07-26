import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../../data/supabaseClient";
import { REGULATORY_EVENTS } from "../../data/mockData";
import { StatusBadge, PriorityBadge, ImpactBadge } from "../ui/SharedComponents";


export default function ChangesFeed() {
  const navigate = useNavigate();
  const [filterType, setFilterType] = useState("all");
  const [filterImpact, setFilterImpact] = useState("all");
  const [sortBy, setSortBy] = useState("date");
  const [viewMode, setViewMode] = useState("list"); // list, timeline

  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadEvents = async () => {
      setLoading(true);
      try {
        if (supabase) {
          const { data, error } = await supabase
            .from("regulatory_events")
            .select("*");
          if (!error && data && data.length > 0) {
            setEvents(data);
            setLoading(false);
            return;
          }
        }
      } catch (err) {
        console.warn("Supabase load failed, falling back to mockData.js:", err);
      }
      setEvents(REGULATORY_EVENTS);
      setLoading(false);
    };

    loadEvents();
  }, []);

  // Filter & sort logic
  const filteredEvents = events.filter(event => {
    if (filterType !== "all" && event.type !== filterType) return false;
    if (filterImpact !== "all" && event.impact_level !== filterImpact) return false;
    return true;
  }).sort((a, b) => {
    if (sortBy === "date") return new Date(b.date_published) - new Date(a.date_published);
    if (sortBy === "impact") {
      const weight = { critical: 4, high: 3, medium: 2, low: 1 };
      return (weight[b.impact_level] || 0) - (weight[a.impact_level] || 0);
    }
    if (sortBy === "effective") return new Date(a.date_effective || a.date_published) - new Date(b.date_effective || b.date_published);
    return 0;
  });

  const eventTypes = ["all", ...new Set(events.map(e => e.type))];
  const impacts = ["all", "critical", "high", "medium", "low"];

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-slate-500" style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", fontStyle: "italic", color: "var(--text-muted)", padding: "100px 0" }}>
        Loading Regulatory Changes Feed...
      </div>
    );
  }

  return (
    <div className="changes-feed flex flex-col gap-6">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="section-header">
        <div>
          <h1 className="text-display">Regulatory Changes</h1>
          <p className="text-small">Track, analyze, and manage regulatory events, notifications, and legislation changes.</p>
        </div>
        
        <div className="flex gap-2">
          <button 
            className={`btn ${viewMode === "list" ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setViewMode("list")}
          >
            📋 List View
          </button>
          <button 
            className={`btn ${viewMode === "timeline" ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setViewMode("timeline")}
          >
            ⏳ Timeline View
          </button>
        </div>
      </div>

      {/* ── Filters & Controls ─────────────────────────────────────── */}
      <div className="card card-compact flex items-center justify-between gap-4" style={{ flexDirection: "row", flexWrap: "wrap" }}>
        <div className="flex gap-4">
          <div className="flex flex-col gap-1">
            <span className="text-meta">Event Type</span>
            <select 
              className="input" 
              value={filterType} 
              onChange={(e) => setFilterType(e.target.value)}
              style={{ minWidth: "160px" }}
            >
              {eventTypes.map(type => (
                <option key={type} value={type}>{type === "all" ? "All Types" : type}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-meta">Impact Level</span>
            <select 
              className="input" 
              value={filterImpact} 
              onChange={(e) => setFilterImpact(e.target.value)}
              style={{ minWidth: "160px" }}
            >
              {impacts.map(imp => (
                <option key={imp} value={imp}>{imp === "all" ? "All Impacts" : imp.toUpperCase()}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <span className="text-meta">Sort By</span>
          <select 
            className="input" 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            style={{ minWidth: "160px" }}
          >
            <option value="date">Most Recent</option>
            <option value="impact">Highest Impact</option>
            <option value="effective">Effective Date Soonest</option>
          </select>
        </div>
      </div>

      {/* ── List View ─────────────────────────────────────────────── */}
      {viewMode === "list" && (
        <div className="flex flex-col gap-4">
          {filteredEvents.length === 0 ? (
            <div className="card text-center" style={{ padding: "var(--space-12)" }}>
              <span style={{ fontSize: "48px" }}>🔍</span>
              <h3>No regulatory changes match the filters.</h3>
              <button className="btn btn-secondary" onClick={() => { setFilterType("all"); setFilterImpact("all"); }} style={{ marginTop: "var(--space-4)" }}>
                Reset Filters
              </button>
            </div>
          ) : (
            filteredEvents.map(event => (
              <div 
                key={event.id} 
                className="card card-interactive flex flex-col gap-3"
                onClick={() => navigate(`/changes/${event.id}`)}
              >
                <div className="flex justify-between items-start gap-4">
                  <div>
                    <span className="text-meta" style={{ display: "block", marginBottom: "4px" }}>
                      {event.authority} • {event.jurisdiction}
                    </span>
                    <h3 style={{ fontSize: "var(--text-h3)", fontWeight: "var(--fw-semibold)", color: "var(--text-primary)" }}>
                      {event.title}
                    </h3>
                  </div>
                  <div className="flex gap-2">
                    <ImpactBadge level={event.impact_level} />
                    <StatusBadge status={event.status} size="small" />
                  </div>
                </div>

                <p className="text-body" style={{ color: "var(--text-body)" }}>
                  {event.summary}
                </p>

                <div className="divider" />

                <div className="flex justify-between items-center text-small">
                  <div className="flex gap-4">
                    <span>Published: <strong>{event.date_published}</strong></span>
                    <span>Effective: <strong>{event.date_effective}</strong></span>
                  </div>
                  <div className="flex gap-3">
                    <span>📚 KOs: {event.affected_ko_urns.length}</span>
                    {event.has_conflicts && <span style={{ color: "var(--error)", fontWeight: "var(--fw-medium)" }}>⚠ Has Conflicts</span>}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* ── Timeline View ─────────────────────────────────────────── */}
      {viewMode === "timeline" && (
        <div className="timeline-container card" style={{ padding: "var(--space-8) var(--space-6)" }}>
          <div className="timeline-line" style={{ 
            position: "absolute", 
            left: "40px", 
            top: "var(--space-8)", 
            bottom: "var(--space-8)", 
            width: "2px", 
            backgroundColor: "var(--border)" 
          }} />
          
          <div className="flex flex-col gap-8" style={{ position: "relative" }}>
            {filteredEvents.map(event => (
              <div key={event.id} className="timeline-event-wrapper flex" style={{ gap: "var(--space-6)" }}>
                <div className="timeline-marker" style={{ 
                  width: "20px", 
                  height: "20px", 
                  borderRadius: "50%", 
                  backgroundColor: "var(--bg-white)", 
                  border: "4px solid var(--verification-green)", 
                  zIndex: 2,
                  marginLeft: "11px",
                  marginTop: "8px"
                }} />
                
                <div className="timeline-card card card-interactive flex-1 flex flex-col gap-3" onClick={() => navigate(`/changes/${event.id}`)}>
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-meta">{event.date_published}</span>
                      <h3 style={{ fontSize: "var(--text-h3)", color: "var(--text-primary)" }}>{event.title}</h3>
                    </div>
                    <ImpactBadge level={event.impact_level} />
                  </div>
                  <p className="text-body">{event.summary}</p>
                  <div className="flex gap-4 text-small text-muted">
                    <span>Effective Date: <strong>{event.date_effective}</strong></span>
                    <span>Authority: <strong>{event.authority}</strong></span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
