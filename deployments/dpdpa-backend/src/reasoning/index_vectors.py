#!/usr/bin/env python3
"""
Pinecone Vector Indexing Script
================================
Fetches all active Knowledge Objects from Supabase, generates embeddings,
and upserts them into a Pinecone vector index.
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

# Add project root to python path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.storage.db_client import DatabaseClient
from src.reasoning.model_client import ModelClient

load_dotenv()

def get_pinecone_headers():
    key = os.getenv("PINECONE_API_KEY")
    if not key:
        raise ValueError("PINECONE_API_KEY is missing from environment/env.")
    return {
        "Api-Key": key,
        "Content-Type": "application/json"
    }

def get_index_host(index_name):
    url = f"https://api.pinecone.io/indexes/{index_name}"
    try:
        response = requests.get(url, headers=get_pinecone_headers(), timeout=15)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json().get("host")
    except Exception as e:
        print(f"[Pinecone] Error getting index status: {str(e)}")
        return None

def create_index(index_name, dimension):
    url = "https://api.pinecone.io/indexes"
    payload = {
        "name": index_name,
        "dimension": dimension,
        "metric": "cosine",
        "spec": {
            "serverless": {
                "cloud": "aws",
                "region": "us-east-1"
            }
        }
    }
    print(f"[Pinecone] Creating serverless index '{index_name}' (dimension={dimension})...")
    try:
        response = requests.post(url, headers=get_pinecone_headers(), json=payload, timeout=20)
        response.raise_for_status()
        print(f"[Pinecone] Index creation request successful. Waiting for initialization...")
        # Poll until host is ready
        for _ in range(12):
            time.sleep(5)
            host = get_index_host(index_name)
            if host:
                print(f"[Pinecone] Index ready! Host: {host}")
                return host
        raise RuntimeError("Timeout waiting for Pinecone index initialization.")
    except Exception as e:
        raise RuntimeError(f"Failed to create Pinecone index: {str(e)}")

def fetch_active_kos(db_client):
    """
    Returns active Knowledge Objects as plain dicts.

    Prefers the Supabase REST client — that is how the reasoning engine and the
    frontends read data, so indexing stays consistent with query time and needs
    no direct Postgres credentials. Falls back to SQLAlchemy when DATABASE_URL
    is configured.
    """
    if getattr(db_client, "supabase", None):
        res = (
            db_client.supabase.table("knowledge_objects")
            .select("*")
            .is_("system_time_end", "null")
            .execute()
        )
        rows = res.data or []
        return [
            {
                "urn": r.get("urn"),
                "title": r.get("title") or "",
                "type": r.get("type") or "",
                "version": r.get("version") or 1,
                "summary": r.get("summary") or "",
                "entities": (r.get("entities") or (r.get("body") or {}).get("entities") or []),
            }
            for r in rows
        ]

    from src.storage.models import KnowledgeObject
    session = db_client.Session()
    try:
        kos = session.query(KnowledgeObject).filter(
            KnowledgeObject.system_time_end == None  # noqa: E711
        ).all()
        return [
            {
                "urn": ko.urn,
                "title": ko.title or "",
                "type": ko.type or "",
                "version": ko.version or 1,
                "summary": ko.summary or "",
                "entities": (ko.body or {}).get("entities", []),
            }
            for ko in kos
        ]
    finally:
        session.close()


def main():
    # DATABASE_URL is optional — without it the Supabase client is used, which
    # only needs SUPABASE_URL + SUPABASE_SERVICE_KEY.
    db_url = os.getenv("DATABASE_URL") or "sqlite:///:memory:"

    index_name = os.getenv("PINECONE_INDEX_NAME", "dpdpa-knowledge")

    print("[*] Initializing Database & Model Clients...")
    db_client = DatabaseClient(db_url)
    model_client = ModelClient()

    if not getattr(db_client, "supabase", None) and not os.getenv("DATABASE_URL"):
        print("[!] ERROR: Need either SUPABASE_URL + SUPABASE_SERVICE_KEY, or DATABASE_URL.")
        sys.exit(1)
    
    # 1. Determine dimension
    # Gemini (text-embedding-004) has 768 dimensions. OpenAI (text-embedding-3-small) has 1536.
    dimension = 768 if model_client.gemini_key else 1536
    
    # 2. Get/Create Pinecone Index
    try:
        host = get_index_host(index_name)
        if not host:
            host = create_index(index_name, dimension)
    except Exception as e:
        print(f"[!] Pinecone Configuration Error: {str(e)}")
        sys.exit(1)
        
    # 3. Fetch Knowledge Objects from Supabase
    print("[*] Fetching active Knowledge Objects from Supabase...")
    try:
        active_kos = fetch_active_kos(db_client)

        print(f"[+] Found {len(active_kos)} active Knowledge Objects.")
        if not active_kos:
            print("[*] No active Knowledge Objects to index.")
            return

        # 4. Generate embeddings and upsert
        vectors = []
        for i, ko in enumerate(active_kos, 1):
            entities_str = ", ".join(ko["entities"]) if ko["entities"] else ""
            text_to_embed = (
                f"Title: {ko['title']}. Type: {ko['type']}. "
                f"Summary: {ko['summary']}. Entities: {entities_str}"
            )

            print(f"  [{i}/{len(active_kos)}] Embedding KO: {ko['title'][:60]}...")
            try:
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
            except Exception as e:
                print(f"  [!] Failed to embed '{ko['urn']}': {str(e)}")
                continue
                
        # Batch upload to Pinecone
        if vectors:
            upsert_url = f"https://{host}/vectors/upsert"
            payload = {"vectors": vectors}
            print(f"[*] Upserting {len(vectors)} vectors to Pinecone index '{index_name}'...")
            response = requests.post(upsert_url, headers=get_pinecone_headers(), json=payload, timeout=30)
            response.raise_for_status()
            print("[+] Pinecone indexing operation completed successfully!")

    except Exception as e:
        print(f"[!] Indexing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
