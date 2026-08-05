import React from "react";

/**
 * Navigation glyphs.
 *
 * These replace the emoji the nav previously used. Emoji are rendered by the
 * operating system, so the sidebar looked different on every machine and
 * carried a colour palette nobody chose — a poor fit for a reference product
 * whose credibility is the point.
 *
 * Drawn on a 24px grid at a single 1.5 stroke weight, inheriting currentColor
 * so the nav's active/hover states drive them without extra rules.
 *
 * Metaphors are drawn from the subject rather than the usual stock set: the
 * factory is a funnel (documents narrowing into structured objects), the graph
 * is actual connected nodes, and "ask" is a question mark inside the reading
 * surface rather than a brain.
 */
const PATHS = {
  // Today — a dated page, not a calendar block
  today: (
    <>
      <path d="M4 3h13l3 3v15H4z" />
      <path d="M17 3v3h3" />
      <path d="M8 11h8M8 15h5" />
    </>
  ),
  // Certification — a seal with a ribbon
  certification: (
    <>
      <circle cx="12" cy="9" r="5.5" />
      <path d="M8.5 13.5 7 21l5-2.5L17 21l-1.5-7.5" />
    </>
  ),
  // Architecture — stacked layers seen edge-on
  architecture: (
    <>
      <path d="M12 3 3 7.5 12 12l9-4.5z" />
      <path d="M3 12.5 12 17l9-4.5" />
      <path d="M3 17 12 21.5 21 17" />
    </>
  ),
  // Changes — a version fork, one line superseding another
  changes: (
    <>
      <circle cx="6.5" cy="5.5" r="2.5" />
      <circle cx="6.5" cy="18.5" r="2.5" />
      <circle cx="17.5" cy="12" r="2.5" />
      <path d="M6.5 8v8M9 6.5h4a2 2 0 0 1 2 2v1M9 17.5h4a2 2 0 0 0 2-2v-1" />
    </>
  ),
  // Knowledge — connected nodes, the graph itself
  knowledge: (
    <>
      <circle cx="6" cy="7" r="2.5" />
      <circle cx="18" cy="7" r="2.5" />
      <circle cx="12" cy="18" r="2.5" />
      <path d="M8.5 7h7M7.3 9.2l3.4 6.6M16.7 9.2l-3.4 6.6" />
    </>
  ),
  // Actions — a checklist against a clause
  actions: (
    <>
      <path d="M4 4h16v16H4z" />
      <path d="m7.5 9 1.75 1.75L12.5 7.5" />
      <path d="m7.5 15.5 1.75 1.75 3.25-3.25" />
      <path d="M15 10h3M15 16.5h3" />
    </>
  ),
  // Factory — a funnel: documents narrowing into structured objects
  factory: (
    <>
      <path d="M3 4h18l-7 8v7l-4 2v-9z" />
      <path d="M8 8h8" />
    </>
  ),
  // Ask — a question resolved inside the reading surface
  ask: (
    <>
      <path d="M4 5h16v11H9l-5 4z" />
      <path d="M9.75 8.5a2.25 2.25 0 1 1 2.75 2.2v1.3" />
      <path d="M12.5 14.2h.01" />
    </>
  ),
  // Bible — an open reference volume
  bible: (
    <>
      <path d="M12 6.5C10.5 5 8 4.5 4 4.5v13c4 0 6.5.5 8 2 1.5-1.5 4-2 8-2v-13c-4 0-6.5.5-8 2z" />
      <path d="M12 6.5v13" />
    </>
  ),
  // Admin — a ledger under seal
  admin: (
    <>
      <path d="M5 3h11l3 3v15H5z" />
      <path d="M9 12h6M9 16h4" />
      <circle cx="16.5" cy="7.5" r="2.5" />
    </>
  ),
  // Knowledge base hand-off (shiksha → wiki)
  library: (
    <>
      <path d="M4 4h5v16H4zM10 4h4v16h-4z" />
      <path d="m15.5 5.5 3.8 1 3 14.2-3.8-1z" />
    </>
  ),
};

export default function NavIcon({ name, size = 20, className = "", strokeWidth = 1.5 }) {
  const glyph = PATHS[name];
  if (!glyph) return null;

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      focusable="false"
    >
      {glyph}
    </svg>
  );
}
