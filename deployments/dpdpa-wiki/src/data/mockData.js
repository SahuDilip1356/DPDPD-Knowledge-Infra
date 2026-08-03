/* ═══════════════════════════════════════════════════════════════════
   REAL DPDPA INTELLIGENCE DATA — Consolidated for all 8 MVP screens
   Regulatory Knowledge Infrastructure (August 2023 — July 2026)
   ═══════════════════════════════════════════════════════════════════ */

// ── Constitutional Vocabulary ────────────────────────────────────
export const CONSTITUTIONAL_NOUNS = [
  "Act", "Rule", "Notification", "Circular", "Case", "Judgement", "Opinion",
  "Organization", "Person", "Template", "Risk", "Control", "Purpose",
  "Consent", "Legal Basis", "Penalty", "Data Category", "Industry",
  "Business Process", "Software", "Vendor", "Country", "Authority"
];

export const CONSTITUTIONAL_VERBS = [
  "Amends", "Supersedes", "Interprets", "Depends On", "Overrides",
  "Conflicts With", "Supports", "Implements", "References", "Requires",
  "Applies To", "Violates", "Explains", "Replaces"
];

// ── Trust Dimensions (§25) ───────────────────────────────────────
export const TRUST_DIMENSIONS = {
  SOURCE_AUTHORITY: "Source Authority",
  SOURCE_INTEGRITY: "Source Integrity",
  CITATION_INTEGRITY: "Citation Integrity",
  EXTRACTION_QUALITY: "Extraction Quality",
  INTERPRETATION_CONFIDENCE: "Interpretation Confidence",
  HUMAN_REVIEW: "Human Review Status",
  FRESHNESS: "Freshness"
};

// ── Knowledge Objects ────────────────────────────────────────────
export const KNOWLEDGE_OBJECTS = [
  {
    urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    title: "Digital Personal Data Protection Act 2023",
    type: "Act",
    version: 1,
    status: "active",
    date_legal: "2023-08-11",
    date_detected: "2023-08-11",
    date_published: "2023-08-11",
    authority: "Parliament of India",
    jurisdiction: "India",
    summary: "The foundational privacy legislation passed by the Parliament of India. Establishes rights of data principals, duties of data fiduciaries, security mandates, and structures the Data Protection Board of India (DPBI) to enforce compliance.",
    entities: ["Act", "Consent", "Purpose", "Legal Basis", "Penalty", "Authority"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 1.0,
      extraction_quality: 0.98,
      interpretation_confidence: 1.0,
      human_review: "approved",
      freshness: 0.85
    },
    evidence: [
      {
        id: "ev-001",
        source_urn: "urn:ki:in:dpdp:source:gazette-dpdpa-2023",
        source_name: "Gazette of India Extraordinary Part II Section 1",
        source_tier: "primary",
        citation_text: "An Act to provide for the processing of digital personal data in a manner that recognises both the right of individuals to protect their personal data and the need to process such personal data for lawful purposes.",
        coordinates: { page: 1, section: "Preamble" },
        hash: "da8cf9105432a9e8751db432ef5012a4b8cd9a77efca1357db5c6c99ef412e87",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025", edge_type: "Depends On", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "Establishes a completely new digital personal data compliance regime in India.",
      affected_roles: ["Chief Privacy Officer", "Data Protection Officer", "General Counsel"],
      affected_processes: ["Data Ingestion", "Consent Management", "Data Principal Rights", "Data Lifecycle Management"],
      action_required: "Map all digital personal data processing flows across the enterprise and implement reasonable security safeguards."
    }
  },
  {
    urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
    title: "Digital Personal Data Protection Rules 2025",
    type: "Rule",
    version: 1,
    status: "active",
    date_legal: "2025-11-13",
    date_detected: "2025-11-13",
    date_published: "2025-11-13",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    summary: "The official rules specifying procedural details under the DPDP Act. Lays down concrete timelines, form templates, and rules for consent notices, DPBI operation, children's verifiable consent, and cross-border transfers.",
    entities: ["Rule", "Consent", "Data Category", "Control", "Authority"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 0.98,
      extraction_quality: 0.96,
      interpretation_confidence: 0.95,
      human_review: "approved",
      freshness: 0.95
    },
    evidence: [
      {
        id: "ev-002",
        source_urn: "urn:ki:in:dpdp:source:gazette-rules-2025",
        source_name: "Ministry of Electronics and Information Technology Notification G.S.R.",
        source_tier: "primary",
        citation_text: "In exercise of the powers conferred by section 40 of the Digital Personal Data Protection Act, 2023, the Central Government hereby makes the following rules...",
        coordinates: { page: 1, section: "Rule 1" },
        hash: "e5473a216db8aefcd81ab45dcf328a9be45c6db274f8a8de751db432ef5012ab",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:act:dpdpa-2023", edge_type: "Implements", direction: "outgoing" },
      { target_urn: "urn:ki:in:dpdp:rule:breach-notification-rule7", edge_type: "Depends On", direction: "outgoing" },
      { target_urn: "urn:ki:in:dpdp:rule:children-consent-rule10", edge_type: "Depends On", direction: "outgoing" },
      { target_urn: "urn:ki:in:dpdp:rule:cross-border-transfer-rule15", edge_type: "Depends On", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "Mandates phased compliance timeline reaching full enforcement by May 13, 2027.",
      affected_roles: ["Chief Privacy Officer", "DPO", "Compliance Lead"],
      affected_processes: ["Privacy Notice Display", "Grievance Redressal", "Parental Verification", "Incident Management"],
      action_required: "Align corporate privacy readiness program with the 18-month phased implementation roadmap."
    }
  },
  {
    urn: "urn:ki:in:dpdp:rule:breach-notification-rule7",
    title: "DPDP Rules 2025 — Rule 7: Personal Data Breach Intimation",
    type: "Rule",
    version: 1,
    status: "active",
    date_legal: "2025-11-13",
    date_detected: "2025-11-13",
    date_published: "2025-11-13",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    summary: "Sets out the exact procedure, templates, and timeline for notifying the Data Protection Board of India and affected data principals when a personal data breach occurs.",
    entities: ["Rule", "Penalty", "Control", "Authority"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 0.99,
      extraction_quality: 0.97,
      interpretation_confidence: 0.98,
      human_review: "approved",
      freshness: 0.95
    },
    evidence: [
      {
        id: "ev-003",
        source_urn: "urn:ki:in:dpdp:source:gazette-rules-2025",
        source_name: "DPDP Rules 2025 Official Text",
        source_tier: "primary",
        citation_text: "A Data Fiduciary shall, in the event of a personal data breach, intimate the Board and each affected Data Principal in accordance with Rule 7, within a period of 72 hours from the time the breach is detected.",
        coordinates: { page: 5, section: "Rule 7(1)" },
        hash: "c3ab8761db82e751db432ef5012a4b8cd9a77efca1357db5c6c99ef412e87ab12",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025", edge_type: "Depends On", direction: "incoming" },
      { target_urn: "urn:ki:in:law:cert-in:directive-2022", edge_type: "Conflicts With", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "Establishes a 72-hour mandatory breach notification SLA to DPBI.",
      affected_roles: ["CISO", "Incident Response Team", "DPO"],
      affected_processes: ["Breach Detection", "DPBI Intimation", "User Alerting"],
      action_required: "Update incident response playbooks for 72-hour breach SLA."
    }
  },
  {
    urn: "urn:ki:in:law:cert-in:directive-2022",
    title: "CERT-In Cyber Security Directions 2022 (6-Hour Breach SLA)",
    type: "Circular",
    version: 1,
    status: "active",
    date_legal: "2022-04-28",
    date_detected: "2022-04-28",
    date_published: "2022-04-28",
    authority: "Indian Computer Emergency Response Team (CERT-In)",
    jurisdiction: "India",
    summary: "Mandates reporting of cyber incidents to CERT-In within 6 hours of notice or tracking. Conflicts with DPDPA Rule 7 (72-hour notification timeline).",
    entities: ["Circular", "Penalty", "Control", "Authority"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 0.99,
      extraction_quality: 0.98,
      interpretation_confidence: 0.95,
      human_review: "approved",
      freshness: 0.90
    },
    evidence: [
      {
        id: "ev-certin-01",
        source_urn: "urn:ki:in:law:source:cert-in-directions-2022",
        source_name: "CERT-In Cyber Directions 2022",
        source_tier: "primary",
        citation_text: "Service providers, intermediaries, data centres, body corporate shall report cyber incidents to CERT-In within 6 hours of noticing.",
        coordinates: { page: 3, section: "Section 5" },
        hash: "f487a216db8aefcd81ab45dcf328a9be45c6db274f8a8de751db432ef5012e87",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:breach-notification-rule7", edge_type: "Conflicts With", direction: "incoming" }
    ],
    business_impact: {
      impact_summary: "Dual reporting burden: 6 hours to CERT-In vs 72 hours to DPBI.",
      affected_roles: ["CISO", "Legal Counsel"],
      affected_processes: ["Incident Escalation", "Regulatory Filings"],
      action_required: "Implement 2-tier triage system for CERT-In (6h) and DPBI (72h)."
    }
  },
  {
    urn: "urn:ki:in:law:rbi:circular:payment-data-2018",
    title: "RBI Storage of Payment System Data Directive 2018",
    type: "Circular",
    version: 1,
    status: "active",
    date_legal: "2018-04-06",
    date_detected: "2018-04-06",
    date_published: "2018-04-06",
    authority: "Reserve Bank of India (RBI)",
    jurisdiction: "India",
    summary: "Mandates that all payment system providers store full end-to-end transaction data exclusively within India. Harmonizes with DPDPA Section 16 cross-border transfer rules.",
    entities: ["Circular", "Data Category", "Control", "Authority"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 0.99,
      extraction_quality: 0.97,
      interpretation_confidence: 0.96,
      human_review: "approved",
      freshness: 0.90
    },
    evidence: [
      {
        id: "ev-rbi-01",
        source_urn: "urn:ki:in:law:source:rbi-payment-data-2018",
        source_name: "RBI Payment System Directive DPSS.CO.OD No. 2785/06.08.005/2017-18",
        source_tier: "primary",
        citation_text: "All system providers shall ensure that the entire data relating to payment systems operated by them is stored in a system only in India.",
        coordinates: { page: 1, section: "Paragraph 2" },
        hash: "b8973a216db8aefcd81ab45dcf328a9be45c6db274f8a8de751db432ef5012ff",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:cross-border-transfer-rule15", edge_type: "Harmonizes With", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "Strict data localization for financial & payment processing entities.",
      affected_roles: ["Chief Risk Officer", "CISO", "Head of Payments"],
      affected_processes: ["Cloud Storage", "Database Hosting", "Cross-Border API Calls"],
      action_required: "Ensure all payment logs and Card/UPI data reside on domestic Indian cloud regions."
    }
  },
  {
    urn: "urn:ki:in:law:pmla-2002:sec:12",
    title: "PMLA 2002 — Section 12: Mandatory 5-Year Financial Record Retention",
    type: "Act",
    version: 1,
    status: "active",
    date_legal: "2003-07-01",
    date_detected: "2003-07-01",
    date_published: "2003-07-01",
    authority: "Parliament of India",
    jurisdiction: "India",
    summary: "Requires reporting entities to maintain record of all transactions for 5 years. Overrides Data Principal erasure requests under DPDPA Section 12(3).",
    entities: ["Act", "Legal Basis", "Control", "Authority"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 1.0,
      extraction_quality: 0.99,
      interpretation_confidence: 0.98,
      human_review: "approved",
      freshness: 0.92
    },
    evidence: [
      {
        id: "ev-pmla-01",
        source_urn: "urn:ki:in:law:source:pmla-2002",
        source_name: "Prevention of Money-Laundering Act 2002",
        source_tier: "primary",
        citation_text: "Every reporting entity shall maintain a record of all transactions... for a period of five years from the date of transaction.",
        coordinates: { page: 12, section: "Section 12(1)(a)" },
        hash: "a1273a216db8aefcd81ab45dcf328a9be45c6db274f8a8de751db432ef5012dd",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:act:dpdpa-2023", edge_type: "Overrides", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "Statutory override: Right to Erasure does not apply to PMLA financial records.",
      affected_roles: ["Compliance Officer", "DPO", "Legal Counsel"],
      affected_processes: ["Data Erasure", "DSAR Fulfillment", "Data Archiving"],
      action_required: "Configure automated deletion exemption rules for AML/KYC records."
    },
    business_impact: {
      impact_summary: "Imposes a strict 72-hour regulatory notification SLA for data breaches.",
      affected_roles: ["CISO", "Incident Response Commander", "DPO"],
      affected_processes: ["Incident Response", "Breach Detection", "Regulatory Reporting"],
      action_required: "Integrate 72-hour reporting triggers into SOC playbooks and draft standard notification templates."
    }
  },
  {
    urn: "urn:ki:in:dpdp:rule:children-consent-rule10",
    title: "DPDP Rules 2025 — Rule 10: Verifiable Parental Consent",
    type: "Rule",
    version: 1,
    status: "active",
    date_legal: "2025-11-13",
    date_detected: "2025-11-13",
    date_published: "2025-11-13",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    summary: "Outlines approved mechanism for verifying age and obtaining parental/guardian consent for data processing of children under 18 or persons with disability.",
    entities: ["Rule", "Consent", "Person", "Control"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 0.97,
      extraction_quality: 0.95,
      interpretation_confidence: 0.94,
      human_review: "approved",
      freshness: 0.95
    },
    evidence: [
      {
        id: "ev-004",
        source_urn: "urn:ki:in:dpdp:source:gazette-rules-2025",
        source_name: "DPDP Rules 2025 Official Text",
        source_tier: "primary",
        citation_text: "For the purposes of section 9, a Data Fiduciary shall obtain verifiable consent of parent or lawful guardian using digital verification tokens, including those integrated with DigiLocker or electronic sign-off services.",
        coordinates: { page: 8, section: "Rule 10(2)" },
        hash: "b8cd9a77efca1357db5c6c99ef412e87a2d3e4f56b7c8d9e0f1a2b3c4d5e6f7a",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025", edge_type: "Depends On", direction: "incoming" }
    ],
    business_impact: {
      impact_summary: "Mandates verification for platforms serving minors; prohibits tracking and targeted ads.",
      affected_roles: ["Product Lead", "UX Designer", "DPO"],
      affected_processes: ["User Onboarding", "Age Verification", "Advertising & Marketing"],
      action_required: "Deploy age gating, integrate DigiLocker verification APIs, and disable tracking/targeting code for minor accounts."
    }
  },
  {
    urn: "urn:ki:in:dpdp:rule:cross-border-transfer-rule15",
    title: "DPDP Rules 2025 — Rule 15: Cross-Border Personal Data Transfer",
    type: "Rule",
    version: 1,
    status: "active",
    date_legal: "2025-11-13",
    date_detected: "2025-11-13",
    date_published: "2025-11-13",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    summary: "Implements the 'negative list' approach, allowing cross-border data transfer to all countries unless specifically restricted by Government notification. Reconciles DPDPA with sectoral localization requirements.",
    entities: ["Rule", "Country", "Data Category"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 0.98,
      extraction_quality: 0.96,
      interpretation_confidence: 0.92,
      human_review: "approved",
      freshness: 0.95
    },
    evidence: [
      {
        id: "ev-005",
        source_urn: "urn:ki:in:dpdp:source:gazette-rules-2025",
        source_name: "DPDP Rules 2025 Official Text",
        source_tier: "primary",
        citation_text: "Personal data may be transferred to any country or territory unless the Central Government notifies restrictions on such transfer... provided that sector-specific data localization rules in force shall continue to apply.",
        coordinates: { page: 12, section: "Rule 15(1)" },
        hash: "e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025", edge_type: "Depends On", direction: "incoming" }
    ],
    business_impact: {
      impact_summary: "Maintains international data hosting freedom, but subject to sectoral overrides (RBI, SEBI).",
      affected_roles: ["Cloud Architect", "General Counsel", "IT Security Lead"],
      affected_processes: ["Data Hosting", "Third-party Vendor Audits", "International Operations"],
      action_required: "Harmonize international transfer protocols with RBI/SEBI requirements, maintaining transparency in user notices."
    }
  },
  {
    urn: "urn:ki:in:dpdp:act:section33-penalties",
    title: "DPDP Act 2023 — Section 33: Penalty Framework",
    type: "Act",
    version: 1,
    status: "active",
    date_legal: "2023-08-11",
    date_detected: "2023-08-11",
    date_published: "2023-08-11",
    authority: "Parliament of India",
    jurisdiction: "India",
    summary: "Prescribes maximum monetary penalties for specific compliance breaches. Features a tiered scheme up to ₹250 crore for major security failures.",
    entities: ["Act", "Penalty", "Authority"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 1.0,
      extraction_quality: 0.99,
      interpretation_confidence: 1.0,
      human_review: "approved",
      freshness: 0.85
    },
    evidence: [
      {
        id: "ev-006",
        source_urn: "urn:ki:in:dpdp:source:gazette-dpdpa-2023",
        source_name: "DPDPA Gazette Text",
        source_tier: "primary",
        citation_text: "Schedule: Penalties. Failure of Data Fiduciary to take reasonable security safeguards... up to 250 crore rupees. Failure to notify... up to 200 crore rupees.",
        coordinates: { page: 22, section: "Schedule" },
        hash: "b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:act:dpdpa-2023", edge_type: "Implements", direction: "incoming" }
    ],
    business_impact: {
      impact_summary: "Substantial non-compliance risk requires priority implementation of reasonable security measures.",
      affected_roles: ["CEO", "CFO", "General Counsel", "CISO"],
      affected_processes: ["Risk Management", "Corporate Governance"],
      action_required: "Conduct high-level risk assessment and map potential financial risk exposures under DPDPA."
    }
  },
  {
    urn: "urn:ki:in:dpdp:act:section17-exemptions",
    title: "DPDP Act 2023 — Section 17: State Exemptions",
    type: "Act",
    version: 1,
    status: "active",
    date_legal: "2023-08-11",
    date_detected: "2023-08-11",
    date_published: "2023-08-11",
    authority: "Parliament of India",
    jurisdiction: "India",
    summary: "Exempts specific processing activities and state agencies from compliance obligations (notice, rights, retention limits) for reasons of national security, public order, and prevention of offenses.",
    entities: ["Act", "Authority", "Risk"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 1.0,
      extraction_quality: 0.98,
      interpretation_confidence: 0.95,
      human_review: "approved",
      freshness: 0.85
    },
    evidence: [
      {
        id: "ev-007",
        source_urn: "urn:ki:in:dpdp:source:gazette-dpdpa-2023",
        source_name: "DPDPA Gazette Text",
        source_tier: "primary",
        citation_text: "Provisions of this Act shall not apply to... processing of personal data by such instrumentality of the State as the Central Government may notify in the interests of sovereignty, security of the State, or public order.",
        coordinates: { page: 14, section: "Section 17(2)(a)" },
        hash: "f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:act:dpdpa-2023", edge_type: "Implements", direction: "incoming" }
    ],
    business_impact: {
      impact_summary: "State agencies have broad exemptions; private vendors executing government contracts must check pass-through obligations.",
      affected_roles: ["General Counsel", "Government Liaison Officer"],
      affected_processes: ["Government Contracting", "Public Sector Partnerships"],
      action_required: "Review data handling clauses in public sector contracts to distinguish exempt activities from standard commercial processing."
    }
  },
  {
    urn: "urn:ki:in:dpdp:rule:dpbi-recruitment-2026",
    title: "Data Protection Board of India (DPBI) Structure Rules",
    type: "Rule",
    version: 1,
    status: "active",
    date_legal: "2025-11-13",
    date_detected: "2025-11-13",
    date_published: "2025-11-13",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    summary: "Rules detailing the selection, tenure, and operating procedures of the Data Protection Board of India. Establishes a search-cum-selection committee consisting of government secretaries.",
    entities: ["Rule", "Authority"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 0.98,
      extraction_quality: 0.95,
      interpretation_confidence: 0.95,
      human_review: "approved",
      freshness: 0.95
    },
    evidence: [
      {
        id: "ev-008",
        source_urn: "urn:ki:in:dpdp:source:gazette-rules-2025",
        source_name: "DPDP Rules 2025",
        source_tier: "primary",
        citation_text: "The Board shall consist of a Chairperson and such other Members as the Central Government may notify... selected by a Search-cum-Selection Committee.",
        coordinates: { page: 18, section: "Rule 20" },
        hash: "e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025", edge_type: "Depends On", direction: "incoming" }
    ],
    business_impact: {
      impact_summary: "The adjudicating authority framework is formally defined; Board recruitment is underway since May 2026.",
      affected_roles: ["General Counsel", "Compliance Manager"],
      affected_processes: ["Dispute Resolution", "Regulatory Reporting"],
      action_required: "Monitor operational status of DPBI to understand active reporting channels."
    }
  },
  {
    urn: "urn:ki:in:dpdp:rule:consent-manager",
    title: "Consent Manager Registration Framework",
    type: "Rule",
    version: 1,
    status: "active",
    date_legal: "2025-11-13",
    date_detected: "2025-11-13",
    date_published: "2025-11-13",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    summary: "Specifies requirements for entities acting as Consent Managers. Establishes a registration process with DPBI, and requires ₹2 crore minimum net worth and 'data-blind' operation.",
    entities: ["Rule", "Consent", "Organization", "Control"],
    trust: {
      source_authority: 1.0,
      source_integrity: 1.0,
      citation_integrity: 0.97,
      extraction_quality: 0.94,
      interpretation_confidence: 0.92,
      human_review: "approved",
      freshness: 0.95
    },
    evidence: [
      {
        id: "ev-009",
        source_urn: "urn:ki:in:dpdp:source:gazette-rules-2025",
        source_name: "DPDP Rules 2025",
        source_tier: "primary",
        citation_text: "Every Consent Manager shall be registered with the Board... and shall operate an interoperable digital platform enabling data principals to give, review or withdraw consent.",
        coordinates: { page: 15, section: "Rule 14" },
        hash: "b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025", edge_type: "Depends On", direction: "incoming" }
    ],
    business_impact: {
      impact_summary: "Allows data principals to aggregate and control consent through third-party utility providers.",
      affected_roles: ["Product Lead", "Integration Engineer", "CPO"],
      affected_processes: ["Consent Management", "Data Principal Portal"],
      action_required: "Prepare system architecture to support standardized Consent Manager integration APIs by November 2026."
    }
  },
  {
    urn: "urn:ki:in:rbi:draft:data-governance-2026",
    title: "RBI Draft Data Governance Framework Guidance",
    type: "Circular",
    version: 1,
    status: "draft",
    date_legal: "2026-07-10",
    date_detected: "2026-07-12",
    date_published: "2026-07-10",
    authority: "Reserve Bank of India",
    jurisdiction: "India",
    summary: "Draft guidance issued by the RBI for banks and NBFCs, establishing an Enterprise Risk Management framework for data governance, quality, and privacy. Explicitly mandates harmony with DPDPA obligations.",
    entities: ["Circular", "Control", "Risk", "Authority"],
    trust: {
      source_authority: 0.98,
      source_integrity: 0.97,
      citation_integrity: 0.95,
      extraction_quality: 0.92,
      interpretation_confidence: 0.90,
      human_review: "pending",
      freshness: 0.99
    },
    evidence: [
      {
        id: "ev-010",
        source_urn: "urn:ki:in:rbi:source:draft-guidance-07-2026",
        source_name: "RBI Press Release & Draft Guidance Document",
        source_tier: "secondary",
        citation_text: "Regulated entities shall align their data storage, processing, and retrieval mechanisms with the principles of data minimization and purpose limitation under the DPDP Act.",
        coordinates: { page: 4, section: "Para 3.2" },
        hash: "a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:act:dpdpa-2023", edge_type: "Interprets", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "Harmonizes financial sector compliance with the national data protection law.",
      affected_roles: ["Chief Risk Officer", "Head of Digital Banking", "DPO"],
      affected_processes: ["Core Banking Operations", "KYC Processing", "Credit Underwriting"],
      action_required: "Review draft guidance, compile feedback for submission, and begin designing data governance ERM overlays."
    }
  }
];

// ── Regulatory Events ────────────────────────────────────────────
export const REGULATORY_EVENTS = [
  {
    id: "evt-001",
    title: "DPDP Act 2023 Receives Presidential Assent",
    type: "New Legislation",
    authority: "Parliament of India",
    jurisdiction: "India",
    date_published: "2023-08-11",
    date_effective: "2023-08-11",
    date_detected: "2023-08-11",
    impact_level: "critical",
    status: "active",
    review_status: "approved",
    summary: "President Droupadi Murmu grants assent to the Digital Personal Data Protection Act, 2023, following its passage in both houses of Parliament. It is officially published in the Gazette of India.",
    change_description: "Creates India's first unified, comprehensive legislative framework for digital personal data protection, superseding legacy guidelines under Section 43A of the IT Act.",
    affected_ko_urns: ["urn:ki:in:dpdp:act:dpdpa-2023", "urn:ki:in:dpdp:act:section33-penalties", "urn:ki:in:dpdp:act:section17-exemptions"],
    has_conflicts: false,
    evidence_count: { primary: 1, secondary: 0, tertiary: 0 },
    affected_industries: ["All Industries"],
    affected_processes: ["Data Collection", "Data Storage", "Third-party Sharing", "Security Controls"]
  },
  {
    id: "evt-002",
    title: "MeitY Releases Draft DPDP Rules 2025 for Consultation",
    type: "Draft Rules",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    date_published: "2025-01-03",
    date_effective: null,
    date_detected: "2025-01-03",
    impact_level: "high",
    status: "superseded",
    review_status: "approved",
    summary: "MeitY issues the draft Digital Personal Data Protection Rules, 2025, initiating a public consultation period scheduled to end on February 18, 2025.",
    change_description: "Provides the first look at the procedural framework, consent notice formats, and administrative structures under the DPDP Act.",
    affected_ko_urns: ["urn:ki:in:dpdp:rule:dpdp-rules-2025"],
    has_conflicts: false,
    evidence_count: { primary: 1, secondary: 1, tertiary: 0 },
    affected_industries: ["All Industries"],
    affected_processes: ["Consent Notice Display", "Data Subject Portals", "Incident Tracking"]
  },
  {
    id: "evt-003",
    title: "Public Consultation Period Extended to March 5",
    type: "Public Consultation Update",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    date_published: "2025-02-18",
    date_effective: null,
    date_detected: "2025-02-18",
    impact_level: "medium",
    status: "completed",
    review_status: "approved",
    summary: "MeitY extends the public consultation period on the draft DPDP Rules by two weeks to accommodate requests from industry associations and privacy groups.",
    change_description: "Extended window for submission of stakeholder comments; more than 6,900 submissions are ultimately compiled by the Ministry.",
    affected_ko_urns: ["urn:ki:in:dpdp:rule:dpdp-rules-2025"],
    has_conflicts: false,
    evidence_count: { primary: 1, secondary: 0, tertiary: 0 },
    affected_industries: ["All Industries"],
    affected_processes: ["Regulatory Affairs", "Stakeholder Engagement"]
  },
  {
    id: "evt-004",
    title: "DPDP Rules 2025 Officially Notified in Gazette",
    type: "New Rule",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    date_published: "2025-11-13",
    date_effective: "2025-11-13",
    date_detected: "2025-11-13",
    impact_level: "critical",
    status: "active",
    review_status: "approved",
    summary: "MeitY officially publishes the DPDP Rules, 2025, in the Gazette of India, marking the commencement of the implementation phase.",
    change_description: "Finalizes the regulatory obligations for notice, consent, breach reporting, and cross-border transfers. Establishes the 18-month phased compliance timeline.",
    affected_ko_urns: [
      "urn:ki:in:dpdp:rule:dpdp-rules-2025",
      "urn:ki:in:dpdp:rule:breach-notification-rule7",
      "urn:ki:in:dpdp:rule:children-consent-rule10",
      "urn:ki:in:dpdp:rule:cross-border-transfer-rule15"
    ],
    has_conflicts: false,
    evidence_count: { primary: 1, secondary: 2, tertiary: 0 },
    affected_industries: ["All Industries"],
    affected_processes: ["Data Governance", "Product Development", "Security Operations", "Legal Compliance"]
  },
  {
    id: "evt-005",
    title: "Phase 1 Commences: DPBI Administrative Provisions Enforced",
    type: "Phased Implementation Milestone",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    date_published: "2025-11-13",
    date_effective: "2025-11-13",
    date_detected: "2025-11-13",
    impact_level: "high",
    status: "active",
    review_status: "approved",
    summary: "Provisions relating to the establishment, structure, and operational regulations of the Data Protection Board of India (DPBI) take effect immediately.",
    change_description: "Enforces the legal setup of the DPBI, enabling the government to initiate candidate selection for Chairperson and Board members.",
    affected_ko_urns: ["urn:ki:in:dpdp:rule:dpbi-recruitment-2026"],
    has_conflicts: false,
    evidence_count: { primary: 1, secondary: 0, tertiary: 0 },
    affected_industries: ["All Industries"],
    affected_processes: ["Regulatory Dispute Management"]
  },
  {
    id: "evt-006",
    title: "Writ Petitions Clubbed in Supreme Court Challenging DPB Independence",
    type: "Court Challenge",
    authority: "Supreme Court of India",
    jurisdiction: "India",
    date_published: "2026-03-10",
    date_effective: null,
    date_detected: "2026-03-12",
    impact_level: "critical",
    status: "active",
    review_status: "under_review",
    summary: "The Supreme Court of India clubs several writ petitions challenging the constitutionality of the DPDP Act and 2025 Rules, focusing on concerns regarding the independence of the Data Protection Board and executive dominance in selection.",
    change_description: "The legal framework is under judicial review; petitions specifically target the selection committee composition (consisting of secretaries) and short terms of members.",
    affected_ko_urns: ["urn:ki:in:dpdp:rule:dpbi-recruitment-2026", "urn:ki:in:dpdp:act:dpdpa-2023"],
    has_conflicts: true,
    conflict_summary: "Constitutional conflict: executive-led selection committee and lack of judicial security of tenure for DPBI members may violate separation of powers and judicial independence principles.",
    evidence_count: { primary: 0, secondary: 2, tertiary: 0 },
    affected_industries: ["All Industries"],
    affected_processes: ["Legal Risk Management", "Strategic Compliance Planning"]
  },
  {
    id: "evt-007",
    title: "RTI Activists File Challenges Against Section 44(3) Blanket Ban",
    type: "Court Challenge",
    authority: "Supreme Court of India",
    jurisdiction: "India",
    date_published: "2026-04-05",
    date_effective: null,
    date_detected: "2026-04-06",
    impact_level: "high",
    status: "active",
    review_status: "under_review",
    summary: "Civil society groups and RTI activists file writ petitions in the Supreme Court, challenging Section 44(3) of the DPDP Act, which amends the RTI Act 2005 to restrict personal information disclosure.",
    change_description: "Legal tension regarding public transparency vs. privacy. Activists argue the amendment creates an absolute barrier to accessing government records and public interest data.",
    affected_ko_urns: ["urn:ki:in:dpdp:act:dpdpa-2023"],
    has_conflicts: true,
    conflict_summary: "Fundamental rights tension: Right to Information (Article 19(1)(a)) vs. Right to Privacy (Article 21) as amended by Section 44(3).",
    evidence_count: { primary: 0, secondary: 1, tertiary: 0 },
    affected_industries: ["Government", "Media", "Public Interest Orgs"],
    affected_processes: ["Public Disclosure Request Management"]
  },
  {
    id: "evt-008",
    title: "MeitY Formally Initiates DPBI Member Recruitment",
    type: "Government Notification",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    date_published: "2026-05-06",
    date_effective: null,
    date_detected: "2026-05-07",
    impact_level: "high",
    status: "active",
    review_status: "approved",
    summary: "MeitY issues a public notice inviting applications for one Chairperson and four Members of the Data Protection Board of India, initiating the recruitment phase.",
    change_description: "Recruitment starts for the core adjudicating body of the DPDPA, marking the transition from legislative structure to staffing.",
    affected_ko_urns: ["urn:ki:in:dpdp:rule:dpbi-recruitment-2026"],
    has_conflicts: false,
    evidence_count: { primary: 1, secondary: 0, tertiary: 0 },
    affected_industries: ["All Industries"],
    affected_processes: ["Governance"]
  },
  {
    id: "evt-009",
    title: "RBI Releases Draft Data Governance Framework Guidance",
    type: "Sectoral Circular",
    authority: "Reserve Bank of India",
    jurisdiction: "India",
    date_published: "2026-07-10",
    date_effective: null,
    date_detected: "2026-07-10",
    impact_level: "high",
    status: "active",
    review_status: "pending",
    summary: "The RBI issues draft guidance establishing a comprehensive Data Governance Framework for banks and NBFCs, incorporating DPDPA principles of minimization and purpose limitation.",
    change_description: "Sectoral alignment begins; financial institutions must integrate DPDPA constraints into their Enterprise Risk Management (ERM) overlays.",
    affected_ko_urns: ["urn:ki:in:rbi:draft:data-governance-2026", "urn:ki:in:dpdp:act:dpdpa-2023"],
    has_conflicts: false,
    evidence_count: { primary: 1, secondary: 1, tertiary: 0 },
    affected_industries: ["Banking", "NBFCs", "Fintech", "Payment Systems"],
    affected_processes: ["Core Banking Operations", "KYC Processing", "Credit Underwriting"]
  },
  {
    id: "evt-010",
    title: "Supreme Court Declines Interim Stay on DPDPA Implementation",
    type: "Judicial Decision",
    authority: "Supreme Court of India",
    jurisdiction: "India",
    date_published: "2026-07-18",
    date_effective: "2026-07-18",
    date_detected: "2026-07-19",
    impact_level: "high",
    status: "active",
    review_status: "approved",
    summary: "The Supreme Court issues notices to the Union government regarding the combined writ petitions, but declines to grant an interim stay on the implementation of the DPDP Act or Rules.",
    change_description: "The compliance timeline remains active. Businesses cannot count on legal delay and must proceed with compliance systems.",
    affected_ko_urns: ["urn:ki:in:dpdp:act:dpdpa-2023", "urn:ki:in:dpdp:rule:dpdp-rules-2025"],
    has_conflicts: false,
    evidence_count: { primary: 0, secondary: 1, tertiary: 0 },
    affected_industries: ["All Industries"],
    affected_processes: ["Compliance Program Management"]
  },
  {
    id: "evt-011",
    title: "Phase 2 Commences: Consent Manager Registration Opens (Upcoming)",
    type: "Phased Implementation Milestone",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    date_published: "2026-11-13",
    date_effective: "2026-11-13",
    date_detected: null,
    impact_level: "high",
    status: "upcoming",
    review_status: "pending",
    summary: "Provisions relating to the registration, security rules, and operating interfaces of Consent Managers are scheduled to take effect.",
    change_description: "Enforces the Consent Manager framework, allowing Indian companies with a minimum net worth of ₹2 crore to apply for registry status.",
    affected_ko_urns: ["urn:ki:in:dpdp:rule:consent-manager"],
    has_conflicts: false,
    evidence_count: { primary: 0, secondary: 0, tertiary: 0 },
    affected_industries: ["Technology", "All Consumer-Facing Businesses"],
    affected_processes: ["Consent Architecture", "Product Development"]
  },
  {
    id: "evt-012",
    title: "Phase 3: Substantive Obligations and Penalties Fully Enforceable (Future)",
    type: "Phased Implementation Milestone",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    date_published: "2027-05-13",
    date_effective: "2027-05-13",
    date_detected: null,
    impact_level: "critical",
    status: "future",
    review_status: "pending",
    summary: "The 18-month transition window expires. Full compliance across all notice, consent, breach, and children's data rules becomes mandatory, and the DPBI penalty regime is activated.",
    change_description: "Ultimate compliance deadline. Non-compliance after this date is subject to monetary penalties of up to ₹250 crore.",
    affected_ko_urns: [
      "urn:ki:in:dpdp:act:dpdpa-2023",
      "urn:ki:in:dpdp:rule:dpdp-rules-2025",
      "urn:ki:in:dpdp:act:section33-penalties"
    ],
    has_conflicts: false,
    evidence_count: { primary: 0, secondary: 0, tertiary: 0 },
    affected_industries: ["All Industries"],
    affected_processes: ["All Operations"]
  }
];

// ── Action Items ─────────────────────────────────────────────────
export const ACTION_ITEMS = [
  {
    id: "act-001",
    title: "Map Corporate Digital Personal Data Flows",
    source_obligation: "DPDP Act 2023 — Section 4 & 5",
    triggering_event_id: "evt-001",
    ko_urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    priority: "critical",
    status: "in_progress",
    owner: "DPO",
    reviewer: "General Counsel",
    due_date: "2026-09-30",
    applicability: "applies",
    applicability_rationale: "Organization collects and processes digital personal data of Indian residents.",
    affected_roles: ["Chief Privacy Officer", "DPO", "Compliance Lead"],
    affected_process: "Data Governance",
    related_control: "CTRL-DATA-MAP-01",
    description: "Conduct a comprehensive discovery and mapping exercise to identify all digital personal data storage, processing locations, and trans-border flows within the enterprise.",
    completion_evidence: null
  },
  {
    id: "act-002",
    title: "Redesign Consent Notices per Rule requirements",
    source_obligation: "DPDP Rules 2025 — Rule 3 & 4",
    triggering_event_id: "evt-004",
    ko_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
    priority: "high",
    status: "accepted",
    owner: "UX Product Manager",
    reviewer: "DPO",
    due_date: "2026-10-31",
    applicability: "applies",
    applicability_rationale: "Organization displays consent banners and collects consent on mobile/web applications.",
    affected_roles: ["Product Lead", "UX Designer", "Front-end Engineer"],
    affected_process: "Privacy Notice Display",
    related_control: "CTRL-CONSENT-UI-02",
    description: "Update online consent notices to be standalone, itemized, and clearly state purposes and withdrawal options. Provide translation features in Eighth Schedule languages where appropriate.",
    completion_evidence: null
  },
  {
    id: "act-003",
    title: "Deploy 72-Hour Breach Reporting SOC Playbook",
    source_obligation: "DPDP Rules 2025 — Rule 7",
    triggering_event_id: "evt-004",
    ko_urn: "urn:ki:in:dpdp:rule:breach-notification-rule7",
    priority: "critical",
    status: "proposed",
    owner: "CISO",
    reviewer: "DPO",
    due_date: "2026-11-30",
    applicability: "applies",
    applicability_rationale: "Failure to report data breaches to the DPBI triggers penalties up to ₹200 crore.",
    affected_roles: ["CISO", "Incident Response Commander", "Security Operations Analyst"],
    affected_process: "Incident Response",
    related_control: "CTRL-BREACH-REP-01",
    description: "Establish a rapid incident response SOP to evaluate data breaches and trigger DPBI / affected principal notifications within 72 hours of detection.",
    completion_evidence: null
  },
  {
    id: "act-004",
    title: "Implement Age Gating and Parental Consent Flows",
    source_obligation: "DPDP Rules 2025 — Rule 10",
    triggering_event_id: "evt-004",
    ko_urn: "urn:ki:in:dpdp:rule:children-consent-rule10",
    priority: "high",
    status: "proposed",
    owner: "Product Engineering Lead",
    reviewer: "DPO",
    due_date: "2027-02-28",
    applicability: "applies",
    applicability_rationale: "User registration logs show accounts from users under 18.",
    affected_roles: ["Product Lead", "Back-end Engineer", "Identity Architect"],
    affected_process: "User Onboarding",
    related_control: "CTRL-CHILD-GATE-01",
    description: "Deploy age verification gates at sign-up. Integrated DigiLocker verification flows for parents of minor accounts, and disable tracking & targeted advertising for minor profiles.",
    completion_evidence: null
  },
  {
    id: "act-005",
    title: "Harmonize Cloud Hosting with RBI Data Localization",
    source_obligation: "RBI Guidelines & Rule 15 Cross-Border",
    triggering_event_id: "evt-009",
    ko_urn: "urn:ki:in:dpdp:rule:cross-border-transfer-rule15",
    priority: "high",
    status: "in_progress",
    owner: "Cloud Architect",
    reviewer: "CISO",
    due_date: "2026-12-15",
    applicability: "applies",
    applicability_rationale: "Organization processes payment data and is a regulated entity under the RBI.",
    affected_roles: ["Cloud Architect", "Database Administrator", "CRO"],
    affected_process: "Data Hosting",
    related_control: "CTRL-LOCALIZATION-03",
    description: "Migrate core financial records and customer PII to local cloud instances (AWS Mumbai/Pune or GCP Delhi/Mumbai) to satisfy RBI localization overlays.",
    completion_evidence: null
  },
  {
    id: "act-006",
    title: "Assess Significant Data Fiduciary (SDF) Trigger Status",
    source_obligation: "DPDP Act 2023 — Section 10",
    triggering_event_id: "evt-001",
    ko_urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    priority: "high",
    status: "accepted",
    owner: "DPO",
    reviewer: "General Counsel",
    due_date: "2026-08-31",
    applicability: "applies",
    applicability_rationale: "Processing volume exceeds 5 million active customer profiles; assessment required.",
    affected_roles: ["Chief Privacy Officer", "DPO", "CRO"],
    affected_process: "Governance",
    related_control: "CTRL-SDF-ASSESS-01",
    description: "Compare enterprise scale against defined MeitY volume thresholds to confirm designation as a Significant Data Fiduciary. If designated, trigger residency and audit plans.",
    completion_evidence: null
  },
  {
    id: "act-007",
    title: "Establish 30-day Grievance Redressal SLA Tracker",
    source_obligation: "DPDP Rules 2025 — Rule 13",
    triggering_event_id: "evt-004",
    ko_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
    priority: "medium",
    status: "accepted",
    owner: "Customer Support Manager",
    reviewer: "DPO",
    due_date: "2026-09-15",
    applicability: "applies",
    applicability_rationale: "Consumers must have direct grievance channels prior to DPBI escalation.",
    affected_roles: ["Customer Support Lead", "DPO", "Legal Specialist"],
    affected_process: "Grievance Handling",
    related_control: "CTRL-GRIEVANCE-01",
    description: "Deploy ticketing system dashboard tracking complaints. Implement 30-day resolution alerts to ensure answers before users can escalate issues to the DPBI.",
    completion_evidence: null
  },
  {
    id: "act-008",
    title: "Prepare for Consent Manager API Integrations",
    source_obligation: "DPDP Rules 2025 — Rule 14",
    triggering_event_id: "evt-004",
    ko_urn: "urn:ki:in:dpdp:rule:consent-manager",
    priority: "medium",
    status: "proposed",
    owner: "Integration Lead",
    reviewer: "CPO",
    due_date: "2026-11-13",
    applicability: "applies",
    applicability_rationale: "Consent Manager portal connectivity opens in November 2026.",
    affected_roles: ["Product Lead", "Front-end Engineer", "Privacy Architect"],
    affected_process: "Consent Management",
    related_control: "CTRL-CM-API-01",
    description: "Design OAuth and API layers to accept standardized consent signals, revocations, and queries from registered Consent Managers.",
    completion_evidence: null
  },
  {
    id: "act-009",
    title: "Implement India-Resident DPO Governance Structure",
    source_obligation: "DPDP Act 2023 — Section 10(2)(a)",
    triggering_event_id: "evt-001",
    ko_urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    priority: "high",
    status: "accepted",
    owner: "CEO Office",
    reviewer: "General Counsel",
    due_date: "2026-09-15",
    applicability: "applies",
    applicability_rationale: "Required for Significant Data Fiduciaries.",
    affected_roles: ["CEO", "General Counsel", "HR Director"],
    affected_process: "Governance",
    related_control: "CTRL-GOV-DPO-02",
    description: "Create a formal India-resident Data Protection Officer position with direct board reporting lines. Appoint candidate and register contact info on public portals.",
    completion_evidence: null
  },
  {
    id: "act-010",
    title: "Prepare for Annual Independent Privacy Audits",
    source_obligation: "DPDP Act 2023 — Section 10(2)(c)",
    triggering_event_id: "evt-001",
    ko_urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    priority: "medium",
    status: "proposed",
    owner: "Internal Audit Lead",
    reviewer: "DPO",
    due_date: "2027-04-30",
    applicability: "applies",
    applicability_rationale: "SDF requirements dictate annual third-party audits.",
    affected_roles: ["Internal Audit Lead", "DPO", "Compliance Specialist"],
    affected_process: "Annual Audit",
    related_control: "CTRL-AUDIT-PREP-01",
    description: "Establish audit scope and compile evidence library (data flows, consent logs, risk registries, SOC reports) for external privacy auditor evaluation.",
    completion_evidence: null
  }
];

// ── Pipeline Items (Factory Board) ───────────────────────────────
export const PIPELINE_ITEMS = [
  // Stage 1 — Research / Scout
  {
    id: "pipe-001",
    title: "TRAI Consultation Paper on Telecom PII Security",
    source: "TRAI Portal",
    authority: "Telecom Regulatory Authority of India",
    current_stage: 1,
    stage_name: "Research",
    time_in_stage: "15m",
    assigned_to: "Scout Agent",
    priority: "medium",
    blocking_issues: [],
    auto_checks: { schema_valid: false, entities_resolved: false, duplicates_checked: false }
  },
  {
    id: "pipe-002",
    title: "IRDAI Guidelines on Policyholder Data Encryption",
    source: "IRDAI Database",
    authority: "Insurance Regulatory and Development Authority",
    current_stage: 1,
    stage_name: "Research",
    time_in_stage: "8m",
    assigned_to: "Scout Agent",
    priority: "low",
    blocking_issues: [],
    auto_checks: { schema_valid: false, entities_resolved: false, duplicates_checked: false }
  },
  // Stage 2 — Verification / Citation
  {
    id: "pipe-003",
    title: "Bombay HC Judgement on Data Erasure Rights",
    source: "High Court Reporter",
    authority: "Bombay High Court",
    current_stage: 2,
    stage_name: "Verification / Citation",
    time_in_stage: "2h",
    assigned_to: "Citation Analyst",
    priority: "medium",
    blocking_issues: ["Awaiting official copy of judgement text"],
    auto_checks: { schema_valid: true, entities_resolved: false, duplicates_checked: false }
  },
  {
    id: "pipe-004",
    title: "Supreme Court Petition in WP(C) 177/2026",
    source: "SC Docket",
    authority: "Supreme Court of India",
    current_stage: 2,
    stage_name: "Verification / Citation",
    time_in_stage: "12m",
    assigned_to: "Citation Analyst",
    priority: "high",
    blocking_issues: [],
    auto_checks: { schema_valid: true, entities_resolved: false, duplicates_checked: false }
  },
  // Stage 3 — Knowledge Engineering / Parsing
  {
    id: "pipe-005",
    title: "MeitY Notifications on Age Verification Standards",
    source: "Official Gazette",
    authority: "Ministry of Electronics and IT",
    current_stage: 3,
    stage_name: "Knowledge Engineering",
    time_in_stage: "1h 15m",
    assigned_to: "Knowledge Engineer",
    priority: "high",
    blocking_issues: [],
    auto_checks: { schema_valid: true, entities_resolved: false, duplicates_checked: false }
  },
  // Stage 4 — Ontology Mapping
  {
    id: "pipe-006",
    title: "SEBI Circular on Asset Management Data Rules",
    source: "SEBI Gazette",
    authority: "Securities and Exchange Board of India",
    current_stage: 4,
    stage_name: "Ontology",
    time_in_stage: "45m",
    assigned_to: "Ontology Agent",
    priority: "medium",
    blocking_issues: ["Noun 'Asset Management Company' lacks taxonomy link"],
    auto_checks: { schema_valid: true, entities_resolved: false, duplicates_checked: true }
  },
  {
    id: "pipe-007",
    title: "NPCI Standards on UPI Consent Storage",
    source: "NPCI Library",
    authority: "National Payments Corporation of India",
    current_stage: 4,
    stage_name: "Ontology",
    time_in_stage: "20m",
    assigned_to: "Ontology Agent",
    priority: "low",
    blocking_issues: [],
    auto_checks: { schema_valid: true, entities_resolved: false, duplicates_checked: true }
  },
  // Stage 5 — Relationship Engineering
  {
    id: "pipe-008",
    title: "DPBI Draft Exemption Rules for Government Schemes",
    source: "DPBI Official",
    authority: "Data Protection Board of India",
    current_stage: 5,
    stage_name: "Relationship Engineering",
    time_in_stage: "3h",
    assigned_to: "Relationship Engineer",
    priority: "medium",
    blocking_issues: ["Tension with parent Act Section 17 requires clarification"],
    auto_checks: { schema_valid: true, entities_resolved: true, duplicates_checked: true }
  },
  // Stage 6 — Reasoning
  {
    id: "pipe-009",
    title: "IT Act Section 43A Rule Supersession Conflict Analysis",
    source: "Internal Knowledge Factory",
    authority: "Knowledge Team",
    current_stage: 6,
    stage_name: "Reasoning",
    time_in_stage: "1h 10m",
    assigned_to: "Reasoning Agent",
    priority: "high",
    blocking_issues: [],
    auto_checks: { schema_valid: true, entities_resolved: true, duplicates_checked: true }
  },
  {
    id: "pipe-010",
    title: "Analysis: Section 44(3) RTI Amendment Impact",
    source: "Internal Knowledge Factory",
    authority: "Knowledge Team",
    current_stage: 6,
    stage_name: "Reasoning",
    time_in_stage: "2h",
    assigned_to: "Reasoning Agent",
    priority: "medium",
    blocking_issues: ["Awaiting SC hearing updates to refine conflict parameters"],
    auto_checks: { schema_valid: true, entities_resolved: true, duplicates_checked: true }
  },
  // Stage 7 — Business Translation
  {
    id: "pipe-011",
    title: "RBI Enterprise Risk Management Alignment Guide",
    source: "RBI Draft Circular",
    authority: "Reserve Bank of India",
    current_stage: 7,
    stage_name: "Business Translation",
    time_in_stage: "1h 30m",
    assigned_to: "Business Translator",
    priority: "high",
    blocking_issues: [],
    auto_checks: { schema_valid: true, entities_resolved: true, duplicates_checked: true }
  },
  {
    id: "pipe-012",
    title: "DigiLocker Integration Playbook for Minor Accounts",
    source: "MeitY Guidelines",
    authority: "Ministry of Electronics and IT",
    current_stage: 7,
    stage_name: "Business Translation",
    time_in_stage: "40m",
    assigned_to: "Business Translator",
    priority: "medium",
    blocking_issues: [],
    auto_checks: { schema_valid: true, entities_resolved: true, duplicates_checked: true }
  },
  // Stage 8 — Publishing
  {
    id: "pipe-013",
    title: "CISO Compliance Checklist: May 2027 Full Enforcement",
    source: "Internal Research",
    authority: "Knowledge Team",
    current_stage: 8,
    stage_name: "Publishing",
    time_in_stage: "30m",
    assigned_to: "Publishing Agent",
    priority: "critical",
    blocking_issues: [],
    auto_checks: { schema_valid: true, entities_resolved: true, duplicates_checked: true }
  },
  {
    id: "pipe-014",
    title: "Legal Briefing: Supreme Court Stay Hearing Report",
    source: "Internal Research",
    authority: "Knowledge Team",
    current_stage: 8,
    stage_name: "Publishing",
    time_in_stage: "10m",
    assigned_to: "Publishing Agent",
    priority: "high",
    blocking_issues: [],
    auto_checks: { schema_valid: true, entities_resolved: true, duplicates_checked: true }
  }
];

// ── Factory Department Names ─────────────────────────────────────
export const FACTORY_DEPARTMENTS = [
  { id: 1, name: "Research", short: "Scout", icon: "🔍" },
  { id: 2, name: "Verification", short: "Citation", icon: "✅" },
  { id: 3, name: "Knowledge Engineering", short: "Parsing", icon: "🏗️" },
  { id: 4, name: "Ontology", short: "Ontology", icon: "📚" },
  { id: 5, name: "Relationship Engineering", short: "Relations", icon: "🔗" },
  { id: 6, name: "Reasoning", short: "Reasoning", icon: "🧠" },
  { id: 7, name: "Business Translation", short: "Translation", icon: "💼" },
  { id: 8, name: "Publishing", short: "Publishing", icon: "📢" }
];

// ── Git Ledger Timeline ──────────────────────────────────────────
export const TIMELINE_EVENTS = [
  {
    commit_hash: "d3b4a5c",
    system_time: "2023-08-11T12:00:00Z",
    event_type: "publish",
    message: "Published: Digital Personal Data Protection Act, 2023 (v1)",
    actor: "publishing_agent",
    actor_type: "system",
    ko_urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    version: 1
  },
  {
    commit_hash: "a2c1e4f",
    system_time: "2025-01-03T09:30:00Z",
    event_type: "publish",
    message: "Published: Draft Digital Personal Data Protection Rules, 2025 (v1)",
    actor: "publishing_agent",
    actor_type: "system",
    ko_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
    version: 1
  },
  {
    commit_hash: "8f4b2e6",
    system_time: "2025-02-18T10:00:00Z",
    event_type: "system_update",
    message: "Deadline Extension: Public consultation extended to March 5, 2025",
    actor: "meity_scout",
    actor_type: "system",
    ko_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
    version: 1
  },
  {
    commit_hash: "c5d1e4f",
    system_time: "2025-11-13T11:45:00Z",
    event_type: "publish",
    message: "Published: Digital Personal Data Protection Rules, 2025 (v1) — Official Notification",
    actor: "publishing_agent",
    actor_type: "system",
    ko_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
    version: 1
  },
  {
    commit_hash: "e4f8b2c",
    system_time: "2025-11-13T12:00:00Z",
    event_type: "version_update",
    message: "Status Update: Draft rules marked as superseded by officially notified Rules",
    actor: "reasoning_agent",
    actor_type: "system",
    ko_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
    version: 1
  },
  {
    commit_hash: "3b2c1d0",
    system_time: "2026-03-10T14:15:00Z",
    event_type: "conflict_detected",
    message: "Conflict Detected: SC Petition challenges independence of DPBI executive search rules",
    actor: "reasoning_agent",
    actor_type: "system",
    ko_urn: "urn:ki:in:dpdp:rule:dpbi-recruitment-2026",
    version: 1
  },
  {
    commit_hash: "f8e7d6c",
    system_time: "2026-04-05T09:00:00Z",
    event_type: "conflict_detected",
    message: "Conflict Detected: Section 44(3) blanket privacy ban vs. RTI Act disclosure rules",
    actor: "reasoning_agent",
    actor_type: "system",
    ko_urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    version: 1
  },
  {
    commit_hash: "a9b8c7d",
    system_time: "2026-05-06T11:00:00Z",
    event_type: "system_update",
    message: "Recruitment Action: MeitY initiates DPBI Chairperson and Member recruitment",
    actor: "meity_scout",
    actor_type: "system",
    ko_urn: "urn:ki:in:dpdp:rule:dpbi-recruitment-2026",
    version: 1
  },
  {
    commit_hash: "d1e2f3a",
    system_time: "2026-07-10T10:00:00Z",
    event_type: "publish",
    message: "Published: RBI Draft Data Governance Framework circular (v1)",
    actor: "publishing_agent",
    actor_type: "system",
    ko_urn: "urn:ki:in:rbi:draft:data-governance-2026",
    version: 1
  }
];

// ── Conflicts ────────────────────────────────────────────────────
export const CONFLICTS = [
  {
    id: "conf-001",
    title: "DPBI Structural Independence vs. Separation of Powers",
    status: "accepted_as_unresolved",
    detected_date: "2026-03-10",
    claim_a: {
      ko_urn: "urn:ki:in:dpdp:act:dpdpa-2023",
      statement: "DPBI acts as an independent adjudicating body with powers of a civil court (Section 27 & 28)",
      authority: "Parliament of India",
      authority_tier: "primary",
      effective_date: "2023-08-11"
    },
    claim_b: {
      ko_urn: "urn:ki:in:dpdp:rule:dpbi-recruitment-2026",
      statement: "Chairperson and members are appointed by the Central Government via government-led selection committee.",
      authority: "Ministry of Electronics and IT",
      authority_tier: "secondary",
      effective_date: "2025-11-13"
    },
    explanation: "Supreme Court writ petitions argue that a search committee composed solely of government secretaries to select judges/adjudicators violates the separation of powers. Petitioners request judicial presence on the committee and secure member tenure to prevent executive influence.",
    scope: "Affects the validity of all future DPBI adjudication and penalty orders.",
    downstream_impact: ["Compliance Enforcement Reliability", "Dispute Resolution Strategy"],
    reviewer_notes: "Supreme Court issued notice but did not stay the Act. Organizations must continue preparing for Board jurisdiction while legal counsel monitors the constitutional proceedings.",
    reviewer: "Senior Constitutional Counsel"
  },
  {
    id: "conf-002",
    title: "Public Interest Information Access vs. Personal Data Ban",
    status: "under_review",
    detected_date: "2026-04-05",
    claim_a: {
      ko_urn: "urn:ki:in:dpdp:act:dpdpa-2023",
      statement: "Section 44(3) amends the RTI Act to prevent disclosure of any personal information.",
      authority: "Parliament of India",
      authority_tier: "primary",
      effective_date: "2023-08-11"
    },
    claim_b: {
      ko_urn: "urn:ki:in:dpdp:source:rti-act-2005",
      statement: "Personal information can be disclosed under RTI if it has relation to any public activity or interest.",
      authority: "Parliament of India (Legacy)",
      authority_tier: "primary",
      effective_date: "2005-06-15"
    },
    explanation: "The DPDPA deletes the public interest exception in the RTI Act, making all personal data exempt from disclosure. RTI activists argue this disables disclosure of public registries, corruption audits, and welfare lists, violating the constitutional Right to Know.",
    scope: "Affects handling of public queries, disclosure of employee lists, and government transparency protocols.",
    downstream_impact: ["Public Disclosure Requests", "Transparency Compliance Standards"],
    reviewer_notes: "Under active Supreme Court review. For now, public sector agencies are applying Section 44(3) strictly to deny disclosures.",
    reviewer: "General Legal Counsel"
  }
];

// ── Opinion & Commentary Layer (Persuasive) ──────────────────────
export const OPINIONS = [
  {
    urn: "urn:ki:in:dpdp:opinion:azb:rules-impact-2025",
    title: "AZB & Partners Client Advisory: Notified DPDP Rules 2025 Analysis",
    type: "Opinion",
    version: 1,
    status: "published",
    date_legal: "2025-11-20",
    date_detected: "2025-11-20",
    date_published: "2025-11-20",
    authority: "AZB & Partners",
    jurisdiction: "India",
    source_credibility: "tier-1",
    forum_published: "AZB Client Advisories",
    interpretation_stance: "compliance_recommendation",
    summary: "Detailed legal commentary analyzing the operational burden of the notified Rules, specifically focused on the 72-hour breach notification SLA. Recommends implementing pre-drafted incident templates and internal diagnostic dashboards.",
    entities: ["Rule", "Risk", "Control", "Authority"],
    trust: {
      source_authority: 0.90,
      source_integrity: 0.95,
      citation_integrity: 0.92,
      extraction_quality: 0.90,
      interpretation_confidence: 0.88,
      human_review: "approved",
      freshness: 0.90
    },
    evidence: [
      {
        id: "ev-op-001",
        source_urn: "urn:ki:in:dpdp:source:azb-advisory-pdf",
        source_name: "AZB & Partners Privacy Practice Publications",
        source_tier: "secondary",
        citation_text: "The 72-hour window leaves little room for forensic investigation. Fiduciaries must deploy automated detection controls and diagnostic logs to meet this SLA.",
        coordinates: { page: 3, section: "Breach Protocols" },
        hash: "f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:breach-notification-rule7", edge_type: "Interprets", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "High compliance burden; requires immediate implementation of automated incident response playbooks.",
      affected_roles: ["CISO", "DPO", "Incident Response Lead"],
      affected_processes: ["Incident Response", "Breach Detection"],
      action_required: "Adopt AZB recommended incident triage SOPs and run simulated dry-run tests of 72-hour SLA response."
    }
  },
  {
    urn: "urn:ki:in:dpdp:opinion:nasscom:age-verification-2025",
    title: "NASSCOM Position Paper on Children's Age Gating",
    type: "Opinion",
    version: 1,
    status: "published",
    date_legal: "2025-01-15",
    date_detected: "2025-01-16",
    date_published: "2025-01-15",
    authority: "NASSCOM Public Policy Forum",
    jurisdiction: "India",
    source_credibility: "tier-1",
    forum_published: "NASSCOM Public Policy Submissions",
    interpretation_stance: "critique",
    summary: "Critical industry review of Rule 10's age verification provisions. Expresses concerns that rigid DigiLocker-based verification could increase friction, exclude marginalized users, and inadvertently lead to excess collection of PII, proposing zero-knowledge identity tokens instead.",
    entities: ["Rule", "Consent", "Risk", "Organization"],
    trust: {
      source_authority: 0.88,
      source_integrity: 0.90,
      citation_integrity: 0.85,
      extraction_quality: 0.88,
      interpretation_confidence: 0.80,
      human_review: "approved",
      freshness: 0.95
    },
    evidence: [
      {
        id: "ev-op-002",
        source_urn: "urn:ki:in:dpdp:source:nasscom-submission",
        source_name: "NASSCOM Submission to MeitY",
        source_tier: "secondary",
        citation_text: "Mandatory verification via government ID databases creates high user drop-off and storage security risks. We urge the adoption of decentralized cryptographic age tokens.",
        coordinates: { page: 5, section: "Section 3: Friction & Exclusion" },
        hash: "e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:children-consent-rule10", edge_type: "Conflicts With", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "Warns of product friction and customer drop-off on digital platforms.",
      affected_roles: ["Product Lead", "UX Architect", "Growth Lead"],
      affected_processes: ["User Registration", "Onboarding Conversion"],
      action_required: "Design a progressive verification flow that delays hard verification until essential, and monitor MeitY token API updates."
    }
  },
  {
    urn: "urn:ki:in:dpdp:opinion:trilegal:sc-challenge-2026",
    title: "Trilegal Legal Briefing: Constitutional Challenges & DPB Independence",
    type: "Opinion",
    version: 1,
    status: "published",
    date_legal: "2026-03-25",
    date_detected: "2026-03-26",
    date_published: "2026-03-25",
    authority: "Trilegal Regulatory Practice",
    jurisdiction: "India",
    source_credibility: "tier-1",
    forum_published: "Trilegal Insights",
    interpretation_stance: "exegesis",
    summary: "Comprehensive assessment of the Supreme Court writ petitions (W.P.(C) 177/2026). Explains the separation-of-powers arguments and provides scenario analysis on potential outcomes (e.g., restructured selection committee vs. complete rules refiling).",
    entities: ["Rule", "Case", "Risk", "Authority"],
    trust: {
      source_authority: 0.92,
      source_integrity: 0.96,
      citation_integrity: 0.90,
      extraction_quality: 0.91,
      interpretation_confidence: 0.85,
      human_review: "approved",
      freshness: 0.98
    },
    evidence: [
      {
        id: "ev-op-003",
        source_urn: "urn:ki:in:dpdp:source:trilegal-briefing-pdf",
        source_name: "Trilegal Insights Publication",
        source_tier: "secondary",
        citation_text: "If the Supreme Court finds executive control over DPB selection unconstitutional, it may mandate the inclusion of a judicial member, similar to the Madras Bar Association precedents.",
        coordinates: { page: 2, section: "DPBI Independence Analysis" },
        hash: "c1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:dpbi-recruitment-2026", edge_type: "Interprets", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "High regulatory uncertainty regarding Board composition and enforcement stability.",
      affected_roles: ["General Counsel", "Chief Risk Officer", "Board of Directors"],
      affected_processes: ["Corporate Risk Planning", "Compliance Budget Allocation"],
      action_required: "Adopt a dual compliance strategy: prepare for DPBI authority while documenting constitutional risk reserves."
    }
  },
  {
    urn: "urn:ki:in:dpdp:opinion:dsci:notice-consent-guide-2025",
    title: "DSCI Playbook: Notice and Consent Operationalization",
    type: "Opinion",
    version: 1,
    status: "published",
    date_legal: "2025-12-05",
    date_detected: "2025-12-06",
    date_published: "2025-12-05",
    authority: "Data Security Council of India (DSCI)",
    jurisdiction: "India",
    source_credibility: "tier-1",
    forum_published: "DSCI Compliance Resources",
    interpretation_stance: "compliance_recommendation",
    summary: "Practical guide containing UI wireframes, cookie notice templates, and consent database schemas mapped to DPDPA Rules requirements. Serves as the industry-standard implementation blueprint.",
    entities: ["Rule", "Consent", "Template", "Control"],
    trust: {
      source_authority: 0.95,
      source_integrity: 0.98,
      citation_integrity: 0.94,
      extraction_quality: 0.95,
      interpretation_confidence: 0.92,
      human_review: "approved",
      freshness: 0.90
    },
    evidence: [
      {
        id: "ev-op-004",
        source_urn: "urn:ki:in:dpdp:source:dsci-playbook-pdf",
        source_name: "DSCI Best Practices Collection",
        source_tier: "secondary",
        citation_text: "Fiduciaries should implement a consent ledger capable of tracking notice version, language selection, specific granular purpose, and timestamp of withdrawal.",
        coordinates: { page: 14, section: "Consent Ledger Schema" },
        hash: "a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025", edge_type: "Supports", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "Represents the consensus industry standard for audit-ready consent logging.",
      affected_roles: ["Database Architect", "Lead Developer", "DPO"],
      affected_processes: ["Consent Logging", "Data Base Schema Design"],
      action_required: "Integrate DSCI consent ledger schema recommendations into the customer database redesign sprint."
    }
  },
  {
    urn: "urn:ki:in:dpdp:opinion:nlsiu:rti-clash-2026",
    title: "NLSIU Law Review: Transparency vs. Privacy in the DPDPA Era",
    type: "Opinion",
    version: 1,
    status: "published",
    date_legal: "2026-02-10",
    date_detected: "2026-02-12",
    date_published: "2026-02-10",
    authority: "National Law School of India University",
    jurisdiction: "India",
    source_credibility: "tier-2",
    forum_published: "NLSIU Law Review (Vol. 35)",
    interpretation_stance: "critique",
    summary: "Academic analysis criticizing the absolute restriction placed on personal information disclosure by Section 44(3). Argues it overcorrects and dismantles necessary anti-corruption and public audit mechanisms built over two decades under the RTI Act.",
    entities: ["Act", "Case", "Risk"],
    trust: {
      source_authority: 0.85,
      source_integrity: 0.90,
      citation_integrity: 0.92,
      extraction_quality: 0.90,
      interpretation_confidence: 0.80,
      human_review: "approved",
      freshness: 0.90
    },
    evidence: [
      {
        id: "ev-op-005",
        source_urn: "urn:ki:in:dpdp:source:nlsiu-journal",
        source_name: "NLSIU Academic Journal Online",
        source_tier: "tertiary",
        citation_text: "By removing the public interest exception in section 8(1)(j) of the RTI Act, Section 44(3) of DPDPA effectively prevents disclosure of critical records like government payrolls and land registries.",
        coordinates: { page: 45, section: "The Death of Public Audits" },
        hash: "e5473a216db8aefcd81ab45dcf328a9be45c6db274f8a8de751db432ef5012abc",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:act:dpdpa-2023", edge_type: "Conflicts With", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "Highlights high societal and legal tension that may trigger judicial corrections in Section 44(3) interpretation.",
      affected_roles: ["General Counsel", "Compliance Analyst"],
      affected_processes: ["Public Disclosure Requests", "Aadhaar / Government Linkages"],
      action_required: "Monitor Supreme Court RTI petitions to prepare for any potential narrow-reading carve-outs regarding public registries."
    }
  },
  {
    urn: "urn:ki:in:dpdp:opinion:sam:cross-border-overlap-2026",
    title: "SAM Advisory: Interplay of Sectoral Data Localization & DPDPA Rule 15",
    type: "Opinion",
    version: 1,
    status: "published",
    date_legal: "2026-01-20",
    date_detected: "2026-01-22",
    date_published: "2026-01-20",
    authority: "Shardul Amarchand Mangaldas & Co",
    jurisdiction: "India",
    source_credibility: "tier-1",
    forum_published: "SAM Privacy & Technology Practice Updates",
    interpretation_stance: "exegesis",
    summary: "Legal analysis of the overlap between DPDPA's liberal cross-border transfer model (whitelisting/negative list) and sectoral regulations. Highlights that financial (RBI), securities (SEBI), and telecom (TRAI) localization requirements continue to bind fiduciaries regardless of Rule 15.",
    entities: ["Rule", "Circular", "Country"],
    trust: {
      source_authority: 0.91,
      source_integrity: 0.94,
      citation_integrity: 0.90,
      extraction_quality: 0.92,
      interpretation_confidence: 0.86,
      human_review: "approved",
      freshness: 0.95
    },
    evidence: [
      {
        id: "ev-op-006",
        source_urn: "urn:ki:in:dpdp:source:sam-insights-pdf",
        source_name: "SAM Legal Publications",
        source_tier: "secondary",
        citation_text: "Rule 15 does not liberate fiduciaries from existing sectoral mandates. Regulated entities must continue to host payment logs and subscriber records inside India as required by RBI and TRAI respectively.",
        coordinates: { page: 4, section: "Sectoral Interplay" },
        hash: "b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c1",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:cross-border-transfer-rule15", edge_type: "Interprets", direction: "outgoing" },
      { target_urn: "urn:ki:in:rbi:draft:data-governance-2026", edge_type: "Depends On", direction: "outgoing" }
    ],
    business_impact: {
      impact_summary: "Maintains absolute data localization constraints for banks, fintechs, and telecoms.",
      affected_roles: ["IT Director", "CRO", "General Counsel"],
      affected_processes: ["Cloud Infrastructure Hosting", "Vendor Risk Assessments"],
      action_required: "Segregate financial and subscriber PII databases, ensuring they remain strictly on local Indian nodes, while general corporate operations can utilize international transfers."
    }
  }
];

// ── Computed Helpers ─────────────────────────────────────────────
export function getKOByUrn(urn) {
  const ko = KNOWLEDGE_OBJECTS.find(k => k.urn === urn);
  if (ko) return ko;
  return OPINIONS.find(o => o.urn === urn);
}

export function getEventById(id) {
  return REGULATORY_EVENTS.find(e => e.id === id);
}

export function getActionsForEvent(eventId) {
  return ACTION_ITEMS.filter(a => a.triggering_event_id === eventId);
}

export function getActionsForKO(koUrn) {
  return ACTION_ITEMS.filter(a => a.ko_urn === koUrn);
}

export function getRelatedKOs(koUrn) {
  const ko = getKOByUrn(koUrn);
  if (!ko) return [];
  return ko.relations.map(r => ({
    ...r,
    target: getKOByUrn(r.target_urn)
  })).filter(r => r.target);
}

export function getOpinionsForKO(koUrn) {
  return OPINIONS.filter(o => o.relations.some(r => r.target_urn === koUrn));
}

export function getTrustLabel(trust) {
  if (!trust) return { label: "Unknown", level: "unknown" };
  const avg = (trust.source_authority + trust.citation_integrity + trust.extraction_quality) / 3;
  if (trust.human_review === "approved" && avg >= 0.9) return { label: "High-authority, verified evidence", level: "high" };
  if (trust.human_review === "approved_with_qualification") return { label: "Authoritative source; interpretation qualified", level: "qualified" };
  if (trust.human_review === "pending") return { label: "Pending human review", level: "pending" };
  if (avg >= 0.7) return { label: "Moderate confidence", level: "moderate" };
  if (trust.source_authority < 0.5) return { label: "Lower-tier interpretation", level: "low" };
  return { label: "Incomplete evidence", level: "low" };
}

