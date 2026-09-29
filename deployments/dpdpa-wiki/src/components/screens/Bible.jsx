import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { PriorityBadge, EmptyState } from "../ui/SharedComponents";
import { apiFetch } from "../../lib/api";
import CometCascadeHeroBackground from "../marketing/CometCascadeHeroBackground";
import "../../styles/bible.css";

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
  { violation: "Failure to take reasonable security safeguards to prevent a data breach", section: "Section 8(5)", max_fine: "₹250 Crore", severity: "critical", urn: "urn:ki:in:dpdp:penalty:security-safeguards" },
  { violation: "Failure to notify the Board and Data Principals in the event of a breach", section: "Section 8(6)", max_fine: "₹200 Crore", severity: "high", urn: "urn:ki:in:dpdp:penalty:notify-breach" },
  { violation: "Breach of obligations in relation to children's data processing", section: "Section 9", max_fine: "₹200 Crore", severity: "high", urn: "urn:ki:in:dpdp:penalty:children-obligations" },
  { violation: "Breach of obligations by Significant Data Fiduciary (SDF)", section: "Section 10", max_fine: "₹150 Crore", severity: "high", urn: "urn:ki:in:dpdp:penalty:sdf-obligations" },
  { violation: "Failure of Data Principal to comply with statutory duties", section: "Section 15", max_fine: "₹10,000", severity: "low", urn: "urn:ki:in:dpdp:penalty:principal-duties" }
];

const PENALTY_BAR = {
  low: 26,
  medium: 45,
  high: 72,
  critical: 100
};

const CHAPTER_LABELS = ["All Chapters", ...new Set(BIBLE_SECTIONS.map((section) => section.chapter))];

function getChapterGroup(sections) {
  const byChapter = {};
  sections.forEach((item) => {
    if (!byChapter[item.chapter]) byChapter[item.chapter] = [];
    byChapter[item.chapter].push(item);
  });
  return Object.entries(byChapter).map(([chapter, items]) => ({
    chapter,
    sections: items
  }));
}

function severityFromPenalty(fineText) {
  if (fineText.includes("250")) return "critical";
  if (fineText.includes("200") || fineText.includes("150")) return "high";
  if (fineText.includes("10,000")) return "low";
  return "medium";
};

export default function Bible() {
  const [activeTab, setActiveTab] = useState("explorer"); // explorer | penalties | raw
  const [searchQuery, setSearchQuery] = useState("");
  const [chapterFilter, setChapterFilter] = useState("All Chapters");
  const [expandedSection, setExpandedSection] = useState("");
  const [rawMarkdown, setRawMarkdown] = useState("");
  const [loadingRaw, setLoadingRaw] = useState(false);
  const [rawError, setRawError] = useState("");
  const [copiedUrn, setCopiedUrn] = useState("");

  useEffect(() => {
    if (activeTab !== "raw") return;

    setLoadingRaw(true);
    setRawError("");
    try {
      apiFetch("/knowledge/bible")
        .then((res) => {
          if (!res.ok) throw new Error("Bible API not available");
          return res.json();
        })
        .then((data) => {
          setRawMarkdown(data.content || "");
        })
        .catch((err) => {
          console.error("Failed to load raw DPDPA Bible:", err);
          setRawMarkdown("");
          setRawError("The canonical Bible text is unavailable. No fallback text is being shown.");
        })
        .finally(() => {
          setLoadingRaw(false);
        });
    } catch (err) {
      console.error("Bible API call failed before request:", err);
      setRawMarkdown("");
      setRawError("The canonical Bible text is unavailable. No fallback text is being shown.");
      setLoadingRaw(false);
    }
  }, [activeTab]);

  useEffect(() => {
    if (activeTab !== "explorer") return;
    const filtered = BIBLE_SECTIONS.filter((s) => {
      const q = searchQuery.toLowerCase();
      const chapterMatch = chapterFilter === "All Chapters" || s.chapter === chapterFilter;
      return (
        chapterMatch &&
        (s.section.toLowerCase().includes(q) ||
          s.title.toLowerCase().includes(q) ||
          s.chapter.toLowerCase().includes(q) ||
          s.summary.toLowerCase().includes(q))
      );
    });

    if (filtered.length > 0) {
      setExpandedSection((current) => {
        return filtered.some((item) => item.section === current) ? current : filtered[0].section;
      });
    } else {
      setExpandedSection("");
    }
  }, [searchQuery, chapterFilter, activeTab]);

  const filteredSections = useMemo(() => {
    const q = searchQuery.toLowerCase();
    return BIBLE_SECTIONS.filter((s) => {
      const chapterMatch = chapterFilter === "All Chapters" || s.chapter === chapterFilter;
      const queryMatch =
        s.section.toLowerCase().includes(q) ||
        s.title.toLowerCase().includes(q) ||
        s.chapter.toLowerCase().includes(q) ||
        s.summary.toLowerCase().includes(q);
      return chapterMatch && queryMatch;
    });
  }, [searchQuery, chapterFilter]);

  const groupedSections = useMemo(
    () => getChapterGroup(filteredSections),
    [filteredSections]
  );

  const handleCopyUrn = (urn) => {
    navigator.clipboard.writeText(urn);
    setCopiedUrn(urn);
    setTimeout(() => setCopiedUrn(""), 2000);
  };

  return (
    <div className="bible-screen">
      <section className="bible-hero">
        <div className="bible-hero-sky" aria-hidden="true">
          <CometCascadeHeroBackground />
        </div>
        <div className="bible-hero-inner">
          <p className="bible-chip">DPDPA 2023 • Canonical Ledger</p>
          <h1 className="bible-title">DPDPA Knowledge Bible</h1>
          <p className="bible-subtitle">
            A complete, chronologically organized statutory operating system for
            compliance with the Digital Personal Data Protection Act, 2023.
          </p>

          <div className="bible-hero-metrics">
            <article className="bible-metric-card">
              <p className="bible-metric-k">44</p>
              <p className="bible-metric-l">Statutory Sections</p>
            </article>
            <article className="bible-metric-card">
              <p className="bible-metric-k">8</p>
              <p className="bible-metric-l">Chapters indexed</p>
            </article>
            <article className="bible-metric-card">
              <p className="bible-metric-k">₹250 Cr</p>
              <p className="bible-metric-l">Maximum statutory cap</p>
            </article>
            <article className="bible-metric-card">
              <p className="bible-metric-k">Layered</p>
              <p className="bible-metric-l">URN, mappings, evidence</p>
            </article>
          </div>
        </div>
      </section>

      <div className="bible-surface">
        <div className="bible-tabbar">
          <button
            type="button"
            className={`bible-tab ${activeTab === "explorer" ? "is-active" : ""}`}
            onClick={() => setActiveTab("explorer")}
          >
            🗂 Act Explorer
          </button>
          <button
            type="button"
            className={`bible-tab ${activeTab === "penalties" ? "is-active" : ""}`}
            onClick={() => setActiveTab("penalties")}
          >
            ⚖️ Penalty Map
          </button>
          <button
            type="button"
            className={`bible-tab ${activeTab === "raw" ? "is-active" : ""}`}
            onClick={() => setActiveTab("raw")}
          >
            📘 Raw Act Ledger
          </button>
        </div>

        {activeTab === "explorer" && (
          <section className="bible-layout">
            <article className="bible-panel bible-panel-main">
              <div className="bible-toolbar">
                <label className="bible-search-wrap" htmlFor="bible-search">
                  <span className="bible-search-icon" aria-hidden="true">🔍</span>
                  <input
                    id="bible-search"
                    type="search"
                    className="bible-search"
                    placeholder="Search section title, text, or obligations..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </label>

                <div className="bible-chips" role="group" aria-label="Chapter filter">
                  {CHAPTER_LABELS.map((chapter) => (
                    <button
                      key={chapter}
                      type="button"
                      className={`bible-mini-chip ${chapterFilter === chapter ? "is-active" : ""}`}
                      onClick={() => setChapterFilter(chapter)}
                    >
                      {chapter}
                    </button>
                  ))}
                </div>
              </div>

              {filteredSections.length === 0 ? (
                <EmptyState
                  title="No sections found"
                  description={`No section matches ${searchQuery ? `"${searchQuery}"` : "your current filter"}.`}
                />
              ) : (
                <div className="bible-chapters">
                  {groupedSections.map((group) => (
                    <section key={group.chapter} className="bible-chapter">
                      <header className="bible-chapter-head">
                        <p className="bible-eyebrow">{group.chapter}</p>
                        <p className="bible-quiet">{group.sections.length} sections</p>
                      </header>

                      <div className="bible-sections">
                        {group.sections.map((item) => {
                          const isExpanded = expandedSection === item.section;
                          return (
                            <article key={item.section} className={`bible-section ${isExpanded ? "is-open" : ""}`}>
                              <button
                                className="bible-section-head"
                                type="button"
                                onClick={() => setExpandedSection(isExpanded ? "" : item.section)}
                              >
                                <div>
                                  <span className="bible-badge">{item.section}</span>
                                  <h3 className="bible-section-title">{item.title}</h3>
                                  <p className="bible-quiet">{item.layer}</p>
                                </div>
                                <span className="bible-chevron" aria-hidden="true">{isExpanded ? "▴" : "▾"}</span>
                              </button>

                              {isExpanded && (
                                <div className="bible-section-body">
                                  <div className="bible-section-grid">
                                    <div className="bible-section-col">
                                      <h4 className="bible-mini-title">Legal Summary</h4>
                                      <p className="bible-section-copy">{item.summary}</p>

                                      <h4 className="bible-mini-title">Statutory Directives</h4>
                                      <ul className="bible-obligations">
                                        {item.obligations.map((obl, idx) => (
                                          <li key={`${item.section}-${idx}`}>{obl}</li>
                                        ))}
                                      </ul>
                                    </div>

                                    <div className="bible-section-col">
                                      <div className="bible-kv">
                                        <span className="bible-kv-l">URN</span>
                                        <code className="bible-urn">{item.urn}</code>
                                        <button type="button" className="bible-copy-btn" onClick={() => handleCopyUrn(item.urn)}>
                                          {copiedUrn === item.urn ? "Copied ✓" : "Copy URN"}
                                        </button>
                                      </div>

                                      <div className="bible-kv-stack">
                                        <div>
                                          <p className="bible-kv-l">Cross-layer references</p>
                                          <p className="bible-kv-m">GDPR: {item.gdpr}</p>
                                          <p className="bible-kv-m">IT Act: {item.it_act}</p>
                                          <p className="bible-kv-m">CERT-In/RBI: {item.certin_rbi}</p>
                                        </div>

                                        <div className="bible-micro">
                                          <p className="bible-kv-l">Penalty cap</p>
                                          <p className="bible-kv-value">{item.max_penalty}</p>
                                        </div>

                                        <div className="bible-micro">
                                          <p className="bible-kv-l">SLA</p>
                                          <p className="bible-kv-value">{item.sla || "Immediate"}</p>
                                        </div>
                                      </div>
                                    </div>
                                  </div>

                                  <div className="bible-journey">
                                    <p>Compliance flow: Notice → Consent → Rights/Controls → Audit Trail</p>
                                  </div>
                                </div>
                              )}
                            </article>
                          );
                        })}
                      </div>
                    </section>
                  ))}
                </div>
              )}
            </article>

            <aside className="bible-panel bible-panel-side">
              <div className="bible-panel-top">
                <h2>Knowledge Infrastructure</h2>
                <p className="bible-quiet">Everything is indexed by URN, section, and legal lineage.</p>
              </div>

              <div className="bible-glass-card">
                <h3>Fast Paths</h3>
                <Link to="/acts" className="bible-side-link">Acts</Link>
                <Link to="/rules" className="bible-side-link">Rules</Link>
                <Link to="/interpretations" className="bible-side-link">Interpretations</Link>
                <Link to="/discussions" className="bible-side-link">Discussions</Link>
              </div>

              <div className="bible-glass-card">
                <h3>Severity legend</h3>
                <div className="bible-legend-row">
                  <span><span className="bible-dot low" /> Low impact</span>
                  <span><span className="bible-dot medium" /> Medium impact</span>
                  <span><span className="bible-dot high" /> High impact</span>
                  <span><span className="bible-dot critical" /> Critical impact</span>
                </div>
              </div>

              <div className="bible-glass-card">
                <h3>Search context</h3>
                <p className="bible-side-note">
                  Use the explorer controls to isolate chapter-wise obligations and open a section to inspect
                  penalties, URNs, and cross-references.
                </p>
              </div>
            </aside>
          </section>
        )}

        {activeTab === "penalties" && (
          <section className="bible-penalties card">
            <header className="bible-panel-head">
              <div>
                <h2>Statutory Penalty Schedule</h2>
                <p className="bible-quiet">Schedule to DPDPA, 2023, indexed by section.</p>
              </div>
              <span className="bible-chip">Max ₹250 Crore</span>
            </header>

            <div className="bible-penalty-grid">
              {PENALTY_SCHEDULE.map((p) => {
                const severity = severityFromPenalty(p.max_fine);
                return (
                  <article key={p.urn} className="bible-penalty-card">
                    <h3>{p.violation}</h3>
                    <p className="bible-urn-line" title={p.section}><strong>Section:</strong> {p.section}</p>
                    <div className="bible-penalty-row">
                      <span className={`bible-pill ${severity}`}>
                        <PriorityBadge priority={severity} showDot={false} />
                      </span>
                      <button type="button" className="bible-copy-btn" onClick={() => handleCopyUrn(p.urn)}>
                        {copiedUrn === p.urn ? "Copied ✓" : "Copy URN"}
                      </button>
                    </div>
                    <p className="bible-fine">{p.max_fine}</p>
                    <div className="bible-penalty-bar" aria-hidden="true">
                      <span style={{ width: `${PENALTY_BAR[severity]}%` }} />
                    </div>
                  </article>
                );
              })}
            </div>
          </section>
        )}

        {activeTab === "raw" && (
          <section className="bible-raw">
            <header className="bible-panel-head">
              <h2>Official Gazette Ledger</h2>
              <span className="bible-chip">Markdown</span>
            </header>

            {loadingRaw ? (
              <div className="bible-loading">Loading canonical act text from API gateway…</div>
            ) : rawError ? (
              <div role="alert" className="bible-alert">
                {rawError}
              </div>
            ) : (
              <pre className="bible-pre">{rawMarkdown || "No content available."}</pre>
            )}
          </section>
        )}
      </div>
    </div>
  );
}
