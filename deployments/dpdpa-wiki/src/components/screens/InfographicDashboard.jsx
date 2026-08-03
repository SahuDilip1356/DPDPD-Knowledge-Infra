import React, { useState } from "react";

export default function InfographicDashboard() {
  const [activeLayer, setActiveLayer] = useState(3);
  const [activeDept, setActiveDept] = useState(1);
  const [activeStatute, setActiveStatute] = useState("certin");

  const layers = [
    {
      id: 5,
      title: "LAYER 5: ECOSYSTEM & DISTRIBUTION REACH",
      tag: "Distribution",
      color: "#3B82F6",
      bg: "#EFF6FF",
      border: "#BFDBFE",
      desc: "Reaches 900M+ native speakers across India's MSME hubs in 6 regional languages + open developer APIs.",
      metrics: ["6 Languages (HI, GU, MR, KN, TA, TE)", "ANI Press Syndication", "Open REST API & Webhook Gateway"]
    },
    {
      id: 4,
      title: "LAYER 4: WEB APPLICATION & UI DASHBOARDS",
      tag: "Experience",
      color: "#1A4FA3",
      bg: "#F0F7FF",
      border: "#93C5FD",
      desc: "7 high-contrast interactive React dashboards powered by the SaralPrivacy design token system.",
      metrics: ["7 Live Dashboards (/today, /bible, /ask...)", "High-Contrast Enterprise Color System", "Mobile-Optimized Responsive SPA"]
    },
    {
      id: 3,
      title: "LAYER 3: KNOWLEDGE STRUCTURE & OPERATE ENGINE",
      tag: "The Brain",
      color: "#138808",
      bg: "#F0FDF4",
      border: "#86EFAC",
      desc: "Transforms complex statutory legal requirements into 7 actionable operational pillars.",
      metrics: ["OPERATE Framework (7 Pillars)", "3-Minute SMB Readiness Assessment", "Canonical URN Indexing (urn:ki:in:dpdp...)"]
    },
    {
      id: 2,
      title: "LAYER 2: PERSISTENCE & VECTOR INTELLIGENCE",
      tag: "The Memory",
      color: "#7C3AED",
      bg: "#F5F3FF",
      border: "#DDD6FE",
      desc: "Bitemporal database storage + Pinecone dense vector index for zero-hallucination semantic search.",
      metrics: ["Supabase PostgreSQL (Bitemporal Schema)", "Pinecone Vector DB (dpdpa-knowledge)", "Immutable Git Audit Ledger Backup"]
    },
    {
      id: 1,
      title: "LAYER 1: RAW STATUTORY SOURCING & INGESTION",
      tag: "The Fuel",
      color: "#D97706",
      bg: "#FFFBEB",
      border: "#FDE68A",
      desc: "Automated hourly web scrapers monitoring primary government gazettes and regulatory boards.",
      metrics: ["Gazette of India (egazette.gov.in)", "MeitY Notifications (meity.gov.in)", "DPBI Board Orders & CERT-In Directives"]
    }
  ];

  const departments = [
    { id: 1, name: "Scout Agent", dept: "Dept 1: Research", desc: "Scans MeitY, Gazette, & CERT-In feeds for new PDF circulars.", icon: "🕵️" },
    { id: 2, name: "Citation Agent", dept: "Dept 2: Evidence", desc: "Hashes raw PDF binaries & assigns statutory URN coordinates.", icon: "🏷️" },
    { id: 3, name: "Parsing Agent", dept: "Dept 3: Extraction", desc: "PyPDF + Gemini Vision OCR for regional font gazette parsing.", icon: "👁️" },
    { id: 4, name: "Ontology Agent", dept: "Dept 4: Vocabulary", desc: "Normalizes terms against 28 Constitutional Nouns.", icon: "📐" },
    { id: 5, name: "Relationship Agent", dept: "Dept 5: Graph Links", desc: "Creates directed edges (Implements, Overrides, Conflicts With).", icon: "🔗" },
    { id: 6, name: "Reasoning Agent", dept: "Dept 6: Grounding", desc: "Enforces zero hallucination & evaluates citation accuracy.", icon: "🧠" },
    { id: 7, name: "Business Translation", dept: "Dept 7: Operations", desc: "Translates legalese into CISO, DPO, & Founder action items.", icon: "💼" },
    { id: 8, name: "Publishing Agent", dept: "Dept 8: Distribution", desc: "JSON-LD schema validation & commit to Supabase, Pinecone, & Git.", icon: "🚀" }
  ];

  const interStatutes = {
    certin: {
      title: "CERT-In Directions 2022 (6-Hour Breach SLA)",
      authority: "CERT-In / MeitY",
      relationship: "Conflicts With DPDPA Rule 7",
      color: "#991B1B",
      bg: "#FEF2F2",
      border: "#FCA5A5",
      desc: "Mandates reporting of cyber incidents to CERT-In within 6 hours of notice. Clashes with DPDPA Rule 7's 72-hour notification timeline, creating a dual SLA reporting burden for CISOs."
    },
    rbi: {
      title: "RBI Storage of Payment System Data Directive 2018",
      authority: "Reserve Bank of India (RBI)",
      relationship: "Harmonizes With DPDPA Section 16",
      color: "#1E3A8A",
      bg: "#EFF6FF",
      border: "#BFDBFE",
      desc: "Mandates that all payment system providers store full transaction data exclusively within domestic Indian cloud regions. Harmonizes with DPDPA Section 16 cross-border transfer rules."
    },
    pmla: {
      title: "PMLA 2002 — Section 12 (5-Year Financial Record Retention)",
      authority: "Parliament of India",
      relationship: "Overrides DPDPA Section 12 Right to Erasure",
      color: "#78350F",
      bg: "#FFFBEB",
      border: "#FDE68A",
      desc: "Requires financial reporting entities to maintain record of all transactions for 5 years. Overrides Data Principal erasure requests under DPDPA Section 12(3)."
    },
    itact: {
      title: "Information Technology Act 2000 — Section 43A",
      authority: "Parliament of India",
      relationship: "Replaced By DPDPA Section 44",
      color: "#166534",
      bg: "#F0FDF4",
      border: "#86EFAC",
      desc: "DPDPA Section 44 formally repeals IT Act Section 43A (SPDI Rules 2011), replacing compensation claims with administrative fines levied by the Data Protection Board of India."
    }
  };

  const languages = [
    { code: "HI", name: "Hindi (हिंदी)", state: "Uttar Pradesh, MP, Delhi", reach: "528 Million", flag: "🇮🇳" },
    { code: "GU", name: "Gujarati (ગુજરાતી)", state: "Gujarat (Surat/Ahmedabad MSMEs)", reach: "60 Million", flag: "🇮🇳" },
    { code: "MR", name: "Marathi (मराठी)", state: "Maharashtra (Pune/Mumbai Belt)", reach: "83 Million", flag: "🇮🇳" },
    { code: "KN", name: "Kannada (ಕನ್ನಡ)", state: "Karnataka (Bengaluru Tech Hub)", reach: "44 Million", flag: "🇮🇳" },
    { code: "TA", name: "Tamil (தமிழ்)", state: "Tamil Nadu (Chennai IT & Retail)", reach: "75 Million", flag: "🇮🇳" },
    { code: "TE", name: "Telugu (తెలుగు)", state: "AP & Telangana (Hyderabad Corridor)", reach: "82 Million", flag: "🇮🇳" }
  ];

  return (
    <div className="infographic-dashboard flex flex-col gap-6" style={{ paddingBottom: "40px" }}>
      
      {/* ── 1. HERO INFOGRAPHIC BANNER ────────────────────────────────────────────── */}
      <div 
        className="hero-infographic-card card"
        style={{
          background: "linear-gradient(135deg, #14213D 0%, #1A4FA3 100%)",
          color: "#FFFFFF",
          padding: "32px 36px",
          borderRadius: "20px",
          boxShadow: "0 12px 32px rgba(20, 33, 61, 0.2)",
          position: "relative",
          overflow: "hidden"
        }}
      >
        <div style={{ position: "absolute", right: "-30px", top: "-30px", opacity: 0.08, fontSize: "200px" }}>
          🌐
        </div>

        <div className="flex justify-between items-start flex-wrap gap-4" style={{ position: "relative", zIndex: 2 }}>
          <div className="flex flex-col gap-2" style={{ maxWidth: "680px" }}>
            <div className="flex items-center gap-2">
              <span style={{ background: "#138808", color: "#FFFFFF", fontSize: "11px", fontWeight: 800, padding: "3px 10px", borderRadius: "9999px", textTransform: "uppercase" }}>
                Interactive Visual Architecture
              </span>
              <span style={{ background: "rgba(255,255,255,0.15)", color: "#E2E8F0", fontSize: "11px", fontWeight: 700, padding: "3px 10px", borderRadius: "9999px" }}>
                SaralPrivacy DPDPA System
              </span>
            </div>

            <h1 style={{ fontSize: "28px", fontWeight: 800, margin: "6px 0", color: "#FFFFFF", lineHeight: 1.2 }}>
              SaralPrivacy DPDPA Knowledge Infrastructure
            </h1>
            <p style={{ fontSize: "14px", color: "#E2E8F0", margin: 0, lineHeight: 1.6 }}>
              Visual blueprint showing how data flows from <strong>Official Gazette Sources</strong> through the <strong>8-Department Agentic Ingestion Factory</strong> into a <strong>Bitemporal Knowledge Graph</strong> powering 6 regional Indian languages and grounded AI reasoning.
            </p>
          </div>

          <div className="flex flex-col gap-3" style={{ background: "rgba(255, 255, 255, 0.1)", backdropFilter: "blur(10px)", padding: "18px 24px", borderRadius: "14px", border: "1px solid rgba(255, 255, 255, 0.2)", minWidth: "240px" }}>
            <div className="text-small" style={{ color: "#94A3B8", fontWeight: 700, textTransform: "uppercase", fontSize: "11px" }}>
              Ecosystem Key Statistics
            </div>
            <div className="flex justify-between items-center">
              <span style={{ color: "#E2E8F0", fontSize: "13px" }}>Vernacular Languages:</span>
              <span style={{ color: "#FF9933", fontWeight: 800, fontSize: "16px" }}>6 Languages</span>
            </div>
            <div className="flex justify-between items-center">
              <span style={{ color: "#E2E8F0", fontSize: "13px" }}>Native Reach:</span>
              <span style={{ color: "#86EFAC", fontWeight: 800, fontSize: "16px" }}>900M+ People</span>
            </div>
            <div className="flex justify-between items-center">
              <span style={{ color: "#E2E8F0", fontSize: "13px" }}>Statutory Sections:</span>
              <span style={{ color: "#93C5FD", fontWeight: 800, fontSize: "16px" }}>44 Sections</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── 2. THE 5-LAYER STACK ARCHITECTURE INFOGRAPHIC ─────────────────────────────── */}
      <div className="card flex flex-col gap-4" style={{ padding: "24px", borderRadius: "16px", background: "#FFFFFF", border: "1px solid var(--border)" }}>
        <div className="flex justify-between items-center flex-wrap gap-2">
          <div>
            <h2 style={{ fontSize: "18px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>
              🏗️ 1. The 5-Layer Stack Architecture Infographic
            </h2>
            <p className="text-small text-muted" style={{ margin: "2px 0 0 0" }}>
              Click any layer to inspect its technical components, database schemas, and output metrics.
            </p>
          </div>
          <span style={{ fontSize: "12px", fontWeight: 700, background: "#EFF6FF", color: "#1A4FA3", padding: "4px 12px", borderRadius: "9999px", border: "1px solid #BFDBFE" }}>
            Active Layer: Layer {activeLayer}
          </span>
        </div>

        <div className="flex flex-col gap-3" style={{ marginTop: "12px" }}>
          {layers.map((layer) => {
            const isSelected = activeLayer === layer.id;
            return (
              <div 
                key={layer.id}
                onClick={() => setActiveLayer(layer.id)}
                style={{
                  background: isSelected ? layer.bg : "#FFFFFF",
                  border: isSelected ? `2px solid ${layer.color}` : "1px solid #E2E8F0",
                  borderRadius: "12px",
                  padding: "16px 20px",
                  cursor: "pointer",
                  transition: "all 200ms ease",
                  boxShadow: isSelected ? "0 4px 12px rgba(0,0,0,0.06)" : "none"
                }}
              >
                <div className="flex justify-between items-center flex-wrap gap-2">
                  <div className="flex items-center gap-3">
                    <span 
                      style={{ 
                        background: layer.color, 
                        color: "#FFFFFF", 
                        fontSize: "11px", 
                        fontWeight: 800, 
                        padding: "4px 10px", 
                        borderRadius: "6px" 
                      }}
                    >
                      {layer.tag}
                    </span>
                    <h3 style={{ fontSize: "15px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>
                      {layer.title}
                    </h3>
                  </div>
                  <span style={{ fontSize: "12px", fontWeight: 700, color: isSelected ? layer.color : "#64748B" }}>
                    {isSelected ? "▼ Expanded" : "► Click to Expand"}
                  </span>
                </div>

                <p style={{ fontSize: "13px", color: "#334155", margin: "10px 0 0 0", lineHeight: "1.5" }}>
                  {layer.desc}
                </p>

                {isSelected && (
                  <div className="flex flex-wrap gap-2" style={{ marginTop: "14px", paddingTop: "12px", borderTop: `1px solid ${layer.border}` }}>
                    {layer.metrics.map((m, idx) => (
                      <span 
                        key={idx} 
                        style={{ 
                          fontSize: "12px", 
                          fontWeight: 700, 
                          background: "#FFFFFF", 
                          color: layer.color, 
                          border: `1px solid ${layer.border}`, 
                          padding: "4px 12px", 
                          borderRadius: "9999px",
                          boxShadow: "0 1px 3px rgba(0,0,0,0.03)"
                        }}
                      >
                        ✓ {m}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ── 3. 8-DEPARTMENT AGENTIC INGESTION FACTORY WORKFLOW ───────────────────────── */}
      <div className="card flex flex-col gap-4" style={{ padding: "24px", borderRadius: "16px", background: "#FFFFFF", border: "1px solid var(--border)" }}>
        <div>
          <h2 style={{ fontSize: "18px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>
            🤖 2. 8-Department Autonomous Ingestion Factory Workflow
          </h2>
          <p className="text-small text-muted" style={{ margin: "2px 0 0 0" }}>
            How multi-agent workers process raw legal PDFs into canonical bitemporal knowledge graph nodes.
          </p>
        </div>

        <div className="grid grid-4 gap-3" style={{ marginTop: "12px" }}>
          {departments.map((dept) => {
            const isSelected = activeDept === dept.id;
            return (
              <div
                key={dept.id}
                onClick={() => setActiveDept(dept.id)}
                style={{
                  background: isSelected ? "#F0F7FF" : "#F8FAFC",
                  border: isSelected ? "2px solid #1A4FA3" : "1px solid #E2E8F0",
                  borderRadius: "12px",
                  padding: "16px",
                  cursor: "pointer",
                  transition: "all 150ms ease"
                }}
              >
                <div className="flex justify-between items-center">
                  <span style={{ fontSize: "24px" }}>{dept.icon}</span>
                  <span className="text-mono" style={{ fontSize: "10px", fontWeight: 700, color: "#64748B" }}>
                    STEP 0{dept.id}
                  </span>
                </div>
                <h4 style={{ fontSize: "14px", fontWeight: 800, color: "var(--brand-navy)", margin: "8px 0 2px 0" }}>
                  {dept.name}
                </h4>
                <div style={{ fontSize: "11px", fontWeight: 700, color: "#1A4FA3", marginBottom: "6px" }}>
                  {dept.dept}
                </div>
                <p className="text-small" style={{ fontSize: "12px", color: "#475569", margin: 0, lineHeight: 1.4 }}>
                  {dept.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── 4. INTER-STATUTORY HARMONIZATION INFOGRAPHIC ──────────────────────────────── */}
      <div className="card flex flex-col gap-4" style={{ padding: "24px", borderRadius: "16px", background: "#FFFFFF", border: "1px solid var(--border)" }}>
        <div>
          <h2 style={{ fontSize: "18px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>
            🔗 3. Inter-Statutory Cross-Regulatory Harmonization Web
          </h2>
          <p className="text-small text-muted" style={{ margin: "2px 0 0 0" }}>
            How DPDPA Section URNs link directly to intersecting non-DPDPA Indian laws (CERT-In, RBI, PMLA, IT Act).
          </p>
        </div>

        <div className="flex gap-2 flex-wrap" style={{ marginTop: "8px" }}>
          {Object.keys(interStatutes).map((key) => {
            const item = interStatutes[key];
            const isSelected = activeStatute === key;
            return (
              <button
                key={key}
                onClick={() => setActiveStatute(key)}
                style={{
                  background: isSelected ? item.bg : "#F8FAFC",
                  border: isSelected ? `2px solid ${item.color}` : "1px solid #E2E8F0",
                  color: isSelected ? item.color : "#475569",
                  padding: "8px 16px",
                  borderRadius: "9999px",
                  fontWeight: 700,
                  fontSize: "13px",
                  cursor: "pointer",
                  transition: "all 150ms ease"
                }}
              >
                {key.toUpperCase()}: {item.authority.split(" ")[0]}
              </button>
            );
          })}
        </div>

        {activeStatute && (
          <div 
            style={{ 
              background: interStatutes[activeStatute].bg, 
              border: `1px solid ${interStatutes[activeStatute].border}`,
              borderRadius: "14px", 
              padding: "20px",
              marginTop: "8px"
            }}
          >
            <div className="flex justify-between items-center flex-wrap gap-2">
              <span style={{ background: interStatutes[activeStatute].color, color: "#FFFFFF", fontSize: "11px", fontWeight: 800, padding: "3px 10px", borderRadius: "6px" }}>
                {interStatutes[activeStatute].relationship}
              </span>
              <span className="text-mono" style={{ fontSize: "12px", fontWeight: 700, color: interStatutes[activeStatute].color }}>
                {interStatutes[activeStatute].authority}
              </span>
            </div>

            <h3 style={{ fontSize: "17px", fontWeight: 800, color: interStatutes[activeStatute].color, margin: "10px 0 6px 0" }}>
              {interStatutes[activeStatute].title}
            </h3>

            <p style={{ fontSize: "13px", color: "#334155", margin: 0, lineHeight: 1.6 }}>
              {interStatutes[activeStatute].desc}
            </p>
          </div>
        )}
      </div>

      {/* ── 5. VERNACULAR REGIONAL REACH INFOGRAPHIC ──────────────────────────────────── */}
      <div className="card flex flex-col gap-4" style={{ padding: "24px", borderRadius: "16px", background: "#FFFFFF", border: "1px solid var(--border)" }}>
        <div>
          <h2 style={{ fontSize: "18px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>
            🇮🇳 4. Multilingual Vernacular Reach Across 6 Indian Languages
          </h2>
          <p className="text-small text-muted" style={{ margin: "2px 0 0 0" }}>
            Reaching India's 63 Million MSMEs in native regional languages covering 900M+ native speakers.
          </p>
        </div>

        <div className="grid grid-3 gap-3" style={{ marginTop: "8px" }}>
          {languages.map((lang) => (
            <div 
              key={lang.code}
              style={{
                background: "#F8FAFC",
                border: "1px solid #E2E8F0",
                borderRadius: "12px",
                padding: "16px"
              }}
            >
              <div className="flex justify-between items-center">
                <span style={{ fontSize: "20px" }}>{lang.flag}</span>
                <span style={{ fontSize: "11px", fontWeight: 800, background: "#EFF6FF", color: "#1A4FA3", padding: "2px 8px", borderRadius: "4px" }}>
                  {lang.code} GUIDE
                </span>
              </div>
              <h4 style={{ fontSize: "15px", fontWeight: 800, color: "var(--brand-navy)", margin: "8px 0 2px 0" }}>
                {lang.name}
              </h4>
              <div style={{ fontSize: "12px", fontWeight: 700, color: "#138808", marginBottom: "4px" }}>
                Reach: {lang.reach}
              </div>
              <p className="text-small text-muted" style={{ fontSize: "11px", margin: 0 }}>
                Target: {lang.state}
              </p>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
