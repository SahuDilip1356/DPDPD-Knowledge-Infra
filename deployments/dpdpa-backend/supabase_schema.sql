-- ═══════════════════════════════════════════════════════════════════
-- SUPABASE POSTGRESQL SCHEMA FOR DPDPA KNOWLEDGE INFRASTRUCTURE
-- Copy and paste this script into your Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. KNOWLEDGE OBJECTS (Bi-temporal versioning)
CREATE TABLE IF NOT EXISTS public.knowledge_objects (
    urn VARCHAR(255) NOT NULL,
    version INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(512) NOT NULL,
    summary TEXT NOT NULL,
    confidence_score NUMERIC(3,2) NOT NULL DEFAULT 1.00,
    source_credibility VARCHAR(50),
    forum_published VARCHAR(255),
    interpretation_stance VARCHAR(50),
    
    -- Bi-temporal columns
    system_time_start TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc'::text, now()),
    system_time_end TIMESTAMP WITH TIME ZONE, -- Null means current active version
    legal_time_start TIMESTAMP WITH TIME ZONE NOT NULL,
    legal_time_end TIMESTAMP WITH TIME ZONE,
    
    -- Dynamic Payloads
    body JSONB NOT NULL DEFAULT '{}'::jsonb,
    business_impact JSONB NOT NULL DEFAULT '{}'::jsonb,
    evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
    linked_objects JSONB NOT NULL DEFAULT '[]'::jsonb,
    entities JSONB NOT NULL DEFAULT '[]'::jsonb,
    relations JSONB NOT NULL DEFAULT '[]'::jsonb,

    PRIMARY KEY (urn, version)
);

-- Indexing for bi-temporal query speed
CREATE INDEX IF NOT EXISTS idx_ko_bitime ON public.knowledge_objects (urn, system_time_start, system_time_end, legal_time_start, legal_time_end);

-- 2. GRAPH EDGES
CREATE TABLE IF NOT EXISTS public.graph_edges (
    source_urn VARCHAR(255) NOT NULL,
    source_version INTEGER NOT NULL,
    target_urn VARCHAR(255) NOT NULL,
    edge_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    
    PRIMARY KEY (source_urn, source_version, target_urn, edge_type)
);

-- 3. REGULATORY EVENTS (Changes Feed)
CREATE TABLE IF NOT EXISTS public.regulatory_events (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    authority VARCHAR(255) NOT NULL,
    jurisdiction VARCHAR(50) NOT NULL DEFAULT 'India',
    date_published DATE NOT NULL,
    date_effective DATE,
    date_detected DATE DEFAULT CURRENT_DATE,
    impact_level VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    review_status VARCHAR(20) NOT NULL DEFAULT 'approved',
    summary TEXT NOT NULL,
    change_description TEXT NOT NULL,
    affected_ko_urns JSONB NOT NULL DEFAULT '[]'::jsonb,
    has_conflicts BOOLEAN DEFAULT FALSE,
    conflict_summary TEXT,
    evidence_count JSONB NOT NULL DEFAULT '{"primary": 0, "secondary": 0, "tertiary": 0}'::jsonb,
    affected_industries JSONB NOT NULL DEFAULT '[]'::jsonb,
    affected_processes JSONB NOT NULL DEFAULT '[]'::jsonb
);

-- 4. ACTION ITEMS (Decisions & Actions)
CREATE TABLE IF NOT EXISTS public.action_items (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    source_obligation TEXT NOT NULL,
    triggering_event_id VARCHAR(50) REFERENCES public.regulatory_events(id),
    ko_urn VARCHAR(255) NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(20) NOT NULL DEFAULT 'proposed',
    owner VARCHAR(100) NOT NULL,
    reviewer VARCHAR(100),
    due_date DATE NOT NULL,
    applicability VARCHAR(20) NOT NULL DEFAULT 'applies',
    applicability_rationale TEXT,
    affected_roles JSONB NOT NULL DEFAULT '[]'::jsonb,
    affected_process VARCHAR(100),
    related_control VARCHAR(50),
    description TEXT NOT NULL,
    completion_evidence TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 5. CONFLICTS
CREATE TABLE IF NOT EXISTS public.conflicts (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'under_review',
    detected_date DATE DEFAULT CURRENT_DATE,
    claim_a JSONB NOT NULL,
    claim_b JSONB NOT NULL,
    explanation TEXT NOT NULL,
    scope TEXT NOT NULL,
    downstream_impact JSONB NOT NULL DEFAULT '[]'::jsonb,
    reviewer_notes TEXT,
    reviewer VARCHAR(100)
);

-- 6. Enable Row Level Security (RLS)
ALTER TABLE public.knowledge_objects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.graph_edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regulatory_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.action_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conflicts ENABLE ROW LEVEL SECURITY;

-- 7. Define RLS Policies

-- Public Read Policies
CREATE POLICY "Allow public read access to knowledge_objects" 
ON public.knowledge_objects FOR SELECT USING (true);

CREATE POLICY "Allow public read access to graph_edges" 
ON public.graph_edges FOR SELECT USING (true);

CREATE POLICY "Allow public read access to regulatory_events" 
ON public.regulatory_events FOR SELECT USING (true);

CREATE POLICY "Allow public read access to conflicts" 
ON public.conflicts FOR SELECT USING (true);

-- Authenticated User Write/Update Policies for Action Items
CREATE POLICY "Allow auth users read and write access to action_items" 
ON public.action_items FOR ALL TO authenticated 
USING (true) WITH CHECK (true);

CREATE POLICY "Allow public read access to action_items" 
ON public.action_items FOR SELECT USING (true);

-- 8. COMPETITOR KNOWLEDGE CARDS (discovery only — never public, never canonical)
CREATE TABLE IF NOT EXISTS public.competitor_knowledge_cards (
    card_id VARCHAR(64) PRIMARY KEY,
    source VARCHAR(64) NOT NULL,
    source_class VARCHAR(32) NOT NULL DEFAULT 'COMPETITOR',
    source_url TEXT NOT NULL,
    content_type VARCHAR(32) NOT NULL,
    title TEXT NOT NULL,
    topic TEXT NOT NULL,
    subtopics JSONB NOT NULL DEFAULT '[]'::jsonb,
    dpdpa_sections JSONB NOT NULL DEFAULT '[]'::jsonb,
    dpdp_rules JSONB NOT NULL DEFAULT '[]'::jsonb,
    audience JSONB NOT NULL DEFAULT '[]'::jsonb,
    claims JSONB NOT NULL DEFAULT '[]'::jsonb,
    statistics JSONB NOT NULL DEFAULT '[]'::jsonb,
    examples JSONB NOT NULL DEFAULT '[]'::jsonb,
    tools_mentioned JSONB NOT NULL DEFAULT '[]'::jsonb,
    primary_sources_cited JSONB NOT NULL DEFAULT '[]'::jsonb,
    verification_required BOOLEAN NOT NULL DEFAULT TRUE,
    authority_level VARCHAR(8) NOT NULL,
    publication_eligible BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc'::text, now()),
    CONSTRAINT competitor_cards_unpublished CHECK (publication_eligible = FALSE),
    CONSTRAINT competitor_cards_must_verify CHECK (verification_required = TRUE),
    CONSTRAINT competitor_cards_source_class CHECK (source_class = 'COMPETITOR')
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_competitor_cards_url
ON public.competitor_knowledge_cards (source_url);

ALTER TABLE public.competitor_knowledge_cards ENABLE ROW LEVEL SECURITY;
-- No public SELECT policy: these cards are competitive discovery, not Setu truth.

-- 9. CLAIMS REGISTRY + TOPIC MATRIX (Source Truth — still not public)
CREATE TABLE IF NOT EXISTS public.competitor_claims_registry (
    claim_id VARCHAR(16) PRIMARY KEY,
    claim_text TEXT NOT NULL,
    found_on VARCHAR(64) NOT NULL DEFAULT 'DPDPA.com',
    card_id VARCHAR(64),
    original_url TEXT NOT NULL,
    claim_type VARCHAR(16) NOT NULL,
    dpdpa_section VARCHAR(32),
    dpdp_rule VARCHAR(32),
    primary_source TEXT,
    verification_status VARCHAR(32) NOT NULL,
    confidence NUMERIC(3,2) NOT NULL,
    verdict_note TEXT,
    publication_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    used_by_saralprivacy BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.competitor_topic_matrix (
    topic_id VARCHAR(16) PRIMARY KEY,
    topic VARCHAR(128) NOT NULL,
    dpdpa_com VARCHAR(16) NOT NULL,
    saralprivacy VARCHAR(16) NOT NULL,
    primary_evidence VARCHAR(8) NOT NULL,
    gap VARCHAR(32) NOT NULL,
    competitor_urls JSONB NOT NULL DEFAULT '[]'::jsonb,
    saralprivacy_evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
    primary_citation TEXT,
    note TEXT,
    publication_eligible BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT topic_matrix_unpublished CHECK (publication_eligible = FALSE)
);

ALTER TABLE public.competitor_claims_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.competitor_topic_matrix ENABLE ROW LEVEL SECURITY;
