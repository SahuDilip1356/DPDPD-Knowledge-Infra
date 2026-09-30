import React from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import {
  listGlossary, glossaryGroups, getTerm, getProvision, documentOf, routeFor, displayLabel, glossaryTitle, GLOSSARY_TITLE
} from "../../lib/law";
import { usePageTitle } from "../../lib/usePageTitle";
import "../../styles/law.css";

/* Index of defined terms, grouped by first letter. */
export function GlossaryIndex() {
  usePageTitle(GLOSSARY_TITLE);
  const groups = glossaryGroups();
  const total = listGlossary().length;

  return (
    <PublicShell>
      <div className="law">
        <header className="law-head">
          <div className="law-wrap">
            <nav className="law-crumbs" aria-label="Breadcrumb">
              <Link to="/">Home</Link>
              <span aria-hidden="true">›</span>
              <span aria-current="page">Glossary</span>
            </nav>
            <p className="law-kicker">Defined terms</p>
            <h1 className="law-title">Glossary</h1>
            <p className="law-lede">
              {total} terms, each defined in the words of Section 2 of the Act or Rule 2 of the Rules.
              Nothing is paraphrased.
            </p>
          </div>
        </header>
        <div className="law-wrap law-main">
          {groups.map((g) => (
            <section key={g.letter} className="law-index-group" aria-labelledby={`gl-${g.letter}`}>
              <h2 id={`gl-${g.letter}`} className="law-h2 law-letter">{g.letter}</h2>
              <ul className="law-index-list law-gloss-list">
                {g.terms.map((t) => (
                  <li key={t.slug}>
                    <Link to={`/glossary/${t.slug}`} className="law-index-item">
                      <span className="law-index-title law-gloss-term">{t.term}</span>
                      <span className="law-index-date">{t.clause}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </div>
    </PublicShell>
  );
}

/* One defined term: the definition clause verbatim and where it comes from. */
export default function GlossaryEntry() {
  const { slug } = useParams();
  const t = getTerm(slug);
  usePageTitle(t ? glossaryTitle(t) : null);

  if (!t) return <Navigate to="/glossary" replace />;

  const p = getProvision(t.provision);
  const terms = listGlossary();
  const i = terms.indexOf(t);
  const prev = terms[i - 1];
  const next = terms[i + 1];

  return (
    <PublicShell>
      <article className="law">
        <header className="law-head">
          <div className="law-wrap">
            <nav className="law-crumbs" aria-label="Breadcrumb">
              <Link to="/">Home</Link>
              <span aria-hidden="true">›</span>
              <Link to="/glossary">Glossary</Link>
              <span aria-hidden="true">›</span>
              <span aria-current="page">{t.term}</span>
            </nav>
            <p className="law-kicker">Defined in {t.clause}</p>
            <h1 className="law-title">{t.term}</h1>
          </div>
        </header>
        <div className="law-wrap law-main">
          <section className="law-text" aria-label={`Definition of ${t.term}`}>
            <p className="law-line law-line-lead law-depth-0">{t.definition}</p>
          </section>
          <p className="law-source">
            {t.clause} of {p ? documentOf(p).name : t.provision}.{" "}
            {p && <Link to={routeFor(p)}>Read {displayLabel(p)} in full →</Link>}
          </p>
          <nav className="law-pager" aria-label="Neighbouring terms">
            {prev ? (
              <Link to={`/glossary/${prev.slug}`} className="law-pager-prev" rel="prev">
                <span className="law-pager-dir">← Previous</span>
                <span className="law-pager-name">{prev.term}</span>
              </Link>
            ) : <span />}
            {next ? (
              <Link to={`/glossary/${next.slug}`} className="law-pager-next" rel="next">
                <span className="law-pager-dir">Next →</span>
                <span className="law-pager-name">{next.term}</span>
              </Link>
            ) : <span />}
          </nav>
        </div>
      </article>
    </PublicShell>
  );
}
