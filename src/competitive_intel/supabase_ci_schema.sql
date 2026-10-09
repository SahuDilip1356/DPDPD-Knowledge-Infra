-- ═══════════════════════════════════════════════════════════════════
-- COMPETITIVE INTELLIGENCE SCHEMA (quarantined from public.*)
-- Copy and paste this script into your Supabase SQL Editor
--
-- Nothing in `ci` is canonical knowledge. The reasoning API and Pinecone
-- index read only from `public`. Rows here are discovery signals: they
-- become knowledge only by being re-derived from a Layer 1/2 source and
-- published as a Knowledge Object through the factory.
-- ═══════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS ci;

-- 1. RAW PAGES (one row per URL per crawl)
CREATE TABLE IF NOT EXISTS ci.raw_pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_domain VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    crawl_date DATE NOT NULL,
    title TEXT,
    content_type VARCHAR(30) NOT NULL DEFAULT 'UNCLASSIFIED', -- LAW, RULES, FAQ, BLOG, TEMPLATE, CASE_LAW, TOOL, COURSE, COMMERCIAL, OTHER
    capture_mode VARCHAR(20) NOT NULL DEFAULT 'FULL',          -- FULL | METADATA_ONLY (templates, tools)
    markdown TEXT,                                             -- NULL when capture_mode = METADATA_ONLY
    headings JSONB NOT NULL DEFAULT '[]'::jsonb,
    content_sha256 CHAR(64) NOT NULL,
    word_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc'::text, now()),
    UNIQUE (url, crawl_date)
);

CREATE INDEX IF NOT EXISTS idx_ci_pages_domain_type ON ci.raw_pages (source_domain, content_type);
CREATE INDEX IF NOT EXISTS idx_ci_pages_hash ON ci.raw_pages (content_sha256);

-- 2. CLAIMS REGISTRY
CREATE TABLE IF NOT EXISTS ci.claims_registry (
    claim_id VARCHAR(20) PRIMARY KEY,                          -- CLM-000018
    claim_text TEXT NOT NULL,
    claim_type VARCHAR(20) NOT NULL,                           -- LEGAL | STATISTIC | MARKET | OPINION
    found_on VARCHAR(255) NOT NULL,                            -- source_domain
    original_url TEXT NOT NULL,
    dpdpa_sections JSONB NOT NULL DEFAULT '[]'::jsonb,
    dpdp_rules JSONB NOT NULL DEFAULT '[]'::jsonb,
    primary_source_urn VARCHAR(255),                           -- public.knowledge_objects.urn once verified
    verification_status VARCHAR(30) NOT NULL DEFAULT 'NEEDS_REVIEW',
        -- VERIFIED_PRIMARY | SUPPORTED_INTERPRETATION | CONTESTED | OUTDATED | UNSUPPORTED | INCORRECT | NEEDS_REVIEW
    confidence NUMERIC(3,2),
    first_seen DATE NOT NULL,
    last_seen DATE NOT NULL,
    used_by_saralprivacy BOOLEAN NOT NULL DEFAULT FALSE,
    publication_allowed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_ci_claims_status ON ci.claims_registry (verification_status);

-- 3. QUESTION UNIVERSE
CREATE TABLE IF NOT EXISTS ci.question_universe (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_text TEXT NOT NULL,
    normalized_key VARCHAR(255) NOT NULL,                      -- lowercased, punctuation-stripped; exact-dup guard
    topic VARCHAR(100),
    dpdpa_sections JSONB NOT NULL DEFAULT '[]'::jsonb,
    origin VARCHAR(30) NOT NULL DEFAULT 'COMPETITOR',          -- COMPETITOR | SEARCH_CONSOLE | REDDIT | SETU_USER | ...
    found_on VARCHAR(255),
    original_url TEXT,
    answered_by_urn VARCHAR(255),                              -- KO that answers it, if any
    first_seen DATE NOT NULL,
    UNIQUE (normalized_key, found_on)
);

-- 4. TOPIC MATRIX (one row per topic per source)
CREATE TABLE IF NOT EXISTS ci.topic_matrix (
    topic VARCHAR(100) NOT NULL,
    source_domain VARCHAR(255) NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 0,
    depth VARCHAR(20) NOT NULL DEFAULT 'NONE',                 -- NONE | MENTION | GENERIC | DEEP
    saralprivacy_ko_count INTEGER NOT NULL DEFAULT 0,
    gap VARCHAR(30),                                           -- NO_GAP | DIFFERENTIATE | INVESTIGATE | SP_ADVANTAGE | SP_GAP
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc'::text, now()),
    PRIMARY KEY (topic, source_domain)
);

-- Lock the schema down: service role only, no anon/authenticated access.
ALTER TABLE ci.raw_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE ci.claims_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE ci.question_universe ENABLE ROW LEVEL SECURITY;
ALTER TABLE ci.topic_matrix ENABLE ROW LEVEL SECURITY;
