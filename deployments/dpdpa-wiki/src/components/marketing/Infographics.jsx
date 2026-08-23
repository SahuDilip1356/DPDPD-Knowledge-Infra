import React from "react";

/**
 * Infographics for guide content.
 *
 * Each is invoked from markdown as a container directive (`::: timeline`).
 * They carry their own data because they describe the statute, not any one
 * article — the penalty bands are the same wherever they appear.
 *
 * Where a directive replaced prose in the source document, the component
 * carries that text in full. These are a better presentation of the content,
 * not a summary of it.
 */

/* ── Commencement timeline ──────────────────────────────────────── */
const PHASES = [
  {
    date: "13 November 2025",
    state: "past",
    title: "Definitions and the Board",
    detail: "The definitions and the machinery of the Data Protection Board came into effect."
  },
  {
    date: "13 November 2026",
    state: "next",
    title: "Consent Managers",
    detail: "The rules for Consent Managers begin."
  },
  {
    date: "13 May 2027",
    state: "future",
    title: "Everything that bites",
    detail: "Notice, consent, security, breach reporting, deletion, people's rights, extra duties for large companies, cross-border rules."
  }
];

export function Timeline() {
  return (
    <figure className="ig ig-timeline">
      <figcaption className="ig-cap">When the DPDP Act takes effect</figcaption>
      <ol className="tl">
        {PHASES.map((p) => (
          <li key={p.date} className={`tl-item tl-${p.state}`}>
            <span className="tl-dot" aria-hidden="true" />
            <div className="tl-body">
              <p className="tl-date">{p.date}</p>
              <h4 className="tl-title">{p.title}</h4>
              <p className="tl-detail">{p.detail}</p>
            </div>
          </li>
        ))}
      </ol>
    </figure>
  );
}

/* ── The seven terms ─────────────────────────────────────────────── */
const TERMS = [
  { term: "Personal data", gloss: "Any data that identifies a person, alone or combined with what else you hold." },
  { term: "Processing", gloss: "Almost anything you do with data — collect, store, change, share, delete." },
  { term: "Data Fiduciary", gloss: "The business deciding why and how data is used. That is you." },
  { term: "Data Principal", gloss: "The person the data is about. For a child, their parent or guardian." },
  { term: "Data Processor", gloss: "Anyone handling data for you, on your instructions." },
  { term: "Consent", gloss: "Permission given freely, for a clearly stated purpose." },
  { term: "Legitimate use", gloss: "Nine specific situations where the law lets you skip consent." }
];

export function Glossary() {
  return (
    <figure className="ig ig-glossary">
      <figcaption className="ig-cap">The seven terms the Act runs on</figcaption>
      <dl className="gl">
        {TERMS.map((t, i) => (
          <div className="gl-item" key={t.term}>
            <span className="gl-num" aria-hidden="true">{String(i + 1).padStart(2, "0")}</span>
            <dt className="gl-term">{t.term}</dt>
            <dd className="gl-gloss">{t.gloss}</dd>
          </div>
        ))}
      </dl>
    </figure>
  );
}

/* ── The two lawful grounds ─────────────────────────────────────── */
export function Grounds() {
  return (
    <figure className="ig ig-grounds">
      <figcaption className="ig-cap">Section 4 — the only two grounds</figcaption>
      <div className="gr">
        <div className="gr-card">
          <span className="gr-num" aria-hidden="true">1</span>
          <h4 className="gr-title">Consent</h4>
          <p className="gr-detail">
            The person's permission, meeting all five tests. Can be withdrawn at any time.
          </p>
          <p className="gr-fits">Fits things people choose — marketing, loyalty programmes, optional features.</p>
        </div>
        <div className="gr-or" aria-hidden="true">or</div>
        <div className="gr-card">
          <span className="gr-num" aria-hidden="true">2</span>
          <h4 className="gr-title">One of nine legitimate uses</h4>
          <p className="gr-detail">
            A closed list in Section 7. Narrow, and not a general excuse.
          </p>
          <p className="gr-fits">Fits things you must do anyway — payroll, court orders, medical emergencies.</p>
        </div>
      </div>
      <p className="ig-note">There is no third option.</p>
    </figure>
  );
}

/* ── The five consent tests ─────────────────────────────────────── */
const TESTS = [
  {
    test: "Free",
    detail: "Given without pressure. If saying no means losing a service the person is otherwise entitled to, the consent is not free."
  },
  {
    test: "Specific",
    detail: "Tied to a clearly named purpose.",
    fails: "We may use your data for business purposes",
    passes: "We will use your mobile number to send you your order status"
  },
  {
    test: "Informed",
    detail: "The person knew what they were agreeing to, because you told them clearly first."
  },
  {
    test: "Unconditional",
    detail: "Not bundled with something unrelated. You cannot make consent for marketing a condition of getting the invoice."
  },
  {
    test: "Unambiguous",
    detail: "Shown by a clear positive action — a tick, a tap, a signature. Silence is not consent. A pre-ticked box is not consent. Someone not replying is not consent."
  }
];

export function ConsentTests() {
  return (
    <figure className="ig ig-tests">
      <figcaption className="ig-cap">Section 6 — consent must pass all five</figcaption>
      <ol className="ct">
        {TESTS.map((t, i) => (
          <li className="ct-item" key={t.test}>
            <span className="ct-num" aria-hidden="true">{i + 1}</span>
            <div>
              <h4 className="ct-test">{t.test}</h4>
              <p className="ct-detail">{t.detail}</p>
              {t.fails && (
                <div className="ct-examples">
                  <p className="ct-fail"><span>Fails</span> “{t.fails}”</p>
                  <p className="ct-pass"><span>Passes</span> “{t.passes}”</p>
                </div>
              )}
            </div>
          </li>
        ))}
      </ol>
    </figure>
  );
}

/* ── The nine legitimate uses, at a glance ──────────────────────── */
const USES = [
  { n: 1, label: "Voluntarily given", who: "Any business" },
  { n: 2, label: "Government benefits", who: "The State" },
  { n: 3, label: "State functions", who: "The State" },
  { n: 4, label: "Legal duty to disclose", who: "Any business" },
  { n: 5, label: "Court orders and claims", who: "Any business" },
  { n: 6, label: "Medical emergencies", who: "Health providers" },
  { n: 7, label: "Public health events", who: "Health providers" },
  { n: 8, label: "Disasters", who: "Any business" },
  { n: 9, label: "Employment", who: "Any employer" }
];

export function LegitimateUses() {
  return (
    <figure className="ig ig-uses">
      <figcaption className="ig-cap">Section 7 — the nine legitimate uses</figcaption>
      <ul className="lu">
        {USES.map((u) => (
          <li className="lu-item" key={u.n}>
            <span className="lu-num" aria-hidden="true">{u.n}</span>
            <span className="lu-label">{u.label}</span>
            <span className="lu-who">{u.who}</span>
          </li>
        ))}
      </ul>
      <p className="ig-note">
        Numbers 1 and 9 cover most of what a small business does day to day.
      </p>
    </figure>
  );
}

/* ── Breach reporting: two clocks ───────────────────────────────── */
export function BreachClock() {
  return (
    <figure className="ig ig-breach">
      <figcaption className="ig-cap">Rule 7 — two clocks start at once</figcaption>
      <div className="bc">
        <div className="bc-track">
          <p className="bc-when">Without delay</p>
          <h4 className="bc-who">To every affected person</h4>
          <p className="bc-detail">
            Through their account or a registered channel: what happened, how wide it is,
            when it happened, what it means for them, what you have done and are doing
            about it, what they can do to protect themselves, and who to contact.
          </p>
        </div>
        <div className="bc-track bc-track-board">
          <p className="bc-when">Without delay, then within 72 hours</p>
          <h4 className="bc-who">To the Data Protection Board</h4>
          <p className="bc-detail">
            First, a description — nature, extent, timing, location and likely impact.
            Then within <strong>72 hours</strong> a fuller report: the facts and reasons,
            the steps you took, anything found about who caused it, what stops a repeat,
            and confirmation that you told the affected people.
          </p>
          <p className="bc-note">The Board can allow longer on a written request.</p>
        </div>
      </div>
    </figure>
  );
}

/* ── Penalty bands ──────────────────────────────────────────────── */
const PENALTIES = [
  { cap: "₹250 cr", weight: 100, what: "Failure to take reasonable security safeguards to prevent a breach" },
  { cap: "₹200 cr", weight: 80, what: "Failure to notify the Board or affected people of a breach; and breach of the children's data duties" },
  { cap: "₹150 cr", weight: 60, what: "Breach of the extra duties of a Significant Data Fiduciary" },
  { cap: "₹50 cr", weight: 20, what: "Breach of any other provision of the Act or the Rules" },
  { cap: "₹10,000", weight: 3, what: "Breach of the duties of a Data Principal" }
];

export function Penalties() {
  return (
    <figure className="ig ig-penalties">
      <figcaption className="ig-cap">The Schedule — maximum penalties</figcaption>
      <ul className="pen">
        {PENALTIES.map((p) => (
          <li className="pen-item" key={p.cap}>
            <span className="pen-cap">{p.cap}</span>
            <span className="pen-bar" aria-hidden="true">
              <span className="pen-fill" style={{ width: `${p.weight}%` }} />
            </span>
            <span className="pen-what">{p.what}</span>
          </li>
        ))}
      </ul>
      <p className="ig-note">
        Breaking a voluntary undertaking accepted by the Board attracts the penalty
        applicable to the original breach. These are ceilings, not tickets.
      </p>
    </figure>
  );
}

/* ── The Six-Column Data Register ───────────────────────────────── */
const COLUMNS = [
  { n: 1, head: "What data?", eg: "Name, mobile, email, PAN, Aadhaar, bank details, CV, photo, biometric, location" },
  { n: 2, head: "Whose?", eg: "Customer, employee, candidate, vendor contact, student, patient" },
  { n: 3, head: "Why?", eg: "One clear purpose in one sentence" },
  { n: 4, head: "On what ground?", eg: "Consent, or which of the nine legitimate uses", hard: true },
  { n: 5, head: "Who else sees it?", eg: "Every tool, vendor and person — CRM, WhatsApp, accountant, cloud drive, courier" },
  { n: 6, head: "When do we delete it?", eg: "A number, not “when needed”", hard: true }
];

export function Register() {
  return (
    <figure className="ig ig-register">
      <figcaption className="ig-cap">The Six-Column Data Register</figcaption>
      <div className="reg-scroll">
        <table className="reg">
          <thead>
            <tr>
              {COLUMNS.map((c) => (
                <th key={c.n} scope="col" className={c.hard ? "reg-hard" : ""}>
                  <span className="reg-num">{c.n}</span>
                  {c.head}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              {COLUMNS.map((c) => (
                <td key={c.n} className={c.hard ? "reg-hard" : ""}>{c.eg}</td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
      <p className="ig-note">
        Columns <strong>4</strong> and <strong>6</strong> are where the gaps live. That is
        not a failure — it is the output of the exercise.
      </p>
    </figure>
  );
}

/* ── Registry consumed by the guide renderer ────────────────────── */
export const INFOGRAPHICS = {
  timeline: Timeline,
  glossary: Glossary,
  grounds: Grounds,
  "consent-tests": ConsentTests,
  "legitimate-uses": LegitimateUses,
  "breach-clock": BreachClock,
  penalties: Penalties,
  register: Register
};
