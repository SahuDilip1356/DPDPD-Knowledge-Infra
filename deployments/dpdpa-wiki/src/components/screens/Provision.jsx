import React from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import {
  getByRoute, displayLabel, documentOf, chapterOf, commencement, clauseLines,
  neighbours, routeFor, heading, pageTitle, moduleTitle, shortHash
} from "../../lib/law";
import { usePageTitle } from "../../lib/usePageTitle";
import "../../styles/law.css";

/* One provision of the Act or the Rules: the gazette text as printed, its
   source, and what the site has to say about it. Everything shown here comes
   from the provision record and nothing else. */
export default function Provision() {
  const { pathname } = useLocation();
  const p = getByRoute(pathname);
  usePageTitle(p ? pageTitle(p) : null);

  if (!p) return <Navigate to={pathname.startsWith("/rules") ? "/rules" : "/act"} replace />;

  const doc = documentOf(p);
  const chapter = chapterOf(p);
  const badge = commencement(p);
  const lines = clauseLines(p.text);
  const { prev, next } = neighbours(p);

  return (
    <PublicShell>
      <article className="law">
        <header className="law-head">
          <div className="law-wrap">
            <nav className="law-crumbs" aria-label="Breadcrumb">
              <Link to="/">Home</Link>
              <span aria-hidden="true">›</span>
              <Link to={doc.route}>{doc.short}</Link>
              <span aria-hidden="true">›</span>
              <span aria-current="page">{displayLabel(p)}</span>
            </nav>
            {/* Sections show their chapter; schedules show their heading as
                printed, since the h1 shortens it. */}
            {chapter && (
              <p className="law-kicker">{`Chapter ${chapter.numeral} — ${chapter.title}`}</p>
            )}
            {(p.kind === "act-schedule" || p.kind === "rules-schedule") && (
              <p className="law-kicker">{p.title}</p>
            )}
            <h1 className="law-title">{heading(p)}</h1>
            {badge && (
              <p className={`law-badge law-badge-${badge.status}`}>{badge.label}</p>
            )}
          </div>
        </header>

        <div className="law-wrap law-main">
          <section className="law-text" aria-label={`Text of ${displayLabel(p)}`}>
            {lines.map((l, i) => (
              <p key={i} className={`law-line law-line-${l.kind} law-depth-${l.depth}`}>{l.text}</p>
            ))}
          </section>

          <p className="law-source">
            Source:{" "}
            <a href={p.source.url} rel="noopener noreferrer" target="_blank">
              {`${p.source.document}, ${p.source.notification}`}
            </a>
            {`; SHA-256 `}<code>{shortHash(p.source.sha256)}</code>{` — verified copy`}
            {p.source.corrigendum && `. Corrigendum ${p.source.corrigendum}`}
          </p>

          <section className="law-note" aria-labelledby="note-h">
            <h2 id="note-h" className="law-h2">Plain-language note</h2>
            {p.note
              ? <p className="law-note-body">{p.note}</p>
              : <p className="law-pending">Plain-language note pending</p>}
          </section>

          {p.questions?.length > 0 && (
            <section className="law-questions" aria-labelledby="q-h">
              <h2 id="q-h" className="law-h2">Questions people ask about this provision</h2>
              <ul>
                {p.questions.map((q) => <li key={q.id}>{q.question}</li>)}
              </ul>
            </section>
          )}

          {p.kind === "act-schedule" && p.rows?.length > 0 && (
            <section className="law-schedule" aria-labelledby="sch-h">
              <h2 id="sch-h" className="law-h2">Penalties as gazetted</h2>
              <div className="law-table-scroll">
                <table className="law-table">
                  <thead>
                    <tr>
                      <th scope="col">Sl.</th>
                      <th scope="col">Breach of provisions of this Act or rules made thereunder</th>
                      <th scope="col">Penalty</th>
                    </tr>
                  </thead>
                  <tbody>
                    {p.rows.map((r) => (
                      <tr key={r.serial}>
                        <td>{r.serial}</td>
                        <td>{r.breach}</td>
                        <td>{r.penalty}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          <p className="law-taught">
            Taught in <Link to={`/learn/${p.module}`}>{moduleTitle(p.module)}</Link>
          </p>

          <nav className="law-pager" aria-label="Neighbouring provisions">
            {prev ? (
              <Link to={routeFor(prev)} className="law-pager-prev" rel="prev">
                <span className="law-pager-dir">← Previous</span>
                <span className="law-pager-name">{displayLabel(prev)} — {prev.title}</span>
              </Link>
            ) : <span />}
            {next ? (
              <Link to={routeFor(next)} className="law-pager-next" rel="next">
                <span className="law-pager-dir">Next →</span>
                <span className="law-pager-name">{displayLabel(next)} — {next.title}</span>
              </Link>
            ) : <span />}
          </nav>
        </div>
      </article>
    </PublicShell>
  );
}
