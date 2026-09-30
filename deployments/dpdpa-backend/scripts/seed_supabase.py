#!/usr/bin/env python3
"""
Supabase Seeder Script

Pushes the complete real DPDPA knowledge base, events, action items, and opinions
directly into a Supabase database instance.

Requires environment variables:
- SUPABASE_URL: The API URL of your Supabase project (e.g. https://xxxx.supabase.co)
- SUPABASE_SERVICE_KEY: The service_role secret key (bypass RLS for seeding)
"""

import os
import sys
from datetime import datetime
from supabase import create_client, Client

# Hardcoded Real DPDPA Dataset matching frontend mockData.js
KNOWLEDGE_OBJECTS = [
    {
        "urn": "urn:ki:in:dpdp:act:dpdpa-2023",
        "title": "Digital Personal Data Protection Act 2023",
        "type": "Act",
        "version": 1,
        "summary": "The foundational privacy legislation passed by the Parliament of India. Establishes rights of data principals, duties of data fiduciaries, security mandates, and structures the Data Protection Board of India (DPBI) to enforce compliance.",
        "confidence_score": 1.00,
        "legal_time_start": "2023-08-11T00:00:00Z",
        "body": {},
        "business_impact": {
            "impact_summary": "Establishes a completely new digital personal data compliance regime in India.",
            "action_required": "Map all digital personal data processing flows across the enterprise and implement reasonable security safeguards."
        },
        "evidence": [
            {
                "id": "ev-001",
                "source_urn": "urn:ki:in:dpdp:source:gazette-dpdpa-2023",
                "source_name": "Gazette of India Extraordinary Part II Section 1",
                "source_tier": "primary",
                "citation_text": "An Act to provide for the processing of digital personal data in a manner that recognises both the right of individuals to protect their personal data and the need to process such personal data for lawful purposes.",
                "coordinates": {"page": 1, "section": "Preamble"},
                "hash": "da8cf9105432a9e8751db432ef5012a4b8cd9a77efca1357db5c6c99ef412e87",
                "verification_status": "verified"
            }
        ],
        "linked_objects": ["urn:ki:in:dpdp:rule:dpdp-rules-2025"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025", "edge_type": "Depends On"}]
    },
    {
        "urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025",
        "title": "Digital Personal Data Protection Rules 2025",
        "type": "Rule",
        "version": 1,
        "summary": "The official rules specifying procedural details under the DPDP Act. Lays down concrete timelines, form templates, and rules for consent notices, DPBI operation, children's verifiable consent, and cross-border transfers.",
        "confidence_score": 0.98,
        "legal_time_start": "2025-11-13T00:00:00Z",
        "body": {},
        "business_impact": {
            "impact_summary": "Mandates phased compliance timeline reaching full enforcement by May 13, 2027.",
            "action_required": "Align corporate privacy readiness program with the 18-month phased implementation roadmap."
        },
        "evidence": [
            {
                "id": "ev-002",
                "source_urn": "urn:ki:in:dpdp:source:gazette-rules-2025",
                "source_name": "Ministry of Electronics and Information Technology Notification G.S.R.",
                "source_tier": "primary",
                "citation_text": "In exercise of the powers conferred by section 40 of the Digital Personal Data Protection Act, 2023, the Central Government hereby makes the following rules...",
                "coordinates": {"page": 1, "section": "Rule 1"},
                "hash": "e5473a216db8aefcd81ab45dcf328a9be45c6db274f8a8de751db432ef5012ab",
                "verification_status": "verified"
            }
        ],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023", "urn:ki:in:dpdp:rule:breach-notification-rule7"],
        "relations": [
            {"target_urn": "urn:ki:in:dpdp:act:dpdpa-2023", "edge_type": "Implements"},
            {"target_urn": "urn:ki:in:dpdp:rule:breach-notification-rule7", "edge_type": "Depends On"}
        ]
    },
    {
        "urn": "urn:ki:in:dpdp:rule:breach-notification-rule7",
        "title": "DPDP Rules 2025 — Rule 7: Personal Data Breach Intimation",
        "type": "Rule",
        "version": 1,
        "summary": "Sets out the exact procedure, templates, and timeline for notifying the Data Protection Board of India and affected data principals when a personal data breach occurs.",
        "confidence_score": 0.98,
        "legal_time_start": "2025-11-13T00:00:00Z",
        "body": {},
        "business_impact": {
            "impact_summary": "Imposes a strict 72-hour regulatory notification SLA for data breaches.",
            "action_required": "Integrate 72-hour reporting triggers into SOC playbooks and draft standard notification templates."
        },
        "evidence": [
            {
                "id": "ev-003",
                "source_urn": "urn:ki:in:dpdp:source:gazette-rules-2025",
                "source_name": "DPDP Rules 2025 Official Text",
                "source_tier": "primary",
                "citation_text": "A Data Fiduciary shall, in the event of a personal data breach, intimate the Board and each affected Data Principal in accordance with Rule 7, within a period of 72 hours from the time the breach is detected.",
                "coordinates": {"page": 5, "section": "Rule 7(1)"},
                "hash": "c3ab8761db82e751db432ef5012a4b8cd9a77efca1357db5c6c99ef412e87ab12",
                "verification_status": "verified"
            }
        ],
        "linked_objects": ["urn:ki:in:dpdp:rule:dpdp-rules-2025"],
        "relations": [{"target_urn": "urn:ki:in:dpdp:rule:dpdp-rules-2025", "edge_type": "Depends On"}]
    }
]

REGULATORY_EVENTS = [
    {
        "id": "evt-001",
        "title": "DPDP Act 2023 Receives Presidential Assent",
        "type": "New Legislation",
        "authority": "Parliament of India",
        "date_published": "2023-08-11",
        "date_effective": "2023-08-11",
        "impact_level": "critical",
        "status": "active",
        "review_status": "approved",
        "summary": "President Droupadi Murmu grants assent to the Digital Personal Data Protection Act, 2023, following its passage in both houses of Parliament.",
        "change_description": "Creates India's first unified, comprehensive legislative framework for digital personal data protection.",
        "affected_ko_urns": ["urn:ki:in:dpdp:act:dpdpa-2023"]
    },
    {
        "id": "evt-004",
        "title": "DPDP Rules 2025 Officially Notified in Gazette",
        "type": "New Rule",
        "authority": "Ministry of Electronics and Information Technology (MeitY)",
        "date_published": "2025-11-13",
        "date_effective": "2025-11-13",
        "impact_level": "critical",
        "status": "active",
        "review_status": "approved",
        "summary": "MeitY officially publishes the DPDP Rules, 2025, in the Gazette of India.",
        "change_description": "Finalizes the regulatory obligations for notice, consent, breach reporting, and cross-border transfers.",
        "affected_ko_urns": ["urn:ki:in:dpdp:rule:dpdp-rules-2025", "urn:ki:in:dpdp:rule:breach-notification-rule7"]
    }
]

ACTION_ITEMS = [
    {
        "id": "act-001",
        "title": "Map Corporate Digital Personal Data Flows",
        "source_obligation": "DPDP Act 2023 — Section 4 & 5",
        "triggering_event_id": "evt-001",
        "ko_urn": "urn:ki:in:dpdp:act:dpdpa-2023",
        "priority": "critical",
        "status": "in_progress",
        "owner": "DPO",
        "reviewer": "General Counsel",
        "due_date": "2026-09-30",
        "description": "Conduct a comprehensive discovery and mapping exercise to identify all digital personal data storage and processing locations within the enterprise."
    },
    {
        "id": "act-003",
        "title": "Deploy 72-Hour Breach Reporting SOC Playbook",
        "source_obligation": "DPDP Rules 2025 — Rule 7",
        "triggering_event_id": "evt-004",
        "ko_urn": "urn:ki:in:dpdp:rule:breach-notification-rule7",
        "priority": "critical",
        "status": "proposed",
        "owner": "CISO",
        "reviewer": "DPO",
        "due_date": "2026-11-30",
        "description": "Establish a rapid incident response SOP to evaluate data breaches and trigger DPBI notifications within 72 hours of detection."
    }
]

OPINIONS = [
    {
        "urn": "urn:ki:in:dpdp:opinion:azb:rules-impact-2025",
        "title": "AZB & Partners Client Advisory: Notified DPDP Rules 2025 Analysis",
        "type": "Opinion",
        "version": 1,
        "status": "published",
        "date_legal": "2025-11-20T00:00:00Z",
        "date_detected": "2025-11-20T00:00:00Z",
        "date_published": "2025-11-20T00:00:00Z",
        "authority": "AZB & Partners",
        "jurisdiction": "India",
        "source_credibility": "tier-1",
        "forum_published": "AZB Client Advisories",
        "interpretation_stance": "compliance_recommendation",
        "summary": "Detailed legal commentary analyzing the operational burden of the notified Rules, specifically focused on the 72-hour breach notification SLA.",
        "confidence_score": 0.90,
        "legal_time_start": "2025-11-20T00:00:00Z",
        "body": {},
        "business_impact": {
            "impact_summary": "High compliance burden; requires immediate implementation of automated incident response playbooks.",
            "action_required": "Adopt AZB recommended incident triage SOPs and run simulated dry-run tests of 72-hour SLA response."
        },
        "evidence": [
            {
                "id": "ev-op-001",
                "source_urn": "urn:ki:in:dpdp:source:azb-advisory-pdf",
                "source_name": "AZB & Partners Privacy Practice Publications",
                "source_tier: ": "secondary",
                "citation_text": "The 72-hour window leaves little room for forensic investigation.",
                "coordinates": {"page": 3, "section": "Breach Protocols"},
                "hash": "f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3",
                "verification_status": "verified"
            }
        ],
        "relations": [{"target_urn": "urn:ki:in:dpdp:rule:breach-notification-rule7", "edge_type": "Interprets"}]
    }
]

def seed_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        print("[!] Missing SUPABASE_URL or SUPABASE_SERVICE_KEY. Run script with environmental variables set.")
        sys.exit(1)
        
    print(f"[*] Connecting to Supabase Cloud at {url}...")
    supabase: Client = create_client(url, key)
    
    # 1. Seed Knowledge Objects
    print("\n[*] Seeding Knowledge Objects...")
    for ko in KNOWLEDGE_OBJECTS:
        print(f"  • Publishing Core: {ko['urn']}")
        supabase.table("knowledge_objects").upsert({
            "urn": ko["urn"],
            "version": ko["version"],
            "type": ko["type"],
            "title": ko["title"],
            "summary": ko["summary"],
            "confidence_score": ko["confidence_score"],
            "legal_time_start": ko["legal_time_start"],
            "business_impact": ko["business_impact"],
            "evidence": ko["evidence"],
            "linked_objects": ko["linked_objects"],
            "entities": ko.get("entities", []),
            "relations": ko["relations"]
        }).execute()
        
        # Insert edges
        for rel in ko["relations"]:
            supabase.table("graph_edges").upsert({
                "source_urn": ko["urn"],
                "source_version": ko["version"],
                "target_urn": rel["target_urn"],
                "edge_type": rel["edge_type"]
            }).execute()

    # 2. Seed Opinions
    print("\n[*] Seeding Opinions...")
    for op in OPINIONS:
        print(f"  • Publishing Opinion: {op['urn']}")
        supabase.table("knowledge_objects").upsert({
            "urn": op["urn"],
            "version": op["version"],
            "type": op["type"],
            "title": op["title"],
            "summary": op["summary"],
            "confidence_score": op["confidence_score"],
            "source_credibility": op["source_credibility"],
            "forum_published": op["forum_published"],
            "interpretation_stance": op["interpretation_stance"],
            "legal_time_start": op["legal_time_start"],
            "business_impact": op["business_impact"],
            "evidence": op["evidence"],
            "linked_objects": op.get("linked_objects", []),
            "entities": op.get("entities", []),
            "relations": op["relations"]
        }).execute()
        
        # Insert edges
        for rel in op["relations"]:
            supabase.table("graph_edges").upsert({
                "source_urn": op["urn"],
                "source_version": op["version"],
                "target_urn": rel["target_urn"],
                "edge_type": rel["edge_type"]
            }).execute()

    # 3. Seed Events
    print("\n[*] Seeding Regulatory Events...")
    for ev in REGULATORY_EVENTS:
        print(f"  • Publishing Event: {ev['id']}")
        supabase.table("regulatory_events").upsert(ev).execute()

    # 4. Seed Actions
    print("\n[*] Seeding Action Items...")
    for act in ACTION_ITEMS:
        print(f"  • Publishing Action: {act['id']}")
        supabase.table("action_items").upsert(act).execute()

    print("\n[+] Supabase Database Seeding Completed Successfully!")

if __name__ == "__main__":
    seed_supabase()
