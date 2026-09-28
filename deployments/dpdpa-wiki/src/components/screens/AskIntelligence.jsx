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

  // A question arriving from the homepage search runs once on mount, so the
  // reader lands on an answer rather than an empty box they must retype into.
  const seeded = useRef(false);
  useEffect(() => {
    if (seeded.current) return;
    const q = new URLSearchParams(window.location.search).get("q");
    if (!q) return;
    seeded.current = true;
    handleSend(null, q);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /**
   * `overrideText` lets a caller send a question that is not yet in `input` —
   * the homepage hero hands its query over through ?q=, and reading state set
   * in the same tick would still see the previous value.
   */
  const handleSend = async (e, overrideText) => {
    e?.preventDefault();
    const userText = (overrideText ?? input).trim();
    if (!userText || loading) return;

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
            </div>
            <h1 style={{ fontSize: "26px", fontWeight: 800, color: "#FFFFFF", margin: 0 }}>
              DPDPA Grounded Intelligence Assistant
            </h1>
            <p style={{ fontSize: "13px", color: "rgba(255, 255, 255, 0.75)", margin: "4px 0 0 0" }}>
              Query canonical Indian data protection law with strict evidence coordinates, gazette citations, and operational guidance.
            </p>
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
              🛡️ Evidence Boundary
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

  // Offline answers cite only the two gazetted documents. citation_text is
  // verbatim from the Act (Gazette No. 22 of 2023) and the Rules (G.S.R. 846(E));
  // the hash is the SHA-256 of the MeitY PDF the text was read from.
  if (q.includes("notice") || q.includes("consent")) {
    return {
      sender: "system",
      text: "Under Section 5(1) of the Digital Personal Data Protection Act 2023, every request for consent under Section 6 must be accompanied or preceded by a notice telling the Data Principal what personal data is proposed to be processed and for what purpose, how she may exercise her rights, and how she may complain to the Board [urn:ki:in:dpdp:act:dpdpa-2023 (Section 5(1))]. Rule 3 of the DPDP Rules 2025 adds that the notice must be understandable on its own, use clear and plain language, itemise the personal data and the specified purposes, and give the link and means to withdraw consent, exercise rights and complain to the Board [urn:ki:in:dpdp:rule:dpdp-rules-2025 (Rule 3)].",
      grounded: true,
      citations: [
        {
          urn: "urn:ki:in:dpdp:act:dpdpa-2023",
          title: "Digital Personal Data Protection Act 2023",
          version: 1,
          evidence: [
            {
              source_name: "The Gazette of India Extraordinary, Part II, Section 1, No. 22 of 2023",
              source_tier: "primary",
              citation_text: "Every request made to a Data Principal under section 6 for consent shall be accompanied or preceded by a notice given by the Data Fiduciary to the Data Principal, informing her,— (i) the personal data and the purpose for which the same is proposed to be processed; (ii) the manner in which she may exercise her rights under sub-section (4) of section 6 and section 13; and (iii) the manner in which the Data Principal may make a complaint to the Board, in such manner and as may be prescribed.",
              coordinates: { section: "5(1)" },
              hash: "4deb23981d3010c8225a2ff6149e7243dc2268455b299e283afebdd7b72a7d15",
              verification_status: "verified"
            }
          ]
        },
        {
          urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
          title: "Digital Personal Data Protection Rules 2025",
          version: 1,
          evidence: [
            {
              source_name: "Ministry of Electronics and Information Technology, G.S.R. 846(E), 13 November 2025",
              source_tier: "primary",
              citation_text: "give, in clear and plain language, a fair account of the details necessary to enable the Data Principal to give specific and informed consent for the processing of her personal data, which shall include, at the minimum, — (i) an itemised description of such personal data; and (ii) the specified purpose or purposes of, and specific description of the goods or services to be provided or uses to be enabled by, such processing",
              coordinates: { section: "Rule 3(b)" },
              hash: "eabc7d05e013144615d78ddc0e8b9c9aac1920e814f4fad38ce6560951f5aa08",
              verification_status: "verified"
            }
          ]
        }
      ],
      qualifications: "Grounded in the gazetted text of the Act and the Rules.",
      suggestedNextSteps: ["notice languages under Section 5(3)", "penalty schedule"]
    };
  }

  if (q.includes("penalty") || q.includes("fine") || q.includes("breach")) {
    return {
      sender: "system",
      text: "The Schedule to the Act (see Section 33(1)) sets a maximum penalty for each kind of breach. Failing to take reasonable security safeguards under Section 8(5) may extend to ₹250 crore; failing to give the Board or affected Data Principals notice of a breach under Section 8(6) may extend to ₹200 crore [urn:ki:in:dpdp:act:dpdpa-2023 (Schedule)]. Penalties are imposed by the Data Protection Board after an inquiry, and every figure is a ceiling, not a fixed fine. On becoming aware of a breach, Rule 7(2) of the DPDP Rules 2025 requires the Data Fiduciary to intimate the Board without delay and to provide detailed information within seventy-two hours, or such longer period as the Board allows [urn:ki:in:dpdp:rule:dpdp-rules-2025 (Rule 7(2))].",
      grounded: true,
      citations: [
        {
          urn: "urn:ki:in:dpdp:act:dpdpa-2023",
          title: "Digital Personal Data Protection Act 2023",
          version: 1,
          evidence: [
            {
              source_name: "The Gazette of India Extraordinary, Part II, Section 1, No. 22 of 2023",
              source_tier: "primary",
              citation_text: "Breach in observing the obligation of Data Fiduciary to take reasonable security safeguards to prevent personal data breach under sub-section (5) of section 8 — May extend to two hundred and fifty crore rupees.",
              coordinates: { section: "Schedule, entry 1" },
              hash: "4deb23981d3010c8225a2ff6149e7243dc2268455b299e283afebdd7b72a7d15",
              verification_status: "verified"
            }
          ]
        },
        {
          urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
          title: "Digital Personal Data Protection Rules 2025",
          version: 1,
          evidence: [
            {
              source_name: "Ministry of Electronics and Information Technology, G.S.R. 846(E), 13 November 2025",
              source_tier: "primary",
              citation_text: "On becoming aware of any personal data breach, the Data Fiduciary shall intimate to the Board, — (a) without delay, a description of the breach, including its nature, extent, timing and location of occurrence and the likely impact; (b) within seventy-two hours of becoming aware of the breach, or within such longer period as the Board may allow on a request made in writing in this behalf, — (i) updated and detailed information in respect of such description",
              coordinates: { section: "Rule 7(2)" },
              hash: "eabc7d05e013144615d78ddc0e8b9c9aac1920e814f4fad38ce6560951f5aa08",
              verification_status: "verified"
            }
          ]
        }
      ],
      qualifications: "Grounded in the gazetted text of the Act and the Rules.",
      suggestedNextSteps: ["breach intimation under Rule 7", "Schedule penalty limits"]
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
