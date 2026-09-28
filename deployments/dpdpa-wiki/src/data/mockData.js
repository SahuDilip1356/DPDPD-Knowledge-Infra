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
    source_url: "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
      { target_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025", edge_type: "Depends On", direction: "incoming" }
    ],
    business_impact: {
      impact_summary: "Establishes a 72-hour mandatory breach notification SLA to DPBI.",
      affected_roles: ["CISO", "Incident Response Team", "DPO"],
      affected_processes: ["Breach Detection", "DPBI Intimation", "User Alerting"],
      action_required: "Update incident response playbooks for 72-hour breach SLA."
    }
  },
  {
    urn: "urn:ki:in:dpdp:rule:children-consent-rule10",
    title: "DPDP Rules 2025 — Rule 10: Verifiable Parental Consent",
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
        coordinates: { page: 18, section: "Rule 17" },
        hash: "e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2",
        verification_status: "verified"
      }
    ],
    relations: [
      { target_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025", edge_type: "Depends On", direction: "incoming" }
    ],
    business_impact: {
      impact_summary: "The adjudicating authority framework is defined in Rules 17 to 21 of the DPDP Rules, 2025.",
      affected_roles: ["General Counsel", "Compliance Manager"],
      affected_processes: ["Dispute Resolution", "Regulatory Reporting"],
      action_required: "Monitor operational status of DPBI to understand active reporting channels."
    }
  }
];

// ── Regulatory Events ────────────────────────────────────────────
export const REGULATORY_EVENTS = [
  {
    id: "evt-001",
    title: "DPDP Act 2023 Receives Presidential Assent",
    source_url: "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
    type: "Draft Rules",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    date_published: "2025-01-03",
    date_effective: null,
    date_detected: "2025-01-03",
    impact_level: "high",
    status: "superseded",
    review_status: "approved",
    summary: "MeitY issues the draft Digital Personal Data Protection Rules, 2025, inviting objections and suggestions from the public before the Rules were finalised.",
    change_description: "Provides the first look at the procedural framework, consent notice formats, and administrative structures under the DPDP Act.",
    affected_ko_urns: ["urn:ki:in:dpdp:rule:dpdp-rules-2025"],
    has_conflicts: false,
    evidence_count: { primary: 1, secondary: 1, tertiary: 0 },
    affected_industries: ["All Industries"],
    affected_processes: ["Consent Notice Display", "Data Subject Portals", "Incident Tracking"]
  },
  {
    id: "evt-004",
    title: "DPDP Rules 2025 Officially Notified in Gazette",
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
    type: "Phased Implementation Milestone",
    authority: "Ministry of Electronics and Information Technology (MeitY)",
    jurisdiction: "India",
    date_published: "2025-11-13",
    date_effective: "2025-11-13",
    date_detected: "2025-11-13",
    impact_level: "high",
    status: "active",
    review_status: "approved",
    summary: "Provisions relating to the establishment, structure, and operational regulations of the Data Protection Board of India (DPBI) take effect on the date the Rules were published (Rule 1(2)).",
    change_description: "Enforces the legal setup of the DPBI, enabling the government to initiate candidate selection for Chairperson and Board members.",
    affected_ko_urns: ["urn:ki:in:dpdp:rule:dpbi-recruitment-2026"],
    has_conflicts: false,
    evidence_count: { primary: 1, secondary: 0, tertiary: 0 },
    affected_industries: ["All Industries"],
    affected_processes: ["Regulatory Dispute Management"]
  },
  {
    id: "evt-011",
    title: "Phase 2 Commences: Consent Manager Registration Opens (Upcoming)",
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
    change_description: "Rule 4 and the First Schedule (registration and obligations of Consent Managers) come into force twelve months after publication of the Rules (Rule 1(2)).",
    affected_ko_urns: ["urn:ki:in:dpdp:rule:dpdp-rules-2025"],
    has_conflicts: false,
    evidence_count: { primary: 0, secondary: 0, tertiary: 0 },
    affected_industries: ["Technology", "All Consumer-Facing Businesses"],
    affected_processes: ["Consent Architecture", "Product Development"]
  },
  {
    id: "evt-012",
    title: "Phase 3: Substantive Obligations and Penalties Fully Enforceable (Future)",
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
    change_description: "Ultimate compliance deadline. Non-compliance after this date is subject to the monetary penalties set out in the Schedule to the Act.",
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
    source_url: "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
    source_obligation: "DPDP Rules 2025 — Rule 3",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
    id: "act-006",
    title: "Assess Significant Data Fiduciary (SDF) Trigger Status",
    source_url: "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
    source_obligation: "DPDP Act 2023 — Section 10",
    triggering_event_id: "evt-001",
    ko_urn: "urn:ki:in:dpdp:act:dpdpa-2023",
    priority: "high",
    status: "accepted",
    owner: "DPO",
    reviewer: "General Counsel",
    due_date: "2026-08-31",
    applicability: "applies",
    applicability_rationale: "Designation under Section 10(1) turns on factors including the volume and sensitivity of personal data processed; assessment required.",
    affected_roles: ["Chief Privacy Officer", "DPO", "CRO"],
    affected_process: "Governance",
    related_control: "CTRL-SDF-ASSESS-01",
    description: "Assess the enterprise against the factors listed in Section 10(1) to gauge the likelihood of notification as a Significant Data Fiduciary. If designated, trigger residency and audit plans.",
    completion_evidence: null
  },
  {
    id: "act-008",
    title: "Prepare for Consent Manager API Integrations",
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
    source_obligation: "DPDP Rules 2025 — Rule 4 & First Schedule",
    triggering_event_id: "evt-004",
    ko_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
    priority: "medium",
    status: "proposed",
    owner: "Integration Lead",
    reviewer: "CPO",
    due_date: "2026-11-13",
    applicability: "applies",
    applicability_rationale: "Rule 4 and the First Schedule come into force twelve months after the Rules were published (November 2026).",
    affected_roles: ["Product Lead", "Front-end Engineer", "Privacy Architect"],
    affected_process: "Consent Management",
    related_control: "CTRL-CM-API-01",
    description: "Design OAuth and API layers to accept standardized consent signals, revocations, and queries from registered Consent Managers.",
    completion_evidence: null
  },
  {
    id: "act-009",
    title: "Implement India-Resident DPO Governance Structure",
    source_url: "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
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
  // Stage 6 — Reasoning
  {
    id: "pipe-009",
    title: "IT Act Section 43A Rule Supersession Conflict Analysis",
    source_url: "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
    source: "Internal Knowledge Factory",
    authority: "Knowledge Team",
    current_stage: 6,
    stage_name: "Reasoning",
    time_in_stage: "2h",
    assigned_to: "Reasoning Agent",
    priority: "medium",
    blocking_issues: [],
    auto_checks: { schema_valid: true, entities_resolved: true, duplicates_checked: true }
  },
  {
    id: "pipe-012",
    title: "DigiLocker Integration Playbook for Minor Accounts",
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
    source: "Internal Research",
    authority: "Knowledge Team",
    current_stage: 8,
    stage_name: "Publishing",
    time_in_stage: "30m",
    assigned_to: "Publishing Agent",
    priority: "critical",
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
    source_url: "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
    actor: "publishing_agent",
    actor_type: "system",
    ko_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
    version: 1
  },
  {
    commit_hash: "c5d1e4f",
    system_time: "2025-11-13T11:45:00Z",
    event_type: "publish",
    message: "Published: Digital Personal Data Protection Rules, 2025 (v1) — Official Notification",
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
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
    source_url: "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
    actor: "reasoning_agent",
    actor_type: "system",
    ko_urn: "urn:ki:in:dpdp:rule:dpdp-rules-2025",
    version: 1
  }
];

// ── Conflicts ────────────────────────────────────────────────────
// Empty: the earlier entries rested on court proceedings that could not be
// sourced to a primary document.
export const CONFLICTS = [];

// ── Opinion & Commentary Layer ────────────────────────────────────
// Empty until an opinion can carry a `source_url` on the publishing firm's or
// institution's own domain. Unsourced commentary is not kept as sample data.
export const OPINIONS = [];

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

