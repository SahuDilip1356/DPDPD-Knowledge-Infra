import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import NotFound from "./NotFound";
import { getModule, modulePath, quizTitleTag } from "../../lib/modules";
import { getProvision, routeFor, displayLabel } from "../../lib/law";
import { usePageTitle } from "../../lib/usePageTitle";
import "../../styles/law.css";
import "../../styles/learn.css";

const storeKey = (slug) => `dpdpa.quiz.${slug}`;
function readLast(slug) {
  try { return JSON.parse(window.localStorage.getItem(storeKey(slug)) || "null"); } catch { return null; }
}
function writeLast(slug, value) {
  try { window.localStorage.setItem(storeKey(slug), JSON.stringify(value)); } catch { /* private mode: fine */ }
}

/* The self-test. The HTML the server sends carries questions and options only;
   marking happens in the browser from the bundled module record, so the answer
   key is never in the page markup (spec AC7). Scores stay in this browser. */
export default function Quiz() {
  const { slug } = useParams();
  const m = getModule(slug);
  usePageTitle(m ? quizTitleTag(m) : null);
  const [picked, setPicked] = useState({});
  const [marked, setMarked] = useState(false);
  const [last, setLast] = useState(null);

  useEffect(() => { if (m) setLast(readLast(m.slug)); }, [m]);
  if (!m) return <NotFound />;

  const complete = m.quiz.every((_, i) => picked[i] !== undefined);
  const score = marked ? m.quiz.reduce((n, q, i) => n + (picked[i] === q.answer ? 1 : 0), 0) : 0;

  const submit = (e) => {
    e.preventDefault();
    if (!complete) return;
    setMarked(true);
    const s = m.quiz.reduce((n, q, i) => n + (picked[i] === q.answer ? 1 : 0), 0);
    const record = { score: s, of: m.quiz.length, at: new Date().toISOString().slice(0, 10) };
    writeLast(m.slug, record);
  };
  const reset = () => { setPicked({}); setMarked(false); setLast(readLast(m.slug)); };

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
              <Link to={modulePath(m)}>Module {m.order}</Link>
              <span aria-hidden="true">›</span>
              <span aria-current="page">Self-test</span>
            </nav>
            <p className="law-kicker">Module {m.order} · Self-test</p>
            <h1 className="law-title">{m.title}</h1>
            <p className="law-lede">
              {m.quiz.length} questions. Pick one answer for each, then mark yourself. Nothing leaves your browser.
            </p>
            {last && !marked && <p className="learn-last">Last time: {last.score}/{last.of}</p>}
          </div>
        </header>

        <div className="law-wrap law-main">
          <form className="quiz" onSubmit={submit}>
            {m.quiz.map((q, i) => {
              const result = marked ? (picked[i] === q.answer ? "right" : "wrong") : null;
              return (
                <fieldset key={i} className={`quiz-item${result ? ` is-${result}` : ""}`}>
                  <legend className="quiz-q"><span className="quiz-n">{i + 1}.</span> {q.q}</legend>
                  {q.options.map((opt, j) => (
                    <label key={j} className={`quiz-opt${marked && j === q.answer ? " is-answer" : ""}`}>
                      <input
                        type="radio"
                        name={`q${i}`}
                        value={j}
                        checked={picked[i] === j}
                        disabled={marked}
                        onChange={() => setPicked((p) => ({ ...p, [i]: j }))}
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                  {marked && (
                    <p className="quiz-feedback" role="status">
                      <strong>{result === "right" ? "Correct." : "Not quite."}</strong>{" "}
                      {result === "wrong" && <>The answer is “{q.options[q.answer]}”. </>}
                      {q.cites.map((label) => {
                        const p = getProvision(label);
                        return p ? (
                          <Link key={label} to={routeFor(p)} className="quiz-cite">See {displayLabel(p)}</Link>
                        ) : null;
                      })}
                    </p>
                  )}
                </fieldset>
              );
            })}

            {!marked ? (
              <button type="submit" className="pub-btn pub-btn-primary quiz-submit" disabled={!complete}>
                {complete ? "Mark my answers" : `Answer all ${m.quiz.length} questions to mark`}
              </button>
            ) : (
              <div className="quiz-score" role="status">
                <p><strong>{score} of {m.quiz.length}</strong> correct.</p>
                <button type="button" className="pub-btn pub-btn-ghost" onClick={reset}>Try again</button>
                <Link className="pub-btn pub-btn-ghost" to={modulePath(m)}>Back to the module</Link>
              </div>
            )}
          </form>
        </div>
      </article>
    </PublicShell>
  );
}
