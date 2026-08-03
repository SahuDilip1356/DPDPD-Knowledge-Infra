// SaralPrivacy DPDPA Capability & Certification System Data Engine

export const INDUSTRY_PROFILES = [
  {
    id: "recruitment",
    name: "Recruitment & Staffing",
    icon: "👥",
    storyTitle: "SimpleStaff Recruitment Services",
    location: "Pune, Maharashtra",
    teamSize: "25 employees",
    description: "Holds 40,000 candidate CVs, uses ATS, Google Drive, WhatsApp groups, and shares profiles with enterprise clients & BGV vendors.",
    highRiskThemes: ["CV reuse without notice", "Aadhaar/PAN over-collection", "WhatsApp candidate groups", "Vendor BGV data sharing", "Lack of deletion schedules"],
    toolContext: "ATS, Gmail, WhatsApp, Google Drive, Excel"
  },
  {
    id: "ca_firm",
    name: "CA & Accounting Firms",
    icon: "📊",
    storyTitle: "ClearBooks Associates CA Firm",
    location: "Gurugram, Haryana",
    teamSize: "15 accountants & 600 clients",
    description: "Processes tax audit files, bank statements, ITR software inputs, client PAN/Aadhaar copies, and outsourced bookkeeping records.",
    highRiskThemes: ["Client file access controls", "PMLA mandatory retention overrides", "Unencrypted email attachments", "Portal credentials sharing", "Former client data archives"],
    toolContext: "Tally, ClearTax, Excel, Gmail, Government Portals"
  },
  {
    id: "training",
    name: "Training Institutes & EdTech",
    icon: "🎓",
    storyTitle: "BrightPath Skill Academy",
    location: "Bengaluru, Karnataka",
    teamSize: "40 staff & 2,500 students",
    description: "Manages student enrolment forms, parent contact details, CRM leads, payment gateways, LMS analytics, and alumni marketing lists.",
    highRiskThemes: ["Minors/children data (Sec 9)", "Verifiable guardian consent", "Parent WhatsApp broadcasts", "Photo/video marketing usage", "Lead list purchasing"],
    toolContext: "LMS, WhatsApp, Lead CRM, Razorpay, Google Sheets"
  },
  {
    id: "clinic",
    name: "Clinics & Diagnostic Labs",
    icon: "🩺",
    storyTitle: "CareFirst Diagnostic & Health Clinic",
    location: "Mumbai, Maharashtra",
    teamSize: "18 staff & 1,200 monthly patients",
    description: "Handles diagnostic reports, patient medical history, billing records, doctor consultations, and sample pickup logistics.",
    highRiskThemes: ["Health data sensitivity", "Sharing reports with family members", "Diagnostic lab vendor sharing", "CCTV in waiting rooms", "WhatsApp report dispatch"],
    toolContext: "Clinic Software, WhatsApp, Billing ERP, Email"
  },
  {
    id: "d2c",
    name: "D2C & E-Commerce",
    icon: "🛍️",
    storyTitle: "FreshKart India Organic D2C",
    location: "Delhi NCR",
    teamSize: "30 staff & 50,000 monthly orders",
    description: "Collects customer addresses, checkout phone numbers, payment details, courier shipping data, and remarketing ad cookies.",
    highRiskThemes: ["Pre-ticked marketing consent checkboxes", "Courier vendor data sharing", "Abandoned cart WhatsApp spam", "Customer support chat logs", "Ad pixel tracking"],
    toolContext: "Shopify, Meta Pixel, WhatsApp API, Delivery ERP, CRM"
  }
];

export const ROLE_PROFILES = [
  {
    id: "founder",
    name: "Founder / Business Owner",
    icon: "👑",
    focus: "Accountability, Penalties, Minimum Viable Compliance, Resource Allocation & Governance"
  },
  {
    id: "hr",
    name: "HR & Recruitment Manager",
    icon: "👩‍💼",
    focus: "Candidate Data, Employee Contracts, Background Verification, Payroll Sharing & Retention"
  },
  {
    id: "finance",
    name: "Finance & Operations Manager",
    icon: "💼",
    focus: "Vendor Agreements, Statutory Overrides (PMLA/Tax), Payment Data & Invoice Records"
  },
  {
    id: "it_ops",
    name: "IT & Information Security Lead",
    icon: "💻",
    focus: "Access Controls, Password Security, 72-Hr Breach Detection, Cloud Backups & Logging"
  },
  {
    id: "privacy_champion",
    name: "Internal Privacy Champion / DPO",
    icon: "🛡️",
    focus: "Full Operating Model, DSAR Workflows, Incident Registers, Audit Evidence & Compliance Reviews"
  }
];

export const DIAGNOSTIC_QUESTIONS = [
  {
    id: "diag_1",
    competency: "law_comprehension",
    question: "Your Pune-based company hires a freelance software developer based in Dubai to build your customer app. Does DPDPA 2023 apply to the digital personal data collected from Indian users on this app?",
    options: [
      "No, because the developer is located outside India.",
      "Yes, because Section 3 applies to digital personal data processed in India and extraterritorially if related to offering goods/services to users in India.",
      "No, because freelancers are exempt from Indian privacy laws.",
      "Only if the company pays a license fee to MeitY."
    ],
    correctAnswer: 1,
    explanation: "Section 3 explicitly establishes extraterritorial jurisdiction for any digital personal data processed in connection with offering goods or services to Data Principals in India."
  },
  {
    id: "diag_2",
    competency: "risk_recognition",
    question: "A recruiter downloads 500 candidate resumes containing PAN and Aadhaar copies onto their personal laptop to work over the weekend. What is the primary DPDPA compliance risk?",
    options: [
      "There is no risk if the recruiter returns to the office on Monday.",
      "Loss of organizational control, unencrypted local storage, unmonitored access, and risk of data breach under Section 8.",
      "The recruiter will be fined ₹250 Crore personally by the DPBI.",
      "Candidates will automatically lose their jobs."
    ],
    correctAnswer: 1,
    explanation: "Downloading unencrypted personal data onto personal devices violates reasonable security safeguards under Section 8 and exposes the business to severe breach liabilities."
  },
  {
    id: "diag_3",
    competency: "process_understanding",
    question: "When collecting customer phone numbers on a website registration form, what must the privacy notice explicitly contain under Section 5?",
    options: [
      "A copy of the company's annual financial balance sheet.",
      "A description of the personal data collected, the specific purpose of processing, and details on how to exercise privacy rights.",
      "A clause stating that data will be stored forever.",
      "An unconditional waiver of the user's legal rights."
    ],
    correctAnswer: 1,
    explanation: "Section 5 requires clear, plain-language notices stating data collected, purpose, rights exercise mechanism, and grievance officer details."
  },
  {
    id: "diag_4",
    competency: "decision_capability",
    question: "A customer requests immediate erasure of their account under Section 12(3). However, income tax laws require retaining transaction tax invoices for 7 years. What is the correct decision?",
    options: [
      "Delete all invoices immediately within 24 hours.",
      "Retain necessary tax transaction records under statutory legal obligations while deleting non-essential marketing profiles.",
      "Refuse to acknowledge the customer's request completely.",
      "Pay a fine of ₹10,000 to the customer."
    ],
    correctAnswer: 1,
    explanation: "Statutory mandatory retention laws (Tax/PMLA) override individual erasure requests for necessary legal accounting records."
  },
  {
    id: "diag_5",
    competency: "operational_maturity",
    question: "In the event of a personal data breach, what is the mandatory reporting timeline under DPDPA Rule 7 to notify the Data Protection Board of India (DPBI) and affected Data Principals?",
    options: [
      "Within 6 Hours",
      "Within 72 Hours of breach detection",
      "Within 30 Days",
      "Only when requested by police"
    ],
    correctAnswer: 1,
    explanation: "DPDPA Rule 7 prescribes a 72-hour notification SLA to notify the DPBI and affected individuals."
  }
];

export const MODULES_DATA = [
  {
    id: 0,
    title: "Module 0: Personal Learning Path & Baseline Diagnostic",
    duration: "10 Mins",
    summary: "Establish your role, industry context, and baseline privacy maturity score.",
    type: "diagnostic",
    ctaText: "Complete Diagnostic to Unlock Custom Learning Path ►"
  },
  {
    id: 1,
    title: "Module 1: What Is Personal Data? (The Personal Data Hunt)",
    duration: "15 Mins",
    summary: "Learn to spot digital personal data hiding in emails, WhatsApp chats, Excel sheets, and paper scans.",
    storySnippet: "At SimpleStaff Recruitment, CVs, Aadhaar scans, salary expectations, and interview notes exist across 5 different tools.",
    interactiveType: "data_hunt",
    syllabus: [
      "Personal Data vs Non-Personal Data",
      "Direct vs Indirect Combination Identifiers",
      "Data Principal, Data Fiduciary, & Data Processor roles",
      "Spotting digital data on an office desk",
      "Assessing data sensitivity levels"
    ],
    toolBridge: {
      text: "Now locate personal data across your own business workflows:",
      buttonText: "🔍 Launch Data Discovery Tool",
      actionScreen: "explorer"
    },
    theme: "blue"
  },
  {
    id: 2,
    title: "Module 2: How Personal Data Travels Through a Business (Follow the CV)",
    duration: "15 Mins",
    summary: "Follow the journey of a single record from intake to storage, client sharing, and hidden backups.",
    storySnippet: "A candidate emails one CV to SimpleStaff. Within 48 hours, 6 separate copies exist in ATS, WhatsApp, Gmail, Drive, and Client folders.",
    interactiveType: "follow_the_cv",
    syllabus: [
      "Mapping Data Ingestion → Storage → Sharing → Archiving",
      "Unstructured copies in WhatsApp groups and desktop folders",
      "Eliminating shadow database copies",
      "Tracking candidate CV multiplication points",
      "Securing client transfer channels"
    ],
    toolBridge: {
      text: "Map the flow of personal data in your organization:",
      buttonText: "🗺️ Open Data Flow Map Builder",
      actionScreen: "explorer"
    },
    theme: "blue"
  },
  {
    id: 3,
    title: "Module 3: Why Are We Collecting This Data? (Need It or Remove It)",
    duration: "15 Mins",
    summary: "Enforce purpose limitation and stop collecting 'nice-to-have' sensitive records.",
    storySnippet: "SimpleStaff asks candidates for Aadhaar cards before the first screening call. Is this necessary?",
    interactiveType: "need_it_or_remove_it",
    syllabus: [
      "Lawful Purpose & Purpose Limitation (Section 4 & 6)",
      "Data Minimization: Necessary vs Optional vs Prohibited",
      "Section 7 Legitimate Uses exceptions",
      "Toggling off excessive profile fields",
      "Form design purpose audits"
    ],
    toolBridge: {
      text: "Audit your business forms and eliminate unnecessary fields:",
      buttonText: "📋 Build Master Data Register",
      actionScreen: "explorer"
    },
    theme: "blue"
  },
  {
    id: 4,
    title: "Module 4: Notice and Consent (Fix the Form)",
    duration: "15 Mins",
    summary: "Draft transparent multilingual notices and remove illegal bundled or pre-ticked consent boxes.",
    storySnippet: "A bad website form says 'By clicking submit you agree to all present and future data uses by us and our partners.'",
    interactiveType: "fix_the_form",
    syllabus: [
      "Section 5 Notice requirements & Multilingual accessibility",
      "Clear affirmative action vs Dark patterns / pre-ticked boxes",
      "Consent withdrawal mechanisms",
      "Notice writer & consent form builder",
      "Assigning Grievance Officer contacts"
    ],
    toolBridge: {
      text: "Generate compliant notices for your website and intake forms:",
      buttonText: "📝 Launch Notice Generator",
      actionScreen: "explorer"
    },
    theme: "blue"
  },
  {
    id: 5,
    title: "Module 5: Using and Sharing Data Safely (Who Should See It)",
    duration: "15 Mins",
    summary: "Restrict internal employee access based on the Need-to-Know principle and secure external sharing.",
    storySnippet: "At ClearBooks CA Firm, a junior accountant can view every client's private tax audit file.",
    interactiveType: "who_should_see_it",
    syllabus: [
      "Need-to-Know Principle & Role-Based Access Control (RBAC)",
      "Securing WhatsApp and unencrypted email sharing",
      "Preventing unauthorized internal data snooping",
      "Defining organizational role access boundaries",
      "Third-party sharing safe controls"
    ],
    toolBridge: {
      text: "Set up role-based access rules for your internal teams:",
      buttonText: "🔐 Review Access Safeguards",
      actionScreen: "actions"
    },
    theme: "orange"
  },
  {
    id: 6,
    title: "Module 6: How Long Should We Keep Data? (Build a Retention Rule)",
    duration: "15 Mins",
    summary: "Define statutory retention vs operational deletion schedules to avoid holding dead records forever.",
    storySnippet: "SimpleStaff holds 40,000 inactive candidate CVs from 2015 with outdated contact details.",
    interactiveType: "build_retention_rule",
    syllabus: [
      "Section 8(7) Duty to erase data when purpose is served",
      "Statutory retention overrides (Income Tax, PMLA, Companies Act)",
      "Secure deletion & anonymization protocols",
      "Selecting operational deletion schedules",
      "Database archiving best practices"
    ],
    toolBridge: {
      text: "Define deletion schedules for your business records:",
      buttonText: "⏱️ Build Retention Schedule Matrix",
      actionScreen: "explorer"
    },
    theme: "orange"
  },
  {
    id: 7,
    title: "Module 7: People's Rights and Grievance Handling (DSAR)",
    duration: "15 Mins",
    summary: "Establish an operational workflow to receive, verify, and fulfill Data Principal rights requests.",
    storySnippet: "A customer emails: 'Please send a copy of all information you hold about me and erase my profile.'",
    interactiveType: "dsar_workflow",
    syllabus: [
      "Data Principal Rights: Access (Sec 11), Correction & Erasure (Sec 12)",
      "Grievance Redressal Mechanism & DPO contact points (Sec 13)",
      "Identity verification & 30-day response logging",
      "Managing rights request lifecycles",
      "Standard Operating Procedures for DSARs"
    ],
    toolBridge: {
      text: "Download standard Operating Procedures for rights handling:",
      buttonText: "📩 Download DSAR Handling SOP",
      actionScreen: "explorer"
    },
    theme: "orange"
  },
  {
    id: 8,
    title: "Module 8: Vendors, Apps and Outside Partners (Review the Vendor)",
    duration: "15 Mins",
    summary: "Audit third-party SaaS vendors, BGV providers, and cloud services under Data Processing Agreements.",
    storySnippet: "SimpleStaff uses a third-party background verification company. Who is legally responsible if they leak candidate Aadhaar scans?",
    interactiveType: "review_the_vendor",
    syllabus: [
      "Data Fiduciary liability for Data Processors (Section 8(2))",
      "10-Point SaaS Vendor Audit Checklist",
      "Data Processing Agreements (DPA) and cross-border restrictions (Section 16)",
      "Appointing and auditing vendor risk ratings",
      "Compliance audit evidence logs"
    ],
    toolBridge: {
      text: "Inventory and score your third-party SaaS vendors:",
      buttonText: "🤝 Open Vendor Risk Register",
      actionScreen: "actions"
    },
    theme: "orange"
  },
  {
    id: 9,
    title: "Module 9: Security and Data Breaches (Lost Laptop Breach)",
    duration: "20 Mins",
    summary: "Simulate a real-world data incident, contain exposure, and execute the 72-hour reporting protocol.",
    storySnippet: "A company laptop containing 2,000 candidate Aadhaar documents is stolen from a recruiter's car.",
    interactiveType: "lost_laptop_breach",
    syllabus: [
      "Defining Personal Data Breaches (Confidentiality, Integrity, Availability)",
      "Rule 7 Mandatory 72-Hour DPBI & Data Principal notification timeline",
      "Containment, evidence preservation, and post-incident remediation",
      "Breach containment sequence game",
      "Filing incident response reports"
    ],
    toolBridge: {
      text: "Prepare your organization's emergency breach response plan:",
      buttonText: "🚨 Open Incident Response Playbook",
      actionScreen: "actions"
    },
    theme: "indigo"
  },
  {
    id: 10,
    title: "Module 10: Governance, Policies and Audit Evidence (Privacy Register)",
    duration: "15 Mins",
    summary: "Move beyond a simple website privacy policy to maintain verifiable compliance proof for auditors.",
    storySnippet: "Compliance is not just having a policy—it is being able to prove what your company actually does.",
    interactiveType: "privacy_register",
    syllabus: [
      "Building the 5 Core Compliance Registers (Data, Consent, DSAR, Vendor, Incident)",
      "Significant Data Fiduciary (SDF) obligations & DPIA requirements (Sec 10)",
      "Continuous compliance monitoring and management reporting",
      "Activating compliance registers",
      "Audit readiness scoring"
    ],
    toolBridge: {
      text: "Audit your organizational privacy readiness score:",
      buttonText: "🛡️ Run DPDPA Compliance Audit",
      actionScreen: "admin"
    },
    theme: "indigo"
  },
  {
    id: 11,
    title: "Module 11: Sector Capstone Simulation",
    duration: "25 Mins",
    summary: "Apply end-to-end DPDPA controls to a realistic business scenario in your selected industry track.",
    interactiveType: "capstone_simulation",
    syllabus: [
      "Integrated end-to-end privacy implementation",
      "Prioritizing high-impact compliance risks first",
      "Creating an executive summary for leadership",
      "Compiling the 30-Day compliance checklist",
      "Role-specific governance handoff"
    ],
    ctaText: "Complete Capstone Simulation ►",
    theme: "indigo"
  },
  {
    id: 12,
    title: "Module 12: Certification Exam",
    duration: "30 Mins",
    summary: "Pass the 10-question final capability exam to generate your Verified Credential & 30-Day Implementation Action Plan.",
    interactiveType: "final_exam",
    syllabus: [
      "10 scenario-based questions",
      "Pass threshold checks",
      "Verified Certificate generator",
      "30-Day implementation roadmap setup",
      "LinkedIn sharing & print options"
    ],
    ctaText: "Take Final Certification Examination 🎓",
    theme: "indigo"
  }
];

export const CERTIFICATION_EXAM_QUESTIONS = [
  {
    id: 1,
    question: "Under DPDPA Rule 7, what is the mandatory statutory SLA for reporting a personal data breach to the Data Protection Board of India (DPBI) and affected Data Principals?",
    options: [
      "6 Hours",
      "24 Hours",
      "72 Hours from breach detection",
      "15 Days"
    ],
    correctAnswer: 2,
    explanation: "DPDPA Rule 7 prescribes a 72-hour reporting SLA to notify the DPBI and affected data principals upon breach detection."
  },
  {
    id: 2,
    question: "Under DPDPA Section 12(3), a user requests complete deletion of their transaction history. However, PMLA 2002 regulations mandate 5-year retention of financial records. How does the law apply?",
    options: [
      "You must delete the data within 24 hours.",
      "PMLA statutory mandatory retention overrides individual DPDPA erasure requests for financial records.",
      "You must pay a ₹10,000 fine to the user.",
      "You must transfer the data to a foreign cloud."
    ],
    correctAnswer: 1,
    explanation: "Statutory mandatory retention laws (e.g. PMLA, Tax Act) supersede individual erasure requests for accounting records."
  },
  {
    id: 3,
    question: "What is the maximum penalty cap under Schedule 1 for failure to implement reasonable security safeguards resulting in a personal data breach?",
    options: [
      "₹10 Lakhs",
      "₹50 Crore",
      "₹200 Crore",
      "₹250 Crore"
    ],
    correctAnswer: 3,
    explanation: "Failure to implement reasonable security safeguards carries the highest penalty cap of up to ₹250 Crore."
  },
  {
    id: 4,
    question: "Which 7 pillars represent SaralPrivacy's operational methodology for SMB business compliance?",
    options: [
      "ISO 27001 Controls",
      "O-P-E-R-A-T-E (Observe, Permission, Evidence, Rights, Accountability, Third-party, Event)",
      "SOC 2 Type II",
      "GDPR Article 30"
    ],
    correctAnswer: 1,
    explanation: "OPERATE is SaralPrivacy's proprietary 7-pillar privacy operating model for SMBs."
  },
  {
    id: 5,
    question: "What are the legal requirements under DPDPA Section 9 for processing personal data belonging to children (under age 18)?",
    options: [
      "Allowed freely without consent",
      "Requires verifiable parental/guardian consent and strictly bans targeted ad tracking or behavioral monitoring",
      "Allowed if the child signs a digital waiver",
      "Requires payment of a royalty to MeitY"
    ],
    correctAnswer: 1,
    explanation: "Section 9 mandates verifiable parental consent and strictly bans targeted advertising and behavioral tracking of minors."
  },
  {
    id: 6,
    question: "When collecting personal data via online forms, which consent practice is illegal under DPDPA Section 6?",
    options: [
      "Providing a clear, un-ticked opt-in checkbox",
      "Pre-ticking the marketing consent box by default (Dark Pattern)",
      "Displaying a clear notice in regional languages",
      "Providing a link to withdraw consent"
    ],
    correctAnswer: 1,
    explanation: "Pre-ticked consent checkboxes are dark patterns and violate Section 6 requirements for unambiguous affirmative consent."
  },
  {
    id: 7,
    question: "If a company engages an external SaaS software vendor to process customer data, who remains legally responsible to the Data Principal under DPDPA Section 8(2)?",
    options: [
      "The SaaS software vendor only",
      "The Data Fiduciary (the hiring company)",
      "The Data Protection Board of India",
      "The Amazon Web Services hosting provider"
    ],
    correctAnswer: 1,
    explanation: "Section 8(2) specifies that the Data Fiduciary remains fully responsible for compliance, even when processing is outsourced to a Data Processor."
  },
  {
    id: 8,
    question: "Which of the following is considered 'Personal Data' under DPDPA Section 2(t)?",
    options: [
      "Anonymized aggregate market research stats",
      "Any data about an individual who is identifiable by or in relation to such data",
      "A company registration GST number",
      "Public weather forecast reports"
    ],
    correctAnswer: 1,
    explanation: "Personal data is defined as any data about an individual who is identifiable by or in relation to such data."
  },
  {
    id: 9,
    question: "What is the primary role of a 'Consent Manager' registered with the Data Protection Board under DPDPA Section 6(7)?",
    options: [
      "To fine companies for data breaches",
      "To act as a single point of contact for Data Principals to manage, grant, and withdraw consent across multiple fiduciaries",
      "To audit tax returns for CA firms",
      "To sell customer lead lists to recruiters"
    ],
    correctAnswer: 1,
    explanation: "Consent Managers provide a unified platform for individuals to manage, give, and revoke consent transparently."
  },
  {
    id: 10,
    question: "Under DPDPA Section 16, what restriction applies to cross-border transfers of personal data outside India?",
    options: [
      "All cross-border transfers are completely banned",
      "Transfers are permitted except to countries specifically blacklisted/restricted by the Central Government",
      "Transfers require a physical permit signed by a magistrate",
      "Transfers are allowed only to USA and UK"
    ],
    correctAnswer: 1,
    explanation: "Section 16 adopts a negative-list approach, allowing cross-border transfers except to countries restricted by Central Government notifications."
  }
];

export const CAPABILITY_ACTION_PLAN_TEMPLATE = [
  {
    dayRange: "Days 1–7",
    phase: "Phase 1: Discovery & Inventory",
    actions: [
      "Run Personal Data Hunt across WhatsApp, Google Drive, Excel, and local laptops.",
      "Create Master Personal Data Register mapping all customer, candidate, and employee records.",
      "Assign internal Privacy Champion / DPO point of contact."
    ]
  },
  {
    dayRange: "Days 8–14",
    phase: "Phase 2: Notice & Consent Alignment",
    actions: [
      "Update website forms & intake applications with clear Section 5 Privacy Notices.",
      "Remove pre-ticked marketing checkboxes (Dark Patterns).",
      "Publish plain-language consent withdrawal mechanism."
    ]
  },
  {
    dayRange: "Days 15–21",
    phase: "Phase 3: Safeguards & Vendor Control",
    actions: [
      "Implement Role-Based Access Control (RBAC) on shared cloud drives and CRM software.",
      "Execute Data Processing Agreements (DPA) with top 5 SaaS vendors and BGV providers.",
      "Publish 72-Hour Breach Incident Playbook for IT/Ops team."
    ]
  },
  {
    dayRange: "Days 22–30",
    phase: "Phase 4: Rights & Retention Execution",
    actions: [
      "Publish DSAR request contact details for Data Principal rights.",
      "Set retention & secure deletion rules for inactive records (>2 years old).",
      "Conduct 30-minute DPDPA Aware employee briefing session."
    ]
  }
];
