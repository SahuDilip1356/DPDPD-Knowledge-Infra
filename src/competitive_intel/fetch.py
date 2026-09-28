"""
Sitemap-driven fetcher for competitor sites. Writes one JSON record per page to
staging/competitive_intel/raw/<domain>/<crawl-date>/ (gitignored).

Run discover.py first. Domains are fetched in parallel, one request per second each.

Usage:  python3 src/competitive_intel/fetch.py            # every source
        python3 src/competitive_intel/fetch.py tsaaro.com cadp.in  # named sources
"""
import glob
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (compatible; research-crawler/1.0)"
DELAY_SECS = 1.0
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))  # paths must not depend on the caller's cwd
SITEMAP_DIR = os.path.join(REPO_ROOT, "staging/competitive_intel/sitemaps")
OUT_ROOT = os.path.join(REPO_ROOT, "staging/competitive_intel/raw")
STRIP_TAGS = ["nav", "footer", "script", "style", "noscript", "svg", "form", "aside"]
NON_HTML = re.compile(r"\.(pdf|jpe?g|png|gif|webp|svg|zip|docx?|xlsx?|pptx?|mp4|xml|json|css|js)$", re.I)
ARTICLE_SECTION = re.compile(r"/(blogs?|articles?|newsletter|insights?|resources?|dpdp-index|your-rights)/")
LINK_CRAWL_PAGES = 40  # for sites that publish no sitemap
MIN_CONTENT_WORDS = 40


def load_config() -> tuple:
    with open(os.path.join(HERE, "sources.yaml")) as f:
        config = yaml.safe_load(f)
    return config["defaults"], config["sources"]


def classify(path: str, rules: list, course: list = ()) -> str:
    if path in ("", "/", "/index.html"):
        return "HOME"
    lowered = path.lower()
    # An article *about* AI training data or certification is knowledge, not a course.
    if any(x in lowered for x in course) and not ARTICLE_SECTION.search(lowered):
        return "COURSE"
    for needle, label in rules:
        if needle in lowered:
            return label
    return "OTHER"


def select_urls(source: dict, defaults: dict) -> list:
    """Apply excludes, locale, relevance and per-section caps to the sitemap URL list."""
    domain = source["domain"]
    sitemap_file = os.path.join(SITEMAP_DIR, f"{domain}.txt")
    urls = open(sitemap_file).read().split() if os.path.exists(sitemap_file) else []
    urls += [f"https://{domain}{p}" for p in source.get("seeds", [])]

    excludes = defaults["exclude"] + source.get("exclude", [])
    locale = re.compile(defaults["locale_prefix"])
    relevance = re.compile(defaults["relevance"], re.I)
    caps, per_section = source.get("section_caps", {}), Counter()
    seeds = set(source.get("seeds", []))

    selected, seen = [], set()
    for url in sorted(set(urls)):
        parsed = urlparse(url)
        path = parsed.path or "/"
        key = path.rstrip("/").lower()
        if parsed.netloc.replace("www.", "") != domain.replace("www.", "") or parsed.query or key in seen:
            continue
        if NON_HTML.search(path) or locale.search(path.lower()):
            continue
        if any(x in path.lower() for x in excludes):
            continue
        if source.get("relevance_only") and path not in seeds and path != "/" \
                and "pricing" not in path and not relevance.search(path):
            continue
        section = path.strip("/").split("/")[0]
        if section in caps:
            per_section[section] += 1
            if per_section[section] > caps[section]:
                continue
        seen.add(key)
        selected.append(url)
    return selected[: source.get("max_pages", defaults["max_pages"])]


def to_markdown(container) -> str:
    """Flatten the main content into headings, paragraphs and list items."""
    block_tags = {"h1", "h2", "h3", "h4", "p", "li", "td", "blockquote", "summary", "dt", "dd"}

    def is_question(el):
        # FAQ accordions put the question in a span/div/button, e.g. class="question-text".
        return any("question" in c.lower() for c in el.get("class", []))

    lines = []
    for el in container.find_all(lambda el: el.name in block_tags or is_question(el)):
        text = el.get_text(" ", strip=True)
        if not text:
            continue
        if is_question(el) and el.name not in block_tags:
            if not el.find(is_question) and len(text) > 8:  # innermost wrapper; skip numbering/toggle glyphs
                lines.append(f"\n#### {text}\n")
        elif el.name in ("h1", "h2", "h3", "h4"):
            lines.append(f"\n{'#' * int(el.name[1])} {text}\n")
        elif el.name == "li":
            lines.append(f"- {text}")
        else:
            lines.append(text)
    # Nested elements (p inside li/td) repeat their text; drop consecutive duplicates.
    deduped = [l for i, l in enumerate(lines) if i == 0 or l.lstrip("- ") != lines[i - 1].lstrip("- ")]
    return "\n".join(deduped).strip()


def jsonld_questions(soup) -> list:
    """Questions declared in schema.org FAQPage blocks (often absent from the visible HTML)."""
    questions = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.get_text())
        except ValueError:
            continue
        if isinstance(data, dict):
            data = data.get("@graph", [data])
        for block in data if isinstance(data, list) else []:
            if isinstance(block, dict) and block.get("@type") == "FAQPage":
                entities = block.get("mainEntity", [])
                entities = entities if isinstance(entities, list) else [entities]
                questions += [q.get("name", "") for q in entities if isinstance(q, dict) and q.get("name")]
    return questions


def _words(element) -> int:
    return len(element.get_text(" ", strip=True).split())


def parse_page(html: bytes, base_url: str = "") -> dict:
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.get_text(strip=True) if soup.title else ""
    description = soup.find("meta", attrs={"name": "description"})
    questions = jsonld_questions(soup)
    links = sorted({urljoin(base_url, a["href"]).split("#")[0] for a in soup.find_all("a", href=True)}) if base_url else []
    for tag in soup.find_all(STRIP_TAGS):
        tag.decompose()
    container = soup.find("main") or soup.find("article")
    if container is None or _words(container) < MIN_CONTENT_WORDS:
        # Next.js streams Suspense content into hidden <div id="S:n"> blocks and moves them
        # into an empty <main> with JavaScript. The text is in the HTML; it is just elsewhere.
        streamed = [d for d in soup.select('div[hidden][id^="S:"]') if _words(d)]
        if sum(_words(d) for d in streamed) >= MIN_CONTENT_WORDS:
            container = soup.new_tag("div")
            for chunk in streamed:
                container.append(chunk.extract())
        else:
            # No semantic wrapper: the site-level <header> is chrome, so drop it.
            for tag in soup.find_all("header"):
                tag.decompose()
            container = soup.body or soup
    headings = [
        {"level": int(h.name[1]), "text": h.get_text(" ", strip=True)}
        for h in container.find_all(["h1", "h2", "h3"])
        if h.get_text(strip=True)
    ]
    return {
        "title": title,
        "meta_description": description.get("content", "") if description else "",
        "headings": headings,
        "jsonld_questions": questions,
        "markdown": to_markdown(container),
        "_links": links,
    }


def fetch_source(source: dict, defaults: dict) -> dict:
    domain = source["domain"]
    # Resume into the latest crawl of this domain when it is incomplete (no manifest),
    # so re-fetched pages land beside the rest instead of in a partial new folder.
    previous = sorted(glob.glob(os.path.join(OUT_ROOT, domain, "*")))
    if previous and not os.path.exists(os.path.join(previous[-1], "_manifest.json")):
        crawl_date = os.path.basename(previous[-1])
    else:
        crawl_date = date.today().isoformat()
    out_dir = os.path.join(OUT_ROOT, domain, crawl_date)
    if os.path.exists(os.path.join(out_dir, "_manifest.json")):
        return {"domain": domain, "skipped": "already crawled today"}
    os.makedirs(out_dir, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    # robotparser's own fetch uses the Python-urllib agent, which CDNs answer with 403 and
    # the parser then reads as "disallow everything". Fetch with our session instead.
    robots = robotparser.RobotFileParser()
    try:
        resp = session.get(f"https://{domain}/robots.txt", timeout=20)
        robots.parse(resp.text.splitlines() if resp.ok and "html" not in resp.headers.get("Content-Type", "") else [])
    except requests.RequestException:
        robots.parse([])

    queue = select_urls(source, defaults)
    link_crawl = len(queue) <= len(source.get("seeds", []))  # no sitemap: follow same-site links
    rules = source.get("classify", []) + defaults["classify"]
    metadata_paths = defaults["metadata_only"] + source.get("metadata_only", [])
    course_paths = defaults["course"] + source.get("course", [])

    manifest, visited = [], set()
    while queue:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        path = urlparse(url).path or "/"
        if not robots.can_fetch(USER_AGENT, url):
            manifest.append({"url": url, "status": "ROBOTS_DISALLOWED"})
            continue

        slug = (re.sub(r"[^a-zA-Z0-9]+", "_", path).strip("_") or "index")[:150]
        out_file = os.path.join(out_dir, f"{slug}.json")
        if os.path.exists(out_file) and not link_crawl:  # resume an interrupted run
            done = json.load(open(out_file))
            manifest.append({"url": url, "status": "OK", "content_type": done["content_type"],
                             "capture_mode": done["capture_mode"], "word_count": done["word_count"]})
            continue

        time.sleep(DELAY_SECS)
        try:
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            if "html" not in resp.headers.get("Content-Type", "html"):
                raise requests.RequestException("not HTML")
        except requests.RequestException as e:
            manifest.append({"url": url, "status": f"ERROR: {str(e)[:120]}"})
            continue

        page = parse_page(resp.content, url)
        links = page.pop("_links")
        room = LINK_CRAWL_PAGES - len(visited) - len(queue)
        if link_crawl and room > 0:
            same_site = [l for l in links if urlparse(l).netloc.replace("www.", "") == domain.replace("www.", "") and not NON_HTML.search(l)
                         and not any(x in l.lower() for x in defaults["exclude"])]
            queue += [l for l in same_site if l not in visited and l not in queue][:room]

        content_type = classify(path, rules, course_paths)
        metadata_only = content_type == "COURSE" or any(x in path.lower() for x in metadata_paths)
        record = {
            "source_domain": domain,
            "tier": source.get("tier"),
            "url": url,
            "crawl_date": crawl_date,
            "content_type": content_type,
            "capture_mode": "METADATA_ONLY" if metadata_only else "FULL",
            "content_sha256": hashlib.sha256(page["markdown"].encode()).hexdigest(),
            "word_count": len(page["markdown"].split()),
            **page,
        }
        if metadata_only:
            record["markdown"] = None

        with open(out_file, "w") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        manifest.append({"url": url, "status": "OK", "content_type": record["content_type"],
                         "capture_mode": record["capture_mode"], "word_count": record["word_count"]})

    with open(os.path.join(out_dir, "_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    ok = [m for m in manifest if m["status"] == "OK"]
    return {"domain": domain, "ok": len(ok), "failed": len(manifest) - len(ok),
            "words": sum(m["word_count"] for m in ok)}


if __name__ == "__main__":
    defaults, sources = load_config()
    if len(sys.argv) > 1:
        sources = [s for s in sources if s["domain"] in sys.argv[1:]] or sys.exit("no matching domain in sources.yaml")
    with ThreadPoolExecutor(max_workers=len(sources)) as pool:
        for result in pool.map(lambda s: fetch_source(s, defaults), sources):
            print(result, flush=True)
