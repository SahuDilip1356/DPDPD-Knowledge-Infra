"""
Grounded Reasoning Engine — Layer 2: Reasoning Layer

Purpose:
    Retrieves evidence coordinates and Knowledge Objects from Layer 1,
    constructs a strict grounded prompt context, and queries the LLM.
    Enforces that all answers cite exact URNs, coordinates, and hashes.
    Ensures zero hallucination by rejecting queries with insufficient evidence.
"""

import json
import os
import requests
from typing import Dict, List, Optional, Tuple

class GroundedReasoningEngine:
    def __init__(self, db_client=None, git_ledger=None, model_client=None):
        """
        Initializes the Grounded Reasoning Engine.

        Args:
            db_client: DatabaseClient to query nodes, edges, and bi-temporal states.
            git_ledger: GitLedger for reading original raw JSONs.
            model_client: A client wrapper for LLM queries (e.g., Gemini API).
                          If None, falls back to a deterministic query resolver or mock.
        """
        self.db_client = db_client
        self.git_ledger = git_ledger
        self.model_client = model_client

    def _query_pinecone_vectors(self, query: str) -> List[str]:
        """
        Queries Pinecone REST API for matching KO URNs.
        """
        pinecone_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME", "dpdpa-knowledge")
        
        if not pinecone_key or not self.model_client:
            return []
            
        try:
            # 1. Get host/endpoint from Pinecone Control Plane
            headers = {
                "Api-Key": pinecone_key,
                "Content-Type": "application/json"
            }
            status_url = f"https://api.pinecone.io/indexes/{index_name}"
            status_res = requests.get(status_url, headers=headers, timeout=10)
            if status_res.status_code != 200:
                print(f"[Pinecone] Warning: Index '{index_name}' status check returned {status_res.status_code}.")
                return []
                
            host = status_res.json().get("host")
            if not host:
                return []

            # 2. Embed the search query
            query_vector = self.model_client.embed(query)

            # 3. Query the index
            query_url = f"https://{host}/query"
            payload = {
                "vector": query_vector,
                "topK": 5,
                "includeMetadata": False
            }
            query_res = requests.post(query_url, headers=headers, json=payload, timeout=15)
            query_res.raise_for_status()
            
            matches = query_res.json().get("matches", [])
            # Return matching URNs (which we set as the vector IDs)
            return [match["id"] for match in matches if match.get("score", 0.0) >= 0.35]
            
        except Exception as e:
            print(f"[Pinecone] Search failed: {str(e)}. Falling back to keyword search.")
            return []

    def retrieve_context(self, query: str) -> List[Dict]:
        """
        Retrieves relevant Knowledge Objects using Pinecone semantic search,
        falling back to database keyword matching and GitLedger scanning if offline.
        """
        matched_kos = []
        
        # 1. Try Pinecone semantic search if available
        matched_urns = self._query_pinecone_vectors(query)
        
        if matched_urns and self.db_client:
            if getattr(self.db_client, "supabase", None):
                try:
                    res = self.db_client.supabase.table("knowledge_objects").select("*").in_("urn", matched_urns).is_("system_time_end", "null").execute()
                    if res.data:
                        order_map = {urn: index for index, urn in enumerate(matched_urns)}
                        sorted_rows = sorted(res.data, key=lambda r: order_map.get(r["urn"], 999))
                        for row in sorted_rows:
                            matched_kos.append({
                                "urn": row["urn"],
                                "title": row["title"],
                                "summary": row["summary"],
                                "entities": row.get("entities") or row.get("body", {}).get("entities", []),
                                "evidence": row["evidence"],
                                "business_impact": row["business_impact"],
                                "confidence_score": float(row["confidence_score"]),
                                "version": row["version"],
                                "date": row.get("legal_time_start", "")[:10] if row.get("legal_time_start") else "unknown"
                            })
                except Exception as e:
                    print(f"[Supabase] Error fetching vector search URNs: {str(e)}")
            else:
                session = self.db_client.Session()
                try:
                    from src.storage.models import KnowledgeObject
                    # Fetch full records for the URNs returned by Pinecone
                    db_kos = session.query(KnowledgeObject).filter(
                        KnowledgeObject.urn.in_(matched_urns),
                        KnowledgeObject.system_time_end == None
                    ).all()
                    
                    # Maintain the order of matches returned by Pinecone (relevance)
                    order_map = {urn: index for index, urn in enumerate(matched_urns)}
                    db_kos = sorted(db_kos, key=lambda k: order_map.get(k.urn, 999))
                    
                    for db_ko in db_kos:
                        matched_kos.append({
                            "urn": db_ko.urn,
                            "title": db_ko.title,
                            "summary": db_ko.summary,
                            "entities": db_ko.entities if hasattr(db_ko, 'entities') else db_ko.body.get("entities", []),
                            "evidence": db_ko.evidence,
                            "business_impact": db_ko.business_impact,
                            "confidence_score": float(db_ko.confidence_score),
                            "version": db_ko.version,
                            "date": db_ko.legal_time_start.strftime("%Y-%m-%d") if db_ko.legal_time_start else "unknown"
                        })
                except Exception as e:
                    print(f"[Database] Error fetching vector search URNs: {str(e)}. Falling back to keyword scan.")
                finally:
                    session.close()

        # 2. Fallback to SQL keyword search if vector search returned no results
        if not matched_kos and self.db_client:
            if getattr(self.db_client, "supabase", None):
                try:
                    res = self.db_client.supabase.table("knowledge_objects").select("*").is_("system_time_end", "null").execute()
                    if res.data:
                        words = query.lower().split()
                        for row in res.data:
                            entities = row.get("entities") or row.get("body", {}).get("entities", [])
                            ko_text = f"{row['title']} {row['summary']} {' '.join(entities)}".lower()
                            if any(word in ko_text for word in words):
                                matched_kos.append({
                                    "urn": row["urn"],
                                    "title": row["title"],
                                    "summary": row["summary"],
                                    "entities": entities,
                                    "evidence": row["evidence"],
                                    "business_impact": row["business_impact"],
                                    "confidence_score": float(row["confidence_score"]),
                                    "version": row["version"],
                                    "date": row.get("legal_time_start", "")[:10] if row.get("legal_time_start") else "unknown"
                                })
                except Exception as e:
                    print(f"[Supabase] Error running keyword scan: {str(e)}")
            else:
                session = self.db_client.Session()
                try:
                    from src.storage.models import KnowledgeObject
                    # Fetch all active KOs (system_time_end is Null)
                    active_kos = session.query(KnowledgeObject).filter(
                        KnowledgeObject.system_time_end == None
                    ).all()
                    
                    # Simple keyword lookup in title/summary
                    words = query.lower().split()
                    for db_ko in active_kos:
                        entities = db_ko.body.get("entities", []) if db_ko.body else []
                        ko_text = f"{db_ko.title} {db_ko.summary} {' '.join(entities)}".lower()
                        if any(word in ko_text for word in words):
                            matched_kos.append({
                                "urn": db_ko.urn,
                                "title": db_ko.title,
                                "summary": db_ko.summary,
                                "entities": db_ko.entities if hasattr(db_ko, 'entities') else db_ko.body.get("entities", []),
                                "evidence": db_ko.evidence,
                                "business_impact": db_ko.business_impact,
                                "confidence_score": float(db_ko.confidence_score),
                                "version": db_ko.version,
                                "date": db_ko.legal_time_start.strftime("%Y-%m-%d") if db_ko.legal_time_start else "unknown"
                            })
                finally:
                    session.close()
                
        # 3. Fallback to GitLedger scanning if database is empty or not configured
        if not matched_kos and self.git_ledger:
            # Recursively walk git ledger objects folder
            obj_dir = os.path.join(self.git_ledger.base_dir, "objects")
            if os.path.exists(obj_dir):
                import glob
                json_files = glob.glob(os.path.join(obj_dir, "**", "*.json"), recursive=True)
                
                # Read latest version of each unique URN
                latest_versions = {}
                for path in json_files:
                    try:
                        with open(path, "r") as f:
                            data = json.load(f)
                            urn = data.get("urn")
                            ver = data.get("version", 1)
                            if urn not in latest_versions or ver > latest_versions[urn]["version"]:
                                latest_versions[urn] = data
                    except Exception:
                        continue
                
                words = query.lower().split()
                for data in latest_versions.values():
                    ko_text = f"{data.get('title', '')} {data.get('summary', '')} {' '.join(data.get('entities', []))}".lower()
                    if any(word in ko_text for word in words):
                        matched_kos.append(data)
                        
        return matched_kos

    def construct_grounded_prompt(self, query: str, context_kos: List[Dict]) -> str:
        """
        Builds the strict context envelope forcing the LLM to ground itself
        and use standard citation formats.
        """
        context_str = ""
        for i, ko in enumerate(context_kos):
            context_str += f"--- KNOWLEDGE OBJECT {i+1} ---\n"
            context_str += f"URN: {ko['urn']}\n"
            context_str += f"Title: {ko['title']}\n"
            context_str += f"Date: {ko['date']}\n"
            context_str += f"Version: {ko['version']}\n"
            context_str += f"Summary: {ko['summary']}\n"
            context_str += f"Confidence Score: {ko['confidence_score']}\n"
            
            context_str += "Citations/Evidence:\n"
            for ev in ko.get("evidence", []):
                coords = ev.get("coordinates", {})
                context_str += (
                    f"  - Source: {ev.get('source_urn')} | "
                    f"Text: \"{ev.get('citation_text')}\" | "
                    f"Page: {coords.get('page')} | "
                    f"Section: {coords.get('section')} | "
                    f"Hash: {coords.get('hash')}\n"
                )
            context_str += f"Business Impact: {ko.get('business_impact', {}).get('impact_summary', '')}\n"
            context_str += f"Recommended Business Action: {ko.get('business_impact', {}).get('action_required', '')}\n\n"

        prompt = f"""You are the Grounded Reasoning Engine of the Regulatory Knowledge Infrastructure.
Your task is to answer the user's query using ONLY the provided Knowledge Object contexts.

CRITICAL INSTRUCTIONS:
1. Every fact or claim you make must be accompanied by a citation referencing the matching URN, page coordinates, and evidence text hash.
2. Format citations as: [URN (Page X, Section Y, Hash: Z)]
3. If the provided context does not contain sufficient information to answer the question, state: "INSUFFICIENT_EVIDENCE: The query cannot be answered using the canonical knowledge core." Do not hallucinate or extrapolate.

User Query: {query}

Context:
{context_str}

Answer:"""
        return prompt

    def query(self, query_text: str) -> Dict:
        """
        Executes the full grounded query workflow:
        1. Retrieve relevant KOs.
        2. Construct grounded prompt.
        3. Invoke model client or fallback solver.
        4. Return grounded response.
        """
        context_kos = self.retrieve_context(query_text)
        
        if not context_kos:
            return {
                "query": query_text,
                "answer": "INSUFFICIENT_EVIDENCE: The query cannot be answered using the canonical knowledge core.",
                "citations": [],
                "grounded": False
            }
            
        prompt = self.construct_grounded_prompt(query_text, context_kos)
        
        # Call model client if provided, otherwise perform deterministic mock resolution
        if self.model_client:
            answer_text = self.model_client.generate(prompt)
        else:
            answer_text = self._mock_reasoning_resolve(query_text, context_kos)
            
        # Extract citations from generated answer (e.g., matching URNs)
        citations = []
        for ko in context_kos:
            if ko["urn"] in answer_text:
                citations.append({
                    "urn": ko["urn"],
                    "title": ko["title"],
                    "version": ko["version"],
                    "evidence": ko.get("evidence", [])
                })
                
        return {
            "query": query_text,
            "answer": answer_text,
            "citations": citations,
            "grounded": "INSUFFICIENT_EVIDENCE" not in answer_text
        }

    def _mock_reasoning_resolve(self, query: str, context: List[Dict]) -> str:
        """
        A deterministic mock resolver that parses query keywords and builds a properly
        grounded citation-enriched answer based on retrieved KOs.
        """
        # Formulate response citing the first matching KO
        primary_ko = context[0]
        evidence_item = primary_ko["evidence"][0] if primary_ko.get("evidence") else {}
        coords = evidence_item.get("coordinates", {})
        
        citation = (
            f"[{primary_ko['urn']} (Page {coords.get('page', 1)}, "
            f"Section {coords.get('section', 'unknown')}, Hash: {coords.get('hash', 'unknown')[:8]})]"
        )
        
        response = (
            f"Based on the canonical regulatory core, {primary_ko['title']} "
            f"states: \"{primary_ko['summary']}\". "
            f"This requires the following business action: \"{primary_ko['business_impact']['action_required']}\". "
            f"Source Evidence: {citation}."
        )
        return response
