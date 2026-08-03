import React, { useState, useEffect } from "react";
import { PriorityBadge, EmptyState } from "../ui/SharedComponents";

// Detailed local data representing the DPDPA Chapters and Sections
const BIBLE_SECTIONS = [
  {
    chapter: "Chapter 1: Preliminary",
    section: "Section 1",
    title: "Short title and commencement",
    urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    summary: "Called the Digital Personal Data Protection Act, 2023. Applies to the processing of digital personal data. Commencement date will be notified by the Central Government.",
    obligations: ["Monitor government gazette notifications for section-wise implementation dates."],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Article 3 (Territorial Scope)",
    it_act: "IT Act 2000 Sec 1 (Title & Scope)",
    certin_rbi: "N/A Statutory Scope",
    max_penalty: "N/A",
    sla: "Phased 18-Month Timeline",
    infographic_type: "scope"
  },
  {
    chapter: "Chapter 1: Preliminary",
    section: "Section 2",
    title: "Definitions",
    urn: "urn:ki:in:dpdp:act:2023:sec:2",
    summary: "Defines 28 key statutory terms including Data Principal (individual), Data Fiduciary (decision maker), Consent Manager, Data Processor, Personal Data, and Data Breach.",
    obligations: [
      "Map internal company roles to statutory roles (Data Fiduciary vs Data Processor).",
      "Identify all Consent Manager touchpoints in user registration flows."
    ],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Article 4 (Definitions)",
    it_act: "IT Act Sec 2 & SPDI Rules 2011",
    certin_rbi: "RBI Payment System Definitions",
    max_penalty: "N/A",
    sla: "N/A",
    infographic_type: "definitions"
  },
  {
    chapter: "Chapter 1: Preliminary",
    section: "Section 3",
    title: "Application and Territorial Scope",
    urn: "urn:ki:in:dpdp:act:2023:sec:3",
    summary: "Applies to digital personal data processed within India, and outside India if related to offering goods or services to individuals in India.",
    obligations: ["Audit global data collection funnels serving Indian users for extraterritorial compliance."],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Art. 3(2) Extraterritoriality",
    it_act: "IT Act Sec 75 (Extraterritorial Scope)",
    certin_rbi: "RBI Data Localization Directive",
    max_penalty: "₹250 Crore",
    sla: "Extraterritorial Tracking",
    infographic_type: "scope"
  },
  {
    chapter: "Chapter 2: Obligations of Data Fiduciary",
    section: "Section 4",
    title: "Grounds for Processing Personal Data",
    urn: "urn:ki:in:dpdp:act:2023:sec:4",
    summary: "Personal data may only be processed for a lawful purpose based on consent of the Data Principal or for legitimate uses.",
    obligations: ["Map every processing pipeline to a valid ground (Consent or Section 7 Legitimate Use)."],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Article 6 (Lawful Processing)",
    it_act: "IT Act Sec 43A (Consent Mandate)",
    certin_rbi: "RBI Payment Consent Rules",
    max_penalty: "₹250 Crore",
    sla: "Point-of-Collection Grounding",
    infographic_type: "lawful"
  },
  {
    chapter: "Chapter 2: Obligations of Data Fiduciary",
    section: "Section 5",
    title: "Notice",
    urn: "urn:ki:in:dpdp:act:2023:sec:5",
    summary: "Before or at the time of seeking consent, data fiduciaries must present a clear notice describing data collected, processing purpose, and rights of the data principal.",
    obligations: [
      "Deploy localized consent notices on all user onboarding screens.",
      "Ensure notices contain contact details of the DPO/Grievance Officer.",
      "Provide translation in all 22 scheduled Indian languages."
    ],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Art 13 & 14 Privacy Notices",
    it_act: "SPDI Rules 2011 Rule 5 (Privacy Policy)",
    certin_rbi: "RBI Customer Disclosure Norms",
    max_penalty: "₹250 Crore",
    sla: "Immediate / Onboarding",
    infographic_type: "notice_flow"
  },
  {
    chapter: "Chapter 2: Obligations of Data Fiduciary",
    section: "Section 6",
    title: "Consent",
    urn: "urn:ki:in:dpdp:act:2023:sec:6",
    summary: "Consent must be free, specific, informed, unconditional, and unambiguous with a clear affirmative action. Data Principal has the right to withdraw consent easily.",
    obligations: [
      "Implement granular opt-ins on all signup forms.",
      "Develop a user dashboard to easily withdraw consent at any time."
    ],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Article 7 (Consent Conditions)",
    it_act: "IT Act Sec 43A Consent Rules",
    certin_rbi: "RBI Customer Opt-in Directive",
    max_penalty: "₹250 Crore",
    sla: "Instant Withdrawal Support",
    infographic_type: "consent_lifecycle"
  },
  {
    chapter: "Chapter 2: Obligations of Data Fiduciary",
    section: "Section 7",
    title: "Certain Legitimate Uses",
    urn: "urn:ki:in:dpdp:act:2023:sec:7",
    summary: "Fiduciaries can process data without explicit consent for specified legitimate uses like voluntary sharing, state functions, medical emergencies, disasters, and employment.",
    obligations: ["Verify that any non-consensual processing strictly falls within legitimate use criteria."],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Art 6(1)(f) Legitimate Interest",
    it_act: "IT Act Mandatory Govt Function",
    certin_rbi: "PMLA / KYC Non-Consensual Record",
    max_penalty: "₹250 Crore",
    sla: "Non-Consensual Logging",
    infographic_type: "legitimate"
  },
  {
    chapter: "Chapter 2: Obligations of Data Fiduciary",
    section: "Section 8",
    title: "General Obligations of Data Fiduciary",
    urn: "urn:ki:in:dpdp:act:2023:sec:8",
    summary: "Fiduciaries are responsible for compliance, ensuring accuracy of processed data, implementing technical security measures, and notifying the Board of any personal data breaches.",
    obligations: [
      "Deploy robust technical and organizational security controls.",
      "Create an incident response playbook with a 72-hour breach notification rule.",
      "Ensure data processors maintain equivalent security standards."
    ],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Art 32 Security & Art 33 Breach",
    it_act: "IT Act Sec 43A Reasonable Security",
    certin_rbi: "CERT-In 6-Hr vs DPDPA 72-Hr SLA",
    max_penalty: "₹250 Crore (Security) / ₹200 Cr (Breach)",
    sla: "72-Hour Breach SLA (DPBI)",
    infographic_type: "breach_sla"
  },
  {
    chapter: "Chapter 2: Obligations of Data Fiduciary",
    section: "Section 9",
    title: "Processing of Children's Data",
    urn: "urn:ki:in:dpdp:act:2023:sec:9",
    summary: "Requires verifiable parental/guardian consent for children (under 18) and persons with disabilities. Bans tracking, behavioral monitoring, or processing that harms children.",
    obligations: [
      "Implement age gates in registration steps.",
      "Deploy parent/guardian verification flows.",
      "Disable advertising trackers on profiles identified as children."
    ],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Art 8 Children Consent (Age <16)",
    it_act: "POCSO / IT Act Children Protection",
    certin_rbi: "N/A Children Specialized",
    max_penalty: "₹200 Crore",
    sla: "Verifiable Age Verification",
    infographic_type: "children_protection"
  },
  {
    chapter: "Chapter 2: Obligations of Data Fiduciary",
    section: "Section 10",
    title: "Significant Data Fiduciary (SDF)",
    urn: "urn:ki:in:dpdp:act:2023:sec:10",
    summary: "Fiduciaries with high data volumes or processing risks designated as Significant. Subject to strict governance including DPO appointment, annual independent audits, and DPIAs.",
    obligations: [
      "Perform self-assessments to see if SDF criteria are met.",
      "Appoint an India-based Data Protection Officer.",
      "Perform periodic Data Protection Impact Assessments (DPIA)."
    ],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Art 35 DPIA & Art 37 DPO",
    it_act: "IT Rules 2021 SSMI Thresholds",
    certin_rbi: "RBI CISO & Audit Framework",
    max_penalty: "₹150 Crore",
    sla: "Annual Audit & DPIA Cycle",
    infographic_type: "sdf_governance"
  },
  {
    chapter: "Chapter 3: Rights and Duties of Data Principal",
    section: "Section 11",
    title: "Right of Access to Information",
    urn: "urn:ki:in:dpdp:act:2023:sec:11",
    summary: "Data Principal has the right to obtain summary of data processed, details of processing activities, and list of other fiduciaries/processors data was shared with.",
    obligations: ["Build a DSAR (Data Subject Access Request) portal for Indian users."],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Art 15 Right of Access",
    it_act: "IT Act User Inquiry Rights",
    certin_rbi: "RBI Banking Statement Rights",
    max_penalty: "₹250 Crore",
    sla: "30-Day Response SLA",
    infographic_type: "dsar_access"
  },
  {
    chapter: "Chapter 3: Rights and Duties of Data Principal",
    section: "Section 12",
    title: "Right of Correction and Erasure",
    urn: "urn:ki:in:dpdp:act:2023:sec:12",
    summary: "Data Principal has the right to correct, complete, or request erasure of personal data that is no longer required for the purpose it was collected.",
    obligations: ["Implement automatic data deletion and user-initiated 'Right to be Forgotten' workflows."],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Art 16 Correction & Art 17 Erasure",
    it_act: "IT Act Data Accuracy Rules",
    certin_rbi: "PMLA 5-Yr Retention Override",
    max_penalty: "₹250 Crore",
    sla: "Purpose Expiry Deletion",
    infographic_type: "erasure_flow"
  },
  {
    chapter: "Chapter 3: Rights and Duties of Data Principal",
    section: "Section 13",
    title: "Right of Grievance Redressal",
    urn: "urn:ki:in:dpdp:act:2023:sec:13",
    summary: "Data Principal has the right to have grievances addressed by a Data Fiduciary or Consent Manager within a reasonable time limit before approaching the Board.",
    obligations: ["Establish a clear grievance redressal channel with SLAs."],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Art 77 Right to Lodge Complaint",
    it_act: "IT Rules 2021 Grievance Officer (15 Days)",
    certin_rbi: "RBI Banking Ombudsman (30 Days)",
    max_penalty: "₹250 Crore",
    sla: "Mandatory Prior Channel",
    infographic_type: "grievance_flow"
  },
  {
    chapter: "Chapter 4: Special Provisions",
    section: "Section 16",
    title: "Transfer of Personal Data Outside India",
    urn: "urn:ki:in:dpdp:act:2023:sec:16",
    summary: "Allows transfer of personal data outside India, except to countries or territories blacklisted by the Central Government.",
    obligations: ["Monitor MeitY's cross-border transfer blacklists and maintain localized backups."],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Chapter V Transfers (SCCs/Adequacy)",
    it_act: "SPDI Rules Rule 7 Transfer",
    certin_rbi: "RBI Payment System Data Localization 2018",
    max_penalty: "₹250 Crore",
    sla: "Blacklist Verification",
    infographic_type: "cross_border"
  },
  {
    chapter: "Chapter 8: Penalties and Adjudication",
    section: "Section 33",
    title: "Penalties",
    urn: "urn:ki:in:dpdp:act:2023:sec:33",
    summary: "Empowers the Board to levy major financial penalties up to ₹250 crore based on the severity and nature of the non-compliance.",
    obligations: ["Review penalty risk indexes periodically during board risk audits."],
    layer: "Layer 1 (Act)",
    gdpr: "GDPR Art 83 Fines (€20M / 4% Turnover)",
    it_act: "IT Act Sec 43A Compensation Caps",
    certin_rbi: "CERT-In 1-Yr Imprisonment / Fines",
    max_penalty: "₹250 Crore",
    sla: "Board Adjudication Order",
    infographic_type: "penalty_gauge"
  }
];

const PENALTY_SCHEDULE = [
  { violation: "Failure to take reasonable security safeguards to prevent data breach", section: "Section 8(5)", max_fine: "₹250 Crore", severity: "critical", urn: "urn:ki:in:dpdp:penalty:security-safeguards" },
  { violation: "Failure to notify the Board and Data Principals in the event of a breach", section: "Section 8(6)", max_fine: "₹200 Crore", severity: "high", urn: "urn:ki:in:dpdp:penalty:notify-breach" },
  { violation: "Breach of obligations in relation to children's data processing", section: "Section 9", max_fine: "₹200 Crore", severity: "high", urn: "urn:ki:in:dpdp:penalty:children-obligations" },
  { violation: "Breach of obligations by Significant Data Fiduciary (SDF)", section: "Section 10", max_fine: "₹150 Crore", severity: "high", urn: "urn:ki:in:dpdp:penalty:sdf-obligations" },
  { violation: "Failure of Data Principal to comply with statutory duties", section: "Section 15", max_fine: "₹10,000", severity: "low", urn: "urn:ki:in:dpdp:penalty:principal-duties" }
];

export default function Bible() {
  const [activeTab, setActiveTab] = useState("explorer"); // explorer | penalties | raw
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedSection, setExpandedSection] = useState("Section 5"); // Expand section 5 by default
  const [rawMarkdown, setRawMarkdown] = useState("");
  const [loadingRaw, setLoadingRaw] = useState(false);
  const [copiedUrn, setCopiedUrn] = useState("");

  useEffect(() => {
    if (activeTab === "raw") {
      setLoadingRaw(true);
      fetch("http://localhost:8000/knowledge/bible")
        .then((res) => {
          if (!res.ok) throw new Error("Bible API not available");
          return res.json();
        })
        .then((data) => {
          setRawMarkdown(data.content || "");
        })
        .catch((err) => {
          console.error("Failed to load raw DPDPA Bible:", err);
          setRawMarkdown(
            "# 📖 DPDPA Bible (Official Gazette Ledger)\n\n" +
            "Digital Personal Data Protection Act, 2023 [NO. 22 OF 2023]\n" +
            "An Act to provide for the processing of digital personal data in a manner that recognises both the right of individuals to protect their personal data and the need to process such personal data for lawful purposes and for matters connected therewith or incidental thereto.\n\n" +
            "BE it enacted by Parliament in the Seventy-fourth Year of the Republic of India as follows:-\n\n" +
            "CHAPTER I: PRELIMINARY\n" +
            "1. (1) This Act may be called the Digital Personal Data Protection Act, 2023.\n" +
            "   (2) It shall come into force on such date as the Central Government may, by notification in the Official Gazette, appoint.\n\n" +
            "2. In this Act, unless the context otherwise requires,—\n" +
            "   (a) 'Board' means the Data Protection Board of India established under section 18;\n" +
            "   (b) 'certain legitimate uses' means the uses referred to in section 7;\n" +
            "   (c) 'child' means an individual who has not completed eighteen years of age;\n" +
            "   (d) 'Consent Manager' means a person registered with the Board who acts as a single point of contact to enable a Data Principal to give, manage, review and withdraw her consent;\n" +
            "   (e) 'Data Fiduciary' means any person who alone or in conjunction with other persons determines the purpose and means of processing of personal data;\n" +
            "   (f) 'Data Principal' means the individual to whom the personal data relates..."
          );
        })
        .finally(() => {
          setLoadingRaw(false);
        });
    }
  }, [activeTab]);

  const handleCopyUrn = (urn) => {
    navigator.clipboard.writeText(urn);
    setCopiedUrn(urn);
    setTimeout(() => setCopiedUrn(""), 2000);
  };

  const filteredSections = BIBLE_SECTIONS.filter((s) => {
    const q = searchQuery.toLowerCase();
    return (
      s.section.toLowerCase().includes(q) ||
      s.title.toLowerCase().includes(q) ||
      s.chapter.toLowerCase().includes(q) ||
      s.summary.toLowerCase().includes(q)
    );
  });

  return (
    <div className="bible-screen flex flex-col gap-6" style={{ paddingBottom: "var(--space-8)" }}>
      {/* ── Hero Telemetry Header ───────────────────────────────────── */}
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
                🇮🇳 Official Gazette Reference
              </span>
              <span style={{ background: "rgba(255, 255, 255, 0.1)", color: "rgba(255, 255, 255, 0.8)", padding: "2px 10px", borderRadius: "9999px", fontSize: "11px", fontWeight: 600 }}>
                Act No. 22 of 2023
              </span>
            </div>
            <h1 style={{ fontSize: "26px", fontWeight: 800, color: "#FFFFFF", margin: 0 }}>
              DPDPA Compliance Bible
            </h1>
            <p style={{ fontSize: "13px", color: "rgba(255, 255, 255, 0.75)", margin: "4px 0 0 0" }}>
              Comprehensive, interactive legal reference for the Digital Personal Data Protection Act, 2023 with canonical URN coordinates.
            </p>
          </div>

          {/* Stat Telemetry */}
          <div style={{ display: "flex", gap: "16px", background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.12)", padding: "12px 20px", borderRadius: "12px" }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "20px", fontWeight: 800, color: "#34D399" }}>44</div>
              <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.6)", textTransform: "uppercase" }}>Statutory Sections</div>
            </div>
            <div style={{ width: "1px", background: "rgba(255,255,255,0.15)" }}></div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "20px", fontWeight: 800, color: "#60A5FA" }}>8</div>
              <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.6)", textTransform: "uppercase" }}>Chapters</div>
            </div>
            <div style={{ width: "1px", background: "rgba(255,255,255,0.15)" }}></div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "20px", fontWeight: 800, color: "#EF4444" }}>₹250 Cr</div>
              <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.6)", textTransform: "uppercase" }}>Max Penalty</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Enterprise Tabs Navigation ──────────────────────────────── */}
      <div style={{ display: "flex", gap: "12px", borderBottom: "2px solid var(--border)", paddingBottom: "2px" }}>
        <button
          onClick={() => setActiveTab("explorer")}
          style={{
            padding: "10px 20px",
            fontSize: "13px",
            fontWeight: 800,
            color: activeTab === "explorer" ? "var(--brand-navy)" : "var(--brand-slate)",
            background: "none",
            border: "none",
            borderBottom: activeTab === "explorer" ? "3px solid var(--brand-green)" : "3px solid transparent",
            cursor: "pointer",
            transition: "all 150ms ease"
          }}
        >
          📚 Act Explorer ({BIBLE_SECTIONS.length} Sections)
        </button>
        <button
          onClick={() => setActiveTab("penalties")}
          style={{
            padding: "10px 20px",
            fontSize: "13px",
            fontWeight: 800,
            color: activeTab === "penalties" ? "var(--brand-navy)" : "var(--brand-slate)",
            background: "none",
            border: "none",
            borderBottom: activeTab === "penalties" ? "3px solid var(--brand-green)" : "3px solid transparent",
            cursor: "pointer",
            transition: "all 150ms ease"
          }}
        >
          ⚖️ Statutory Penalty Schedule
        </button>
        <button
          onClick={() => setActiveTab("raw")}
          style={{
            padding: "10px 20px",
            fontSize: "13px",
            fontWeight: 800,
            color: activeTab === "raw" ? "var(--brand-navy)" : "var(--brand-slate)",
            background: "none",
            border: "none",
            borderBottom: activeTab === "raw" ? "3px solid var(--brand-green)" : "3px solid transparent",
            cursor: "pointer",
            transition: "all 150ms ease"
          }}
        >
          📝 Raw Gazette Ledger
        </button>
      </div>

      {/* ── Tab 1: Act Explorer ─────────────────────────────────────── */}
      {activeTab === "explorer" && (
        <div className="flex flex-col gap-4">
          {/* Search bar */}
          <div style={{ display: "flex", gap: "12px" }}>
            <div style={{ position: "relative", flex: 1 }}>
              <span style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", fontSize: "14px", color: "var(--brand-slate)" }}>🔍</span>
              <input
                type="text"
                placeholder="Search by section number, statutory term, or compliance directive..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  width: "100%",
                  padding: "12px 14px 12px 42px",
                  borderRadius: "10px",
                  border: "1px solid var(--border)",
                  fontSize: "13px",
                  background: "#FFFFFF",
                  color: "var(--brand-navy)",
                  boxShadow: "0 2px 6px rgba(0,0,0,0.02)"
                }}
              />
            </div>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="btn btn-secondary"
                style={{ padding: "0 16px" }}
              >
                Clear Search
              </button>
            )}
          </div>

          {/* List of Sections */}
          {filteredSections.length === 0 ? (
            <EmptyState
              title="No sections found"
              description={`We couldn't find any DPDPA sections matching "${searchQuery}".`}
            />
          ) : (
            <div className="flex flex-col gap-3">
              {filteredSections.map((item, idx) => {
                const isExpanded = expandedSection === item.section;
                return (
                  <div
                    key={idx}
                    style={{
                      background: "#FFFFFF",
                      border: isExpanded ? "2px solid var(--brand-navy)" : "1px solid var(--border)",
                      borderRadius: "12px",
                      overflow: "hidden",
                      boxShadow: isExpanded ? "0 4px 16px rgba(20, 33, 61, 0.08)" : "0 2px 6px rgba(0,0,0,0.02)",
                      transition: "all 150ms ease"
                    }}
                  >
                    {/* Collapsible Header */}
                    <div
                      onClick={() => setExpandedSection(isExpanded ? "" : item.section)}
                      style={{
                        padding: "16px 20px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        cursor: "pointer",
                        background: isExpanded ? "#F8FAFC" : "#FFFFFF",
                        userSelect: "none"
                      }}
                    >
                      <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--brand-slate)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                            {item.chapter}
                          </span>
                          <span style={{ fontSize: "11px", fontWeight: 800, background: "#EFF6FF", color: "#1A4FA3", border: "1px solid #BFDBFE", padding: "2px 8px", borderRadius: "9999px" }}>
                            {item.section}
                          </span>
                        </div>
                        <h3 style={{ fontSize: "16px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>
                          {item.title}
                        </h3>
                      </div>
                      <span style={{ fontSize: "13px", color: "var(--brand-slate)", fontWeight: 700 }}>
                        {isExpanded ? "▲" : "▼"}
                      </span>
                    </div>

                    {/* Content Section — Side-by-Side Split View */}
                    {isExpanded && (
                      <div style={{ padding: "20px", borderTop: "1px solid var(--border)", background: "#FFFFFF" }}>
                        <div className="grid grid-2 gap-4" style={{ gridTemplateColumns: "1.3fr 0.9fr" }}>
                          
                          {/* ── LEFT SIDE: Statutory Text & Directives (60%) ── */}
                          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                            {/* URN Reference Pill */}
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "#F8FAFC", border: "1px solid #E2E8F0", padding: "8px 12px", borderRadius: "8px" }}>
                              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--brand-slate)", textTransform: "uppercase" }}>Canonical URN:</span>
                                <span className="text-mono" style={{ fontSize: "11px", fontWeight: 700, color: "var(--brand-navy)", background: "#FFFFFF", padding: "2px 8px", borderRadius: "4px", border: "1px solid #CBD5E1" }}>
                                  {item.urn}
                                </span>
                              </div>
                              <button
                                onClick={() => handleCopyUrn(item.urn)}
                                style={{
                                  fontSize: "11px",
                                  fontWeight: 700,
                                  color: "#1A4FA3",
                                  background: "#EFF6FF",
                                  border: "1px solid #BFDBFE",
                                  padding: "3px 10px",
                                  borderRadius: "6px",
                                  cursor: "pointer"
                                }}
                              >
                                {copiedUrn === item.urn ? "Copied! ✓" : "Copy URN"}
                              </button>
                            </div>

                            {/* Summary */}
                            <div>
                              <h4 style={{ fontSize: "12px", fontWeight: 800, color: "var(--brand-navy)", margin: "0 0 4px 0", textTransform: "uppercase", letterSpacing: "0.03em" }}>
                                Statutory Summary
                              </h4>
                              <p style={{ fontSize: "13px", color: "var(--brand-slate)", lineHeight: 1.5, margin: 0 }}>
                                {item.summary}
                              </p>
                            </div>

                            {/* Compliance Directives */}
                            <div>
                              <h4 style={{ fontSize: "12px", fontWeight: 800, color: "var(--brand-navy)", margin: "0 0 6px 0", textTransform: "uppercase", letterSpacing: "0.03em" }}>
                                Business Compliance Directives
                              </h4>
                              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                                {item.obligations.map((obl, oIdx) => (
                                  <div key={oIdx} style={{ display: "flex", alignItems: "flex-start", gap: "8px", background: "#F0FDF4", border: "1px solid #86EFAC", padding: "8px 12px", borderRadius: "8px" }}>
                                    <span style={{ fontSize: "12px", color: "#138808", marginTop: "1px" }}>⚡</span>
                                    <span style={{ fontSize: "12px", fontWeight: 600, color: "#14532D", lineHeight: 1.4 }}>{obl}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>

                          {/* ── RIGHT SIDE: Side-by-Side Infographic Micro-Card (40%) ── */}
                          <div 
                            style={{ 
                              background: "linear-gradient(180deg, #F8FAFC 0%, #EFF6FF 100%)", 
                              border: "1px solid #BFDBFE", 
                              borderRadius: "14px", 
                              padding: "16px",
                              display: "flex",
                              flexDirection: "column",
                              gap: "12px"
                            }}
                          >
                            <div className="flex justify-between items-center">
                              <span style={{ fontSize: "11px", fontWeight: 800, color: "#1A4FA3", background: "#FFFFFF", padding: "2px 8px", borderRadius: "9999px", border: "1px solid #BFDBFE", textTransform: "uppercase" }}>
                                📊 Visual Infographic Card
                              </span>
                              <span style={{ fontSize: "11px", fontWeight: 700, color: "#D97706" }}>
                                SLA: {item.sla || "Immediate"}
                              </span>
                            </div>

                            {/* Penalty & Severity Gauge */}
                            <div style={{ background: "#FFFFFF", border: "1px solid #E2E8F0", padding: "10px 12px", borderRadius: "10px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                              <div>
                                <div style={{ fontSize: "10px", fontWeight: 700, color: "#64748B", textTransform: "uppercase" }}>Max Statutory Fine Cap</div>
                                <div style={{ fontSize: "16px", fontWeight: 800, color: item.max_penalty !== "N/A" ? "#991B1B" : "#14213D" }}>{item.max_penalty}</div>
                              </div>
                              <span style={{ fontSize: "10px", fontWeight: 800, background: item.max_penalty !== "N/A" ? "#FEF2F2" : "#F1F5F9", color: item.max_penalty !== "N/A" ? "#991B1B" : "#475569", padding: "4px 8px", borderRadius: "6px", border: item.max_penalty !== "N/A" ? "1px solid #FCA5A5" : "1px solid #CBD5E1" }}>
                                {item.max_penalty !== "N/A" ? "HIGH SEVERITY" : "STANDARD"}
                              </span>
                            </div>

                            {/* Comparative Law Matrix */}
                            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                              <div style={{ fontSize: "11px", fontWeight: 800, color: "var(--brand-navy)", textTransform: "uppercase" }}>
                                ⚖️ Comparative Laws Matrix
                              </div>
                              <div style={{ fontSize: "11px", background: "#FFFFFF", border: "1px solid #E2E8F0", padding: "6px 10px", borderRadius: "6px", display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "#64748B", fontWeight: 700 }}>EU GDPR:</span>
                                <span style={{ color: "#1E3A8A", fontWeight: 700 }}>{item.gdpr}</span>
                              </div>
                              <div style={{ fontSize: "11px", background: "#FFFFFF", border: "1px solid #E2E8F0", padding: "6px 10px", borderRadius: "6px", display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "#64748B", fontWeight: 700 }}>IT Act 2000:</span>
                                <span style={{ color: "#166534", fontWeight: 700 }}>{item.it_act}</span>
                              </div>
                              <div style={{ fontSize: "11px", background: "#FFFFFF", border: "1px solid #E2E8F0", padding: "6px 10px", borderRadius: "6px", display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "#64748B", fontWeight: 700 }}>CERT-In / RBI:</span>
                                <span style={{ color: "#D97706", fontWeight: 700 }}>{item.certin_rbi}</span>
                              </div>
                            </div>

                            {/* Process Micro-Flowchart */}
                            <div style={{ background: "#FFFFFF", border: "1px solid #E2E8F0", padding: "10px", borderRadius: "10px" }}>
                              <div style={{ fontSize: "10px", fontWeight: 800, color: "#64748B", textTransform: "uppercase", marginBottom: "6px" }}>Visual Compliance Flow</div>
                              <div style={{ display: "flex", alignItems: "center", justifyBetween: "space-between", gap: "4px", fontSize: "10px", fontWeight: 700 }}>
                                <span style={{ background: "#EFF6FF", color: "#1A4FA3", padding: "3px 6px", borderRadius: "4px" }}>1. Notice</span>
                                <span style={{ color: "#94A3B8" }}>►</span>
                                <span style={{ background: "#F0FDF4", color: "#138808", padding: "3px 6px", borderRadius: "4px" }}>2. Consent</span>
                                <span style={{ color: "#94A3B8" }}>►</span>
                                <span style={{ background: "#FFFBEB", color: "#D97706", padding: "3px 6px", borderRadius: "4px" }}>3. Action</span>
                                <span style={{ color: "#94A3B8" }}>►</span>
                                <span style={{ background: "#F5F3FF", color: "#7C3AED", padding: "3px 6px", borderRadius: "4px" }}>4. Audit</span>
                              </div>
                            </div>

                          </div>

                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ── Tab 2: Penalties Schedule ───────────────────────────────── */}
      {activeTab === "penalties" && (
        <div style={{ background: "#FFFFFF", border: "1px solid var(--border)", borderRadius: "14px", boxShadow: "var(--shadow-card)", overflow: "hidden" }}>
          <div style={{ padding: "16px 20px", background: "#F8FAFC", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <h3 style={{ fontSize: "16px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>
                Statutory Penalties (Schedule 1 of DPDPA 2023)
              </h3>
              <p style={{ fontSize: "12px", color: "var(--brand-slate)", margin: "2px 0 0 0" }}>
                Financial penalty limits levied by the Data Protection Board of India for statutory breaches.
              </p>
            </div>
            <span style={{ fontSize: "11px", fontWeight: 800, background: "#FEF2F2", color: "#991B1B", border: "1px solid #FCA5A5", padding: "4px 10px", borderRadius: "9999px" }}>
              Max Cap: ₹250 Crore
            </span>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
              <thead>
                <tr style={{ background: "linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%)", borderBottom: "2px solid #E2E8F0" }}>
                  <th style={{ padding: "12px 18px", fontSize: "11px", fontWeight: 800, color: "#475569", textTransform: "uppercase", letterSpacing: "0.06em", width: "45%" }}>Violation / Breach Description</th>
                  <th style={{ padding: "12px 18px", fontSize: "11px", fontWeight: 800, color: "#475569", textTransform: "uppercase", letterSpacing: "0.06em", width: "15%" }}>Section</th>
                  <th style={{ padding: "12px 18px", fontSize: "11px", fontWeight: 800, color: "#475569", textTransform: "uppercase", letterSpacing: "0.06em", width: "20%" }}>Max Fine Limit</th>
                  <th style={{ padding: "12px 18px", fontSize: "11px", fontWeight: 800, color: "#475569", textTransform: "uppercase", letterSpacing: "0.06em", width: "12%" }}>Severity</th>
                  <th style={{ padding: "12px 18px", fontSize: "11px", fontWeight: 800, color: "#475569", textTransform: "uppercase", letterSpacing: "0.06em", width: "8%" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {PENALTY_SCHEDULE.map((p, idx) => (
                  <tr key={idx} style={{ borderBottom: "1px solid #F1F5F9", background: idx % 2 === 0 ? "#FFFFFF" : "#FAFAF8" }}>
                    <td style={{ padding: "14px 18px", fontSize: "13px", fontWeight: 700, color: "var(--brand-navy)", lineHeight: 1.4 }}>
                      {p.violation}
                    </td>
                    <td style={{ padding: "14px 18px" }}>
                      <span className="text-mono" style={{ fontSize: "11px", fontWeight: 700, background: "#EFF6FF", color: "#1A4FA3", padding: "3px 8px", borderRadius: "4px", border: "1px solid #BFDBFE" }}>
                        {p.section}
                      </span>
                    </td>
                    <td style={{ padding: "14px 18px" }}>
                      <span style={{ fontSize: "13px", fontWeight: 800, color: p.severity === "critical" ? "#991B1B" : "#92400E", background: p.severity === "critical" ? "#FEF2F2" : "#FFF7ED", border: p.severity === "critical" ? "1px solid #FCA5A5" : "1px solid #FDBA74", padding: "4px 10px", borderRadius: "6px" }}>
                        {p.max_fine}
                      </span>
                    </td>
                    <td style={{ padding: "14px 18px" }}>
                      <PriorityBadge priority={p.severity} />
                    </td>
                    <td style={{ padding: "14px 18px" }}>
                      <button
                        onClick={() => handleCopyUrn(p.urn)}
                        style={{ fontSize: "11px", fontWeight: 700, color: "#1A4FA3", background: "none", border: "none", cursor: "pointer" }}
                      >
                        {copiedUrn === p.urn ? "Copied! ✓" : "Copy URN"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Tab 3: Raw Gazette Ledger ─────────────────────────────── */}
      {activeTab === "raw" && (
        <div style={{ background: "#FFFFFF", border: "1px solid var(--border)", borderRadius: "14px", padding: "24px", boxShadow: "var(--shadow-card)", minHeight: "450px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", paddingBottom: "12px", borderBottom: "1px solid var(--border)" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 800, color: "var(--brand-navy)", margin: 0 }}>
              Official Gazette Text Ledger
            </h3>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--brand-slate)", background: "#F1F5F9", padding: "2px 8px", borderRadius: "4px" }}>
              Markdown View
            </span>
          </div>

          {loadingRaw ? (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "200px", color: "var(--brand-slate)", fontStyle: "italic" }}>
              Loading Raw Markdown from API Gateway...
            </div>
          ) : (
            <pre className="text-mono" style={{ fontSize: "12px", lineHeight: 1.65, background: "#F8FAFC", border: "1px solid #E2E8F0", padding: "20px", borderRadius: "10px", color: "var(--brand-navy)", whiteSpace: "pre-wrap", overflowX: "auto" }}>
              {rawMarkdown}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

