import React, { useState } from "react";
import { Link } from "react-router-dom";
import { SaralPrivacyLogo } from "../ui/SaralPrivacyLogo";
import "../../styles/home.css";

const SHIKSHA_URL = import.meta.env.VITE_SHIKSHA_URL || "https://dpdpa.shiksha";
const SARAL_ASSESSMENT = "https://saralprivacy.com/assessment";

/**
 * Public navigation, in one place.
 *
 * Only public, prerendered destinations belong here. The workspace (Today,
 * Knowledge, Ask, Factory, Admin) is a working surface for the founder and is
 * reached by its own URL, never from public chrome — see spec AC9.
 *
 * Learn and Tools join this list when the course modules and decision aids
 * ship (plan T14, T16); a link to a page that does not exist yet is worse
 * than no link.
 */
export const PUBLIC_NAV = [
  { to: "/act", label: "The Act" },
  { to: "/rules", label: "The Rules" },
  { to: "/glossary", label: "Glossary" },
  { to: "/guide", label: "Guides" }
];

export default function PublicShell({ children }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="pub">
      <a className="skip-link" href="#main">Skip to content</a>

      <header className="pub-header">
        <div className="pub-container pub-header-inner">
          <Link to="/" className="pub-brand" aria-label="dpdpa.wiki home">
            <SaralPrivacyLogo lockup="compact" theme="light" size={30} showTagline={false} />
          </Link>

          <button
            type="button"
            className="pub-menu-btn"
            aria-expanded={open}
            aria-controls="pub-nav"
            onClick={() => setOpen((v) => !v)}
          >
            <span className="pub-menu-icon" aria-hidden="true">
              <span /><span /><span />
            </span>
            <span>{open ? "Close" : "Menu"}</span>
          </button>

          <nav id="pub-nav" className={`pub-nav${open ? " is-open" : ""}`} aria-label="Primary">
            {PUBLIC_NAV.map((item) => (
              <Link key={item.to} to={item.to} onClick={() => setOpen(false)}>{item.label}</Link>
            ))}
            <a href={SHIKSHA_URL}>Certification&nbsp;↗</a>
            <a href={SARAL_ASSESSMENT} className="pub-nav-cta">Check your readiness&nbsp;↗</a>
          </nav>
        </div>
      </header>

      <main id="main">{children}</main>

      <footer className="pub-footer">
        <div className="pub-container pub-footer-inner">
          <div className="pub-footer-brand">
            <SaralPrivacyLogo lockup="compact" theme="dark" size={28} showTagline={false} />
            <p className="pub-footer-note">
              India's Digital Personal Data Protection Act, 2023 and the DPDP Rules, 2025,
              in the gazette's own words. Every statement carries its provision.
            </p>
          </div>

          <nav className="pub-footer-cols" aria-label="Footer">
            <div>
              <h2 className="pub-footer-heading">The law</h2>
              <Link to="/act">The Act</Link>
              <Link to="/act/schedule">Penalties</Link>
              <Link to="/rules">The Rules</Link>
              <Link to="/glossary">Glossary</Link>
            </div>
            <div>
              <h2 className="pub-footer-heading">Learn</h2>
              <Link to="/guide">Guides</Link>
              <a href={SHIKSHA_URL}>Certification ↗</a>
            </div>
            <div>
              <h2 className="pub-footer-heading">Act on it</h2>
              <a href={SARAL_ASSESSMENT}>Readiness assessment ↗</a>
              <a href="https://saralprivacy.com/tools/dpdpa-privacy-notice-generator">Privacy notice generator ↗</a>
              <a href="mailto:hello@saralprivacy.com">Contact</a>
            </div>
          </nav>
        </div>

        <div className="pub-container pub-footer-base">
          <span>A SaralPrivacy initiative</span>
          <span className="pub-footer-legal">
            Reference material, not legal advice.
          </span>
        </div>
      </footer>
    </div>
  );
}
