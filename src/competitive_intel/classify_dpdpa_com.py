"""Classify a DPDPA.com URL into one of the nine discovery trays."""

from __future__ import annotations

from urllib.parse import unquote, urlparse


CONTENT_TYPES = (
    "LAW / RULES",
    "INTERPRETATION",
    "FAQ",
    "BLOG",
    "TEMPLATE",
    "CASE LAW",
    "TOOL",
    "COURSE",
    "COMMERCIAL",
)


def normalize_url(url: str) -> str:
    """Collapse apex/www, trailing slashes, and index.html to one key."""
    if not url:
        raise ValueError("url is required")
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"unsupported url scheme: {url}")
    host = parsed.netloc.lower()
    if host == "dpdpa.com":
        host = "www.dpdpa.com"
    path = unquote(parsed.path or "/")
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return f"https://{host}{path}"


def classify_dpdpa_com(url: str, title: str = "") -> str:
    """Return one tray label for a DPDPA.com page."""
    if not url:
        raise ValueError("url is required")
    key = normalize_url(url)
    path = urlparse(key).path.lower()
    title_l = (title or "").lower()

    if "www.prashantmali.com" in path:
        raise ValueError("junk relative link, not a DPDPA.com page")

    if path in {
        "/",
        "/disclaimer.html",
        "/privacypolicy.html",
        "/cookiepolicy.html",
        "/postersofdpdpa.html",
    }:
        return "COMMERCIAL"

    if path.endswith("dpdpa-faq.html") or "faq" in path:
        return "FAQ"

    if path.startswith("/blogs/") or path.endswith("/blog.html"):
        return "BLOG"

    if path.startswith("/dpdpacases/") or path.endswith("/cases.html"):
        return "CASE LAW"

    if path.startswith("/templates/") or "templatesandpolicies" in path:
        return "TEMPLATE"

    if path.startswith("/tools/") or path.endswith("/dpdpa-quiz.html"):
        return "TOOL"

    if any(
        token in path
        for token in (
            "certificate-course",
            "dpdpa-module-",
            "dpdpa-examination",
            "interview-questions",
            "verify-certificate",
            "/ccl.html",
        )
    ):
        return "COURSE"

    if (
        path.startswith("/dpdparules")
        or path.startswith("/schedule/")
        or path.endswith("/mappingofdpdpatodpdprules.html")
        or path.endswith("/dpdpa_enforcement_timeline.html")
    ):
        return "LAW / RULES"

    if path.startswith("/dpdpa2023/") or path.endswith("/theschedule.html"):
        return "INTERPRETATION"

    if "section" in title_l and "interpretation" in title_l:
        return "INTERPRETATION"

    return "COMMERCIAL"


def authority_level_for(content_type: str) -> str:
    """Competitor pages cannot be L1–L3. Those layers are official sources."""
    if content_type not in CONTENT_TYPES:
        raise ValueError(f"unknown content_type: {content_type}")
    if content_type in {"LAW / RULES", "INTERPRETATION", "CASE LAW"}:
        return "L4"
    if content_type == "COMMERCIAL":
        return "L6"
    return "L5"
