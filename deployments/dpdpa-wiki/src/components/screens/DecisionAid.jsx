import React, { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import NotFound from "./NotFound";
import { getTool, toolTitle } from "../../lib/tools";
import { getProvision, routeFor, displayLabel, commencement } from "../../lib/law";
import { usePageTitle } from "../../lib/usePageTitle";
import "../../styles/law.css";
import "../../styles/tools.css";

const APPLICABILITY = "does-dpdpa-apply";

/**
 * One decision aid: a tree of questions that ends in a conclusion, each step
 * showing the provision it rests on. The prerender emits the first question;
 * the reader's path lives in component state and is never stored. Below the
 * interactive part, every step is listed inside a collapsed <details> so the
 * whole tool is on the page for a reader — or a crawler — without JavaScript.
 */
export default function DecisionAid() {
  const { slug } = useParams();
  const tool = getTool(slug);
  usePageTitle(tool ? toolTitle(tool) : null);

  if (!tool) return <NotFound />;

  return (
    <PublicShell>
      <article className="law tool">
        <header className="law-head">
          <div className="law-wrap">
            <nav className="law-crumbs" aria-label="Breadcrumb">
              <Link to="/">Home</Link>
              <span aria-hidden="true">›</span>
              <span>Tools</span>
              <span aria-hidden="true">›</span>
              <span aria-current="page">{tool.title}</span>
            </nav>
            <p className="law-kicker">Decision aid</p>
            <h1 className="law-title">{tool.title}</h1>
            <p className="law-lede">{tool.intro}</p>
          </div>
        </header>

        <div className="law-wrap law-main">
          {/* Keyed on the slug so moving between tools starts the new one afresh. */}
          <Runner key={tool.slug} tool={tool} />
          <AllSteps tool={tool} />
        </div>
      </article>
    </PublicShell>
  );
}

function Runner({ tool }) {
  const [state, setState] = useState({ current: tool.start, history: [] });
  const node = tool.nodes[state.current];
  const step = state.history.length + 1;
  const headingRef = useRef(null);
  const mounted = useRef(false);

  // Move focus to the new step's heading after each answer so keyboard and
  // screen-reader users land on the question, not the button they pressed.
  useEffect(() => {
    if (!mounted.current) { mounted.current = true; return; }
    headingRef.current?.focus();
  }, [state.current]);

  const choose = (next) => setState((s) => ({ current: next, history: [...s.history, s.current] }));
  const back = () => setState((s) => {
    if (s.history.length === 0) return s;
    const history = s.history.slice(0, -1);
    return { current: s.history[s.history.length - 1], history };
  });
  const restart = () => setState({ current: tool.start, history: [] });

  return (
    <section className="tool-run" aria-live="polite" aria-labelledby="tool-step-h">
      <p className="tool-step-count">
        {node.type === "result" ? `Conclusion after ${step - 1} ${step - 1 === 1 ? "step" : "steps"}` : `Step ${step}`}
      </p>

      {node.type === "question" ? (
        <>
          <h2 id="tool-step-h" className="tool-question" tabIndex={-1} ref={headingRef}>{node.text}</h2>
          <ProvisionLinks label="Rests on" cites={node.cites} />
          <div className="tool-options" role="group" aria-label="Your answer">
            {node.options.map((o) => (
              <button key={o.next + o.label} type="button" className="tool-option" onClick={() => choose(o.next)}>
                {o.label}
              </button>
            ))}
          </div>
        </>
      ) : (
        <div className={`tool-result tool-result-${verdictTone(node.result.verdict)}`}>
          <h2 id="tool-step-h" className="tool-verdict" tabIndex={-1} ref={headingRef}>{node.result.verdict}</h2>
          <p className="tool-explanation">{node.result.explanation}</p>
          <ProvisionLinks label="Provisions this rests on" cites={node.result.cites} />
          {tool.slug === APPLICABILITY && (
            <p className="tool-anchor">
              Section 3 decides what the Act applies to.{" "}
              <Link to="/act/section-3">Read Section 3 in full</Link>
              {node.result.cites.includes("S17") && (
                <>{" · "}<Link to="/act/section-17">Read Section 17 — Exemptions</Link></>
              )}
            </p>
          )}
        </div>
      )}

      <div className="tool-nav">
        <button type="button" className="tool-nav-btn" onClick={back} disabled={state.history.length === 0}>
          ← Back
        </button>
        <button type="button" className="tool-nav-btn tool-nav-quiet" onClick={restart} disabled={state.history.length === 0}>
          Start over
        </button>
      </div>
    </section>
  );
}

/* A verdict's tone is read from its opening words; the words themselves
   carry the meaning, the colour only echoes it. */
function verdictTone(verdict) {
  const v = String(verdict).toLowerCase();
  if (v.startsWith("not valid") || v.startsWith("cannot rely")) return "no";
  if (v.startsWith("the act does not apply") || v.startsWith("you are not")) return "no";
  if (v.includes("with exemptions")) return "partly";
  return "yes";
}

/* Links to the provisions a step rests on: label, gazette heading and, for a
   rule not yet in force, the date it applies from. */
function ProvisionLinks({ label, cites }) {
  return (
    <div className="tool-cites">
      <span className="tool-cites-label">{label}</span>
      <ul className="tool-cites-list">
        {cites.map((l) => <li key={l}><ProvisionLink label={l} /></li>)}
      </ul>
    </div>
  );
}

function ProvisionLink({ label }) {
  const p = getProvision(label);
  if (!p) return <span>{label}</span>;
  const badge = commencement(p);
  return (
    <Link to={routeFor(p)} className="tool-cite">
      <span className="tool-cite-label">{displayLabel(p)}</span>
      <span className="tool-cite-title">{p.title}</span>
      {badge?.status === "future" && <span className="tool-cite-date">{badge.label}</span>}
    </Link>
  );
}

/* Every node in the tree, in a collapsed list. This is the crawlable copy of
   the tool (spec AC13) and a way to read the whole thing at once. */
function AllSteps({ tool }) {
  const ids = orderedIds(tool);
  return (
    <details className="tool-steps">
      <summary className="tool-steps-summary">All steps in this tool</summary>
      <ol className="tool-steps-list">
        {ids.map((id) => {
          const n = tool.nodes[id];
          return (
            <li key={id} id={`step-${id}`} className={`tool-steps-item tool-steps-${n.type}`}>
              {n.type === "question" ? (
                <>
                  <p className="tool-steps-text">{n.text}</p>
                  <ul className="tool-steps-options">
                    {n.options.map((o) => (
                      <li key={o.next + o.label}>{o.label}{" → "}<a href={`#step-${o.next}`}>{shortText(tool.nodes[o.next])}</a></li>
                    ))}
                  </ul>
                </>
              ) : (
                <>
                  <p className="tool-steps-text"><strong>{n.result.verdict}.</strong> {n.text}</p>
                  <p className="tool-steps-explanation">{n.result.explanation}</p>
                </>
              )}
              <p className="tool-steps-cites">
                Rests on:{" "}
                {(n.type === "result" ? n.result.cites : n.cites).map((l, i) => {
                  const p = getProvision(l);
                  return (
                    <React.Fragment key={l}>
                      {i > 0 && ", "}
                      {p ? <Link to={routeFor(p)}>{`${displayLabel(p)} — ${p.title}`}</Link> : l}
                    </React.Fragment>
                  );
                })}
              </p>
            </li>
          );
        })}
      </ol>
    </details>
  );
}

/* Nodes in the order a reader meets them: a breadth-first walk from the start,
   then anything the walk did not reach, so nothing is left out. */
function orderedIds(tool) {
  const out = [];
  const seen = new Set();
  const queue = [tool.start];
  while (queue.length) {
    const id = queue.shift();
    if (seen.has(id) || !tool.nodes[id]) continue;
    seen.add(id);
    out.push(id);
    for (const o of tool.nodes[id].options || []) queue.push(o.next);
  }
  for (const id of Object.keys(tool.nodes)) if (!seen.has(id)) out.push(id);
  return out;
}

function shortText(node) {
  if (!node) return "?";
  return node.type === "result" ? node.result.verdict : node.text;
}
