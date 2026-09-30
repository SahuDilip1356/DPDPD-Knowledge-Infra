"""
Second-pass classifier over the raw crawl. Rule-based (no LLM): refines content_type from
page content, tags topics / sectors / cited DPDPA sections and Rules, pulls out questions,
and flags thin or duplicate pages.

Writes  staging/competitive_intel/classified/pages.jsonl      one row per page (no body text)
        staging/competitive_intel/classified/questions.jsonl  one row per distinct question per domain
        docs/competitive_intel/coverage.md                    topic x competitor matrix (our analysis)

Usage:  python3 src/competitive_intel/classify.py
"""
import glob
import json
import os
import re
from collections import Counter, defaultdict

RAW = "staging/competitive_intel/raw"
OUT = "staging/competitive_intel/classified"
REPORT = "docs/competitive_intel/coverage.md"
THIN_WORDS = 40

# Matched against title + headings (strong signal) and body (needs repeated mentions).
TOPICS = {
    "Consent": r"\bconsent\b(?! manager)",
    "Consent Manager": r"consent manager",
    "Notice": r"privacy notice|\bnotice\b",
    "Data Principal rights": r"data principal|right to (access|erasure|correction|nominate)|rights request|dsar|\bdsr\b",
    "Children & guardians": r"\bchild|\bminor|parental|guardian|age verif",
    "Breach": r"breach|incident response",
    "Security safeguards": r"security safeguard|encryption|access control|\bvapt\b|iso 27001",
    "Cross-border transfer": r"cross.border|data transfer|localis|localiz",
    "SDF & DPIA": r"significant data fiduciar|\bsdf\b|\bdpia\b|impact assessment|data audit",
    "DPO & grievance": r"data protection officer|\bdpo\b|grievance",
    "Retention & erasure": r"retention|erasure|deletion|delete my data",
    "Processors & vendors": r"data processor|vendor|third.party|\bdpa\b agreement|processing agreement",
    "Data mapping & inventory": r"data mapping|data inventory|data discovery|ropa|record of processing",
    "Legitimate uses": r"legitimate use|legitimate interest",
    "Penalties & enforcement": r"penalt|₹\s?250|250 crore|data protection board|\bdpb\b|enforcement",
    "Exemptions": r"exemption|exempt\b",
    "DPDP Rules": r"dpdp rules|rules,? 2025|draft rules",
    "GDPR comparison": r"gdpr|ccpa",
    "AI": r"\bai\b|artificial intelligence|\bllm\b|machine learning",
    "Cookies & tracking": r"cookie|tracker|\bcmp\b",
    "Compliance roadmap & checklist": r"checklist|roadmap|readiness|gap assessment|compliance (program|framework|steps)",
    "Templates & policies": r"template|policy generator|privacy policy",
    "Pricing": r"pricing|per month|/month|₹\s?\d",
}
SECTORS = {
    "BFSI & fintech": r"\bbank|fintech|nbfc|insur|lending|\brbi\b",
    "Healthcare": r"health|hospital|clinic|patient|pharma",
    "E-commerce & D2C": r"e.?commerce|d2c|retail|marketplace",
    "EdTech & schools": r"edtech|school|student|universit",
    "HR & recruitment": r"employee|recruit|\bhr\b|payroll|candidate",
    "SaaS & IT": r"\bsaas\b|software compan|it services",
    "SMB & startups": r"startup|msme|\bsme\b|small business",
    "CA & professional firms": r"chartered accountant|\bca firm|law firm",
    "Telecom & media": r"telecom|\bott\b|media compan",
    "Real estate & hospitality": r"real estate|hotel|hospitality|travel",
    "Government": r"government|public sector|\bpsu\b",
    "WhatsApp & messaging": r"whatsapp",
    "Excel & offline records": r"excel|spreadsheet|paper record|offline",
}


def refine_type(record: dict, text: str, questions: list) -> str:
    """URL rules leave many pages as OTHER; use the content to place them."""
    label = record["content_type"]
    if label != "OTHER":
        return label
    head = (record["title"] + " " + " ".join(h["text"] for h in record["headings"][:3])).lower()
    if re.search(r"\bsection \d+|\bchapter [ivx\d]+|\bschedule\b", head):
        return "LAW"
    if re.search(r"\brule \d+", head):
        return "RULES"
    if len(questions) >= 5:
        return "FAQ"
    if re.search(r"pricing|plans", head):
        return "PRICING"
    if re.search(r" vs\.? | versus |alternative", head):
        return "COMPARISON"
    if re.search(r"what is|how to|guide|explained|checklist|step", head) or record["word_count"] > 700:
        return "BLOG"
    if re.search(r"platform|software|solution|feature|demo", head):
        return "PRODUCT"
    return "OTHER"


def tag(patterns: dict, head: str, body: str) -> list:
    tags = []
    for name, pattern in patterns.items():
        if re.search(pattern, head, re.I) or len(re.findall(pattern, body, re.I)) >= 5:
            tags.append(name)
    return tags


def extract_questions(record: dict, body: str) -> list:
    candidates = list(record.get("jsonld_questions", []))
    candidates += [h["text"] for h in record["headings"] if h["text"].rstrip().endswith("?")]
    candidates += re.findall(r"^#### (.+\?)\s*$", body, re.M)
    cleaned = {}
    for q in candidates:
        q = re.sub(r"^[\W\d]+", "", q).strip()
        key = re.sub(r"\W+", " ", q.lower()).strip()
        if 15 <= len(q) <= 220:
            cleaned.setdefault(key, q)
    return list(cleaned.items())


def latest_crawls() -> list:
    dirs = []
    for domain_dir in sorted(glob.glob(os.path.join(RAW, "*"))):
        crawls = sorted(glob.glob(os.path.join(domain_dir, "*")))
        if crawls:
            dirs.append(crawls[-1])
    return dirs


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    pages, questions, seen_hash = [], [], {}

    for crawl_dir in latest_crawls():
        for path in sorted(glob.glob(os.path.join(crawl_dir, "*.json"))):
            if os.path.basename(path).startswith("_"):
                continue
            record = json.load(open(path))
            body = record.get("markdown") or ""
            head = record["title"] + " " + record.get("meta_description", "") + " " + \
                " ".join(h["text"] for h in record["headings"])
            page_questions = extract_questions(record, body)
            duplicate_of = seen_hash.get(record["content_sha256"]) if record["word_count"] >= THIN_WORDS else None
            seen_hash.setdefault(record["content_sha256"], record["url"])

            pages.append({
                "source_domain": record["source_domain"],
                "tier": record.get("tier"),
                "url": record["url"],
                "title": record["title"],
                "content_type": refine_type(record, body, page_questions),
                # TRAINING is boxed apart: tracked for curriculum intelligence, never stacked as knowledge.
                "box": "TRAINING" if record["content_type"] == "COURSE" else "KNOWLEDGE",
                "capture_mode": record["capture_mode"],
                "word_count": record["word_count"],
                "topics": tag(TOPICS, head, body),
                "sectors": tag(SECTORS, head, body),
                "dpdpa_sections": sorted({int(n) for n in re.findall(r"\b[Ss]ec(?:tion|\.)\s*(\d{1,2})\b", body) if 1 <= int(n) <= 44}),
                "dpdp_rules": sorted({int(n) for n in re.findall(r"\bRule\s+(\d{1,2})\b", body) if 1 <= int(n) <= 23}),
                "question_count": len(page_questions),
                "thin": record["capture_mode"] == "FULL" and record["word_count"] < THIN_WORDS,
                "duplicate_of": duplicate_of,
                "source_class": "COMPETITOR",
                "verification_required": True,
                "publication_eligible": False,
            })
            for key, text in page_questions:
                questions.append({"normalized_key": key, "question_text": text,
                                  "found_on": record["source_domain"], "original_url": record["url"]})

    with open(os.path.join(OUT, "pages.jsonl"), "w") as f:
        f.writelines(json.dumps(p, ensure_ascii=False) + "\n" for p in pages)
    distinct = {(q["normalized_key"], q["found_on"]): q for q in questions}
    with open(os.path.join(OUT, "questions.jsonl"), "w") as f:
        f.writelines(json.dumps(q, ensure_ascii=False) + "\n" for q in distinct.values())

    write_report(pages, distinct)
    print(f"{len(pages)} pages, {len(distinct)} questions -> {OUT}; report -> {REPORT}")


def write_report(pages: list, questions: dict):
    usable = [p for p in pages if not p["thin"] and not p["duplicate_of"] and p["box"] != "TRAINING"]
    domains = sorted({p["source_domain"] for p in pages})
    by_domain = defaultdict(list)
    for p in usable:
        by_domain[p["source_domain"]].append(p)
    types = [t for t, _ in Counter(p["content_type"] for p in usable).most_common()]
    q_per_domain = Counter(d for _, d in questions)

    lines = ["# Competitor coverage", "",
             "Generated by `src/competitive_intel/classify.py` from the latest crawl of each source. "
             "Rule-based tagging on titles, headings and body text; counts are pages, not quality. "
             "Thin (<40 words, usually JS-rendered) and exact-duplicate pages are left out of the matrices.", "",
             "## Corpus", "",
             "| Source | Tier | Pages | Thin | Words | Questions | " + " | ".join(types) + " |",
             "|---|---|---|---|---|---|" + "---|" * len(types)]
    for d in domains:
        all_d = [p for p in pages if p["source_domain"] == d]
        c = Counter(p["content_type"] for p in by_domain[d])
        lines.append(f"| {d} | {all_d[0]['tier']} | {len(by_domain[d])} | {sum(p['thin'] for p in all_d)} | "
                     f"{sum(p['word_count'] for p in by_domain[d]):,} | {q_per_domain[d]} | "
                     + " | ".join(str(c[t] or '') for t in types) + " |")
    lines.append(f"| **Total** | | **{len(usable)}** | **{sum(p['thin'] for p in pages)}** | "
                 f"**{sum(p['word_count'] for p in usable):,}** | **{len(questions)}** | "
                 + " | ".join(str(sum(1 for p in usable if p['content_type'] == t)) for t in types) + " |")

    for title, key, names in (("Topic", "topics", TOPICS), ("Sector and channel", "sectors", SECTORS)):
        lines += ["", f"## {title} coverage (pages per source)", "",
                  f"| {title} | Sources | Pages | " + " | ".join(d.replace("www.", "") for d in domains) + " |",
                  "|---|---|---|" + "---|" * len(domains)]
        rows = []
        for name in names:
            counts = [sum(1 for p in by_domain[d] if name in p[key]) for d in domains]
            rows.append((sum(1 for c in counts if c), sum(counts), name, counts))
        for covered, total, name, counts in sorted(rows, reverse=True):
            lines.append(f"| {name} | {covered}/{len(domains)} | {total} | " + " | ".join(str(c or "") for c in counts) + " |")

    training = [p for p in pages if p["box"] == "TRAINING"]
    lines += ["", "## Training and certification box", "",
              "Kept apart from the knowledge corpus. Title and headings only; no course material is stored.", "",
              "| Source | Page | Title |", "|---|---|---|"]
    lines += [f"| {p['source_domain']} | {p['url'].split('/', 3)[-1][:70]} | {p['title'][:90].replace('|', '/')} |"
              for p in training]

    sections = Counter(n for p in usable for n in p["dpdpa_sections"])
    lines += ["", "## DPDPA sections cited (pages citing each)", "",
              ", ".join(f"S{n}: {sections[n]}" for n in range(1, 45))]
    with open(REPORT, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
