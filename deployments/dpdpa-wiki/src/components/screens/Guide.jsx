import React, { useEffect, useMemo, useState } from "react";
import { Link, useParams, Navigate } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";
import { INFOGRAPHICS } from "../marketing/Infographics";
import { getGuide, listGuides } from "../../lib/guides";
import "../../styles/guide.css";

const SITE = "https://dpdpa.wiki";

/* Sets document title and head tags for this guide, restoring them on unmount
   so navigating back to the homepage does not leave a stale description. */
function useGuideHead(guide) {
  useEffect(() => {
    if (!guide) return;
    const prevTitle = document.title;
    const added = [];

    document.title = guide.meta_title || guide.title;

    const meta = (attr, key, content) => {
      let el = document.head.querySelector(`meta[${attr}="${key}"]`);
      if (el) {
        added.push({ el, prev: el.getAttribute("content"), owned: false });
        el.setAttribute("content", content);
      } else {
        el = document.createElement("meta");
        el.setAttribute(attr, key);
        el.setAttribute("content", content);
        document.head.appendChild(el);
        added.push({ el, owned: true });
      }
    };

    const canonicalHref = guide.canonical || `${SITE}/guide/${guide.slug}`;
    let link = document.head.querySelector('link[rel="canonical"]');
    const prevCanonical = link?.getAttribute("href");
    if (!link) {
      link = document.createElement("link");
      link.setAttribute("rel", "canonical");
      document.head.appendChild(link);
    }
    link.setAttribute("href", canonicalHref);

    meta("name", "description", guide.meta_description || "");
    meta("property", "og:type", "article");
    meta("property", "og:title", guide.title);
    meta("property", "og:description", guide.meta_description || "");
    meta("property", "og:url", canonicalHref);

    const ld = document.createElement("script");
    ld.type = "application/ld+json";
    ld.text = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Article",
      headline: guide.title,
      description: guide.meta_description,
      datePublished: guide.published,
      inLanguage: "en-IN",
      author: { "@type": "Organization", name: guide.author || "SaralPrivacy" },
      publisher: { "@type": "Organization", name: "SaralPrivacy" },
      mainEntityOfPage: { "@type": "WebPage", "@id": canonicalHref },
      keywords: [guide.primary_keyword, ...(guide.secondary_keywords || [])].filter(Boolean).join(", ")
    });
    document.head.appendChild(ld);

    return () => {
      document.title = prevTitle;
      for (const rec of added) {
        if (rec.owned) rec.el.remove();
        else if (rec.prev != null) rec.el.setAttribute("content", rec.prev);
      }
      if (prevCanonical) link.setAttribute("href", prevCanonical);
      ld.remove();
    };
  }, [guide]);
}

/* Reading progress. Cheap enough to run on scroll without throttling, and it
   gives a long document a sense of how much is left. */
function useReadingProgress() {
  const [pct, setPct] = useState(0);
  useEffect(() => {
    const onScroll = () => {
      const h = document.documentElement;
      const max = h.scrollHeight - h.clientHeight;
      setPct(max > 0 ? Math.min(100, (h.scrollTop / max) * 100) : 0);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return pct;
}

/* Highlights the section currently in view. Without this the contents list
   shows where you can go but never where you are, which in a 7,000-word
   document is most of its value. */
function useActiveHeading(ids) {
  const [active, setActive] = useState(null);
  useEffect(() => {
    if (!ids.length) return;
    const seen = new Map();
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) seen.set(e.target.id, e);
        // The topmost heading that is above the fold wins, so the highlight
        // follows reading position rather than jumping to whatever intersects.
        const visible = ids
          .map((id) => seen.get(id))
          .filter((e) => e && e.isIntersecting);
        if (visible.length) {
          setActive(visible[0].target.id);
          return;
        }
        const above = ids
          .map((id) => seen.get(id))
          .filter((e) => e && e.boundingClientRect.top < 0);
        if (above.length) setActive(above.at(-1).target.id);
      },
      { rootMargin: "-100px 0px -70% 0px", threshold: 0 }
    );
    const els = ids.map((id) => document.getElementById(id)).filter(Boolean);
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, [ids]);
  return active;
}

function Directive({ block }) {
  const Figure = INFOGRAPHICS[block.name];
  if (Figure) return <Figure />;

  if (block.name === "pullquote") {
    return <blockquote className="g-pullquote" dangerouslySetInnerHTML={{ __html: block.html }} />;
  }
  if (block.name === "share-line") {
    return <aside className="g-share" dangerouslySetInnerHTML={{ __html: block.html }} />;
  }
  if (block.name === "cta") {
    const f = block.fields || {};
    const external = f.url && /^https?:/i.test(f.url);
    return (
      <aside className="g-cta">
        <h3 className="g-cta-h">{f.heading}</h3>
        <p className="g-cta-b">{f.body}</p>
        {f.url && (external
          ? <a className="pub-btn pub-btn-primary" href={f.url}>{f.button}</a>
          : <Link className="pub-btn pub-btn-primary" to={f.url}>{f.button}</Link>)}
      </aside>
    );
  }
  // Unknown directive: render its content rather than dropping it silently.
  return <div dangerouslySetInnerHTML={{ __html: block.html }} />;
}

export default function Guide() {
  const { slug } = useParams();
  const guide = useMemo(() => getGuide(slug), [slug]);
  const progress = useReadingProgress();
  const tocIds = useMemo(
    () => (guide?.headings || []).filter((h) => h.depth === 2).map((h) => h.id),
    [guide]
  );
  const active = useActiveHeading(tocIds);
  useGuideHead(guide);

  if (!guide) return <Navigate to="/guide" replace />;

  const others = listGuides().filter((g) => g.slug !== guide.slug).slice(0, 3);
  const minutes = guide.reading_time || `${Math.max(1, Math.round(guide.wordCount / 230))} min`;

  return (
    <PublicShell>
      <div className="g-progress" aria-hidden="true">
        <span className="g-progress-fill" style={{ width: `${progress}%` }} />
      </div>

      <article className="g">
        <header className="g-head">
          <div className="g-head-inner">
            <nav className="g-crumbs" aria-label="Breadcrumb">
              <Link to="/">Home</Link>
              <span aria-hidden="true">/</span>
              <Link to="/guide">Guides</Link>
            </nav>
            <h1 className="g-title">{guide.title}</h1>
            <p className="g-meta">
              <span>{guide.author}</span>
              <span aria-hidden="true">·</span>
              <time dateTime={guide.published}>
                {new Date(guide.published).toLocaleDateString("en-IN", {
                  day: "numeric", month: "long", year: "numeric"
                })}
              </time>
              <span aria-hidden="true">·</span>
              <span>{minutes} read</span>
              <span aria-hidden="true">·</span>
              <span>{guide.wordCount.toLocaleString("en-IN")} words</span>
            </p>
          </div>
        </header>

        <div className="g-layout">
          {guide.headings?.length > 0 && (
            <nav className="g-toc" aria-label="On this page">
              <p className="g-toc-h">On this page</p>
              <ol>
                {guide.headings.filter((h) => h.depth === 2).map((h) => (
                  <li key={h.id}>
                    <a
                      href={`#${h.id}`}
                      className={active === h.id ? "is-active" : ""}
                      aria-current={active === h.id ? "true" : undefined}
                    >
                      {h.text}
                    </a>
                  </li>
                ))}
              </ol>
            </nav>
          )}

          <div className="g-body">
            {guide.blocks.map((block, i) =>
              block.type === "html"
                ? <div key={i} className="g-prose" dangerouslySetInnerHTML={{ __html: block.html }} />
                : <Directive key={i} block={block} />
            )}

            {guide.sources?.length > 0 && (
              <section className="g-sources" aria-labelledby="src-h">
                <h2 id="src-h" className="g-sources-h">Sources</h2>
                <ul>
                  {guide.sources.map((s) => (
                    <li key={s.url}>
                      <a href={s.url} rel="noopener noreferrer" target="_blank">{s.title}</a>
                    </li>
                  ))}
                </ul>
                <p className="g-freshness">
                  Reviewed {new Date(guide.published).toLocaleDateString("en-IN", {
                    day: "numeric", month: "long", year: "numeric"
                  })}. Government notifications on Significant Data Fiduciaries, restricted
                  countries and startup exemptions were awaited at the time of writing.
                  Check for newer notifications before acting on the dates here.
                </p>
                <p className="g-disclaimer">Reference material, not legal advice.</p>
              </section>
            )}
          </div>
        </div>

        {others.length > 0 && (
          <section className="g-more" aria-labelledby="more-h">
            <div className="g-more-inner">
              <h2 id="more-h" className="pub-h2">Keep reading</h2>
              <div className="g-more-list">
                {others.map((g) => (
                  <Link key={g.slug} to={`/guide/${g.slug}`} className="g-more-item">
                    <h3>{g.title}</h3>
                    <p>{g.meta_description}</p>
                  </Link>
                ))}
              </div>
            </div>
          </section>
        )}
      </article>
    </PublicShell>
  );
}
