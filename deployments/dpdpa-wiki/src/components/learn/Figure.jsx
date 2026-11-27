import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { extractCitations, routeForLabel } from "../../lib/citations";
import { CHAPTERS, formatDate } from "../../lib/law";
import { useToday } from "../../lib/useToday";

/* ═══════════════════════════════════════════════════════════════════
   Lesson figures.

   Each lesson carries one figure that shows the legal mechanism itself:
   who is inside the Act, how the Rules hang off it, when things start.
   The figure is data in the lesson's Markdown (a JSON block), rendered
   here, so authors never write layout and every label stays checkable
   by the build's citation guard.

   Colour is a grammar, the same in every figure on the site:
     principal  — the individual the data is about        (green)
     fiduciary  — the business deciding purpose and means  (saffron)
     processor  — the vendor processing on its behalf      (teal)
     manager    — the Consent Manager                      (violet)
     state      — Parliament, the Government, the Board    (navy)
     neutral    — everything else                          (slate)

   Motion: one reveal per figure, when it first scrolls into view, in the
   order the law reasons. It only runs when JavaScript has loaded and the
   reader has not asked for reduced motion; without either, the figure is
   simply complete. A Replay control re-runs it on request.
   ═══════════════════════════════════════════════════════════════════ */

export const ROLES = {
  principal: "Data Principal",
  fiduciary: "Data Fiduciary",
  processor: "Data Processor",
  manager: "Consent Manager",
  state: "Government and Board",
  neutral: ""
};

/** "Section 3(c)" → a link to the provision page, keeping the words. */
export function Cite({ text }) {
  if (!text) return null;
  const label = extractCitations(text)[0];
  const href = label && routeForLabel(label);
  return href ? (
    <Link className="fig-cite" to={href}>{text}</Link>
  ) : (
    <span className="fig-cite">{text}</span>
  );
}

function prefersReducedMotion() {
  try {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch {
    return true;
  }
}

/** Frame, caption and the one reveal. */
function Frame({ spec, kind, children }) {
  const ref = useRef(null);
  const [anim, setAnim] = useState(false); // the page may animate at all
  const [live, setLive] = useState(false); // the reveal has run

  useEffect(() => {
    if (prefersReducedMotion() || typeof IntersectionObserver === "undefined") return undefined;
    setAnim(true);
    const el = ref.current;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setLive(true);
          io.disconnect();
        }
      },
      { threshold: 0.3 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const replay = () => {
    setLive(false);
    // Two frames: one to paint the reset state, one to start again.
    requestAnimationFrame(() => requestAnimationFrame(() => setLive(true)));
  };

  const cls = ["fig", `fig-${kind}`, anim ? "is-anim" : "", live ? "is-live" : ""].filter(Boolean).join(" ");
  return (
    <figure className={cls} ref={ref}>
      {spec.title && <figcaption className="fig-title">{spec.title}</figcaption>}
      <div className="fig-body">{children}</div>
      {(spec.caption || anim) && (
        <div className="fig-foot">
          {spec.caption && <p className="fig-caption">{spec.caption}</p>}
          {anim && (
            <button type="button" className="fig-replay" onClick={replay} aria-label={`Replay the figure: ${spec.title || kind}`}>
              Replay
            </button>
          )}
        </div>
      )}
    </figure>
  );
}

const step = (i) => ({ "--i": i });

/* ── gate: tests applied in order; failing any one exits ─────────── */
function Gate({ spec }) {
  const steps = spec.steps || [];
  return (
    <Frame spec={spec} kind="gate">
      <ol className="gate">
        {steps.map((s, i) => (
          <li key={i} className="gate-step fig-step" style={step(i)}>
            <div className="gate-q">
              <span className="gate-n" aria-hidden="true">{i + 1}</span>
              <div>
                <p className="gate-text">{s.q}</p>
                <Cite text={s.cite} />
              </div>
            </div>
            {s.fail && (
              <div className="gate-exit">
                <span className="gate-exit-label">{s.failLabel || "If not"}</span>
                <span className="gate-exit-out">{s.fail}</span>
              </div>
            )}
            {s.pass && <p className="gate-pass">{s.pass}</p>}
          </li>
        ))}
        {spec.result && (
          <li className={`gate-result role-${spec.result.role || "fiduciary"} fig-step`} style={step(steps.length)}>
            <p className="gate-result-text">{spec.result.label}</p>
            <Cite text={spec.result.cite} />
          </li>
        )}
      </ol>
    </Frame>
  );
}

/* ── stack: layers of authority, each resting on the one above ──── */
function Stack({ spec }) {
  const layers = spec.layers || [];
  const links = spec.links || [];
  return (
    <Frame spec={spec} kind="stack">
      <div className="stack-wrap">
        <ol className="stack">
          {layers.map((l, i) => (
            <React.Fragment key={i}>
              <li className={`stack-layer role-${l.role || "state"} fig-step`} style={step(i * 2)}>
                <div className="stack-name">{l.name}</div>
                {l.detail && <p className="stack-detail">{l.detail}</p>}
                <Cite text={l.cite} />
              </li>
              {i < layers.length - 1 && (
                <li className="stack-link fig-step" style={step(i * 2 + 1)} aria-hidden={!links[i]}>
                  <span className="stack-arrow" aria-hidden="true" />
                  {links[i] && <span className="stack-link-text">{links[i]}</span>}
                </li>
              )}
            </React.Fragment>
          ))}
        </ol>
        {spec.checks?.length > 0 && (
          <aside className="stack-checks">
            {spec.checksTitle && <p className="stack-checks-h">{spec.checksTitle}</p>}
            <ul>
              {spec.checks.map((c, i) => (
                <li key={i} className="fig-step" style={step(layers.length * 2 + i)}>
                  <strong>{c.label}</strong>
                  {c.detail && <span> {c.detail}</span>}
                  <Cite text={c.cite} />
                </li>
              ))}
            </ul>
          </aside>
        )}
      </div>
    </Frame>
  );
}

/* ── timeline: dated events, with where today falls ─────────────── */
function Timeline({ spec }) {
  const events = [...(spec.events || [])].sort((a, b) => String(a.date).localeCompare(String(b.date)));
  // The build day on first render, so hydration matches the prerender; the reader's day after.
  const today = useToday().toISOString().slice(0, 10);
  const nowIndex = events.findIndex((e) => e.date > today); // first future event
  const markerAt = nowIndex === -1 ? events.length : nowIndex;

  const items = [];
  events.forEach((e, i) => {
    if (i === markerAt) items.push({ now: true });
    items.push(e);
  });
  if (markerAt === events.length) items.push({ now: true });

  return (
    <Frame spec={spec} kind="timeline">
      <ol className="tl">
        {items.map((e, i) =>
          e.now ? (
            <li key="now" className="tl-now fig-step" style={step(i)}>
              <span className="tl-now-dot" aria-hidden="true" />
              <span className="tl-now-label">Today, {formatDate(today)}</span>
            </li>
          ) : (
            <li key={i} className={`tl-event role-${e.role || "state"} ${e.date <= today ? "is-past" : "is-future"} fig-step`} style={step(i)}>
              <span className="tl-dot" aria-hidden="true" />
              <time className="tl-date" dateTime={e.date}>{formatDate(e.date)}</time>
              <p className="tl-label">{e.label}</p>
              {e.detail && <p className="tl-detail">{e.detail}</p>}
              <Cite text={e.cite} />
            </li>
          )
        )}
      </ol>
    </Frame>
  );
}

/* ── roles: the cast, and what runs between them ─────────────────── */
function Roles({ spec }) {
  const nodes = spec.nodes || [];
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
  return (
    <Frame spec={spec} kind="roles">
      <ul className="roles">
        {nodes.map((n, i) => (
          <li key={n.id} className={`role-card role-${n.role || "neutral"} fig-step`} style={step(i)}>
            <span className="role-name">{n.name}</span>
            {n.def && <p className="role-def">{n.def}</p>}
            {n.example && <p className="role-eg">{n.example}</p>}
            <Cite text={n.cite} />
          </li>
        ))}
      </ul>
      {spec.edges?.length > 0 && (
        <ul className="role-edges">
          {spec.edges.map((e, i) => {
            const a = byId[e.from], b = byId[e.to];
            return (
              <li key={i} className="role-edge fig-step" style={step(nodes.length + i)}>
                <span className={`role-chip role-${a?.role || "neutral"}`}>{a?.name || e.from}</span>
                <span className="role-edge-label">{e.label}</span>
                <span className={`role-chip role-${b?.role || "neutral"}`}>{b?.name || e.to}</span>
                <Cite text={e.cite} />
              </li>
            );
          })}
        </ul>
      )}
    </Frame>
  );
}

/* ── changes: what an amendment did to another law ──────────────── */
function Changes({ spec }) {
  return (
    <Frame spec={spec} kind="changes">
      <ul className="chg">
        {(spec.items || []).map((c, i) => (
          <li key={i} className="chg-item fig-step" style={step(i)}>
            <p className="chg-law">{c.law}</p>
            <div className="chg-diff">
              {c.before && <span className="chg-before"><span className="sr-only">Before: </span>{c.before}</span>}
              <span className="chg-arrow" aria-hidden="true" />
              <span className={`chg-after${c.omitted ? " is-omitted" : ""}`}><span className="sr-only">After: </span>{c.after}</span>
            </div>
            <Cite text={c.cite} />
          </li>
        ))}
      </ul>
    </Frame>
  );
}

/* ── actmap: the Act's nine chapters, sized by sections ─────────── */
const CHAPTER_ROLE = { I: "neutral", II: "fiduciary", III: "principal", IV: "neutral", V: "state", VI: "state", VII: "state", VIII: "state", IX: "neutral" };
function ActMap({ spec }) {
  return (
    <Frame spec={spec} kind="actmap">
      <ol className="am">
        {CHAPTERS.map((c, i) => {
          const n = c.to - c.from + 1;
          return (
            <li key={c.numeral} className={`am-ch role-${CHAPTER_ROLE[c.numeral]} fig-step`} style={{ ...step(i), "--n": n }}>
              <Link to={`/act/section-${c.from}`} className="am-link">
                <span className="am-bar" aria-hidden="true" />
                <span className="am-num">Chapter {c.numeral}</span>
                <span className="am-title">{c.title}</span>
                <span className="am-range">{c.from === c.to ? `Section ${c.from}` : `Sections ${c.from}–${c.to}`}</span>
              </Link>
            </li>
          );
        })}
        <li className="am-ch role-state fig-step" style={{ ...step(CHAPTERS.length), "--n": 2 }}>
          <Link to="/act/schedule" className="am-link">
            <span className="am-bar" aria-hidden="true" />
            <span className="am-num">Schedule</span>
            <span className="am-title">Penalties</span>
            <span className="am-range">7 entries</span>
          </Link>
        </li>
      </ol>
    </Frame>
  );
}

/** Columns that avoid a lone orphan: 4 → 2×2, 5 → 3+2, 6 → 3×2, 7 → 4+3. */
const gridCols = (n) => (n <= 3 ? n : n === 4 ? 2 : n <= 6 ? 3 : 4);

/* ── steps: an ordered procedure, each step with its time limit ───── */
function Steps({ spec }) {
  return (
    <Frame spec={spec} kind="steps">
      <ol className="steps" style={{ "--cols": gridCols((spec.steps || []).length) }}>
        {(spec.steps || []).map((st, i) => (
          <li key={i} className={`steps-item role-${st.role || "fiduciary"} fig-step`} style={step(i)}>
            {st.when && <span className="steps-when">{st.when}</span>}
            <p className="steps-label">{st.label}</p>
            {st.detail && <p className="steps-detail">{st.detail}</p>}
            <Cite text={st.cite} />
          </li>
        ))}
      </ol>
    </Frame>
  );
}

/* ── checklist: tests that must all hold (or items a thing must carry) ─ */
function Checklist({ spec }) {
  return (
    <Frame spec={spec} kind="checklist">
      <ul className={`checks role-${spec.role || "fiduciary"}`}>
        {(spec.items || []).map((c, i) => (
          <li key={i} className="checks-item fig-step" style={step(i)}>
            <span className="checks-mark" aria-hidden="true" />
            <div>
              <p className="checks-label">{c.label}</p>
              {c.detail && <p className="checks-detail">{c.detail}</p>}
              <Cite text={c.cite} />
            </div>
          </li>
        ))}
      </ul>
    </Frame>
  );
}

/* ── scale: magnitudes on one axis (e.g. the penalty ceilings) ─────── */
function Scale({ spec }) {
  const items = spec.items || [];
  const max = Math.max(1, ...items.map((x) => Number(x.value) || 0));
  return (
    <Frame spec={spec} kind="scale">
      <ul className="scale">
        {items.map((x, i) => (
          <li key={i} className={`scale-item role-${x.role || "state"} fig-step`} style={{ ...step(i), "--w": (Number(x.value) || 0) / max }}>
            <p className="scale-label">{x.label}</p>
            <div className="scale-row">
              <span className="scale-bar" aria-hidden="true" />
              <span className="scale-value">{x.display}</span>
            </div>
            <Cite text={x.cite} />
          </li>
        ))}
      </ul>
    </Frame>
  );
}

/* ── compare: two sides of a distinction ───────────────────────────── */
function Compare({ spec }) {
  return (
    <Frame spec={spec} kind="compare">
      <div className="cmp">
        {(spec.columns || []).slice(0, 2).map((col, ci) => (
          <section key={ci} className={`cmp-col role-${col.role || "neutral"} fig-step`} style={step(ci)}>
            <p className="cmp-h">{col.heading}</p>
            <ul>
              {(col.points || []).map((pt, i) => (
                <li key={i}>
                  {typeof pt === "string" ? pt : pt.text}
                  {typeof pt === "object" && <> <Cite text={pt.cite} /></>}
                </li>
              ))}
            </ul>
            <Cite text={col.cite} />
          </section>
        ))}
      </div>
    </Frame>
  );
}

/* ── map: where data sits and travels, with the border it crosses ── */
function MapFig({ spec }) {
  const regions = spec.regions || [];
  const roleOf = Object.fromEntries(regions.flatMap((r) => (r.places || []).map((pl) => [pl.name, pl.role || "neutral"])));
  let n = 0;
  return (
    <Frame spec={spec} kind="map">
      <div className="map" style={{ "--cols": regions.length || 1 }}>
        {regions.map((r, ri) => (
          <section key={ri} className="map-region" aria-label={r.name}>
            <p className="map-region-name">{r.name}</p>
            <ul className="map-places">
              {(r.places || []).map((pl, i) => (
                <li key={i} className={`map-place role-${pl.role || "neutral"} fig-step`} style={step(n++)}>
                  <span className="map-place-name">{pl.name}</span>
                  {pl.detail && <p className="map-place-detail">{pl.detail}</p>}
                  <Cite text={pl.cite} />
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
      {spec.routes?.length > 0 && (
        <ul className="role-edges map-routes" aria-label="Where the data goes">
          {spec.routes.map((e, i) => (
            <li key={i} className="role-edge map-route fig-step" style={step(n + i)}>
              <span className={`role-chip role-${roleOf[e.from] || "neutral"}`}>{e.from}</span>
              <span className="map-route-label"><span aria-hidden="true">→ </span>{e.label}<span aria-hidden="true"> →</span></span>
              <span className={`role-chip role-${roleOf[e.to] || "neutral"}`}>{e.to}</span>
              <Cite text={e.cite} />
            </li>
          ))}
        </ul>
      )}
    </Frame>
  );
}

/* ── plot: things placed by two questions at once ───────────────────
   Each point is numbered on the chart and explained in the key below it,
   so the chart never depends on labels fitting beside the dots. */
const clamp01 = (v) => Math.min(1, Math.max(0, Number(v) || 0));
function Plot({ spec }) {
  const points = spec.points || [];
  const x = spec.x || {}, y = spec.y || {};
  return (
    <Frame spec={spec} kind="plot">
      <div className="plot-wrap">
        <p className="plot-y-label">{y.label}</p>
        <div className="plot-area-wrap">
          <span className="plot-y-end plot-y-high">{y.high}</span>
          <div className="plot-area" role="img" aria-label={`${points.length} points placed by two questions: ${x.label}; ${y.label}. The key below lists each one.`}>
            {points.map((pt, i) => (
              <span key={i} className={`plot-dot ${pt.ok ? "is-ok" : "is-no"} fig-step`}
                style={{ ...step(i), left: `${clamp01(pt.x) * 100}%`, bottom: `${clamp01(pt.y) * 100}%` }} aria-hidden="true">
                {i + 1}
              </span>
            ))}
          </div>
          <span className="plot-y-end plot-y-low">{y.low}</span>
          <div className="plot-x">
            <span>{x.low}</span>
            <span className="plot-x-label">{x.label}</span>
            <span>{x.high}</span>
          </div>
        </div>
      </div>
      <ol className="plot-key">
        {points.map((pt, i) => (
          <li key={i} className={`plot-key-item ${pt.ok ? "is-ok" : "is-no"} fig-step`} style={step(points.length + i)}>
            <span className="plot-key-n" aria-hidden="true">{i + 1}</span>
            <div>
              <p className="plot-key-label">{pt.label} <span className="plot-key-verdict">{pt.verdict}</span></p>
              {pt.detail && <p className="plot-key-detail">{pt.detail}</p>}
              <Cite text={pt.cite} />
            </div>
          </li>
        ))}
      </ol>
    </Frame>
  );
}

const TYPES = { gate: Gate, stack: Stack, timeline: Timeline, roles: Roles, changes: Changes, actmap: ActMap,
  steps: Steps, checklist: Checklist, scale: Scale, compare: Compare, map: MapFig, plot: Plot };
export const FIGURE_TYPES = Object.keys(TYPES);

export default function Figure({ spec }) {
  const C = TYPES[spec?.type];
  return C ? <C spec={spec} /> : null;
}

/** The role legend, shown once near the top of a module. */
export function RoleLegend() {
  return (
    <ul className="fig-legend" aria-label="What the colours in the figures mean">
      {["principal", "fiduciary", "processor", "manager", "state"].map((r) => (
        <li key={r} className={`role-${r}`}><span className="fig-legend-dot" aria-hidden="true" />{ROLES[r]}</li>
      ))}
    </ul>
  );
}
