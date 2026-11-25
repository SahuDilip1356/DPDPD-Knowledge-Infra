"""
Official sources: the registry, its authority allowlist, and the fetcher (spec official-sources T2).

An official document enters the law lane only as its own text, fetched from the issuing
authority's site. The registry (sources/official.yaml, committed) names each document and
records two hashes: of the file as fetched, and of the text extracted from it. The file
and the text live in staging/official_sources/<id>/ (gitignored).

Rules this module enforces:
  - a URL must be https on one of its authority's own domains, including after redirects;
  - robots.txt is honoured, with at least one second between requests to a domain;
  - a registered document is never written over: if the file has changed, the change is
    reported and nothing is stored (a new version becomes a new registry entry);
  - text typed from an image-only document needs a named reviewer.

Usage:
  python src/competitive_intel/official_sources.py check
  python src/competitive_intel/official_sources.py fetch [--id ID ...]
"""

import argparse
import hashlib
import io
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from typing import Callable, Dict, List, Optional
from urllib import robotparser
from urllib.parse import urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
REGISTRY_PATH = os.path.join(REPO_ROOT, "sources", "official.yaml")
STORE_ROOT = os.path.join(REPO_ROOT, "staging", "official_sources")

# Each authority's own domains. A host matches a domain exactly or as a subdomain of it.
AUTHORITIES: Dict[str, tuple] = {
    "meity": ("meity.gov.in",),
    "dpb": (),  # the Board's official site is added once it is confirmed (spec, Authority allowlist)
    "egazette": ("egazette.gov.in",),
    "indiacode": ("indiacode.nic.in",),
    "certin": ("cert-in.org.in",),
    "rbi": ("rbi.org.in",),
    "sebi": ("sebi.gov.in",),
    "irdai": ("irdai.gov.in",),
    "sci": ("sci.gov.in",),
}
KINDS = ("notification", "direction", "order", "circular", "judgment", "faq", "act", "rules")
TEXT_METHODS = ("pdf", "html", "manual")
STATUSES = ("active", "superseded")
REQUIRED = ("id", "urn", "authority", "kind", "title", "url", "status")

ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
URN_RE = re.compile(r"^urn:ki:in:dpdp:source:[a-z0-9_-]+$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")

USER_AGENT = "SaralPrivacy-KnowledgeInfra/1.0 (+https://dpdpa.wiki; official-source fetcher)"
MAX_BYTES = 25 * 1024 * 1024
MIN_GAP_SECONDS = 1.0
TIMEOUT = 60


class RegistryError(ValueError):
    pass


def url_allowed(authority: str, url: str) -> bool:
    """https, no credentials, and a host on the authority's own domains."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    host = (parts.hostname or "").lower().rstrip(".")
    if parts.scheme != "https" or not host or parts.username or parts.password:
        return False
    return any(host == d or host.endswith("." + d) for d in AUTHORITIES.get(authority, ()))


def _check_entry(e: Dict, n: int) -> List[str]:
    where = f"entry {n} ({e.get('id', '?')})" if isinstance(e, dict) else f"entry {n}"
    if not isinstance(e, dict):
        return [f"{where}: not a mapping"]
    problems = [f"{where}: missing {k}" for k in REQUIRED if not e.get(k)]
    if problems:
        return problems
    if not ID_RE.match(str(e["id"])):
        problems.append(f"{where}: id must be lowercase letters, digits and hyphens")
    if not URN_RE.match(str(e["urn"])):
        problems.append(f"{where}: urn {e['urn']!r} is not urn:ki:in:dpdp:source:<id>")
    if e["authority"] not in AUTHORITIES:
        problems.append(f"{where}: unknown authority {e['authority']!r}")
    elif not url_allowed(e["authority"], str(e["url"])):
        host = urlsplit(str(e["url"])).hostname
        problems.append(f"{where}: url host {host} is not on the {e['authority']} allowlist "
                        f"{list(AUTHORITIES[e['authority']])}")
    if e["kind"] not in KINDS:
        problems.append(f"{where}: kind {e['kind']!r} is not one of {KINDS}")
    if e["status"] not in STATUSES:
        problems.append(f"{where}: status {e['status']!r} is not one of {STATUSES}")
    if e["status"] == "superseded" and not e.get("superseded_by"):
        problems.append(f"{where}: a superseded source must name superseded_by")
    method = e.get("text_method")
    if method is not None and method not in TEXT_METHODS:
        problems.append(f"{where}: text_method {method!r} is not one of {TEXT_METHODS}")
    if method == "manual" and not e.get("reviewed_by"):
        problems.append(f"{where}: text_method manual needs reviewed_by")
    for key in ("sha256", "text_sha256"):
        if e.get(key) is not None and not HEX64.match(str(e[key])):
            problems.append(f"{where}: {key} is not a 64-character hex digest")
    issued = e.get("issued_on")
    if issued is not None and not isinstance(issued, date) and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(issued)):
        problems.append(f"{where}: issued_on must be YYYY-MM-DD")
    return problems


def load_registry(path: str = REGISTRY_PATH) -> List[Dict]:
    """Every entry, validated. Raises RegistryError naming each bad entry."""
    import yaml
    with open(path, encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []
    if not isinstance(entries, list):
        raise RegistryError(f"{path}: the registry must be a list of entries")
    problems: List[str] = []
    seen_id, seen_urn = set(), set()
    for n, e in enumerate(entries, 1):
        problems += _check_entry(e, n)
        if isinstance(e, dict):
            if e.get("id") in seen_id:
                problems.append(f"entry {n}: duplicate id {e.get('id')}")
            if e.get("urn") in seen_urn:
                problems.append(f"entry {n}: duplicate urn {e.get('urn')}")
            seen_id.add(e.get("id"))
            seen_urn.add(e.get("urn"))
    ids = {e.get("id") for e in entries if isinstance(e, dict)}
    for n, e in enumerate(entries, 1):
        if isinstance(e, dict) and e.get("superseded_by") and e["superseded_by"] not in ids:
            problems.append(f"entry {n}: superseded_by {e['superseded_by']} is not in the registry")
    if problems:
        raise RegistryError("\n".join(problems))
    return entries


# ── text extraction ─────────────────────────────────────────────────────────

class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "template", "svg", "nav", "header", "footer", "head"}
    BLOCK = {"p", "div", "li", "tr", "br", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "td", "th"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth, self.parts = 0, []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.depth += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.depth:
            self.depth -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.depth:
            self.parts.append(data)


def _tidy(text: str) -> str:
    lines = (re.sub(r"[ \t ]+", " ", line).strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line) + "\n"


def html_text(body: bytes, charset: str = "utf-8") -> str:
    parser = _Text()
    parser.feed(body.decode(charset or "utf-8", errors="replace"))
    return _tidy("".join(parser.parts))


def pdf_text(body: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(body))
    return _tidy("\n".join((page.extract_text() or "") for page in reader.pages))


def sha256(data) -> str:
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


# ── fetcher ─────────────────────────────────────────────────────────────────

@dataclass
class Result:
    id: str
    status: str  # stored | unchanged | changed | needs_manual | refused
    detail: str = ""
    sha256: Optional[str] = None
    text_sha256: Optional[str] = None
    text_method: Optional[str] = None


class Fetcher:
    def __init__(self, out_root: str = STORE_ROOT, session=None,
                 clock: Callable[[], float] = time.monotonic, sleep: Callable[[float], None] = time.sleep):
        if session is None:
            import requests
            session = requests.Session()
        session.headers["User-Agent"] = USER_AGENT
        self.out_root, self.session, self.clock, self.sleep = out_root, session, clock, sleep
        self.last: Dict[str, float] = {}
        self.robots: Dict[str, robotparser.RobotFileParser] = {}

    def _get(self, url: str, **kwargs):
        host = urlsplit(url).hostname
        if host in self.last:
            wait = MIN_GAP_SECONDS - (self.clock() - self.last[host])
            if wait > 0:
                self.sleep(wait)
        try:
            return self.session.get(url, timeout=TIMEOUT, **kwargs)
        finally:
            self.last[host] = self.clock()

    def _robots_allow(self, url: str) -> bool:
        parts = urlsplit(url)
        host = parts.hostname
        if host not in self.robots:
            rp = robotparser.RobotFileParser()
            try:
                resp = self._get(f"https://{host}/robots.txt")
                if resp.status_code in (401, 403):
                    rp.disallow_all = True
                elif resp.status_code < 400:
                    rp.parse(resp.text.splitlines())
                else:
                    rp.allow_all = True
            except Exception:
                rp.allow_all = True  # unreachable robots.txt: the standard reading is "no rules"
            self.robots[host] = rp
        return self.robots[host].can_fetch(USER_AGENT, url)

    def _download(self, e: Dict):
        """(body, content_type, problem). The whole redirect chain must stay on the allowlist."""
        resp = self._get(e["url"], stream=True, allow_redirects=True)
        try:
            for hop in [*getattr(resp, "history", []), resp]:
                if not url_allowed(e["authority"], hop.url):
                    return None, None, f"redirected off the allowlist to {urlsplit(hop.url).hostname}"
            if resp.status_code >= 400:
                return None, None, f"HTTP {resp.status_code}"
            declared = resp.headers.get("Content-Length")
            if declared and declared.isdigit() and int(declared) > MAX_BYTES:
                return None, None, "response is over 25 MB"
            body = bytearray()
            for chunk in resp.iter_content(chunk_size=65536):
                body += chunk
                if len(body) > MAX_BYTES:
                    return None, None, "response is over 25 MB"
            return bytes(body), resp.headers.get("Content-Type", ""), None
        finally:
            resp.close()

    def fetch(self, e: Dict) -> Result:
        rid = e["id"]
        if not url_allowed(e.get("authority", ""), e.get("url", "")):
            return Result(rid, "refused", f"{e.get('url')} is not on the {e.get('authority')} allowlist")
        if not self._robots_allow(e["url"]):
            return Result(rid, "refused", "robots.txt disallows this URL")
        body, ctype, problem = self._download(e)
        if problem:
            return Result(rid, "refused", problem)

        file_hash = sha256(body)
        folder = os.path.join(self.out_root, rid)
        existing = [n for n in os.listdir(folder) if n.startswith("source.")] if os.path.isdir(folder) else []
        stored_hash = e.get("sha256")
        if not stored_hash and existing:
            with open(os.path.join(folder, existing[0]), "rb") as f:
                stored_hash = sha256(f.read())
        if stored_hash:
            if stored_hash == file_hash:
                return Result(rid, "unchanged", "", file_hash, e.get("text_sha256"), e.get("text_method"))
            return Result(rid, "changed", f"file hash is now {file_hash}; registered {stored_hash}", file_hash)

        if body.startswith(b"%PDF") or "pdf" in ctype.lower():
            ext, method = "pdf", "pdf"
            try:
                text = pdf_text(body)
            except Exception as exc:  # a malformed PDF is a manual case, never a crash
                text = ""
                problem = f"pdf text extraction failed: {type(exc).__name__}"
        elif "html" in ctype.lower():
            charset = (re.search(r"charset=([\w-]+)", ctype) or [None, "utf-8"])[1]
            ext, method, text = "html", "html", html_text(body, charset)
        else:
            return Result(rid, "refused", f"unsupported content type {ctype!r}")

        os.makedirs(folder, exist_ok=True)
        _write(os.path.join(folder, f"source.{ext}"), body)
        if not text.strip():
            return Result(rid, "needs_manual", problem or "no extractable text; register with text_method: manual",
                          file_hash, None, None)
        _write(os.path.join(folder, "text.txt"), text.encode("utf-8"))
        return Result(rid, "stored", "", file_hash, sha256(text), method)


def _write(path: str, data: bytes) -> None:
    """Write once, never over an existing file."""
    with open(path, "xb") as f:
        f.write(data)


HEADER = ("# Official sources in the law lane (spec specs/official-sources/spec.md).\n"
          "# One entry per document. Hashes are filled by `official_sources.py fetch`; never edit them by hand.\n"
          "# A changed document becomes a new entry; the old one is marked superseded.\n")


def record(path: str, results: List[Result]) -> List[str]:
    """Write fetched hashes into entries that have none yet. Returns the ids updated."""
    import yaml
    entries = load_registry(path)
    by_id = {r.id: r for r in results if r.status in ("stored", "needs_manual")}
    updated = []
    for e in entries:
        r = by_id.get(e["id"])
        if r and not e.get("sha256"):
            e["sha256"] = r.sha256
            if r.text_sha256:
                e["text_sha256"], e["text_method"] = r.text_sha256, r.text_method
            updated.append(e["id"])
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEADER + (yaml.safe_dump(entries, sort_keys=False, allow_unicode=True) if entries else "[]\n"))
    load_registry(path)
    return updated


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="validate the registry")
    f = sub.add_parser("fetch", help="fetch, hash and extract registered documents")
    f.add_argument("--id", action="append", help="only these ids (repeatable)")
    args = ap.parse_args(argv)

    entries = load_registry()
    if args.cmd == "check":
        print(f"registry: {len(entries)} entries conform")
        return 0
    chosen = [e for e in entries if e["status"] == "active" and (not args.id or e["id"] in args.id)]
    fetcher = Fetcher()
    results = [fetcher.fetch(e) for e in chosen]
    for r in results:
        print(f"{r.status:12s} {r.id}  {r.detail}")
    updated = record(REGISTRY_PATH, results)
    print(f"recorded hashes for {len(updated)} entries")
    return 1 if any(r.status == "changed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
