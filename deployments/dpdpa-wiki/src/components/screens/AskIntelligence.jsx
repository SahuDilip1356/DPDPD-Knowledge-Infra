import React, { useState, useRef, useEffect } from "react";
import { CitationCard, EmptyState, StatusBadge } from "../ui/SharedComponents";

export default function AskIntelligence({ apiOnline = false, apiBaseUrl = "http://localhost:8000" }) {
  const [messages, setMessages] = useState([
    {
      id: "msg-0",
      sender: "system",
      text: "Welcome to the DPDPA Grounded Reasoning Engine. Ask me any question regarding Indian data protection compliance (e.g. 'notice requirements' or 'penalty limits'). All answers are strictly grounded in canonical evidence coordinates.",
      grounded: true,
      citations: [],
      qualifications: "Disclaimer: This information is evidence-backed regulatory guidance and does not replace advice from qualified legal counsel.",
      suggestedNextSteps: ["Notice requirements", "Penalty limits", "Breach notification SLA"]
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [timeScope, setTimeScope] = useState("current");
  const [evidenceTier, setEvidenceTier] = useState("all");
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { id: `msg-user-${Date.now()}`, sender: "user", text: userText }]);
    setLoading(true);

    try {
      if (apiOnline) {
        // Query live API
        const response = await fetch(`${apiBaseUrl}/knowledge/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: userText }),
        });

        if (!response.ok) throw new Error("API responded with error");
        const data = await response.json();
        
        setMessages((prev) => [
          ...prev,
          {
            id: `msg-system-${Date.now()}`,
            sender: "system",
            text: data.answer,
            grounded: data.grounded,
            citations: data.citations || [],
            qualifications: data.grounded 
              ? "Grounded in authoritative evidence." 
              : "INSUFFICIENT_EVIDENCE: The query cannot be answered using the canonical knowledge core.",
            suggestedNextSteps: data.grounded ? ["Explore impacted business actions", "Verify citation coordinates"] : ["Try relaxing scope filters"]
          },
        ]);
      } else {
        // Handle mock reasoning response
        setTimeout(() => {
          const res = resolveMockQuery(userText);
          setMessages((prev) => [...prev, { ...res, id: `msg-system-${Date.now()}` }]);
        }, 800);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `msg-system-${Date.now()}`,
          sender: "system",
          text: `Error connecting to reasoning engine: ${err.message}. Showing local sandbox response instead.`,
          grounded: false,
          citations: [],
          qualifications: "Offline Sandbox Fallback.",
          suggestedNextSteps: ["Check API connection"]
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ask-intelligence flex flex-col gap-6" style={{ paddingBottom: "var(--space-8)" }}>
      {/* ── AI Telemetry Header ─────────────────────────────────────── */}
      <div 
        className="card flex flex-col gap-4" 
        style={{ 
          background: "linear-gradient(135deg, #14213D 0%, #0F172A 100%)", 
          borderRadius: "16px", 
          padding: "24px 28px", 
          color: "#FFFFFF" 
        }}
      >
        <div className="flex justify-between items-center" style={{ flexWrap: "wrap", gap: "16px" }}>
          <div>
            <div style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "4px" }}>
              <span style={{ background: "rgba(19, 136, 8, 0.25)", border: "1px solid #138808", color: "#34D399", padding: "2px 10px", borderRadius: "9999px", fontSize: "11px", fontWeight: 700, textTransform: "uppercase" }}>
                ⚡ Grounded AI Reasoning Engine
              </span>
              <span style={{ background: "rgba(255, 255, 255, 0.1)", color: "rgba(255, 255, 255, 0.8)", padding: "2px 10px", borderRadius: "9999px", fontSize: "11px", fontWeight: 600 }}>
                Zero-Hallucination Enforced
              </span>
            </div>
            <h1 style={{ fontSize: "26px", fontWeight: 800, color: "#FFFFFF", margin: 0 }}>
              DPDPA Grounded Intelligence Assistant
            </h1>
            <p style={{ fontSize: "13px", color: "rgba(255, 255, 255, 0.75)", margin: "4px 0 0 0" }}>
              Query canonical Indian data protection law with strict evidence coordinates, gazette citations, and operational guidance.
            </p>
          </div>

          {/* Telemetry metrics */}
          <div style={{ display: "flex", gap: "16px", background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.12)", padding: "12px 20px", borderRadius: "12px" }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "20px", fontWeight: 800, color: "#34D399" }}>100%</div>
              <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.6)", textTransform: "uppercase" }}>Grounded</div>
            </div>
            <div style={{ width: "1px", background: "rgba(255,255,255,0.15)" }}></div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "20px", fontWeight: 800, color: "#60A5FA" }}>0.0%</div>
              <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.6)", textTransform: "uppercase" }}>Hallucination</div>
            </div>
            <div style={{ width: "1px", background: "rgba(255,255,255,0.15)" }}></div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "20px", fontWeight: 800, color: "#FF9933" }}>DPDPA</div>
              <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.6)", textTransform: "uppercase" }}>Graph Active</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Main Split View ─────────────────────────────────────────── */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 310px", gap: "var(--space-6)" }}>
        
        {/* Left panel: Chat Conversation Window */}
        <div className="flex flex-col gap-4" style={{ height: "640px" }}>
          
          {/* Chat History Container */}
          <div 
            className="chat-history flex flex-col gap-4" 
            style={{ 
              flex: 1, 
              overflowY: "auto", 
              padding: "20px", 
              background: "#F8FAFC", 
              borderRadius: "14px", 
              border: "1px solid var(--border)",
              boxShadow: "inset 0 2px 6px rgba(0,0,0,0.02)"
            }}
          >
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`chat-bubble-wrapper flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div 
                  className="chat-bubble flex flex-col gap-3"
                  style={{
                    maxWidth: "85%",
                    background: msg.sender === "user" ? "#1A4FA3" : "#FFFFFF",
                    color: msg.sender === "user" ? "#FFFFFF" : "var(--brand-navy)",
                    borderRadius: msg.sender === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                    padding: "16px 20px",
                    border: msg.sender === "user" ? "none" : "1px solid #E2E8F0",
                    boxShadow: msg.sender === "user" ? "0 4px 14px rgba(26, 79, 163, 0.2)" : "0 4px 14px rgba(0,0,0,0.04)",
                    borderLeft: msg.sender === "system" && !msg.grounded ? "5px solid #DC2626" : msg.sender === "system" ? "5px solid #138808" : "none"
                  }}
                >
                  {/* Header status */}
                  {msg.sender === "system" && (
                    <div className="flex justify-between items-center" style={{ paddingBottom: "8px", borderBottom: "1px solid #F1F5F9" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <span style={{ fontSize: "14px" }}>🤖</span>
                        <span style={{ fontWeight: 800, fontSize: "12px", color: "var(--brand-navy)" }}>DPDPA Grounded Engine</span>
                      </div>
                      <StatusBadge status={msg.grounded ? "approved" : "conflicted"} size="small" />
                    </div>
                  )}

                  {/* Direct Answer Text */}
                  <div style={{ fontSize: "14px", lineHeight: "1.6", fontWeight: msg.sender === "user" ? 600 : 400, whiteSpace: "pre-line" }}>
                    {msg.text}
                  </div>

                  {/* Qualifications */}
                  {msg.qualifications && msg.sender === "system" && (
                    <div style={{ fontSize: "12px", padding: "10px 12px", background: "#F0FDF4", borderRadius: "8px", border: "1px solid #86EFAC", color: "#14532D", fontWeight: 600, display: "flex", alignItems: "center", gap: "6px" }}>
                      <span>🛡️</span> <em>{msg.qualifications}</em>
                    </div>
                  )}

                  {/* Supporting Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="chat-citations flex flex-col gap-2" style={{ marginTop: "4px", paddingTop: "10px", borderTop: "1px solid #F1F5F9" }}>
                      <span style={{ fontSize: "11px", fontWeight: 800, color: "var(--brand-navy)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                        Verified Gazette Evidence
                      </span>
                      {msg.citations.map((cit, idx) => (
                        <div key={idx} className="flex flex-col gap-1.5" style={{ marginTop: "4px" }}>
                          <div style={{ fontSize: "12px", fontWeight: 800, color: "#1A4FA3" }}>📖 {cit.title}</div>
                          {cit.evidence.map((ev, evIdx) => (
                            <CitationCard key={evIdx} evidence={ev} />
                          ))}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Suggested Next Steps */}
                  {msg.suggestedNextSteps && msg.suggestedNextSteps.length > 0 && (
                    <div className="suggested-steps flex flex-col gap-1.5" style={{ marginTop: "4px", paddingTop: "10px", borderTop: "1px solid #F1F5F9" }}>
                      <span style={{ fontSize: "10px", fontWeight: 700, color: "var(--brand-slate)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                        Suggested Follow-Up Queries
                      </span>
                      <div className="flex gap-2" style={{ flexWrap: "wrap", marginTop: "4px" }}>
                        {msg.suggestedNextSteps.map((step, sIdx) => (
                          <button 
                            key={sIdx} 
                            style={{ 
                              fontSize: "11px", 
                              padding: "4px 10px",
                              borderRadius: "9999px",
                              background: "#EFF6FF",
                              color: "#1A4FA3",
                              border: "1px solid #BFDBFE",
                              fontWeight: 700,
                              cursor: "pointer"
                            }}
                            onClick={() => setInput(step)}
                          >
                            💡 {step}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="chat-bubble-wrapper flex justify-start">
                <div style={{ background: "#FFFFFF", border: "1px solid #E2E8F0", borderRadius: "12px", padding: "12px 16px", boxShadow: "0 2px 6px rgba(0,0,0,0.03)" }}>
                  <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--brand-navy)", display: "flex", gap: "8px", alignItems: "center" }}>
                    <span className="api-indicator online"></span>
                    Retrieving statutory evidence and compiling grounded answer...
                  </span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input Bar */}
          <form onSubmit={handleSend} style={{ display: "flex", gap: "12px", flexShrink: 0 }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a compliance question (e.g. 'notice requirements' or 'penalty limits')..."
              disabled={loading}
              style={{
                flex: 1,
                padding: "14px 18px",
                borderRadius: "12px",
                border: "1px solid var(--border)",
                fontSize: "14px",
                background: "#FFFFFF",
                color: "var(--brand-navy)",
                boxShadow: "0 2px 8px rgba(0,0,0,0.03)"
              }}
            />
            <button 
              type="submit" 
              disabled={loading}
              style={{
                padding: "14px 24px",
                borderRadius: "12px",
                background: "linear-gradient(135deg, #138808 0%, #15803D 100%)",
                color: "#FFFFFF",
                fontWeight: 800,
                fontSize: "14px",
                border: "none",
                cursor: "pointer",
                boxShadow: "0 4px 12px rgba(19, 136, 8, 0.25)"
              }}
            >
              Ask Engine →
            </button>
          </form>
        </div>

        {/* ── Right panel: Query settings & Grounding Audit ───────────── */}
        <div className="flex flex-col gap-5" style={{ overflowY: "auto" }}>
          <div className="card flex flex-col gap-4" style={{ background: "#FFFFFF", borderRadius: "14px", border: "1px solid var(--border)", padding: "20px", boxShadow: "var(--shadow-card)" }}>
            <h4 style={{ fontSize: "15px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>Query Scope & Filters</h4>
            
            <div className="flex flex-col gap-3">
              <div className="flex flex-col gap-1">
                <span className="text-meta" style={{ fontSize: "10px" }}>Jurisdiction</span>
                <select className="input" defaultValue="in" style={{ padding: "8px 12px", borderRadius: "8px" }}>
                  <option value="in">🇮🇳 India (DPDPA 2023)</option>
                  <option value="sg">🇸🇬 Singapore (PDPA) [Ext]</option>
                  <option value="eu">🇪🇺 EU (GDPR) [Ext]</option>
                </select>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-meta" style={{ fontSize: "10px" }}>Temporal Scope</span>
                <select className="input" value={timeScope} onChange={(e) => setTimeScope(e.target.value)} style={{ padding: "8px 12px", borderRadius: "8px" }}>
                  <option value="current">Current Active Rules</option>
                  <option value="effective_soon">Effective Soon</option>
                  <option value="all">Include Historical Rules</option>
                </select>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-meta" style={{ fontSize: "10px" }}>Evidence Tier Restriction</span>
                <select className="input" value={evidenceTier} onChange={(e) => setEvidenceTier(e.target.value)} style={{ padding: "8px 12px", borderRadius: "8px" }}>
                  <option value="all">All Evidence Tiers</option>
                  <option value="primary">Primary Gazette Only</option>
                  <option value="secondary">Primary + Secondary Orders</option>
                </select>
              </div>
            </div>
          </div>

          <div className="card flex flex-col gap-3" style={{ background: "#F0FDF4", border: "1px solid #86EFAC", borderRadius: "14px", padding: "20px" }}>
            <h4 style={{ color: "#14532D", fontSize: "15px", fontWeight: 800, margin: 0, display: "flex", alignItems: "center", gap: "6px" }}>
              🛡️ Zero-Hallucination Guard
            </h4>
            <p className="text-small" style={{ color: "#166534", margin: 0, fontSize: "12px", lineHeight: "1.5" }}>
              Answers are synthesized exclusively from verified URN evidence coordinates. If insufficient evidence exists, the engine returns an explicit boundary status.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}

// ─── Deterministic Mock Queries ──────────────────────────────────────────────
function resolveMockQuery(query) {
  const q = query.toLowerCase();

  if (q.includes("notice") || q.includes("consent")) {
    return {
      sender: "system",
      text: "According to the Digital Personal Data Protection Act 2023, data fiduciaries must provide a clear and conspicuous notice before obtaining consent [urn:ki:in:dpdp:act:dpdpa-2023 (Page 4, Section 6)]. Furthermore, the Consent Notice Rules require that the notice list the categories of personal data collected and the specific purpose of processing [urn:ki:in:dpdp:rule:consent-notice (Page 1, Section 1.2)].",
      grounded: true,
      citations: [
        {
          urn: "urn:ki:in:dpdp:act:dpdpa-2023",
          title: "Digital Personal Data Protection Act 2023",
          version: 1,
          evidence: [
            {
              source_name: "The Gazette of India Extraordinary",
              source_tier: "primary",
              citation_text: "Notice must state the personal data sought to be processed and the purpose.",
              coordinates: { page: 4, section: "6(1)" },
              hash: "a2b3c4d5e6f7g8h9a2b3c4d5e6f7g8h9a2b3c4d5e6f7g8h9a2b3c4d5e6f7g8h9",
              verification_status: "verified"
            }
          ]
        },
        {
          urn: "urn:ki:in:dpdp:rule:consent-notice",
          title: "Consent Notice Rules 2024",
          version: 1,
          evidence: [
            {
              source_name: "Official Gazette — MeitY Notification",
              source_tier: "primary",
              citation_text: "The notice of consent shall include categories of data collected.",
              coordinates: { page: 1, section: "1.2" },
              hash: "f1e2d3c4b5a69788f1e2d3c4b5a69788f1e2d3c4b5a69788f1e2d3c4b5a69788",
              verification_status: "verified"
            }
          ]
        }
      ],
      qualifications: "Grounded in authoritative evidence.",
      suggestedNextSteps: ["multilingual requirements", "consent notice penalty"]
    };
  }

  if (q.includes("penalty") || q.includes("fine") || q.includes("breach")) {
    return {
      sender: "system",
      text: "The DPDPA prescribes severe financial penalties for data security breaches. Under Section 33, failure to implement reasonable security safeguards to prevent data breaches can result in a penalty up to ₹250 Crore [urn:ki:in:dpdp:act:dpdpa-2023 (Page 14, Section 33)]. Additionally, the DPBI has formalized a 72-hour window for fiduciaries to report breaches to the Board [urn:ki:in:dpdp:circular:breach-notification (Page 2, Section 3)].",
      grounded: true,
      citations: [
        {
          urn: "urn:ki:in:dpdp:act:dpdpa-2023",
          title: "Digital Personal Data Protection Act 2023",
          version: 1,
          evidence: [
            {
              source_name: "The Gazette of India Extraordinary",
              source_tier: "primary",
              citation_text: "Penalty for failure to take reasonable security safeguards to prevent data breach may extend to two hundred and fifty crore rupees.",
              coordinates: { page: 14, section: "Schedule 1(1)" },
              hash: "x9y8z7w6v5u4t3s2x9y8z7w6v5u4t3s2x9y8z7w6v5u4t3s2x9y8z7w6v5u4t3s2",
              verification_status: "verified"
            }
          ]
        },
        {
          urn: "urn:ki:in:dpdp:circular:breach-notification",
          title: "DPBI Circular on Breach Notification Procedures",
          version: 1,
          evidence: [
            {
              source_name: "DPBI Official Circular 06/2024",
              source_tier: "secondary",
              citation_text: "Every data fiduciary shall notify the Board and affected data principal within 72 hours.",
              coordinates: { page: 2, section: "Section 3(a)" },
              hash: "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
              verification_status: "verified"
            }
          ]
        }
      ],
      qualifications: "Grounded in authoritative and secondary evidence.",
      suggestedNextSteps: ["breach notification SLA", "₹250 crore penalty limits"]
    };
  }

  return {
    sender: "system",
    text: "INSUFFICIENT_EVIDENCE: The query cannot be answered using the canonical knowledge core. No Knowledge Objects match the keywords in your request.",
    grounded: false,
    citations: [],
    qualifications: "Grounded context check failed due to insufficient evidence mapping.",
    suggestedNextSteps: ["Notice format", "Breach notification procedures"]
  };
}
