import React from "react";
import { Link } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import { RoleLegend } from "../learn/Figure";
import { Lesson } from "../learn/Lesson";
import { getScenarios, SCENARIOS_TITLE } from "../../lib/scenarios";
import { getProvision, routeFor, displayLabel } from "../../lib/law";
import { usePageTitle } from "../../lib/usePageTitle";
import "../../styles/law.css";
import "../../styles/learn.css";
import "../../styles/figures.css";

/* The six questions, each with the picture it calls for. */
const NAPKINS = [
  ["Who?", "a portrait"],
  ["How much?", "a chart"],
  ["Where?", "a map"],
  ["When?", "a timeline"],
  ["How?", "a flow"],
  ["Why?", "a plot"]
];

/* /learn/scenarios — one customer, one tiffin service, six questions about
   her data, each answered with one picture (Dan Roam's six ways of seeing). */
export default function Scenarios() {
  usePageTitle(SCENARIOS_TITLE);
  const s = getScenarios();

  return (
    <PublicShell>
      <article className="law learn">
        <header className="law-head module-head">
          <div className="law-wrap">
            <nav className="law-crumbs" aria-label="Breadcrumb">
              <Link to="/">Home</Link>
              <span aria-hidden="true">›</span>
              <Link to="/learn">Learn</Link>
              <span aria-hidden="true">›</span>
              <span aria-current="page">Six napkins</span>
            </nav>
            <p className="law-kicker">Scenarios</p>
            <h1 className="law-title module-title">{s.title}</h1>
            {s.summary && <p className="law-lede">{s.summary}</p>}
          </div>
        </header>

        <div className="law-wrap law-main">
          <nav className="napkins" aria-label="The six questions">
            <ol>
              {s.lessons.map((l, i) => (
                <li key={l.id}>
                  <a href={`#${l.id}`}>
                    <span className="napkin-q">{NAPKINS[i]?.[0]}</span>
                    <span className="napkin-pic">{NAPKINS[i]?.[1]}</span>
                    <span className="napkin-h">{l.heading}</span>
                  </a>
                </li>
              ))}
            </ol>
          </nav>

          <div className="module-legend">
            <p>Figures use one colour per role, as in the course:</p>
            <RoleLegend />
          </div>

          {s.intro_html && <div className="learn-prose module-lede" dangerouslySetInnerHTML={{ __html: s.intro_html }} />}

          {s.lessons.map((l, i) => <Lesson key={l.id} lesson={l} n={i + 1} />)}

          <nav className="learn-provisions" aria-label="Provisions on this page">
            <span className="learn-provisions-h">Provisions on this page</span>
            <ul>
              {s.provisions.map((label) => {
                const p = getProvision(label);
                return p ? (
                  <li key={label}><Link to={routeFor(p)} title={p.title}>{displayLabel(p)}</Link></li>
                ) : null;
              })}
            </ul>
          </nav>

          <footer className="learn-foot">
            <p className="napkins-credit">
              The method is from Dan Roam's <cite>The Back of the Napkin</cite> (2008): name the question, and the
              question picks the picture. This page explains the law; it is not legal advice.
            </p>
            <Link to="/learn" className="pub-btn pub-btn-primary">Take the six-module course</Link>
          </footer>
        </div>
      </article>
    </PublicShell>
  );
}
