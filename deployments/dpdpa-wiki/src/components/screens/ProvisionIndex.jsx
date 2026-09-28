import React from "react";
import { Link } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import {
  DOCS, CHAPTERS, listProvisions, getProvision, documentOf, displayLabel,
  routeFor, commencement, ACT_INDEX_TITLE, RULES_INDEX_TITLE
} from "../../lib/law";
import { usePageTitle } from "../../lib/usePageTitle";
import "../../styles/law.css";

function Item({ p, showDate }) {
  const badge = showDate ? commencement(p) : null;
  return (
    <li>
      <Link to={routeFor(p)} className="law-index-item">
        <span className="law-index-label">{displayLabel(p)}</span>
        <span className="law-index-title">{p.title}</span>
        {badge && <span className={`law-index-date law-badge-${badge.status}`}>{badge.label}</span>}
      </Link>
    </li>
  );
}

function ActIndex() {
  const schedule = getProvision("ACT-SCHEDULE");
  return (
    <>
      {CHAPTERS.map((c) => (
        <section key={c.numeral} className="law-index-group" aria-labelledby={`ch-${c.numeral}`}>
          <h2 id={`ch-${c.numeral}`} className="law-h2">
            <span className="law-index-num">Chapter {c.numeral}</span> {c.title}
          </h2>
          <ol className="law-index-list">
            {Array.from({ length: c.to - c.from + 1 }, (_, i) => getProvision(`S${c.from + i}`))
              .filter(Boolean)
              .map((p) => <Item key={p.label} p={p} />)}
          </ol>
        </section>
      ))}
      {schedule && (
        <section className="law-index-group" aria-labelledby="ch-sch">
          <h2 id="ch-sch" className="law-h2">The Schedule</h2>
          <ol className="law-index-list">
            <Item p={schedule} />
          </ol>
        </section>
      )}
    </>
  );
}

function RulesIndex() {
  const rules = listProvisions().filter((p) => p.kind === "rule");
  const schedules = listProvisions().filter((p) => p.kind === "rules-schedule");
  return (
    <>
      <section className="law-index-group" aria-labelledby="rules-h">
        <h2 id="rules-h" className="law-h2">Rules</h2>
        <ol className="law-index-list">
          {rules.map((p) => <Item key={p.label} p={p} showDate />)}
        </ol>
      </section>
      <section className="law-index-group" aria-labelledby="sched-h">
        <h2 id="sched-h" className="law-h2">Schedules</h2>
        <ol className="law-index-list">
          {schedules.map((p) => <Item key={p.label} p={p} showDate />)}
        </ol>
      </section>
    </>
  );
}

/* Index of the Act (by chapter) or of the Rules (rules, then schedules). */
export default function ProvisionIndex({ doc = "act" }) {
  const d = DOCS[doc];
  const isAct = doc === "act";
  usePageTitle(isAct ? ACT_INDEX_TITLE : RULES_INDEX_TITLE);
  const count = listProvisions().filter((p) => documentOf(p) === d).length;

  return (
    <PublicShell>
      <div className="law">
        <header className="law-head">
          <div className="law-wrap">
            <nav className="law-crumbs" aria-label="Breadcrumb">
              <Link to="/">Home</Link>
              <span aria-hidden="true">›</span>
              <span aria-current="page">{d.short}</span>
            </nav>
            <p className="law-kicker">{d.name}</p>
            <h1 className="law-title">
              {isAct ? "The Act, section by section" : "The Rules, rule by rule"}
            </h1>
            <p className="law-lede">
              {isAct
                ? "Forty-four sections in nine chapters, and the Schedule of penalties, each on its own page with the gazette text as printed."
                : "Twenty-three rules and seven schedules, each on its own page with the gazette text as printed and the date it applies from."}
              {" "}{count} provisions.
            </p>
          </div>
        </header>
        <div className="law-wrap law-main">
          {isAct ? <ActIndex /> : <RulesIndex />}
        </div>
      </div>
    </PublicShell>
  );
}
