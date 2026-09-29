import React from "react";
import { Link, useParams } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import NotFound from "./NotFound";
import {
  getModule, nextModule, prevModule, modulePath, quizPath, moduleTitleTag, TOTAL_MODULES
} from "../../lib/modules";
import { getProvision, routeFor, displayLabel } from "../../lib/law";
import { usePageTitle } from "../../lib/usePageTitle";
import "../../styles/law.css";
import "../../styles/learn.css";

/* One module: lessons rendered from Markdown with every citation linked to its
   provision page, then the self-test, then the next module (or, on the last
   module, the handoff to SaralPrivacy). */
export default function Module() {
  const { slug } = useParams();
  const m = getModule(slug);
  usePageTitle(m ? moduleTitleTag(m) : null);
  if (!m) return <NotFound />;

  const next = m.handoff ? null : nextModule(m);
  const prev = prevModule(m);

  return (
    <PublicShell>
      <article className="law learn">
        <header className="law-head">
          <div className="law-wrap">
            <nav className="law-crumbs" aria-label="Breadcrumb">
              <Link to="/">Home</Link>
              <span aria-hidden="true">›</span>
              <Link to="/learn">Learn</Link>
              <span aria-hidden="true">›</span>
              <span aria-current="page">Module {m.order}</span>
            </nav>
            <p className="law-kicker">Module {m.order} of {TOTAL_MODULES} · {m.minutes} min read</p>
            <h1 className="law-title">{m.title}</h1>
            {m.summary && <p className="law-lede">{m.summary}</p>}
          </div>
        </header>

        <div className="law-wrap law-main">
          <nav className="learn-provisions" aria-label="Provisions in this module">
            <span className="learn-provisions-h">Provisions in this module</span>
            <ul>
              {m.provisions.map((label) => {
                const p = getProvision(label);
                return p ? (
                  <li key={label}><Link to={routeFor(p)} title={p.title}>{displayLabel(p)}</Link></li>
                ) : null;
              })}
            </ul>
          </nav>

          {m.lessons.length > 1 && (
            <nav className="learn-toc" aria-label="Lessons">
              <ol>
                {m.lessons.map((l) => <li key={l.id}><a href={`#${l.id}`}>{l.heading}</a></li>)}
              </ol>
            </nav>
          )}

          {m.intro_html && <div className="learn-prose" dangerouslySetInnerHTML={{ __html: m.intro_html }} />}

          {m.lessons.map((l) => (
            <section key={l.id} className="learn-lesson" aria-labelledby={l.id}>
              <h2 id={l.id} className="learn-lesson-h">{l.heading}</h2>
              <div className="learn-prose" dangerouslySetInnerHTML={{ __html: l.html }} />
            </section>
          ))}

          <footer className="learn-foot">
            {m.quiz.length > 0 && (
              <Link to={quizPath(m)} className="pub-btn pub-btn-ghost learn-quiz-link">
                Check your understanding · {m.quiz.length} questions
              </Link>
            )}
            {m.handoff && (
              <div className="learn-handoff">
                <p>You have finished the course. The next step is to act on it.</p>
                <a className="pub-btn pub-btn-primary" href={m.handoff.url} rel="noopener">{m.handoff.label} ↗</a>
              </div>
            )}
            <nav className="law-pager" aria-label="Course">
              {prev ? (
                <Link to={modulePath(prev)} className="law-pager-prev">
                  <span className="law-pager-dir">← Previous</span>
                  <span className="law-pager-name">{prev.title}</span>
                </Link>
              ) : <span />}
              {next && (
                <Link to={modulePath(next)} className="law-pager-next learn-next">
                  <span className="law-pager-dir">Next →</span>
                  <span className="law-pager-name">{next.title}</span>
                </Link>
              )}
            </nav>
          </footer>
        </div>
      </article>
    </PublicShell>
  );
}
