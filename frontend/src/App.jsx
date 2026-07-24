import React, { useState, useEffect } from "react";
import "./App.css";

import ChatInterface from "./components/ChatInterface";
import GraphExplorer from "./components/GraphExplorer";
import BusinessActions from "./components/BusinessActions";
import GitTimeline from "./components/GitTimeline";

const API_BASE_URL = "http://localhost:8000";

// ─── Shared Mock Data ────────────────────────────────────────────────────────
const MOCK_KNOWLEDGE_OBJECTS = [
  {
    urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    title: "Digital Personal Data Protection Act 2023",
    version: 1,
    date: "2023-08-11",
    confidence_score: 0.98,
    summary: "The foundational privacy legislation passed by the Parliament of India. Establishes the rights of data principals, duties of data fiduciaries, security mandates, and structures the Data Protection Board of India (DPBI) to enforce compliance.",
    entities: ["Act", "Consent", "Purpose", "Legal Basis", "Penalty", "Authority"],
    relations: [],
    evidence: [
      {
        source_urn: "urn:ki:in:dpdp:source:parliament-gazette-2023",
        citation_text: "An Act to provide for the processing of digital personal data in a manner that recognizes both the right of individuals to protect their personal data and the need to process such personal data for lawful purposes.",
        coordinates: { page: 1, section: "Preamble", hash: "a1c2e3f4" + "0" * 56 }
      },
      {
        source_urn: "urn:ki:in:dpdp:source:parliament-gazette-2023",
        citation_text: "Penalty for failure to take reasonable security safeguards to prevent personal data breach under section 8 may extend to two hundred and fifty crore rupees.",
        coordinates: { page: 14, section: "Schedule 1", hash: "x9y8z7w6" + "0" * 56 }
      }
    ],
    business_impact: {
      impact_summary: "Establishes a mandatory legal basis for processing personal data, requiring either explicit consent or specified legitimate uses.",
      action_required: "Conduct data mapping, review privacy notices, and audit consent flows to ensure compliance with Sections 4, 5, and 6."
    }
  },
  {
    urn: "urn:ki:in:dpdp:rule:consent-notice",
    title: "Consent Notice Rules 2024",
    version: 1,
    date: "2024-03-15",
    confidence_score: 0.92,
    summary: "Rules detailing format, requirements, and languages of the consent notices. Mandates that notices must list categories of personal data collected, specific processing purposes, and methods for withdrawing consent.",
    entities: ["Rule", "Consent", "Purpose", "Data Category"],
    relations: [
      {
        target_urn: "urn:ki:in:dpdp:act:dpdpa-2023",
        edge_type: "Depends On"
      }
    ],
    evidence: [
      {
        source_urn: "urn:ki:in:dpdp:source:gazette-rules-2024",
        citation_text: "The notice of consent under Section 6(1) shall list the items of personal data to be collected, processing purpose, and right of withdrawal.",
        coordinates: { page: 1, section: "Rule 1.2", hash: "f1e2d3c4" + "0" * 56 }
      }
    ],
    business_impact: {
      impact_summary: "Standardizes notices. Introduces strict formatting requirements for consumer privacy policies.",
      action_required: "Modify user consent notices on websites and mobile apps. Add language translation capabilities for 8th Schedule languages."
    }
  },
  {
    urn: "urn:ki:in:dpdp:circular:breach-notification",
    title: "DPBI Circular on Breach Notification Procedures",
    version: 1,
    date: "2024-06-20",
    confidence_score: 0.88,
    summary: "Guideline issued by the Data Protection Board of India regarding breach reporting timelines and templates. Establishes a 72-hour notification window for notifying the Board and affected data principals.",
    entities: ["Circular", "Notification", "Penalty"],
    relations: [
      {
        target_urn: "urn:ki:in:dpdp:act:dpdpa-2023",
        edge_type: "Interprets"
      }
    ],
    evidence: [
      {
        source_urn: "urn:ki:in:dpdp:source:dpbi-circular-06-2024",
        citation_text: "Every data fiduciary shall, in the event of a personal data breach, notify the Board and each affected data principal within 72 hours of detection.",
        coordinates: { page: 2, section: "Section 3(a)", hash: "b2c3d4e5" + "0" * 56 }
      }
    ],
    business_impact: {
      impact_summary: "Enforces strict time bounds on incident response. Non-reporting will be treated as an independent violation.",
      action_required: "Deploy automated breach incident detection. Update the Incident Response Policy and train the security team on the 72-hour SLA."
    }
  }
];

const MOCK_ACTION_ITEMS = [
  {
    urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    ko_title: "Audit Consent Architecture (Sections 4, 5, 6)",
    priority: "CRITICAL",
    affected_roles: ["Chief Privacy Officer", "Data Protection Officer", "Legal Counsel"],
    action_description: "Audit current processing activities and mapping documents to confirm legal basis (consent or legitimate use) for every data item collected.",
    deadline_category: "IMMEDIATE (within 7 days)"
  },
  {
    urn: "urn:ki:in:dpdp:rule:consent-notice",
    ko_title: "Notice Translation & Localization (Consent Notice Rules)",
    priority: "HIGH",
    affected_roles: ["Product Manager", "Engineering Lead", "Marketing Director"],
    action_description: "Update online privacy consent dialogs to specify data categories, purpose of processing, and provide translation options in English and regional languages.",
    deadline_category: "SHORT_TERM (within 30 days)"
  },
  {
    urn: "urn:ki:in:dpdp:circular:breach-notification",
    ko_title: "Implement Incident Reporting Playbook (DPBI SLA)",
    priority: "CRITICAL",
    affected_roles: ["IT Security Lead", "Data Protection Officer", "CEO / Managing Director"],
    action_description: "Update the Data Security Incident SOP to support the Board and principal notification forms within the 72-hour detection window.",
    deadline_category: "IMMEDIATE (within 7 days)"
  },
  {
    urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    ko_title: "CISO Review of Security Safeguards (Section 8)",
    priority: "HIGH",
    affected_roles: ["IT Security Lead", "Compliance Manager"],
    action_description: "Verify technical compliance controls including data encryption at rest and in transit to prevent ₹250 Crore penalty triggers.",
    deadline_category: "SHORT_TERM (within 30 days)"
  }
];

const MOCK_TIMELINE_EVENTS = [
  {
    commit_hash: "a2f9e4d",
    system_time: "2026-07-24 07:12:00",
    commit_message: "Publish: Ingested Digital Personal Data Protection Act 2023 (v1)",
    author_id: "publishing_agent",
    version: 1
  },
  {
    commit_hash: "7f4c3a2",
    system_time: "2026-07-24 07:45:00",
    commit_message: "Publish: Ingested Consent Notice Rules 2024 (v1)",
    author_id: "publishing_agent",
    version: 1
  },
  {
    commit_hash: "d9e8b1a",
    system_time: "2026-07-24 08:15:00",
    commit_message: "Publish: DPBI Circular on Breach Notification Procedures (v1)",
    author_id: "publishing_agent",
    version: 1
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [apiOnline, setApiOnline] = useState(false);
  const [loadingHealth, setLoadingHealth] = useState(true);

  // Check API health status
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`, { method: "GET" });
        if (response.ok) {
          setApiOnline(true);
        } else {
          setApiOnline(false);
        }
      } catch (err) {
        setApiOnline(false);
      } finally {
        setLoadingHealth(false);
      }
    };
    checkHealth();
  }, []);

  return (
    <div className="dashboard">
      {/* Top Header */}
      <header className="header">
        <div className="brand">
          <span className="brand-icon">🛡️</span>
          <div>
            <div className="brand-name">India Privacy Knowledge Infrastructure</div>
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.2rem" }}>
              <span className="brand-tag">DPDPA-CORE</span>
              <span className="brand-tag">v1.0.0</span>
            </div>
          </div>
        </div>

        <div className="api-badge">
          <span className={`api-indicator ${apiOnline ? "online" : ""}`}></span>
          <span>{loadingHealth ? "Checking status..." : apiOnline ? "Live API Online" : "Sandbox Mode"}</span>
        </div>
      </header>

      {/* Tabs Menu */}
      <nav className="nav-tabs">
        <button
          className={`nav-tab ${activeTab === "chat" ? "active" : ""}`}
          onClick={() => setActiveTab("chat")}
        >
          💬 Grounded Chat
        </button>
        <button
          className={`nav-tab ${activeTab === "explorer" ? "active" : ""}`}
          onClick={() => setActiveTab("explorer")}
        >
          🕸️ Graph Explorer
        </button>
        <button
          className={`nav-tab ${activeTab === "actions" ? "active" : ""}`}
          onClick={() => setActiveTab("actions")}
        >
          ✅ Business Actions
        </button>
        <button
          className={`nav-tab ${activeTab === "timeline" ? "active" : ""}`}
          onClick={() => setActiveTab("timeline")}
        >
          📜 Git Ledger
        </button>
      </nav>

      {/* Main Container */}
      <main className="main-content">
        {activeTab === "chat" && (
          <ChatInterface apiOnline={apiOnline} apiBaseUrl={API_BASE_URL} />
        )}
        {activeTab === "explorer" && (
          <GraphExplorer knowledgeObjects={MOCK_KNOWLEDGE_OBJECTS} />
        )}
        {activeTab === "actions" && (
          <BusinessActions actionItems={MOCK_ACTION_ITEMS} />
        )}
        {activeTab === "timeline" && (
          <GitTimeline timelineEvents={MOCK_TIMELINE_EVENTS} />
        )}
      </main>
    </div>
  );
}
