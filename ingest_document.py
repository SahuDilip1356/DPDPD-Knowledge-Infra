#!/usr/bin/env python3
"""
DPDPA Research Factory Ingestion CLI Tool
===========================================
Scouts, downloads, parses, structures, orchestrates, and indexes any regulatory document PDF/URL
directly into the live Supabase and Pinecone databases.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Ensure local imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.storage.db_client import DatabaseClient
from src.storage.git_ledger import GitLedger
from src.reasoning.model_client import ModelClient
from src.factory.factory_orchestrator import FactoryOrchestrator
from src.factory.structuring_agent import StructuringAgent

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Ingest regulatory documents into DPDPA Knowledge Graph.")
    parser.add_argument("source_url", help="URL or local path to the regulatory PDF/document.")
    parser.add_argument("--urn", required=True, help="Canonical source URN (e.g. urn:ki:in:dpdp:source:gazette-rule-xyz)")
    parser.add_argument("--layer", type=int, default=1, help="Trust Layer of the source (1=Primary, 2=Courts, 3=Regulator, etc.)")
    parser.add_argument("--ledger-dir", default="staging/temp_ledger", help="Path to temp Git Ledger.")
    args = parser.parse_args()

    # Load environmental credentials
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("[!] ERROR: DATABASE_URL is missing from environment/env.")
        sys.exit(1)

    print("\n" + "═" * 70)
    print("   📥 RUNNING DPDPA RESEARCH INGESTION FACTORY")
    print("═" * 70)

    # Initialize Core Infrastructure Clients
    git_ledger = GitLedger(os.path.abspath(args.ledger_dir))
    db_client = DatabaseClient(db_url)
    model_client = ModelClient()
    
    # Initialize Orchestrator
    orchestrator = FactoryOrchestrator(git_ledger=git_ledger, db_client=db_client)
    structurer = StructuringAgent(model_client=model_client)

    # 1. Scout & Collection (Dept 1)
    print(f"\n[*] Stage 1: Scouting & downloading '{args.source_url}'...")
    try:
        local_path = orchestrator.scout.download_document(args.source_url)
        print(f"[+] Downloaded successfully to: {local_path}")
    except Exception as e:
        print(f"[!] Error downloading document: {e}")
        sys.exit(1)

    # 2. Parsing & Chunking (Dept 3)
    print(f"\n[*] Stage 2: Parsing PDF layout...")
    try:
        parsed_pages = orchestrator.parser.parse_pdf(local_path)
        print(f"[+] Parsed {len(parsed_pages)} pages.")
    except Exception as e:
        print(f"[!] Error parsing PDF: {e}")
        sys.exit(1)

    # 3. Citation & Evidence Coordinates (Dept 2)
    print(f"\n[*] Stage 3: Generating bitemporal evidence packets (SHA-256 coordinates)...")
    evidence_packet = orchestrator.process_evidence_packet(
        source_urn=args.urn,
        source_layer=args.layer,
        parsed_pages=parsed_pages
    )
    print(f"[+] Created {len(evidence_packet['chunks'])} evidence coordinate chunks.")

    # 4. LLM Structuring & Extraction
    print(f"\n[*] Stage 4: AI structuring of raw paragraphs into Knowledge Objects...")
    draft_kos = structurer.structure_document(
        filename=os.path.basename(local_path),
        source_urn=args.urn,
        source_layer=args.layer,
        evidence_packet=evidence_packet
    )
    if not draft_kos:
        print("[!] No draft Knowledge Objects were structured. Aborting Ingestion.")
        sys.exit(1)

    # 5. Core Factory Orchestrator Run (Depts 4-8)
    print(f"\n[*] Stage 5: Executing relationship engineering, bitemporal checks, and publishing...")
    report = orchestrator.run_pipeline(
        ko_list=draft_kos,
        expected_entities=["Data Fiduciary", "Data Principal", "Consent"],
        edge_confidence=0.5
    )

    # Print summary report
    print("\n" + "═" * 70)
    print("   📊 INGESTION PIPELINE EXECUTION SUMMARY")
    print("═" * 70)
    print(f"• Knowledge Objects Input:      {report.get('ko_count', 0)}")
    print(f"• Knowledge Objects Published:  {report['stages']['publishing'].get('published', 0) if 'publishing' in report['stages'] else 0}")
    print(f"• Confirmed Graph Edges:        {report['stages']['relationships'].get('confirmed_count', 0)}")
    print(f"• Duplicate Merges Proposed:   {report['stages']['deduplication'].get('duplicates_found', 0)}")
    print(f"• Grounded Reasoning Conflicts: {len(report['insights'].get('conflicts', []))}")
    print(f"• Status:                        SUCCESS ✅")
    print("═" * 70)

    # 6. Pinecone Semantic Vector Indexing
    print("\n[*] Stage 6: Semantic Vector Indexing in Pinecone...")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "dpdpa-knowledge")
    
    if not pinecone_key:
        print("[!] Warning: PINECONE_API_KEY missing. Skipping vector search indexing.")
        return

    # Call Pinecone REST API to index
    from src.reasoning.index_vectors import get_index_host
    try:
        host = get_index_host(index_name)
        if not host:
            print(f"[!] Pinecone index '{index_name}' not found. Cannot index vectors.")
            return

        import requests
        headers = {
            "Api-Key": pinecone_key,
            "Content-Type": "application/json"
        }
        upsert_url = f"https://{host}/vectors/upsert"
        
        vectors = []
        for ko in draft_kos:
            entities_str = ", ".join(ko.get("entities", []))
            text_to_embed = f"Title: {ko['title']}. Type: {ko['type']}. Summary: {ko['summary']}. Entities: {entities_str}"
            embedding = model_client.embed(text_to_embed)
            vectors.append({
                "id": ko["urn"],
                "values": embedding,
                "metadata": {
                    "title": ko["title"],
                    "type": ko["type"],
                    "version": ko["version"],
                    "summary": ko["summary"]
                }
            })
            
        if vectors:
            payload = {"vectors": vectors}
            res = requests.post(upsert_url, headers=headers, json=payload, timeout=20)
            res.raise_for_status()
            print(f"[+] Successfully indexed {len(vectors)} vectors in Pinecone index '{index_name}'!")
            
    except Exception as ex:
        print(f"[!] Pinecone indexing failed: {ex}")

if __name__ == "__main__":
    main()
