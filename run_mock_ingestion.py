#!/usr/bin/env python3
"""
Mock Ingestion Pipeline Runner

Demonstrates the continuous learning flywheel of the Research Ingestion Factory:
1. Scout HTML feed for new regulatory signals (PDFs).
2. Download and parse raw documents (simulated PDF parsing).
3. Execute the Factory Orchestrator pipeline across Ontology, Relationships, 
   Deduplication, Reasoning (detecting Split Opinions), Business Translation, and Publishing.
"""

import os
import sys
import shutil
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.factory.factory_orchestrator import FactoryOrchestrator
from src.storage.db_client import DatabaseClient
from src.storage.git_ledger import GitLedger

def setup_mock_environment():
    """Sets up temp folders for staging and ledger."""
    staging_dir = os.path.abspath("staging/inbox")
    ledger_dir = os.path.abspath("staging/temp_ledger")
    
    os.makedirs(staging_dir, exist_ok=True)
    if os.path.exists(ledger_dir):
        shutil.rmtree(ledger_dir)
    os.makedirs(ledger_dir, exist_ok=True)
    
    return staging_dir, ledger_dir

def run_pipeline_demo():
    print("═" * 70)
    print("   🚀 STARTING DPDPA RESEARCH FACTORY MOCK INGESTION PIPELINE")
    print("═" * 70)
    
    # Step 1: Environment Setup
    staging_dir, ledger_dir = setup_mock_environment()
    print(f"[*] Staging Inbox: {staging_dir}")
    print(f"[*] Git Ledger Dir: {ledger_dir}")
    
    # Initialize Core Infrastructure Clients
    git_ledger = GitLedger(ledger_dir)
    db_client = DatabaseClient("sqlite:///:memory:") # In-memory DB for demo
    orchestrator = FactoryOrchestrator(git_ledger=git_ledger, db_client=db_client)
    
    # Step 2: Scout (Department 1)
    print("\n[Stage 1: Scout] Scanning MeitY feed index for new PDF links...")
    mock_feed_html = """
    <html>
      <body>
        <h1>MeitY Gazettes & Notifications</h1>
        <table>
          <tr>
            <td>25-07-2026</td>
            <td><a href="https://mock.meity.gov.in/G.S.R_102_E_25_07_2026.pdf">DPDP Consent Manager Registration & net worth rules</a></td>
          </tr>
        </table>
      </body>
    </html>
    """
    signals = orchestrator.scout.scout_feed(mock_feed_html, source_layer=3)
    print(f"  └─ Found {len(signals)} regulatory signal(s) in feed:")
    for sig in signals:
        print(f"     • URN Signal: {sig['scraped_title']} | Date: {sig['scraped_date']} | URL: {sig['source_url']}")
    
    # Step 3: Download & Parse (Department 2 & 3)
    signal = signals[0]
    print(f"\n[Stage 2: Ingestion] Downloading document: {signal['source_url']}...")
    local_path = orchestrator.scout.download_document(signal["source_url"])
    print(f"  └─ Saved to: {local_path}")
    
    print("\n[Stage 3: Parsing] Extracting structured pages & paragraphs...")
    parsed_pages = orchestrator.parser.parse_pdf(local_path)
    print(f"  └─ Extracted {len(parsed_pages)} page(s). Content:")
    for page in parsed_pages:
        print(f"     Page {page['page_num']}: {page['paragraphs']}")

    # Step 4: Synthesize Draft KOs (Simulated output of Parsing/Extraction)
    print("\n[Stage 4: Knowledge Synthesis] Creating draft Knowledge Objects...")
    
    # Draft 1: The Core Rule discovered
    draft_rule_ko = {
        "urn": "urn:ki:in:dpdp:rule:consent-manager-net-worth",
        "type": "Rule",
        "title": "DPDP Rules 2025 — Rule 14: Consent Manager Net Worth Requirements",
        "source": {
            "name": "DPDP Rules Gazette Notification",
            "layer": 3,
            "url": signal["source_url"],
            "hash": "d" * 64
        },
        "date": signal["scraped_date"],
        "version": 1,
        "summary": "Every registered Consent Manager shall maintain a net worth of not less than two crore rupees and operate an interoperable digital platform enabling data principals to manage consent.",
        "entities": ["Rule", "Consent", "Organization"],
        "evidence": [
            {
                "source_urn": "urn:ki:in:dpdp:source:gazette-rules-2025",
                "citation_text": "Every registered Consent Manager shall maintain a net worth of not less than two crore rupees.",
                "coordinates": {
                    "page": 15,
                    "section": "Rule 14(1)",
                    "hash": "d" * 64
                }
            }
        ],
        "business_impact": {
            "impact_summary": "Establishes capital thresholds for companies wishing to register as Consent Managers.",
            "action_required": "Ensure audit certificate of Rs 2 crore net worth is submitted before registration."
        },
        "confidence_score": 0.70, # Layer 3 = 0.70
        "relations": [
            {
                "target_urn": "urn:ki:in:dpdp:act:dpdpa-2023",
                "edge_type": "Implements"
            }
        ],
        "linked_objects": ["urn:ki:in:dpdp:act:dpdpa-2023"],
        "history": [
            {
                "version": 1,
                "system_time": datetime.utcnow().isoformat() + "Z",
                "commit_message": "Ingested Rule 14 details from MeitY notification.",
                "author_id": "scout_agent_v1"
            }
        ]
    }

    # Draft 2: Trilegal Opinion on this Rule
    draft_opinion_trilegal = {
        "urn": "urn:ki:in:dpdp:opinion:trilegal:consent-manager-networth",
        "type": "Opinion",
        "title": "Trilegal Insight: The 2 Crore Bar for Consent Managers",
        "source": {
            "name": "Trilegal Publications",
            "layer": 4,
            "url": "https://trilegal.com/networth.pdf",
            "hash": "e" * 64
        },
        "date": "2026-07-26",
        "version": 1,
        "summary": "Commentary on Rule 14. Argues the ₹2 crore threshold is reasonable to filter out shell companies and ensure secure data architecture.",
        "entities": ["Rule", "Organization"],
        "source_credibility": "tier-1",
        "forum_published": "Trilegal Regulatory Briefings",
        "interpretation_stance": "exegesis",
        "evidence: ": [
            {
                "source_urn": "urn:ki:in:dpdp:source:trilegal-briefing",
                "citation_text": "The 2 crore bar acts as a crucial safety filter to prevent under-capitalized entities from handling critical public consent pipelines.",
                "coordinates": {
                    "page": 1,
                    "section": "Capital Constraints",
                    "hash": "e" * 64
                }
            }
        ],
        "business_impact": {
            "impact_summary": "Supports capital guidelines for Consent Managers.",
            "action_required": "Prepare financial backing documents confirming ₹2 crore liquidity."
        },
        "confidence_score": 0.50, # Layer 4 = 0.50
        "relations": [
            {
                "target_urn": "urn:ki:in:dpdp:rule:consent-manager-net-worth",
                "edge_type": "Interprets"
            }
        ],
        "linked_objects": ["urn:ki:in:dpdp:rule:consent-manager-net-worth"],
        "history": [
            {
                "version": 1,
                "system_time": datetime.utcnow().isoformat() + "Z",
                "commit_message": "Ingested Trilegal regulatory briefing on net worth.",
                "author_id": "scout_agent_v1"
            }
        ]
    }

    # Draft 3: NASSCOM Opinion expressing alternative view (split opinion!)
    draft_opinion_nasscom = {
        "urn": "urn:ki:in:dpdp:opinion:nasscom:consent-manager-barrier",
        "type": "Opinion",
        "title": "NASSCOM Position: High Capital Barriers Exclude Startups",
        "source": {
            "name": "NASSCOM Submissions",
            "layer": 4,
            "url": "https://nasscom.in/capital.pdf",
            "hash": "f" * 64
        },
        "date": "2026-07-26",
        "version": 1,
        "summary": "Commentary arguing that the ₹2 crore capital requirement represents an entry barrier for grassroots fintech startups, suggesting alternative tiered net worth requirements.",
        "entities": ["Rule", "Organization"],
        "source_credibility": "tier-1",
        "forum_published": "NASSCOM Policy Forum",
        "interpretation_stance": "critique",
        "evidence": [
            {
                "source_urn": "urn:ki:in:dpdp:source:nasscom-capital-paper",
                "citation_text": "A rigid 2 crore net worth rule excludes bootstrap startups from participating in the consent broker ecosystem, slowing down privacy innovation.",
                "coordinates": {
                    "page": 2,
                    "section": "SME Impact",
                    "hash": "f" * 64
                }
            }
        ],
        "business_impact": {
            "impact_summary": "Identifies compliance friction and market barriers for smaller players.",
            "action_required": "Submit policy suggestions advocating for tier-based capitalization levels."
        },
        "confidence_score": 0.50, # Layer 4 = 0.50
        "relations": [
            {
                "target_urn": "urn:ki:in:dpdp:rule:consent-manager-net-worth",
                "edge_type": "Interprets"
            }
        ],
        "linked_objects": ["urn:ki:in:dpdp:rule:consent-manager-net-worth"],
        "history": [
            {
                "version": 1,
                "system_time": datetime.utcnow().isoformat() + "Z",
                "commit_message": "Ingested NASSCOM advisory advocating tiered capital rules.",
                "author_id": "scout_agent_v1"
            }
        ]
    }

    draft_kos = [draft_rule_ko, draft_opinion_trilegal, draft_opinion_nasscom]
    
    # Step 5: Execute Factory Orchestration (Departments 4 to 8)
    print("\n[Stage 5: Factory Pipeline] Executing orchestrator cycle...")
    pipeline_report = orchestrator.run_pipeline(
        ko_list=draft_kos,
        expected_entities=["Rule", "Consent", "Organization", "Case"],
        edge_confidence=0.50
    )
    
    # Step 6: Print Exec Report
    print("\n" + "═" * 70)
    print("   📊 PIPELINE EXECUTION REPORT SUMMARY")
    print("═" * 70)
    print(f"Pipeline ID   : {pipeline_report['pipeline_id']}")
    print(f"Duration      : {pipeline_report['total_duration_ms']:.2f} ms")
    print(f"Ingested KOs  : {pipeline_report['ko_count']}")
    
    print("\n[+] Stage Results:")
    for stage_name, res in pipeline_report["stages"].items():
        status = res.get("status", "UNKNOWN")
        duration = res.get("duration_ms", 0.0)
        print(f"  • {stage_name.capitalize().ljust(22)}: {status} ({duration:.1f} ms)")
        if stage_name == "relationships":
            print(f"    - Confirmed Edges : {res.get('confirmed_count')}")
        if stage_name == "publishing":
            print(f"    - Published KOs   : {res.get('published')}")
            
    print("\n[+] Reasoning Department Insights:")
    insights = pipeline_report["insights"]["insights"]
    print(f"  Total Insights Generated: {pipeline_report['insights']['total_insights']}")
    for ins in insights:
        print(f"  • [{ins['type']}] (Severity: {ins.get('severity', 'INFO')})")
        print(f"    Description: {ins['description']}")

    print("\n[+] Business Translation Actions Created:")
    actions = pipeline_report["business_actions"]["actions"]
    for act in actions:
        print(f"  • Action Category: {act['obligation_category']} (Priority: {act['priority']})")
        print(f"    Parent URN     : {act['urn']} ({act['ko_title']})")
        print(f"    Control/Task   : {act['action_description']}")

    print("\n[+] Git Ledger Commit History:")
    commits = os.listdir(os.path.join(ledger_dir, "objects", "in", "dpdp"))
    for category in commits:
        cat_path = os.path.join(ledger_dir, "objects", "in", "dpdp", category)
        if os.path.isdir(cat_path):
            for item in os.listdir(cat_path):
                print(f"  • Committed: objects/in/dpdp/{category}/{item}")

    print("\n" + "═" * 70)
    print("   ✅ INGESTION PIPELINE RUN COMPLETED SUCCESSFULLY")
    print("═" * 70)

if __name__ == "__main__":
    run_pipeline_demo()
