import React from "react";
import { Link, useParams } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import NotFound from "./NotFound";
import Figure, { RoleLegend } from "../learn/Figure";
import {
  listModules, nextModule, prevModule, modulePath, quizPath, moduleTitleTag, moduleQuestions, TOTAL_MODULES
} from "../../lib/modules";
import { getProvision, routeFor, displayLabel } from "../../lib/law";
import { usePageTitle } from "../../lib/usePageTitle";
import { useModule } from "../../lib/useContent";
import "../../styles/law.css";
import "../../styles/learn.css";
import "../../styles/figures.css";

/* The six modules as a line of stations; the current one is lit. */
function CourseTrack({ current }) {
  const all = listModules();
  return (
    <nav className="track" aria-label="Course progress">
      <ol>
        {all.map((m) => {
          const state = m.order < current.order ? "is-done" : m.order === current.order ? "is-here" : "";
          return (
            <li key={m.slug} className={`track-stop ${state}`}>
              <Link to={modulePath(m)} aria-current={m.slug === current.slug ? "step" : undefined}>
                <span className="track-dot" aria-hidden="true">{m.order}</span>
                <span className="track-name">{m.title}</span>
              </Link>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

function Block({ b }) {
  if (b.type === "short") return <div className="lesson-short" dangerouslySetInnerHTML={{ __html: b.html }} />;
  if (b.type === "figure") return <Figure spec={b.spec} />;
  if (b.type === "example") {
    return (
      <aside className="lesson-example">
        <p className="lesson-example-h">{b.title ? `Example: ${b.title}` : "Example"}</p>
        <div dangerouslySetInnerHTML={{ __html: b.html }} />
      </aside>
    );
  }
  return <div className="learn-prose" dangerouslySetInnerHTML={{ __html: b.html }} />;
}

/* A lesson with a short version leads with the short version, the figure
   and the example, and keeps the full text one tap away. The full text is
   still in the HTML, so search engines and readers who want depth get it. */
function Lesson({ lesson, n }) {
  const visual = lesson.blocks.filter((b) => b.type !== "prose");
  const prose = lesson.blocks.filter((b) => b.type === "prose");
  const layered = lesson.blocks.some((b) => b.type === "short");
  const words = prose.reduce((w, b) => w + b.html.replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length, 0);
  return (
    <section className="lesson" aria-labelledby={lesson.id}>
      <header className="lesson-head">
        <span className="lesson-n" aria-hidden="true">{n}</span>
        <h2 id={lesson.id} className="lesson-h">{lesson.heading}</h2>
      </header>
      {layered ? (
        <>
          {visual.map((b, i) => <Block key={i} b={b} />)}
          {prose.length > 0 && (
            <details className="lesson-more">
              <summary>Read the full lesson, with every provision it rests on ({Math.max(1, Math.round(words / 200))} min)</summary>
              {prose.map((b, i) => <Block key={i} b={b} />)}
            </details>
          )}
        </>
      ) : (
        lesson.blocks.map((b, i) => <Block key={i} b={b} />)
      )}
    </section>
  );
}

/* One module: where it sits in the course, what it answers, then each
   lesson as short version, figure, full text and a worked example. Ends
   with the self-test and the next module, or the handoff on the last. */
export default function Module() {
  const { slug } = useParams();
  const m = useModule(slug);
  usePageTitle(m ? moduleTitleTag(m) : null);
  if (!m) return <NotFound />;

  const next = m.handoff ? null : nextModule(m);
  const prev = prevModule(m);
  const questions = moduleQuestions(m);
  const hasFigures = m.lessons.some((l) => l.blocks.some((b) => b.type === "figure"));

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
              <span aria-current="page">Module {m.order}</span>
            </nav>
            <CourseTrack current={m} />
            <h1 className="law-title module-title">{m.title}</h1>
            {m.summary && <p className="law-lede">{m.summary}</p>}
            <p className="module-meta">
              Module {m.order} of {TOTAL_MODULES}, {m.minutes} minutes, {m.lessons.length} lessons
            </p>
          </div>
        </header>

        <div className="law-wrap law-main">
          <div className="module-intro">
            {questions.length > 0 && (
              <section className="module-answers" aria-labelledby="answers-h">
                <h2 id="answers-h" className="module-answers-h">Questions this module answers</h2>
                <ul>
                  {questions.map((q) => <li key={q.id}>{q.question}</li>)}
                </ul>
              </section>
            )}
            <nav className="module-toc" aria-label="Lessons">
              <h2 className="module-answers-h">Lessons</h2>
              <ol>
                {m.lessons.map((l) => <li key={l.id}><a href={`#${l.id}`}>{l.heading}</a></li>)}
              </ol>
            </nav>
          </div>

          {hasFigures && (
            <div className="module-legend">
              <p>Figures use one colour per role, throughout the course:</p>
              <RoleLegend />
            </div>
          )}

          {m.intro_html && <div className="learn-prose module-lede" dangerouslySetInnerHTML={{ __html: m.intro_html }} />}

          {m.lessons.map((l, i) => <Lesson key={l.id} lesson={l} n={i + 1} />)}

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

          <footer className="learn-foot">
            {m.quiz.length > 0 && (
              <Link to={quizPath(m)} className="pub-btn pub-btn-primary learn-quiz-link">
                Test yourself: {m.quiz.length} questions
              </Link>
            )}
            {m.handoff && (
              <div className="learn-handoff">
                <p>You have finished the course. The next step is to act on it.</p>
                <a className="pub-btn pub-btn-primary" href={m.handoff.url} rel="noopener">{m.handoff.label}</a>
              </div>
            )}
            <nav className="law-pager" aria-label="Course">
              {prev ? (
                <Link to={modulePath(prev)} className="law-pager-prev">
                  <span className="law-pager-dir">Previous module</span>
                  <span className="law-pager-name">{prev.title}</span>
                </Link>
              ) : <span />}
              {next && (
                <Link to={modulePath(next)} className="law-pager-next learn-next">
                  <span className="law-pager-dir">Next module</span>
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
