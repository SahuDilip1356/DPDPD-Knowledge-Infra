import React from "react";
import { Link } from "react-router-dom";
import { SaralPrivacyLogo } from "../ui/SaralPrivacyLogo";
import "../../styles/home.css";

const SHIKSHA_URL = import.meta.env.VITE_SHIKSHA_URL || "https://dpdpa.shiksha";

/**
 * Chrome for public, indexable pages.
 *
 * Deliberately not AppShell: the sidebar drawer is a working surface for
 * someone already inside the product. A first-time visitor arriving from
 * search needs a way in, not a way around.
 */
export default function PublicShell({ children }) {
  return (
    <div className="pub">
      <a className="skip-link" href="#main">Skip to content</a>

      <header className="pub-header">
        <div className="pub-container pub-header-inner">
          <Link to="/" className="pub-brand" aria-label="dpdpa.wiki home">
            <SaralPrivacyLogo lockup="compact" theme="light" size={30} showTagline={false} />
          </Link>

          <nav className="pub-nav" aria-label="Primary">
            <Link to="/guide">Guides</Link>
            <Link to="/bible">The Act</Link>
            <Link to="/knowledge">Knowledge</Link>
            <Link to="/ask">Ask</Link>
            <a href={SHIKSHA_URL}>Certification&nbsp;↗</a>
          </nav>

          <Link to="/today" className="pub-btn pub-btn-quiet">
            Open the workspace
          </Link>
        </div>
      </header>

      <main id="main">{children}</main>

      <footer className="pub-footer">
        <div className="pub-container pub-footer-inner">
          <div className="pub-footer-brand">
            <SaralPrivacyLogo lockup="compact" theme="dark" size={28} showTagline={false} />
            <p className="pub-footer-note">
              A reference for India's Digital Personal Data Protection Act, 2023.
              Every claim carries its source.
            </p>
          </div>

          <nav className="pub-footer-cols" aria-label="Footer">
            <div>
              <h2 className="pub-footer-heading">Reference</h2>
              <Link to="/guide">Guides</Link>
              <Link to="/bible">The Act</Link>
              <Link to="/knowledge">Definitions</Link>
              <Link to="/changes">Changes</Link>
            </div>
            <div>
              <h2 className="pub-footer-heading">Act on it</h2>
              <Link to="/actions">Templates</Link>
              <Link to="/ask">Ask a question</Link>
              <a href={SHIKSHA_URL}>Certification ↗</a>
            </div>
            <div>
              <h2 className="pub-footer-heading">About</h2>
              <Link to="/infographic">How it is built</Link>
              <Link to="/factory">Sources</Link>
              <a href="mailto:hello@saralprivacy.com">Contact</a>
            </div>
          </nav>
        </div>

        <div className="pub-container pub-footer-base">
          <span>A SaralPrivacy Initiative</span>
          <span className="pub-footer-legal">
            Reference material, not legal advice.
          </span>
        </div>
      </footer>
    </div>
  );
}
