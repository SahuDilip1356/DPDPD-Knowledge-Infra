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
    <div className="ask-intelligence" style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: "var(--space-6)" }}>
      {/* ── Left panel: Chat Interface ──────────────────────────────── */}
      <div className="flex flex-col gap-4" style={{ height: "calc(100vh - var(--topbar-height) - 2 * var(--space-6))" }}>
        
        {/* Chat History */}
        <div className="chat-history card flex flex-col gap-4" style={{ flex: 1, overflowY: "auto", padding: "var(--space-4)", background: "var(--bg-cloud)" }}>
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`chat-bubble-wrapper flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div 
                className="chat-bubble card card-compact"
                style={{
                  maxWidth: "80%",
                  background: msg.sender === "user" ? "var(--bg-selected)" : "var(--bg-white)",
                  borderColor: msg.sender === "user" ? "var(--verification-green)" : "var(--border)",
                  borderLeft: msg.sender === "system" && !msg.grounded ? "4px solid var(--status-conflict)" : ""
                }}
              >
                {/* Header status */}
                {msg.sender === "system" && (
                  <div className="flex justify-between items-center" style={{ marginBottom: "var(--space-2)", borderBottom: "1px solid var(--border)", paddingBottom: "4px" }}>
                    <span className="text-meta" style={{ fontSize: "10px" }}>Reasoning Engine</span>
                    <StatusBadge status={msg.grounded ? "approved" : "conflicted"} size="small" />
                  </div>
                )}

                {/* Direct Answer */}
                <div className="text-body" style={{ whiteSpace: "pre-line" }}>{msg.text}</div>

                {/* Qualifications */}
                {msg.qualifications && (
                  <div className="text-small" style={{ marginTop: "var(--space-2)", padding: "var(--space-2)", background: "var(--bg-cloud)", borderRadius: "var(--radius-sm)", borderLeft: "2px solid var(--border-strong)" }}>
                    💡 <em>{msg.qualifications}</em>
                  </div>
                )}

                {/* Supporting Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="chat-citations flex flex-col gap-2" style={{ marginTop: "var(--space-3)", borderTop: "1px solid var(--border)", paddingTop: "var(--space-2)" }}>
                    <span className="text-meta">Supporting Claims & Evidence</span>
                    {msg.citations.map((cit, idx) => (
                      <div key={idx} className="flex flex-col gap-1">
                        <div className="text-small" style={{ fontWeight: "var(--fw-semibold)" }}>{cit.title}</div>
                        {cit.evidence.map((ev, evIdx) => (
                          <CitationCard key={evIdx} evidence={ev} />
                        ))}
                      </div>
                    ))}
                  </div>
                )}

                {/* Suggested Next Steps */}
                {msg.suggestedNextSteps && msg.suggestedNextSteps.length > 0 && (
                  <div className="suggested-steps flex flex-col gap-1" style={{ marginTop: "var(--space-3)", borderTop: "1px solid var(--border)", paddingTop: "var(--space-2)" }}>
                    <span className="text-meta" style={{ fontSize: "9px" }}>Suggested Investigations</span>
                    <div className="flex gap-2" style={{ marginTop: "4px" }}>
                      {msg.suggestedNextSteps.map((step, sIdx) => (
                        <button 
                          key={sIdx} 
                          className="filter-pill" 
                          style={{ fontSize: "11px", padding: "2px 8px" }}
                          onClick={() => setInput(step)}
                        >
                          {step}
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
              <div className="card card-compact" style={{ background: "var(--bg-white)" }}>
                <span className="text-small flex gap-2 items-center">
                  <span className="api-indicator online"></span>
                  Reasoning Department generating insights...
                </span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="flex gap-3" style={{ flexShrink: 0 }}>
          <input
            type="text"
            className="input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a compliance question... (e.g. 'notice requirements')"
            disabled={loading}
          />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            Send Q&A
          </button>
        </form>
      </div>

      {/* ── Right panel: Query settings ─────────────────────────────── */}
      <div className="flex flex-col gap-6" style={{ borderLeft: "1px solid var(--border)", paddingLeft: "var(--space-4)", overflowY: "auto" }}>
        <div className="card flex flex-col gap-4">
          <h4>Query Settings</h4>
          
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-1">
              <span className="text-meta">Jurisdiction</span>
              <select className="input" defaultValue="in">
                <option value="in">India (DPDPA)</option>
                <option value="sg">Singapore (PDPA) [Ext]</option>
                <option value="eu">EU (GDPR) [Ext]</option>
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <span className="text-meta">Temporal Scope</span>
              <select className="input" value={timeScope} onChange={(e) => setTimeScope(e.target.value)}>
                <option value="current">Current Active Rules</option>
                <option value="effective_soon">Effective Soon</option>
                <option value="all">Include Historical Rules</option>
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <span className="text-meta">Evidence Tier Restriction</span>
              <select className="input" value={evidenceTier} onChange={(e) => setEvidenceTier(e.target.value)}>
                <option value="all">All Evidence Tiers</option>
                <option value="primary">Primary Gazette/Legislation Only</option>
                <option value="secondary">Primary + Secondary Board Orders</option>
              </select>
            </div>
          </div>
        </div>

        <div className="card flex flex-col gap-3" style={{ background: "var(--status-review-bg)", borderColor: "var(--warning-border)" }}>
          <h4 style={{ color: "#92400E" }}>🛡️ Grounded Reasoning</h4>
          <p className="text-small" style={{ color: "#78350F", lineHeight: "1.5" }}>
            The engine retrieves Knowledge Objects matching your query context, compiles them into a prompt constrained to evidence coordinates, and returns a verified answer.
          </p>
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
