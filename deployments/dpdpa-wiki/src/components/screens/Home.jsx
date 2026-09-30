import React, { useState } from "react";
import { Link } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import { HERO, JOURNEYS, RESOURCES, COURSE, READINESS, FAQ, TRUST, CAPTURE } from "../../data/homeContent";
import { listModules } from "../../lib/modules";
import CometCascadeHeroBackground from "../marketing/CometCascadeHeroBackground";
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
      setMessage("Enter a valid email address.");
      return;
    }

    setState("sending");
    setMessage("");

    // Loaded on submit so the Supabase SDK never weighs down the public pages.
    let supabase = null;
    try {
      ({ supabase } = await import("../../data/supabaseClient"));
    } catch {
      supabase = null;
    }
    if (!supabase) {
      setState("error");
      setMessage("Subscriptions are unavailable right now. Try again shortly.");
      return;
    }

    let error;
    try {
      ({ error } = await supabase.from("subscribers").insert({
        email: value,
        intent,
        source_path: window.location.pathname,
        assessment_score: score
      }));
    } catch {
      setState("error");
      setMessage("We couldn't save that. Try again in a moment.");
      return;
    }

    // A repeat address is a success from the reader's point of view.
    if (error && error.code !== "23505") {
      setState("error");
      setMessage("We couldn't save that. Try again in a moment.");
      return;
    }

    setState("done");
    setMessage("Your request was saved. Email delivery is not yet enabled.");
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

/* ── Page ───────────────────────────────────────────────────────────── */
export default function Home() {
  // Authored module titles win over the fallback list once the files exist.
  const authored = listModules();
  const course = COURSE.map((c) => {
    const m = authored.find((x) => x.slug === c.slug);
    return m ? { ...c, title: m.title, blurb: m.summary || c.blurb } : c;
  });
  // The hero search used to hand off to Ask Intelligence, which is not
  // public this cycle (spec NG2); the provision index is the way in.

  // FAQPage structured data is emitted into the HTML by the prerender step
  // (see lib/seo.js), so it is present before any script runs. Injecting it
  // again here would duplicate the block for anyone with JavaScript on.

  return (
    <PublicShell>
      {/* ── Hero ─────────────────────────────────────────────────── */}
      <section className="hero">
        <CometCascadeHeroBackground />
        <div className="pub-container hero-inner">
          <p className="hero-eyebrow">{HERO.eyebrow}</p>
          <h1 className="hero-title">{HERO.title}</h1>
          <p className="hero-sub">{HERO.subtitle}</p>

          <div className="hero-actions">
            <Link className="pub-btn pub-btn-primary" to={HERO.primaryCta.href}>{HERO.primaryCta.label}</Link>
            <Link className="pub-btn pub-btn-ghost" to={HERO.secondaryCta.href}>
              {HERO.secondaryCta.label} <span aria-hidden="true">→</span>
            </Link>
          </div>

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

      {/* ── The course ───────────────────────────────────────────── */}
      <section className="pub-section" aria-labelledby="course-h">
        <div className="pub-container">
          <p className="pub-eyebrow">The course</p>
          <h2 id="course-h" className="pub-h2">Six modules, from the basics to your business</h2>
          <p className="pub-lede">Read them in order. Each one ends with a short self-test and a link to the next.</p>
          <ol className="course">
            {course.map((m, i) => (
              <li key={m.slug} className="course-item">
                <Link to={`/learn/${m.slug}`} className="course-link">
                  <span className="course-num" aria-hidden="true">{String(i + 1).padStart(2, "0")}</span>
                  <span className="course-body">
                    <span className="course-title">{m.title}</span>
                    <span className="course-blurb">{m.blurb}</span>
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* ── Readiness: SaralPrivacy owns the assessment ───────────── */}
      <section className="pub-section pub-section-alt" id="assessment" aria-labelledby="ready-h">
        <div className="pub-container">
          <p className="pub-eyebrow">{READINESS.eyebrow}</p>
          <h2 id="ready-h" className="pub-h2">{READINESS.title}</h2>
          <p className="pub-lede">{READINESS.body}</p>
          <a className="pub-btn pub-btn-primary" href={READINESS.cta.href} rel="noopener">{READINESS.cta.label}</a>
        </div>
      </section>

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
                {item.cite && (
                  <p className="faq-cite"><Link to={item.cite}>Read the provision →</Link></p>
                )}
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
