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
    def __init__(self, url, body=b"", status=200, ctype="application/pdf", history=(), length=None,
                 location=None, on_chunk=None):
        self.url, self.status_code, self.history = url, status, list(history)
        self.headers = {"Content-Type": ctype}
        if length is not None:
            self.headers["Content-Length"] = str(length)
        if location is not None:
            self.headers["Location"] = location
        self.on_chunk = on_chunk
        self._body = body
        self.text = body.decode("latin-1") if isinstance(body, bytes) else body

    @property
    def ok(self):
        return self.status_code < 400

    def iter_content(self, chunk_size=1):
        for i in range(0, len(self._body), chunk_size):
            if self.on_chunk:
                self.on_chunk()
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


@pytest.mark.parametrize("location", [
    "https://evil.example/fake.pdf",
    "http://169.254.169.254/latest/meta-data/",
    "http://www.meity.gov.in/static/plain.pdf",          # same host, but not https
    "https://www.meity.gov.in:8443/static/a.pdf",       # an unusual port
])
def test_redirect_off_the_allowlist_is_never_requested(tmp_path, location):  # E2.11, security F1
    e = entry()
    evil = Response(location, pdf_bytes("Fake."))
    session = Session({e["url"]: Response(e["url"], status=302, location=location), location: evil})
    result = fetcher(tmp_path, session).fetch(e)
    assert result.status == "refused" and "allowlist" in result.detail
    assert location not in session.calls
    assert not (tmp_path / "store" / e["id"]).exists()


def test_a_redirect_within_the_allowlist_is_followed(tmp_path):
    e = entry()
    target = "https://www.meity.gov.in/static/uploads/2025/11/moved.pdf"
    session = Session({e["url"]: Response(e["url"], status=301, location="/static/uploads/2025/11/moved.pdf"),
                       target: Response(target, pdf_bytes("Moved text."))})
    assert fetcher(tmp_path, session).fetch(e).status == "stored"


def test_redirect_loops_are_cut_off(tmp_path):
    e = entry()
    session = Session({e["url"]: Response(e["url"], status=302, location=e["url"])})
    result = fetcher(tmp_path, session).fetch(e)
    assert result.status == "refused" and "redirects" in result.detail


def test_robots_redirect_off_the_allowlist_is_not_followed(tmp_path):     # security F1 variant
    e = entry()
    robots = "https://www.meity.gov.in/robots.txt"
    session = Session({e["url"]: Response(e["url"], pdf_bytes("x")),
                       robots: Response(robots, status=302, location="https://evil.example/huge")})
    session.get = lambda url, **kw: (session.calls.append(url), session.routes[url])[1]
    assert fetcher(tmp_path, session).fetch(e).status == "stored"
    assert "https://evil.example/huge" not in session.calls


def test_a_slow_download_is_cut_off(tmp_path):                            # security F3
    e = entry()
    clock = Clock()
    slow = Response(e["url"], pdf_bytes("x") + b" " * 200_000, on_chunk=lambda: setattr(clock, "now", clock.now + 120))
    result = fetcher(tmp_path, Session({e["url"]: slow}), clock).fetch(e)
    assert result.status == "refused" and "took longer" in result.detail


@pytest.mark.parametrize("ctype", ["text/html; charset=utf-7", "text/html; charset=no-such-codec"])
def test_an_unexpected_charset_is_refused(tmp_path, ctype):               # security F4
    e = entry(url="https://www.meity.gov.in/notice")
    result = fetcher(tmp_path, Session({e["url"]: Response(e["url"], HTML, ctype=ctype)})).fetch(e)
    assert result.status == "refused" and "charset" in result.detail


def test_an_id_with_a_trailing_newline_is_refused(tmp_path):              # security F5
    with pytest.raises(osrc.RegistryError):
        osrc.load_registry(write_registry(tmp_path, [entry(id="abc\n")]))
    assert fetcher(tmp_path, Session({})).fetch(entry(id="abc\n")).status == "refused"


def test_a_fresh_clone_gets_its_files_back(tmp_path):                     # security A1
    doc, e = pdf_bytes("Section 2 comes into force."), entry()
    first = fetcher(tmp_path / "a", Session({e["url"]: Response(e["url"], doc)})).fetch(e)
    e.update(sha256=first.sha256, text_sha256=first.text_sha256, text_method="pdf")
    again = fetcher(tmp_path / "b", Session({e["url"]: Response(e["url"], doc)})).fetch(e)
    folder = tmp_path / "b" / "store" / e["id"]
    assert again.status == "unchanged"
    assert sha((folder / "text.txt").read_text(encoding="utf-8")) == e["text_sha256"]


def test_an_edited_text_file_is_reported(tmp_path):                       # security A1
    doc, e = pdf_bytes("Section 2 comes into force."), entry()
    first = fetcher(tmp_path, Session({e["url"]: Response(e["url"], doc)})).fetch(e)
    e.update(sha256=first.sha256, text_sha256=first.text_sha256, text_method="pdf")
    text = tmp_path / "store" / e["id"] / "text.txt"
    text.write_text("Section 2 never comes into force.\n", encoding="utf-8")
    result = fetcher(tmp_path, Session({e["url"]: Response(e["url"], doc)})).fetch(e)
    assert result.status == "changed" and "text.txt" in result.detail


def test_a_half_written_folder_is_reported_not_crashed(tmp_path):         # security A2
    e = entry()
    folder = tmp_path / "store" / e["id"]
    folder.mkdir(parents=True)
    (folder / "text.txt").write_text("left over", encoding="utf-8")
    result = fetcher(tmp_path, Session({e["url"]: Response(e["url"], pdf_bytes("x"))})).fetch(e)
    assert result.status == "refused" and "incomplete" in result.detail


def test_a_pdf_over_the_page_cap_needs_manual_text(tmp_path, monkeypatch):  # security F2
    monkeypatch.setattr(osrc, "MAX_PAGES", 0)
    e = entry()
    result = fetcher(tmp_path, Session({e["url"]: Response(e["url"], pdf_bytes("x"))})).fetch(e)
    assert result.status == "needs_manual" and "pages" in result.detail


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


# ── code review round 1 ─────────────────────────────────────────────────────

class Boom(Session):
    def get(self, url, **kwargs):
        if url.endswith("/robots.txt"):
            return super().get(url, **kwargs)
        if "broken" in url:
            raise ConnectionError("connection reset")
        return super().get(url, **kwargs)


def two_entries():
    good = entry()
    bad = entry(id="broken", urn="urn:ki:in:dpdp:source:broken", url="https://www.meity.gov.in/broken.pdf")
    return bad, good


def test_one_failing_entry_does_not_stop_the_run(tmp_path):              # review 2
    bad, good = two_entries()
    path = write_registry(tmp_path, [bad, good])
    session = Boom({good["url"]: Response(good["url"], pdf_bytes("Good text."))})
    results, updated = osrc.run(path, fetcher(tmp_path, session))
    by_id = {r.id: r for r in results}
    assert by_id["broken"].status == "refused" and "ConnectionError" in by_id["broken"].detail
    assert by_id[good["id"]].status == "stored" and updated == [good["id"]]


def test_files_without_registry_hashes_get_recorded_on_rerun(tmp_path):  # review 2, local-file fallback
    e = entry()
    path = write_registry(tmp_path, [e])
    doc = pdf_bytes("Section 2 comes into force.")
    fetcher(tmp_path, Session({e["url"]: Response(e["url"], doc)})).fetch(e)   # files written, hashes never recorded
    results, updated = osrc.run(path, fetcher(tmp_path, Session({e["url"]: Response(e["url"], doc)})))
    assert results[0].status == "unchanged" and updated == [e["id"]]
    saved = osrc.load_registry(path)[0]
    assert saved["sha256"] == sha(doc) and saved["text_sha256"] and saved["text_method"] == "pdf"


def test_a_changed_file_on_disk_without_a_registry_hash_is_reported(tmp_path):  # review 3, local-file fallback
    e = entry()
    fetcher(tmp_path, Session({e["url"]: Response(e["url"], pdf_bytes("Old."))})).fetch(e)
    result = fetcher(tmp_path, Session({e["url"]: Response(e["url"], pdf_bytes("New."))})).fetch(e)
    assert result.status == "changed"


def test_a_changed_document_leaves_the_registry_file_untouched(tmp_path):  # E2.10 through record()
    old, new = pdf_bytes("Original."), pdf_bytes("Amended.")
    e = entry()
    path = write_registry(tmp_path, [e])
    osrc.run(path, fetcher(tmp_path, Session({e["url"]: Response(e["url"], old)})))
    before = open(path, "rb").read()
    results, updated = osrc.run(path, fetcher(tmp_path, Session({e["url"]: Response(e["url"], new)})))
    assert results[0].status == "changed" and updated == []
    assert open(path, "rb").read() == before


def test_record_leaves_the_file_alone_when_nothing_changed(tmp_path):    # review 5
    path = tmp_path / "official.yaml"
    path.write_text("# a maintainer's note\n[]\n")
    assert osrc.record(str(path), []) == []
    assert path.read_text() == "# a maintainer's note\n[]\n"


@pytest.mark.parametrize("status", [403, 503])
def test_robots_403_or_5xx_means_do_not_fetch(tmp_path, status):        # review 3 and 6
    e = entry()

    class Robots(Session):
        def get(self, url, **kwargs):
            self.calls.append(url)
            if url.endswith("/robots.txt"):
                return Response(url, b"", status=status, ctype="text/plain")
            return self.routes[url]

    session = Robots({e["url"]: Response(e["url"], pdf_bytes("x"))})
    result = fetcher(tmp_path, session).fetch(e)
    assert result.status == "refused" and "robots" in result.detail
    assert e["url"] not in session.calls


def test_a_redirect_chain_cannot_bounce_through_an_off_list_host(tmp_path):  # review 3
    e = entry()
    hop = "https://www.meity.gov.in/static/hop"
    session = Session({
        e["url"]: Response(e["url"], status=302, location=hop),
        hop: Response(hop, status=302, location="https://evil.example/bounce"),
        "https://evil.example/bounce": Response("https://evil.example/bounce", status=302, location=e["url"]),
    })
    result = fetcher(tmp_path, session).fetch(e)
    assert result.status == "refused" and "https://evil.example/bounce" not in session.calls
