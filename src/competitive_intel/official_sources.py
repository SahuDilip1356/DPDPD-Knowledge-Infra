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
import shutil
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from typing import Callable, Dict, List, Optional
from urllib import robotparser
from urllib.parse import urljoin, urlsplit

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
ROBOTS_MAX_BYTES = 512 * 1024
MAX_PAGES = 2000
MAX_HOPS = 5
MIN_GAP_SECONDS = 1.0
TIMEOUT = 60             # per socket read
DEADLINE_SECONDS = 300   # whole download
REDIRECTS = (301, 302, 303, 307, 308)
CHARSETS = {"utf-8", "utf8", "us-ascii", "ascii", "iso-8859-1", "latin-1", "windows-1252"}


_UMASK = os.umask(0)
os.umask(_UMASK)


class RegistryError(ValueError):
    pass


def url_allowed(authority: str, url: str) -> bool:
    """https, no credentials, and a host on the authority's own domains."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    host = (parts.hostname or "").lower().rstrip(".")
    try:
        port = parts.port
    except ValueError:
        return False
    if parts.scheme != "https" or not host or parts.username or parts.password or port not in (None, 443):
        return False
    return any(host == d or host.endswith("." + d) for d in AUTHORITIES.get(authority, ()))


def _check_entry(e: Dict, n: int) -> List[str]:
    where = f"entry {n} ({e.get('id', '?')})" if isinstance(e, dict) else f"entry {n}"
    if not isinstance(e, dict):
        return [f"{where}: not a mapping"]
    problems = [f"{where}: missing {k}" for k in REQUIRED if not e.get(k)]
    if problems:
        return problems
    if not ID_RE.fullmatch(str(e["id"])):
        problems.append(f"{where}: id must be lowercase letters, digits and hyphens")
    if not URN_RE.fullmatch(str(e["urn"])):
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
        if e.get(key) is not None and not HEX64.fullmatch(str(e[key])):
            problems.append(f"{where}: {key} is not a 64-character hex digest")
    issued = e.get("issued_on")
    if issued is not None and not isinstance(issued, date) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(issued)):
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
    """Extracted text; empty when the PDF is over the page cap (it then needs manual text)."""
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(body))
    if len(reader.pages) > MAX_PAGES:
        raise ValueError(f"pdf has {len(reader.pages)} pages, over the {MAX_PAGES}-page cap")
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

    def _get(self, url: str):
        """One request, never following redirects, at least MIN_GAP_SECONDS after the last one to this host."""
        host = urlsplit(url).hostname
        if host in self.last:
            wait = MIN_GAP_SECONDS - (self.clock() - self.last[host])
            if wait > 0:
                self.sleep(wait)
        try:
            return self.session.get(url, timeout=TIMEOUT, stream=True, allow_redirects=False)
        finally:
            self.last[host] = self.clock()

    def _follow(self, authority: str, url: str):
        """(response, problem). Each hop is checked against the allowlist before it is requested."""
        for _ in range(MAX_HOPS + 1):
            if not url_allowed(authority, url):
                return None, f"{url} is off the {authority} allowlist"
            resp = self._get(url)
            if resp.status_code not in REDIRECTS:
                return resp, None
            location = resp.headers.get("Location")
            resp.close()
            if not location:
                return None, f"HTTP {resp.status_code} without a Location"
            url = urljoin(url, location)
        return None, f"more than {MAX_HOPS} redirects"

    def _read(self, resp, cap: int = MAX_BYTES):
        """(body, problem), within the size cap and the whole-download deadline."""
        try:
            declared = resp.headers.get("Content-Length")
            if declared and declared.isdigit() and int(declared) > cap:
                return None, f"response is over {cap // (1024 * 1024) or cap} {'MB' if cap >= 1024 * 1024 else 'bytes'}"
            deadline = self.clock() + DEADLINE_SECONDS
            late = f"download took longer than {DEADLINE_SECONDS} s"
            expired = threading.Event()
            timer = threading.Timer(DEADLINE_SECONDS, lambda: (expired.set(), _abort(resp)))
            timer.daemon = True
            timer.start()
            body = bytearray()
            try:
                for chunk in resp.iter_content(chunk_size=8192):
                    body += chunk
                    if len(body) > cap:
                        return None, f"response is over {cap // (1024 * 1024) or cap} {'MB' if cap >= 1024 * 1024 else 'bytes'}"
                    if expired.is_set() or self.clock() > deadline:
                        return None, late
            except Exception:
                if expired.is_set():
                    return None, late
                raise
            finally:
                timer.cancel()
            if expired.is_set():
                return None, late
            return bytes(body), None
        finally:
            resp.close()

    def _robots_allow(self, authority: str, url: str) -> bool:
        host = urlsplit(url).hostname
        if host not in self.robots:
            rp = robotparser.RobotFileParser()
            rp.disallow_all = True  # unreachable or 5xx: assume complete disallow (RFC 9309, 2.3.1.4)
            try:
                resp, problem = self._follow(authority, f"https://{host}/robots.txt")
                if resp is None:
                    # robots.txt redirects off the allowlist: we cannot read it, so it counts as unavailable
                    rp.disallow_all, rp.allow_all = False, True
                elif resp.status_code in (401, 403) or resp.status_code >= 500:
                    resp.close()
                elif resp.status_code < 400:
                    body, problem = self._read(resp, ROBOTS_MAX_BYTES)
                    if body is not None:
                        rp.disallow_all = False
                        rp.parse(body.decode("utf-8", errors="replace").splitlines())
                else:  # 4xx: unavailable, no rules apply
                    resp.close()
                    rp.disallow_all, rp.allow_all = False, True
            except Exception:
                pass
            self.robots[host] = rp
        return self.robots[host].can_fetch(USER_AGENT, url)

    def _extract(self, body: bytes, ctype: str):
        """(ext, method, text, problem); ext None means refused."""
        if body.startswith(b"%PDF") or "pdf" in ctype.lower():
            try:
                return "pdf", "pdf", pdf_text(body), None
            except Exception as exc:  # malformed or oversized: a manual case, never a crash
                return "pdf", "pdf", "", f"pdf text not extracted: {exc if isinstance(exc, ValueError) else type(exc).__name__}"
        if "html" in ctype.lower():
            found = re.search(r"charset=([\w-]+)", ctype, re.I)
            charset = (found.group(1) if found else "utf-8").lower()
            if charset not in CHARSETS:
                return None, None, "", f"charset {charset!r} is not accepted"
            return "html", "html", html_text(body, charset), None
        return None, None, "", f"unsupported content type {ctype!r}"

    def fetch(self, e: Dict) -> Result:
        rid = str(e.get("id"))
        problems = _check_entry(e, 0)
        if problems:
            return Result(rid, "refused", "; ".join(problems))
        if not self._robots_allow(e["authority"], e["url"]):
            return Result(rid, "refused", "robots.txt disallows this URL")
        resp, problem = self._follow(e["authority"], e["url"])
        if problem:
            return Result(rid, "refused", problem)
        if resp.status_code >= 400:
            resp.close()
            return Result(rid, "refused", f"HTTP {resp.status_code}")
        ctype = resp.headers.get("Content-Type", "")
        body, problem = self._read(resp)
        if problem:
            return Result(rid, "refused", problem)

        file_hash = sha256(body)
        folder = os.path.join(self.out_root, rid)
        names = os.listdir(folder) if os.path.isdir(folder) else []
        sources = [n for n in names if n.startswith("source.")]
        if names and not sources:
            return Result(rid, "refused", f"incomplete folder {folder}: it has no source file; remove it and retry")
        stored_hash = e.get("sha256")
        if not stored_hash and sources:
            with open(os.path.join(folder, sources[0]), "rb") as f:
                stored_hash = sha256(f.read())

        if stored_hash and stored_hash != file_hash:
            return Result(rid, "changed", f"file hash is now {file_hash}; registered {stored_hash}", file_hash)

        ext, method, text, problem = self._extract(body, ctype)
        if ext is None:
            return Result(rid, "refused", problem)

        if stored_hash:  # unchanged: check what is on disk, and restore what is missing
            text_path, want = os.path.join(folder, "text.txt"), e.get("text_sha256")
            if os.path.exists(text_path):
                with open(text_path, encoding="utf-8") as f:
                    on_disk = sha256(f.read())
                # Registered hash if there is one; otherwise a fresh extraction is the reference, so a
                # hand-edited text.txt is never recorded as machine-extracted law.
                expected = want or (sha256(text) if text.strip() and e.get("text_method") != "manual" else None)
                if expected and on_disk != expected:
                    return Result(rid, "changed", "text.txt on disk does not match the extracted text", file_hash)
                if not expected and not want and e.get("text_method") != "manual":
                    return Result(rid, "unchanged", "text.txt kept, not verifiable without a registered hash",
                                  file_hash, None, None)
            missing = {} if sources else {f"source.{ext}": body}
            if not os.path.exists(text_path) and want:
                if sha256(text) != want:
                    return Result(rid, "changed", "extracted text no longer matches text_sha256", file_hash)
                missing["text.txt"] = text.encode("utf-8")
            if missing:
                _store(folder, missing, {})
            have = want
            if not have and os.path.exists(text_path):
                with open(text_path, encoding="utf-8") as f:
                    have = sha256(f.read())
            return Result(rid, "unchanged", "", file_hash, have, e.get("text_method") or (method if have else None))

        if not text.strip():
            _store(folder, {f"source.{ext}": body}, {})
            return Result(rid, "needs_manual", problem or "no extractable text; register with text_method: manual",
                          file_hash, None, None)
        _store(folder, {f"source.{ext}": body, "text.txt": text.encode("utf-8")}, {})
        return Result(rid, "stored", "", file_hash, sha256(text), method)


def _abort(resp) -> None:
    """Stop a download from another thread. Closing the response does not wake a read blocked on the
    socket, so shut the socket down first (requests -> urllib3 -> http.client -> socket)."""
    import socket as _socket
    sock = None
    try:
        sock = resp.raw._fp.fp.raw._sock
    except AttributeError:
        pass
    if sock is not None:
        try:
            sock.shutdown(_socket.SHUT_RDWR)
        except OSError:
            pass
    try:
        resp.close()
    except Exception:
        pass


def _store(folder: str, fresh: Dict[str, bytes], extra: Dict[str, bytes]) -> None:
    """New folder: write into a temporary folder, then rename it into place, so a failed run leaves nothing
    half-written. Existing folder: add only files that are missing, never writing over one."""
    files = {**fresh, **extra}
    if not os.path.isdir(folder):
        parent = os.path.dirname(folder)
        os.makedirs(parent, exist_ok=True)
        tmp = tempfile.mkdtemp(prefix=f".{os.path.basename(folder)}.partial-", dir=parent)
        os.chmod(tmp, 0o777 & ~_UMASK)  # mkdtemp makes 0700; keep the folder as readable as any other
        try:
            for name, data in files.items():
                _write(os.path.join(tmp, name), data)
            os.rename(tmp, folder)
        except BaseException:
            shutil.rmtree(tmp, ignore_errors=True)
            raise
        return
    for name, data in files.items():
        _write(os.path.join(folder, name), data)


def _write(path: str, data: bytes) -> None:
    """Write once, never over an existing file."""
    with open(path, "xb") as f:
        f.write(data)


HEADER = ("# Official sources in the law lane (spec specs/official-sources/spec.md).\n"
          "# One entry per document. Hashes are filled by `official_sources.py fetch`; never edit them by hand.\n"
          "# A changed document becomes a new entry; the old one is marked superseded.\n")


def record(path: str, results: List[Result]) -> List[str]:
    """Write fetched hashes into entries that have none yet, and never over existing ones.
    The file is rewritten only when something changed, via a validated temporary file."""
    import yaml
    entries = load_registry(path)
    by_id = {r.id: r for r in results if r.sha256 and r.status in ("stored", "needs_manual", "unchanged")}
    updated = []
    for e in entries:
        r = by_id.get(e["id"])
        if r and not e.get("sha256"):
            e["sha256"] = r.sha256
            if r.text_sha256:
                e["text_sha256"], e["text_method"] = r.text_sha256, r.text_method
            updated.append(e["id"])
    if not updated:
        return []
    tmp = f"{path}.tmp-{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(HEADER + yaml.safe_dump(entries, sort_keys=False, allow_unicode=True))
    try:
        load_registry(tmp)
    except Exception:
        os.remove(tmp)
        raise
    os.replace(tmp, path)
    return updated


def run(path: str = REGISTRY_PATH, fetcher: Optional["Fetcher"] = None, ids: Optional[List[str]] = None):
    """Fetch every active entry (or the given ids); one failure never stops the rest. Returns (results, updated)."""
    fetcher = fetcher or Fetcher()
    results = []
    for e in load_registry(path):
        if e["status"] != "active" or (ids and e["id"] not in ids):
            continue
        try:
            results.append(fetcher.fetch(e))
        except Exception as exc:
            results.append(Result(e["id"], "refused", f"error: {type(exc).__name__}: {str(exc)[:160]}"))
    return results, record(path, results)


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
    results, updated = run(REGISTRY_PATH, ids=args.id)
    for r in results:
        print(f"{r.status:12s} {r.id}  {r.detail}")
    print(f"recorded hashes for {len(updated)} entries")
    return 1 if any(r.status == "changed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
