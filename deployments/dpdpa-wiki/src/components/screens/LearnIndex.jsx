import React from "react";
import { Link } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import { listModules, modulePath, LEARN_TITLE, TOTAL_MODULES } from "../../lib/modules";
import { usePageTitle } from "../../lib/usePageTitle";
import "../../styles/law.css";
import "../../styles/learn.css";

/* /learn — the course in order. Renders whatever modules exist, so a module
   still being written simply does not appear yet. */
export default function LearnIndex() {
  usePageTitle(LEARN_TITLE);
  const modules = listModules();

  return (
    <PublicShell>
      <article className="law learn">
        <header className="law-head">
          <div className="law-wrap">
            <nav className="law-crumbs" aria-label="Breadcrumb">
              <Link to="/">Home</Link>
              <span aria-hidden="true">›</span>
              <span aria-current="page">Learn</span>
            </nav>
            <p className="law-kicker">The course</p>
            <h1 className="law-title">Learn the DPDPA</h1>
            <p className="law-lede">
              {TOTAL_MODULES} short modules, from what the Act is to what it asks of your business.
              Read them in order. Each cites the provisions it rests on and ends with a self-test.
            </p>
          </div>
        </header>

        <div className="law-wrap law-main">
          <ol className="learn-list">
            {modules.map((m) => (
              <li key={m.slug} className="learn-card">
                <Link to={modulePath(m)} className="learn-card-link">
                  <span className="learn-card-num">Module {m.order}</span>
                  <span className="learn-card-title">{m.title}</span>
                  <span className="learn-card-summary">{m.summary}</span>
                  <span className="learn-card-meta">
                    {m.minutes} min read · {m.lessonCount} lessons · {m.provisions.length} provisions · {m.quizCount}-question self-test
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        </div>
      </article>
    </PublicShell>
  );
}
