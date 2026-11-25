"""Official-source registry, allowlist and fetcher (spec official-sources T2; evals E2.1-E2.13).

Offline: documents are built in memory and served by a stub session; the clock is fake.
"""

import hashlib
import os
import sys

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "competitive_intel"))
import official_sources as osrc  # noqa: E402

pytest.importorskip("yaml")


# ── fixtures ────────────────────────────────────────────────────────────────

def pdf_bytes(text=None):
    """A one-page PDF; with text, a Helvetica line pypdf can extract; without, an image-only page."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode() if text else b""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for n, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % n + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)
    return bytes(out)


HTML = (b"<html><head><title>Notice</title><script>var tracker=1;</script><style>p{}</style></head>"
        b"<body><nav>Home | About</nav><main><h1>Notification</h1><p>The Board shall sit in New Delhi.</p>"
        b"</main><footer>Copyright</footer></body></html>")


class Response:
    def __init__(self, url, body=b"", status=200, ctype="application/pdf", history=(), length=None):
        self.url, self.status_code, self.history = url, status, list(history)
        self.headers = {"Content-Type": ctype}
        if length is not None:
            self.headers["Content-Length"] = str(length)
        self._body = body
        self.text = body.decode("latin-1") if isinstance(body, bytes) else body

    @property
    def ok(self):
        return self.status_code < 400

    def iter_content(self, chunk_size=1):
        for i in range(0, len(self._body), chunk_size):
            yield self._body[i:i + chunk_size]

    def close(self):
        pass


class Session:
    """Serves canned responses by URL; robots.txt allows everything unless told otherwise."""

    def __init__(self, routes, robots=""):
        self.routes, self.robots, self.headers, self.calls = routes, robots, {}, []

    def get(self, url, **kwargs):
        self.calls.append(url)
        if url.endswith("/robots.txt"):
            return Response(url, self.robots.encode(), ctype="text/plain")
        return self.routes[url]


class Clock:
    def __init__(self):
        self.now, self.slept = 1000.0, []

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds


def entry(**over):
    base = {
        "id": "gsr-843e-2025",
        "urn": "urn:ki:in:dpdp:source:gsr-843e-2025",
        "authority": "meity",
        "kind": "notification",
        "title": "Commencement of the DPDP Act, 2023",
        "reference": "G.S.R. 843(E)",
        "issued_on": "2025-11-13",
        "url": "https://www.meity.gov.in/static/uploads/2025/11/commencement.pdf",
        "status": "active",
    }
    base.update(over)
    return base


def write_registry(tmp_path, entries):
    import yaml
    path = tmp_path / "official.yaml"
    path.write_text(yaml.safe_dump(entries, sort_keys=False))
    return str(path)


def fetcher(tmp_path, session, clock=None):
    clock = clock or Clock()
    return osrc.Fetcher(out_root=str(tmp_path / "store"), session=session, clock=clock.time, sleep=clock.sleep)


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


# ── registry: E2.1-E2.6 ─────────────────────────────────────────────────────

def test_valid_entry_loads(tmp_path):                                     # E2.1
    assert [e["id"] for e in osrc.load_registry(write_registry(tmp_path, [entry()]))] == ["gsr-843e-2025"]


def test_empty_registry_loads(tmp_path):
    assert osrc.load_registry(write_registry(tmp_path, [])) == []


def test_committed_registry_loads():
    osrc.load_registry(osrc.REGISTRY_PATH)


def test_off_domain_url_is_refused(tmp_path):                             # E2.2
    path = write_registry(tmp_path, [entry(id="rbi-x", urn="urn:ki:in:dpdp:source:rbi-x",
                                           authority="rbi", url="https://example.com/rbi.pdf")])
    with pytest.raises(osrc.RegistryError, match=r"rbi-x.*example\.com"):
        osrc.load_registry(path)


@pytest.mark.parametrize("url,ok", [
    ("https://meity.gov.in.evil.com/a.pdf", False),
    ("https://evilmeity.gov.in/a.pdf", False),
    ("http://www.meity.gov.in/a.pdf", False),
    ("https://user@evil.com/@www.meity.gov.in/a.pdf", False),
    ("https://www.meity.gov.in/a.pdf", True),
    ("https://meity.gov.in/a.pdf", True),
])
def test_lookalike_domains_are_refused(url, ok):                          # E2.3
    assert osrc.url_allowed("meity", url) is ok


def test_unknown_authority_is_refused(tmp_path):                          # E2.4
    with pytest.raises(osrc.RegistryError, match="dpdpa-com"):
        osrc.load_registry(write_registry(tmp_path, [entry(authority="dpdpa-com")]))


def test_board_has_no_domain_until_confirmed():
    assert osrc.AUTHORITIES["dpb"] == ()
    assert osrc.url_allowed("dpb", "https://dpboard.gov.in/order.pdf") is False


def test_manual_text_needs_a_reviewer(tmp_path):                          # E2.5
    with pytest.raises(osrc.RegistryError, match="reviewed_by"):
        osrc.load_registry(write_registry(tmp_path, [entry(text_method="manual")]))
    assert osrc.load_registry(write_registry(tmp_path, [entry(text_method="manual", reviewed_by="Dilip Sahu")]))


@pytest.mark.parametrize("second", [
    entry(urn="urn:ki:in:dpdp:source:other"),                             # same id
    entry(id="other"),                                                    # same urn
])
def test_duplicate_id_or_urn_is_refused(tmp_path, second):                # E2.6
    with pytest.raises(osrc.RegistryError, match="duplicate"):
        osrc.load_registry(write_registry(tmp_path, [entry(), second]))


@pytest.mark.parametrize("field,value", [
    ("urn", "urn:ki:in:dpdp:source:Bad URN"), ("kind", "blog"), ("status", "draft"),
    ("sha256", "nothex"), ("id", "Has Spaces"),
])
def test_malformed_fields_are_refused(tmp_path, field, value):
    with pytest.raises(osrc.RegistryError):
        osrc.load_registry(write_registry(tmp_path, [entry(**{field: value})]))


# ── fetcher: E2.7-E2.13 ─────────────────────────────────────────────────────

def test_fetch_stores_hashes_and_extracts_a_pdf(tmp_path):                # E2.7
    doc = pdf_bytes("Section 2 comes into force on publication.")
    e = entry()
    result = fetcher(tmp_path, Session({e["url"]: Response(e["url"], doc)})).fetch(e)
    folder = tmp_path / "store" / e["id"]
    text = (folder / "text.txt").read_text(encoding="utf-8")
    assert result.status == "stored" and result.text_method == "pdf"
    assert "Section 2 comes into force on publication." in text
    assert (folder / "source.pdf").read_bytes() == doc
    assert result.sha256 == sha(doc) and result.text_sha256 == sha(text)


def test_fetch_extracts_html_without_scripts_or_navigation(tmp_path):    # E2.8
    e = entry(url="https://www.meity.gov.in/notice")
    result = fetcher(tmp_path, Session({e["url"]: Response(e["url"], HTML, ctype="text/html; charset=utf-8")})).fetch(e)
    text = (tmp_path / "store" / e["id"] / "text.txt").read_text(encoding="utf-8")
    assert result.status == "stored" and result.text_method == "html"
    assert (tmp_path / "store" / e["id"] / "source.html").exists()
    assert "The Board shall sit in New Delhi." in text
    assert "tracker" not in text and "Home | About" not in text and "Copyright" not in text


def test_image_only_pdf_needs_manual_text(tmp_path):                      # E2.9
    e = entry()
    result = fetcher(tmp_path, Session({e["url"]: Response(e["url"], pdf_bytes())})).fetch(e)
    assert result.status == "needs_manual" and result.text_sha256 is None
    assert not (tmp_path / "store" / e["id"] / "text.txt").exists()


def test_a_changed_document_never_overwrites_the_registered_one(tmp_path):  # E2.10
    old, new = pdf_bytes("Original text."), pdf_bytes("Amended text.")
    e = entry()
    f = fetcher(tmp_path, Session({e["url"]: Response(e["url"], old)}))
    first = f.fetch(e)
    e.update(sha256=first.sha256, text_sha256=first.text_sha256, text_method=first.text_method)
    folder = tmp_path / "store" / e["id"]
    before = {p.name: p.read_bytes() for p in folder.iterdir()}
    registered = dict(e)
    again = fetcher(tmp_path, Session({e["url"]: Response(e["url"], new)})).fetch(e)
    assert again.status == "changed" and again.sha256 == sha(new)
    assert {p.name: p.read_bytes() for p in folder.iterdir()} == before
    assert e == registered


def test_an_unchanged_document_is_reported_unchanged(tmp_path):
    doc, e = pdf_bytes("Same text."), entry()
    first = fetcher(tmp_path, Session({e["url"]: Response(e["url"], doc)})).fetch(e)
    e.update(sha256=first.sha256)
    assert fetcher(tmp_path, Session({e["url"]: Response(e["url"], doc)})).fetch(e).status == "unchanged"


def test_redirect_off_the_allowlist_stores_nothing(tmp_path):             # E2.11
    e = entry()
    hop = Response(e["url"], status=302)
    final = Response("https://evil.example/fake.pdf", pdf_bytes("Fake."), history=[hop])
    result = fetcher(tmp_path, Session({e["url"]: final})).fetch(e)
    assert result.status == "refused" and "evil.example" in result.detail
    assert not (tmp_path / "store" / e["id"]).exists()


def test_user_agent_names_the_project(tmp_path):                          # E2.12
    session = Session({})
    fetcher(tmp_path, session)
    assert "dpdpa.wiki" in session.headers["User-Agent"]


def test_robots_txt_is_honoured(tmp_path):                                # E2.12
    e = entry()
    session = Session({e["url"]: Response(e["url"], pdf_bytes("x"))}, robots="User-agent: *\nDisallow: /static/\n")
    result = fetcher(tmp_path, session).fetch(e)
    assert result.status == "refused" and "robots" in result.detail
    assert e["url"] not in session.calls


def test_one_second_between_requests_to_a_domain(tmp_path):              # E2.12
    a = entry()
    b = entry(id="gsr-844e-2025", urn="urn:ki:in:dpdp:source:gsr-844e-2025",
              url="https://www.meity.gov.in/static/uploads/2025/11/board.pdf")
    clock = Clock()
    session = Session({a["url"]: Response(a["url"], pdf_bytes("A")), b["url"]: Response(b["url"], pdf_bytes("B"))})
    f = fetcher(tmp_path, session, clock)
    stamps = []
    real_get = session.get
    session.get = lambda url, **kw: (stamps.append(clock.now), real_get(url, **kw))[1]
    f.fetch(a)
    f.fetch(b)
    assert len(stamps) == 3  # robots.txt once per domain, then two documents
    assert all(later - earlier >= 1.0 for earlier, later in zip(stamps, stamps[1:]))


@pytest.mark.parametrize("declared", [True, False])
def test_responses_over_25_mb_are_refused(tmp_path, declared):            # E2.13
    e = entry()
    big = b"%PDF-1.4\n" + b"0" * (osrc.MAX_BYTES + 1)
    resp = Response(e["url"], big, length=len(big) if declared else None)
    result = fetcher(tmp_path, Session({e["url"]: resp})).fetch(e)
    assert result.status == "refused" and "25 MB" in result.detail
    assert not (tmp_path / "store" / e["id"]).exists()


def test_an_off_allowlist_entry_is_not_requested(tmp_path):
    e = entry(url="https://example.com/a.pdf")
    session = Session({})
    assert fetcher(tmp_path, session).fetch(e).status == "refused"
    assert session.calls == []


def test_record_writes_hashes_into_the_registry(tmp_path):                # AC1
    e = entry()
    path = write_registry(tmp_path, [e])
    doc = pdf_bytes("Section 2 comes into force on publication.")
    result = fetcher(tmp_path, Session({e["url"]: Response(e["url"], doc)})).fetch(e)
    osrc.record(path, [result])
    saved = osrc.load_registry(path)[0]
    assert saved["sha256"] == result.sha256 and saved["text_sha256"] == result.text_sha256
    assert saved["text_method"] == "pdf"
