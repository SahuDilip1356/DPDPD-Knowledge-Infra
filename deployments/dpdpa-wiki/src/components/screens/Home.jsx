import React, { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import { supabase } from "../../data/supabaseClient";
import {
  HERO, JOURNEYS, RESOURCES, ASSESSMENT, ASSESSMENT_BANDS, FAQ, TRUST, CAPTURE
} from "../../data/homeContent";
import "../../styles/home.css";

/* ── Email capture ──────────────────────────────────────────────────
   Used by both conversion paths. `intent` distinguishes a low-friction
   checklist download from a high-intent assessment follow-up, so the two
   are never mixed in the same list.                                  */
function SubscribeForm({ intent = "checklist", score = null, compact = false }) {
  const [email, setEmail] = useState("");
  const [state, setState] = useState("idle"); // idle | sending | done | error
  const [message, setMessage] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    const value = email.trim();

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
      setState("error");
      setMessage("Enter an email address we can send the checklist to.");
      return;
    }

    setState("sending");
    setMessage("");

    if (!supabase) {
      setState("error");
      setMessage("Subscriptions are unavailable right now. Try again shortly.");
      return;
    }

    const { error } = await supabase.from("subscribers").insert({
      email: value,
      intent,
      source_path: window.location.pathname,
      assessment_score: score
    });

    // A repeat address is a success from the reader's point of view.
    if (error && error.code !== "23505") {
      setState("error");
      setMessage("We couldn't save that. Try again in a moment.");
      return;
    }

    setState("done");
    setMessage("Check your inbox — the checklist is on its way.");
  };

  if (state === "done") {
    return (
      <p className="cap-done" role="status">
        <span aria-hidden="true">✓</span> {message}
      </p>
    );
  }

  return (
    <form className={`cap-form ${compact ? "cap-form-compact" : ""}`} onSubmit={submit} noValidate>
      <label className="sr-only" htmlFor={`email-${intent}`}>Email address</label>
      <input
        id={`email-${intent}`}
        className="cap-input"
        type="email"
        inputMode="email"
        autoComplete="email"
        placeholder={CAPTURE.placeholder}
        value={email}
        onChange={(e) => { setEmail(e.target.value); if (state === "error") setState("idle"); }}
        aria-invalid={state === "error"}
        aria-describedby={state === "error" ? `err-${intent}` : undefined}
      />
      <button className="pub-btn pub-btn-primary" type="submit" disabled={state === "sending"}>
        {state === "sending" ? "Sending…" : CAPTURE.cta}
      </button>
      {state === "error" && (
        <p className="cap-error" id={`err-${intent}`} role="alert">{message}</p>
      )}
    </form>
  );
}

/* ── Readiness assessment ─────────────────────────────────────────── */
function Assessment() {
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const total = useMemo(
    () => Object.values(answers).reduce((sum, n) => sum + n, 0),
    [answers]
  );
  const complete = Object.keys(answers).length === ASSESSMENT.length;
  const band = ASSESSMENT_BANDS.find((b) => total >= b.min) || ASSESSMENT_BANDS.at(-1);
  const maxScore = ASSESSMENT.length * 2;

  return (
    <section className="pub-section assess" id="assessment" aria-labelledby="assess-h">
      <div className="pub-container">
        <p className="pub-eyebrow">Readiness</p>
        <h2 id="assess-h" className="pub-h2">How ready is your organisation?</h2>
        <p className="pub-lede">
          Five questions, each tied to a specific obligation. Nothing is stored unless you ask for the result.
        </p>

        <ol className="assess-list">
          {ASSESSMENT.map((q, i) => (
            <li key={q.id} className="assess-item">
              <div className="assess-q">
                <span className="assess-num" aria-hidden="true">{String(i + 1).padStart(2, "0")}</span>
                <div>
                  <p className="assess-question">{q.question}</p>
                  <p className="assess-section">{q.section}</p>
                </div>
              </div>
              <div className="assess-options" role="group" aria-label={q.question}>
                {q.options.map((opt) => {
                  const active = answers[q.id] === opt.score;
                  return (
                    <button
                      key={opt.label}
                      type="button"
                      className={`assess-opt ${active ? "is-active" : ""}`}
                      aria-pressed={active}
                      onClick={() => {
                        setAnswers((a) => ({ ...a, [q.id]: opt.score }));
                        setSubmitted(false);
                      }}
                    >
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </li>
          ))}
        </ol>

        {!submitted ? (
          <button
            className="pub-btn pub-btn-primary assess-submit"
            type="button"
            disabled={!complete}
            onClick={() => setSubmitted(true)}
          >
            {complete ? "See where you stand" : `Answer all ${ASSESSMENT.length} questions`}
          </button>
        ) : (
          <div className="assess-result" role="status">
            <div className="assess-score">
              <span className="assess-score-num">{total}</span>
              <span className="assess-score-of">of {maxScore}</span>
            </div>
            <div>
              <h3 className="assess-band">{band.label}</h3>
              <p className="assess-note">{band.note}</p>
              <p className="assess-followup">
                Want the gaps written up against each section?
              </p>
              <SubscribeForm intent="assessment" score={total} compact />
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

/* ── Page ───────────────────────────────────────────────────────────── */
export default function Home() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  // Search intent belongs to the grounded Q&A surface, not a new engine.
  const search = (e) => {
    e.preventDefault();
    const q = query.trim();
    navigate(q ? `/ask?q=${encodeURIComponent(q)}` : "/ask");
  };

  // FAQPage structured data — the visible FAQ below is the same source.
  useEffect(() => {
    const el = document.createElement("script");
    el.type = "application/ld+json";
    el.text = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      mainEntity: FAQ.map(({ q, a }) => ({
        "@type": "Question",
        name: q,
        acceptedAnswer: { "@type": "Answer", text: a }
      }))
    });
    document.head.appendChild(el);
    return () => { document.head.removeChild(el); };
  }, []);

  return (
    <PublicShell>
      {/* ── Hero ─────────────────────────────────────────────────── */}
      <section className="hero">
        <div className="pub-container hero-inner">
          <p className="hero-eyebrow">{HERO.eyebrow}</p>
          <h1 className="hero-title">{HERO.title}</h1>
          <p className="hero-sub">{HERO.subtitle}</p>

          <div className="hero-actions">
            <a className="pub-btn pub-btn-primary" href="#checklist">{HERO.primaryCta.label}</a>
            <Link className="pub-btn pub-btn-ghost" to={HERO.secondaryCta.href}>
              {HERO.secondaryCta.label} <span aria-hidden="true">→</span>
            </Link>
          </div>

          <form className="hero-search" onSubmit={search} role="search">
            <label className="sr-only" htmlFor="hero-q">Search the DPDP Act</label>
            <input
              id="hero-q"
              className="hero-search-input"
              type="search"
              placeholder={HERO.searchPlaceholder}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button className="hero-search-btn" type="submit">Search</button>
          </form>
        </div>
      </section>

      {/* ── Journeys ─────────────────────────────────────────────── */}
      <section className="pub-section" aria-labelledby="journeys-h">
        <div className="pub-container">
          <p className="pub-eyebrow">Start where you are</p>
          <h2 id="journeys-h" className="pub-h2">Popular journeys</h2>
          <div className="journeys">
            {JOURNEYS.map((j) => (
              <Link key={j.id} to={j.href} className="journey">
                <h3 className="journey-label">{j.label}</h3>
                <p className="journey-lede">{j.lede}</p>
                <span className="journey-step">{j.firstStep} <span aria-hidden="true">→</span></span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Resources ────────────────────────────────────────────── */}
      <section className="pub-section pub-section-alt" aria-labelledby="res-h">
        <div className="pub-container">
          <p className="pub-eyebrow">Reference</p>
          <h2 id="res-h" className="pub-h2">The core material</h2>
          <div className="resources">
            {RESOURCES.map((r) => (
              <Link key={r.title} to={r.href} className="resource">
                <div className="resource-top">
                  <h3 className="resource-title">{r.title}</h3>
                  <span className="resource-meta">{r.meta}</span>
                </div>
                <p className="resource-desc">{r.description}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Assessment ───────────────────────────────────────────── */}
      <Assessment />

      {/* ── Trust ────────────────────────────────────────────────── */}
      <section className="trust" aria-labelledby="trust-h">
        <div className="pub-container trust-inner">
          <h2 id="trust-h" className="trust-claim">{TRUST.reviewNote}</h2>
          <dl className="trust-points">
            {TRUST.points.map((p) => (
              <div key={p.label} className="trust-point">
                <dt>{p.label}</dt>
                <dd>{p.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      {/* ── FAQ ──────────────────────────────────────────────────── */}
      <section className="pub-section" aria-labelledby="faq-h">
        <div className="pub-container">
          <p className="pub-eyebrow">Common questions</p>
          <h2 id="faq-h" className="pub-h2">What people ask first</h2>
          <div className="faq">
            {FAQ.map((item) => (
              <article key={item.q} className="faq-item">
                <h3 className="faq-q">{item.q}</h3>
                <p className="faq-a">{item.a}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ── Capture ──────────────────────────────────────────────── */}
      <section className="capture" id="checklist" aria-labelledby="cap-h">
        <div className="pub-container capture-inner">
          <div>
            <h2 id="cap-h" className="capture-title">{CAPTURE.title}</h2>
            <p className="capture-body">{CAPTURE.body}</p>
          </div>
          <div>
            <SubscribeForm intent="checklist" />
            <p className="capture-reassurance">{CAPTURE.reassurance}</p>
          </div>
        </div>
      </section>
    </PublicShell>
  );
}
