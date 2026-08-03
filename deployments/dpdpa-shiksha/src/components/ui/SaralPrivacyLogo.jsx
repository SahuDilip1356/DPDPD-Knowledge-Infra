import React from "react";

/**
 * SaralPrivacy Knowledge Mark — Official Brand Icon
 * Geodesic network graph with central "S" (Green) and "P" (Navy) authority hub.
 */
export function SaralPrivacyMark({ size = 36, className = "", theme = "light" }) {
  const isDark = theme === "dark";
  
  // Official Brand Sector Colors (matching uploaded logo image)
  const orange = "#F97316";
  const blue = "#2563EB";
  const darkNavy = isDark ? "#E2E8F0" : "#0F172A";
  const green = isDark ? "#22C55E" : "#138808";
  const teal = "#0D9488";

  const outerRingColor = isDark ? "rgba(255, 255, 255, 0.7)" : "#0F172A";
  const centerBg = "#FFFFFF";

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`saral-privacy-mark ${className}`}
      aria-label="SaralPrivacy Knowledge Mark"
    >
      {/* ── Outer Circular Geodesic Ring ──────────────────────────── */}
      <circle cx="60" cy="60" r="46" stroke={outerRingColor} strokeWidth="2.5" />
      
      {/* ── Sector Connecting Web Lines ───────────────────────────── */}
      {/* Left Sector Lines (Orange) */}
      <path d="M14 60 L20 37 M14 60 L20 83 M14 60 L38 52 M20 83 L38 52" stroke={orange} strokeWidth="1.4" />
      
      {/* Top Sector Lines (Royal Blue) */}
      <path d="M20 37 L37 20 M37 20 L60 14 M60 14 L83 20 M37 20 L44 38 M60 14 L44 38 M60 14 L76 38" stroke={blue} strokeWidth="1.4" />

      {/* Right Sector Lines (Green / Teal) */}
      <path d="M83 20 L100 37 M100 37 L106 60 M106 60 L100 83 M100 37 L82 52 M106 60 L82 52 M100 83 L82 52" stroke={green} strokeWidth="1.4" />

      {/* Bottom Sector Lines (Navy) */}
      <path d="M100 83 L83 100 M83 100 L60 106 M60 106 L37 100 M37 100 L20 83 M60 106 L72 80 M60 106 L48 80 M83 100 L72 80 M37 100 L48 80" stroke={darkNavy} strokeWidth="1.4" />

      {/* Inner Concentric Mesh Web Lines */}
      <path d="M44 38 L76 38 M76 38 L82 52 M82 52 L72 80 M72 80 L48 80 M48 80 L38 52 M38 52 L44 38" stroke={outerRingColor} strokeWidth="1.2" opacity="0.6" />

      {/* ── Outer Ring Nodes (12 Quadrant Nodes) ────────────────────── */}
      {/* 12 o'clock */}
      <circle cx="60" cy="14" r="5" fill={blue} />
      {/* 1 o'clock */}
      <circle cx="83" cy="20" r="4" fill={blue} />
      {/* 2 o'clock */}
      <circle cx="100" cy="37" r="5" fill={teal} />
      {/* 3 o'clock */}
      <circle cx="106" cy="60" r="5" fill={green} />
      {/* 4 o'clock */}
      <circle cx="100" cy="83" r="5" fill={green} />
      {/* 5 o'clock */}
      <circle cx="83" cy="100" r="4.5" fill={darkNavy} />
      {/* 6 o'clock */}
      <circle cx="60" cy="106" r="5.5" fill={darkNavy} />
      {/* 7 o'clock */}
      <circle cx="37" cy="100" r="4.5" fill={blue} />
      {/* 8 o'clock */}
      <circle cx="20" cy="83" r="4" fill={orange} />
      {/* 9 o'clock */}
      <circle cx="14" cy="60" r="5.5" fill={orange} />
      {/* 10 o'clock */}
      <circle cx="20" cy="37" r="5" fill={blue} />
      {/* 11 o'clock */}
      <circle cx="37" cy="20" r="4" fill={blue} />

      {/* ── Inner Ring Nodes ──────────────────────────────────────── */}
      <circle cx="44" cy="38" r="4" fill={blue} />
      <circle cx="76" cy="38" r="4" fill={darkNavy} />
      <circle cx="38" cy="52" r="4" fill={blue} />
      <circle cx="82" cy="52" r="4" fill={green} />
      <circle cx="72" cy="80" r="4" fill={darkNavy} />
      <circle cx="48" cy="80" r="4" fill={darkNavy} />

      {/* ── Central "SP" Hub (White Circle with S:Green, P:Navy) ───── */}
      <circle cx="60" cy="60" r="20" fill={centerBg} stroke={darkNavy} strokeWidth="2.2" />
      <text
        x="60"
        y="67"
        textAnchor="middle"
        fontSize="21"
        fontWeight="800"
        fontFamily="'Inter', 'Space Grotesk', system-ui, -apple-system, sans-serif"
        letterSpacing="-0.5px"
      >
        <tspan fill="#138808">S</tspan>
        <tspan fill="#0F172A">P</tspan>
      </text>
    </svg>
  );
}

/**
 * SaralPrivacy Knowledge Infra — Complete Brand Lockup
 */
export function SaralPrivacyLogo({
  lockup = "horizontal", // "horizontal" | "stacked" | "compact" | "wordmark"
  theme = "light",       // "light" | "dark"
  size = 40,
  showTagline = true,
  className = "",
  onClick
}) {
  const isDark = theme === "dark";
  const saralColor = isDark ? "#FFFFFF" : "#14213D";
  const privacyColor = isDark ? "#22C55E" : "#138808"; // High-contrast green on dark background!
  const infraColor = isDark ? "#60A5FA" : "#1A4FA3";
  const taglineColor = isDark ? "rgba(255,255,255,0.75)" : "#4B5563";

  if (lockup === "compact") {
    return (
      <div 
        className={`saral-logo-lockup lockup-compact ${className}`} 
        style={{ display: "flex", alignItems: "center", gap: "10px", cursor: onClick ? "pointer" : "default" }}
        onClick={onClick}
      >
        <SaralPrivacyMark size={size} theme={theme} />
        <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.1 }}>
          <div style={{ fontSize: `${size * 0.42}px`, fontWeight: 700, fontFamily: "var(--font-sans)" }}>
            <span style={{ color: saralColor }}>Saral</span>
            <span style={{ color: privacyColor }}>Privacy</span>
          </div>
          <div style={{ fontSize: `${size * 0.32}px`, fontWeight: 600, color: infraColor, letterSpacing: "0.02em" }}>
            Knowledge Infra
          </div>
        </div>
      </div>
    );
  }

  if (lockup === "wordmark") {
    return (
      <div className={`saral-logo-lockup lockup-wordmark ${className}`} style={{ display: "flex", flexDirection: "column", lineHeight: 1.1 }}>
        <div style={{ fontSize: `${size * 0.65}px`, fontWeight: 700, fontFamily: "var(--font-sans)" }}>
          <span style={{ color: saralColor }}>Saral</span>
          <span style={{ color: privacyColor }}>Privacy</span>
        </div>
        <div style={{ fontSize: `${size * 0.48}px`, fontWeight: 600, color: infraColor, marginTop: "2px" }}>
          Knowledge Infra
        </div>
      </div>
    );
  }

  if (lockup === "stacked") {
    return (
      <div 
        className={`saral-logo-lockup lockup-stacked ${className}`}
        style={{ display: "flex", flexDirection: "column", alignItems: "center", textAlignment: "center", gap: "8px", cursor: onClick ? "pointer" : "default" }}
        onClick={onClick}
      >
        <SaralPrivacyMark size={size * 1.5} theme={theme} />
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: `${size * 0.5}px`, fontWeight: 700, fontFamily: "var(--font-sans)", lineHeight: 1.1 }}>
            <span style={{ color: saralColor }}>Saral</span>
            <span style={{ color: privacyColor }}>Privacy</span>
          </div>
          <div style={{ fontSize: `${size * 0.38}px`, fontWeight: 600, color: infraColor, marginTop: "2px" }}>
            Knowledge Infra
          </div>
          {showTagline && (
            <div style={{ fontSize: `${size * 0.24}px`, color: taglineColor, marginTop: "4px", fontWeight: 500 }}>
              India's Living Privacy Knowledge Infrastructure
            </div>
          )}
        </div>
      </div>
    );
  }

  // Default: Horizontal Lockup
  return (
    <div
      className={`saral-logo-lockup lockup-horizontal ${className}`}
      style={{ display: "flex", alignItems: "center", gap: `${Math.max(8, size * 0.3)}px`, cursor: onClick ? "pointer" : "default" }}
      onClick={onClick}
    >
      <SaralPrivacyMark size={size} theme={theme} />
      <div style={{ display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <div style={{ fontSize: `${size * 0.44}px`, fontWeight: 700, fontFamily: "var(--font-sans)", lineHeight: 1.15, display: "flex", alignItems: "baseline", gap: "2px" }}>
          <span style={{ color: saralColor, fontWeight: 800 }}>Saral</span>
          <span style={{ color: privacyColor, fontWeight: 800 }}>Privacy</span>
        </div>
        <div style={{ fontSize: `${size * 0.35}px`, fontWeight: 600, color: infraColor, marginTop: "1px", letterSpacing: "0.01em" }}>
          Knowledge Infra
        </div>
        {showTagline && (
          <div 
            style={{ 
              fontSize: `${Math.max(10, size * 0.24)}px`, 
              color: taglineColor, 
              marginTop: "3px", 
              fontWeight: 500,
              display: "flex",
              alignItems: "center",
              gap: "6px"
            }}
          >
            <span>India's Living Privacy Knowledge Infrastructure</span>
            <span style={{ height: "2px", width: "24px", background: "linear-gradient(90deg, #1A4FA3 0%, #FF9933 100%)", borderRadius: "1px", display: "inline-block" }}></span>
          </div>
        )}
      </div>
    </div>
  );
}

export default SaralPrivacyLogo;
