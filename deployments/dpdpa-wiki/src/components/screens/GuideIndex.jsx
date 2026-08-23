import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import { listGuides } from "../../lib/guides";
import "../../styles/guide.css";

export default function GuideIndex() {
  const guides = listGuides();

  useEffect(() => {
    const prev = document.title;
    document.title = "Guides to the DPDP Act | dpdpa.wiki";
    return () => { document.title = prev; };
  }, []);

  return (
    <PublicShell>
      <section className="gi-head">
        <div className="pub-container">
          <p className="hero-eyebrow">Guides</p>
          <h1 className="gi-title">Long-form guides to the DPDP Act</h1>
          <p className="gi-lede">
            Each guide covers one part of the law end to end, in plain language, with
            worked examples from Indian businesses and the sections cited throughout.
          </p>
        </div>
      </section>

      <section className="pub-section">
        <div className="pub-container">
          {guides.length === 0 ? (
            <p className="gi-empty">No guides published yet.</p>
          ) : (
            <ul className="gi-list">
              {guides.map((g) => {
                const minutes = g.reading_time || `${Math.max(1, Math.round(g.wordCount / 230))} min`;
                return (
                  <li key={g.slug}>
                    <Link to={`/guide/${g.slug}`} className="gi-item">
                      <div className="gi-item-main">
                        <h2 className="gi-item-title">{g.title}</h2>
                        <p className="gi-item-desc">{g.meta_description}</p>
                        <p className="gi-item-meta">
                          <time dateTime={g.published}>
                            {new Date(g.published).toLocaleDateString("en-IN", {
                              day: "numeric", month: "long", year: "numeric"
                            })}
                          </time>
                          <span aria-hidden="true">·</span>
                          <span>{minutes} read</span>
                          {g.format && <><span aria-hidden="true">·</span><span>{g.format}</span></>}
                        </p>
                      </div>
                      <span className="gi-item-go" aria-hidden="true">→</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </section>
    </PublicShell>
  );
}
