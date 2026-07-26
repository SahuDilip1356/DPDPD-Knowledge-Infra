import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { KNOWLEDGE_OBJECTS, OPINIONS, REGULATORY_EVENTS, ACTION_ITEMS } from "../../data/mockData";
import { ObjectTypeBadge, StatusBadge } from "../ui/SharedComponents";

export default function SearchOverlay({ isOpen, onClose }) {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");

  // Handle Cmd+K / Esc listener
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  if (!isOpen) return null;

  // Search results
  const matchingEvents = REGULATORY_EVENTS.filter(e => 
    e.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
    e.summary.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const allObjects = [...KNOWLEDGE_OBJECTS, ...OPINIONS];

  const matchingKOs = allObjects.filter(ko => 
    ko.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
    ko.urn.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const matchingActions = ACTION_ITEMS.filter(a => 
    a.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelectResult = (path) => {
    navigate(path);
    onClose();
  };

  return (
    <div className="search-overlay-backdrop" onClick={onClose}>
      <div className="search-overlay-modal card" onClick={(e) => e.stopPropagation()}>
        {/* Search Input */}
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            className="search-input-field"
            type="text"
            placeholder="Search all Knowledge, URNs, Actions, Events..."
            autoFocus
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button className="search-close-btn" onClick={onClose}>ESC</button>
        </div>

        {/* Results Pane */}
        <div className="search-results-pane flex flex-col gap-4">
          
          {/* Regulatory Events */}
          {matchingEvents.length > 0 && (
            <div className="flex flex-col gap-2">
              <span className="text-meta">Regulatory Changes & Events</span>
              {matchingEvents.map(e => (
                <button
                  key={e.id}
                  className="search-result-row card card-compact card-interactive flex items-center justify-between"
                  onClick={() => handleSelectResult(`/changes/${e.id}`)}
                >
                  <div style={{ textAlign: "left" }}>
                    <div style={{ fontWeight: "var(--fw-semibold)" }}>{e.title}</div>
                    <span className="text-small">{e.authority}</span>
                  </div>
                  <span className="text-meta" style={{ fontSize: "10px" }}>Event</span>
                </button>
              ))}
            </div>
          )}

          {/* Knowledge Objects */}
          {matchingKOs.length > 0 && (
            <div className="flex flex-col gap-2">
              <span className="text-meta">Knowledge Objects (URNs)</span>
              {matchingKOs.map(ko => (
                <button
                  key={ko.urn}
                  className="search-result-row card card-compact card-interactive flex items-center justify-between"
                  onClick={() => handleSelectResult("/knowledge")}
                >
                  <div style={{ textAlign: "left" }}>
                    <div style={{ fontWeight: "var(--fw-semibold)" }}>{ko.title}</div>
                    <span className="text-small text-mono" style={{ fontSize: "10px" }}>{ko.urn}</span>
                  </div>
                  <ObjectTypeBadge type={ko.type} />
                </button>
              ))}
            </div>
          )}

          {/* Compliance Actions */}
          {matchingActions.length > 0 && (
            <div className="flex flex-col gap-2">
              <span className="text-meta">Decisions & Actions</span>
              {matchingActions.map(a => (
                <button
                  key={a.id}
                  className="search-result-row card card-compact card-interactive flex items-center justify-between"
                  onClick={() => handleSelectResult("/actions")}
                >
                  <div style={{ textAlign: "left" }}>
                    <div style={{ fontWeight: "var(--fw-semibold)" }}>{a.title}</div>
                    <span className="text-small">Owner: {a.owner}</span>
                  </div>
                  <StatusBadge status={a.status} size="small" />
                </button>
              ))}
            </div>
          )}

          {searchTerm && matchingEvents.length === 0 && matchingKOs.length === 0 && matchingActions.length === 0 && (
            <div style={{ padding: "var(--space-6)", textAlign: "center", color: "var(--text-muted)" }}>
              No matches found for "{searchTerm}"
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
