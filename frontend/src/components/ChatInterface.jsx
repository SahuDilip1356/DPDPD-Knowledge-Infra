import React, { useState, useRef, useEffect } from "react";

export default function ChatInterface({ apiOnline, apiBaseUrl }) {
  const [messages, setMessages] = useState([
    {
      sender: "system",
      text: "Welcome to the DPDPA Grounded Reasoning Engine. Ask me any question regarding Indian data protection compliance (e.g. 'notice requirements' or 'penalty limits'). All answers are strictly grounded in canonical evidence coordinates.",
      grounded: true,
      citations: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
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
    setMessages((prev) => [...prev, { sender: "user", text: userText }]);
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
            sender: "system",
            text: data.answer,
            grounded: data.grounded,
            citations: data.citations || [],
          },
        ]);
      } else {
        // Handle mock reasoning response
        setTimeout(() => {
          const res = resolveMockQuery(userText);
          setMessages((prev) => [...prev, res]);
        }, 800);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "system",
          text: `Error connecting to reasoning engine: ${err.message}. Showing local sandbox response instead.`,
          grounded: false,
          citations: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel chat-container">
      <div className="chat-history">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`chat-bubble ${msg.sender} ${!msg.grounded ? "ungrounded" : ""}`}
          >
            <div>{msg.text}</div>
            
            {msg.citations && msg.citations.length > 0 && (
              <div className="citation-list">
                <div className="citation-title">🛡️ Verified Source Citations</div>
                {msg.citations.map((cit, idx) => (
                  <div key={idx} className="citation-item">
                    <div className="citation-meta">
                      <span className="citation-urn">{cit.urn} (v{cit.version})</span>
                    </div>
                    {cit.evidence && cit.evidence.map((ev, evIdx) => (
                      <div key={evIdx} className="citation-text">
                        "{ev.citation_text}" 
                        <span style={{ color: "var(--text-muted)", marginLeft: "0.5rem" }}>
                          (Page {ev.coordinates?.page}, Sec {ev.coordinates?.section}, Hash: {ev.coordinates?.hash?.substring(0, 8)})
                        </span>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="chat-bubble system" style={{ display: "flex", gap: "0.5rem" }}>
            <span className="api-indicator online" style={{ animation: "pulse 1s infinite alternate" }}></span>
            <span>Reasoning Department generating insights...</span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <form onSubmit={handleSend} className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a compliance question... (e.g. 'what are consent notice requirements?')"
          className="chat-input"
          disabled={loading}
        />
        <button type="submit" className="chat-send-btn" disabled={loading}>
          Send
        </button>
      </form>
    </div>
  );
}

// ─── Deterministic Mock Queries ──────────────────────────────────────────────
function resolveMockQuery(query) {
  const q = query.toLowerCase();

  if (q.includes("notice") || q.includes("consent")) {
    return {
      sender: "system",
      text: "According to the Digital Personal Data Protection Act 2023, data fiduciaries must provide a clear and conspicuous notice before obtaining consent [urn:ki:in:dpdp:act:dpdpa-2023 (Page 4, Section 6, Hash: a2b3c4d5)]. Furthermore, the Consent Notice Rules require that the notice list the categories of personal data collected and the specific purpose of processing [urn:ki:in:dpdp:rule:consent-notice (Page 1, Section 1, Hash: f1e2d3c4)].",
      grounded: true,
      citations: [
        {
          urn: "urn:ki:in:dpdp:act:dpdpa-2023",
          title: "Digital Personal Data Protection Act 2023",
          version: 1,
          evidence: [
            {
              citation_text: "Notice must state the personal data sought to be processed and the purpose.",
              coordinates: { page: 4, section: "6(1)", hash: "a2b3c4d5e6f7g8h9" }
            }
          ]
        },
        {
          urn: "urn:ki:in:dpdp:rule:consent-notice",
          title: "Consent Notice Rules 2024",
          version: 1,
          evidence: [
            {
              citation_text: "The notice of consent shall include categories of data collected.",
              coordinates: { page: 1, section: "1.2", hash: "f1e2d3c4b5a69788" }
            }
          ]
        }
      ]
    };
  }

  if (q.includes("penalty") || q.includes("fine") || q.includes("breach")) {
    return {
      sender: "system",
      text: "The DPDPA prescribes severe financial penalties for data security breaches. Under Section 33, failure to implement reasonable security safeguards to prevent data breaches can result in a penalty up to ₹250 Crore [urn:ki:in:dpdp:act:dpdpa-2023 (Page 14, Section 33, Hash: x9y8z7w6)]. The Data Protection Board of India (DPBI) will evaluate the breach severity to determine the exact fine.",
      grounded: true,
      citations: [
        {
          urn: "urn:ki:in:dpdp:act:dpdpa-2023",
          title: "Digital Personal Data Protection Act 2023",
          version: 1,
          evidence: [
            {
              citation_text: "Penalty for failure to take reasonable security safeguards to prevent data breach may extend to two hundred and fifty crore rupees.",
              coordinates: { page: 14, section: "Schedule 1(1)", hash: "x9y8z7w6v5u4t3s2" }
            }
          ]
        }
      ]
    };
  }

  return {
    sender: "system",
    text: "INSUFFICIENT_EVIDENCE: The query cannot be answered using the canonical knowledge core. No Knowledge Objects match the keywords in your request.",
    grounded: false,
    citations: []
  };
}
