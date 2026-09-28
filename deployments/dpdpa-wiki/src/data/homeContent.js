/**
 * Content for the public dpdpa.wiki homepage.
 *
 * Kept separate from layout so copy can be edited without touching JSX, and
 * so the FAQ can be emitted twice — once as visible markup, once as
 * schema.org JSON-LD for search engines.
 *
 * Figures are the real statutory ones. Where a number appears it is checked
 * against the Act, not rounded for effect.
 */

export const HERO = {
  eyebrow: "The Digital Personal Data Protection Act, 2023",
  title: "Understand and implement India's DPDP Act",
  subtitle:
    "Every obligation traced to its section, every answer carrying its citation. Built for the people who have to act on the law, not only read it.",
  primaryCta: { label: "Get the compliance checklist", intent: "checklist" },
  secondaryCta: { label: "Read the Act", href: "/act" },
  searchPlaceholder: "Search the DPDP Act, rules, and guidance"
};

/** Entry points by role. Each names the first thing that person actually needs. */
export const JOURNEYS = [
  {
    id: "founder",
    label: "Founders",
    lede: "You need to know what applies to you and what it costs to get wrong.",
    firstStep: "Start with who the Act applies to",
    href: "/act/section-3"
  },
  {
    id: "legal",
    label: "Legal teams",
    lede: "You need the text, its amendments, and what supersedes what.",
    firstStep: "Read the Act and the Rules, section by section",
    href: "/act"
  },
  {
    id: "product",
    label: "Product teams",
    lede: "You need consent and notice that hold up in a real user flow.",
    firstStep: "See what a notice has to contain",
    href: "/act/section-5"
  },
  {
    id: "developer",
    label: "Developers",
    lede: "You need retention, access control, and breach handling in code.",
    firstStep: "Review the obligations of a Data Fiduciary",
    href: "/act/section-8"
  }
];

/** Core reference surfaces. Order runs from 'what the law says' to 'what to do'. */
export const RESOURCES = [
  {
    title: "The Act",
    description: "The full text of the DPDP Act 2023, section by section, in the gazette's words, with the date each provision applies from.",
    meta: "44 sections + Schedule",
    href: "/act"
  },
  {
    title: "Definitions",
    description: "Data Principal, Data Fiduciary, Significant Data Fiduciary, Consent Manager — who each term binds.",
    meta: "32 defined terms",
    href: "/glossary"
  },
  {
    title: "Obligations",
    description: "What a Data Fiduciary must do: notice, consent, purpose limitation, retention, security safeguards.",
    meta: "Section 8",
    href: "/act/section-8"
  },
  {
    title: "Rights",
    description: "Access, correction, erasure, grievance redressal, and nomination — and the timelines attached.",
    meta: "Sections 11–15",
    href: "/act/section-11"
  },
  {
    title: "The Rules",
    description: "The DPDP Rules 2025: notice, consent managers, security safeguards, breach intimation, retention periods, and the Board.",
    meta: "23 rules + 7 schedules",
    href: "/rules"
  },
  {
    title: "Breach response",
    description: "What to do in the first 72 hours, who to notify, and what the Board expects on record.",
    meta: "Rule 7 · up to ₹200 crore",
    href: "/rules/rule-7"
  }
];

/**
 * Readiness assessment. Five questions, each mapped to a statutory obligation
 * so the result can cite why a gap matters rather than just scoring it.
 */
export const ASSESSMENT = [
  {
    id: "inventory",
    question: "Do you know every place personal data enters your business?",
    section: "Section 4 — grounds for processing",
    options: [
      { label: "We have a current, written data inventory", score: 2 },
      { label: "We know roughly, nothing written down", score: 1 },
      { label: "We have not mapped this", score: 0 }
    ]
  },
  {
    id: "notice",
    question: "Does your consent notice state the purpose in plain language?",
    section: "Section 5 — notice",
    options: [
      { label: "Yes, itemised and separate from the terms", score: 2 },
      { label: "It exists, but it is buried in the privacy policy", score: 1 },
      { label: "We do not have a standalone notice", score: 0 }
    ]
  },
  {
    id: "retention",
    question: "Do you delete personal data once its purpose is served?",
    section: "Section 8(7) — erasure",
    options: [
      { label: "Yes, on a defined retention schedule", score: 2 },
      { label: "Sometimes, handled case by case", score: 1 },
      { label: "We retain indefinitely by default", score: 0 }
    ]
  },
  {
    id: "rights",
    question: "Can a Data Principal reach you to access or correct their data?",
    section: "Sections 11–13 — rights",
    options: [
      { label: "Yes, with a named contact and a tracked process", score: 2 },
      { label: "There is an email address, no defined process", score: 1 },
      { label: "No route exists today", score: 0 }
    ]
  },
  {
    id: "breach",
    question: "Do you have a written breach response plan?",
    section: "Section 8(6) — breach intimation",
    options: [
      { label: "Yes, tested, with Board notification steps", score: 2 },
      { label: "Written down but never rehearsed", score: 1 },
      { label: "We would work it out at the time", score: 0 }
    ]
  }
];

export const ASSESSMENT_BANDS = [
  {
    min: 8,
    label: "Largely ready",
    note: "The structure is in place. Focus on evidence — the Board asks what you can show, not what you intended."
  },
  {
    min: 4,
    label: "Partially ready",
    note: "The obvious gaps are documentation and process. Most of this is written work, not engineering."
  },
  {
    min: 0,
    label: "Early",
    note: "Start with the data inventory. Nothing else can be scoped until you know what you hold and why."
  }
];

/** Written against the questions people actually search, not the ones we'd prefer to answer. */
export const FAQ = [
  {
    q: "Who does the DPDP Act apply to?",
    a: "It applies to anyone processing digital personal data in India, and to processing outside India where goods or services are offered to people in India. It does not cover personal data processed for a purely personal or domestic purpose, or data made publicly available by the person themselves or under a legal obligation."
  },
  {
    q: "What is the penalty for a data breach in India?",
    a: "Failing to take reasonable security safeguards carries a penalty of up to ₹250 crore. Failing to notify the Data Protection Board or affected Data Principals of a breach carries up to ₹200 crore. Penalties are set by the Board after an inquiry, weighing the nature, gravity, and duration of the breach."
  },
  {
    q: "What must a consent notice contain?",
    a: "It must describe the personal data being sought, the purpose of processing, how a Data Principal may exercise their rights, and how to complain to the Board. It must be standalone, itemised, and written in plain language, and be available in English or any of the 22 languages in the Eighth Schedule."
  },
  {
    q: "What is a Significant Data Fiduciary?",
    a: "A class the Central Government may notify based on the volume and sensitivity of data processed, risk to Data Principals, and impact on sovereignty, electoral democracy, and public order. Additional obligations follow: appointing a Data Protection Officer based in India, an independent data auditor, and periodic Data Protection Impact Assessments."
  },
  {
    q: "How is children's data treated under the DPDP Act?",
    a: "Anyone under 18 is a child. Verifiable consent from a parent or lawful guardian is required before processing. Tracking, behavioural monitoring, and targeted advertising directed at children are prohibited, though the Government may exempt certain classes of Data Fiduciary."
  },
  {
    q: "When do the DPDP Rules come into force?",
    a: "The Rules were notified on 13 November 2025. Rules 1, 2 and 17 to 21 (definitions and the Data Protection Board) apply from that date; Rule 4 (Consent Manager registration) from 13 November 2026; the remaining rules, including notice, security safeguards, breach intimation and children's consent, from 13 May 2027. Each rule page shows its own date."
  },
  {
    q: "Do I need a Data Protection Officer?",
    a: "Only Significant Data Fiduciaries must appoint a Data Protection Officer, who has to be based in India and answerable to the board of directors or equivalent. Every Data Fiduciary must nevertheless publish the contact details of someone able to answer questions about processing."
  },
  {
    q: "What rights do individuals have?",
    a: "A Data Principal can obtain a summary of the personal data being processed and the identities of others it has been shared with, ask for correction or erasure, nominate someone to act on their behalf in the event of death or incapacity, and use a grievance redressal route before approaching the Board."
  }
];

export const TRUST = {
  reviewNote: "Every statement traces to a section, rule, or gazette notification.",
  points: [
    { label: "Sourced from", value: "Act, Rules, and e-Gazette" },
    { label: "Citations", value: "Section and hash on every claim" },
    { label: "Version history", value: "Bi-temporal — see what applied when" }
  ]
};

export const CAPTURE = {
  title: "Get the DPDP compliance checklist",
  body: "A working checklist covering notice, consent, retention, rights, and breach response. No sales sequence.",
  placeholder: "you@company.com",
  cta: "Add me to the list",
  reassurance: "We email the checklist when it is ready, and nothing else unless you ask."
};
