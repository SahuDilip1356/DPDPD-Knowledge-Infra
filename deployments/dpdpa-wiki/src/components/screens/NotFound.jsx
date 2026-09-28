import React from "react";
import { Link } from "react-router-dom";
import PublicShell from "../marketing/PublicShell";

/**
 * A real 404. Unknown URLs used to land on the home page, which told search
 * engines that every broken link was a duplicate of the home page.
 */
export default function NotFound() {
  return (
    <PublicShell>
      <section className="pub-container" style={{ paddingBlock: "clamp(48px, 8vw, 96px)", maxWidth: 720 }}>
        <p className="hero-eyebrow" style={{ color: "var(--saffron)" }}>404</p>
        <h1 style={{ fontFamily: "var(--font-serif)", fontSize: "clamp(28px, 4vw, 40px)", color: "var(--ink)", margin: "8px 0 16px" }}>
          There is no page at this address.
        </h1>
        <p>The law itself is all here. Start from one of these:</p>
        <ul style={{ lineHeight: 2.2, paddingInlineStart: 20 }}>
          <li><Link to="/act">The Digital Personal Data Protection Act, 2023</Link></li>
          <li><Link to="/rules">The DPDP Rules, 2025</Link></li>
          <li><Link to="/glossary">Glossary of defined terms</Link></li>
          <li><Link to="/">Home</Link></li>
        </ul>
      </section>
    </PublicShell>
  );
}
