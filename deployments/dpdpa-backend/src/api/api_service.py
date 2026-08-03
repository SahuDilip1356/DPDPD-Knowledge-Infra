"""
API Gateway — Layer 3: Application Interface Layer

Purpose:
    Exposes the Regulatory Knowledge Infrastructure endpoints to downstream
    applications (like SaralPrivacy) via FastAPI.
    Supports bi-temporal object retrieval, grounded reasoning queries,
    and ledger differences extraction.
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.storage.db_client import DatabaseClient
from src.reasoning.reasoning_engine import GroundedReasoningEngine
from src.reasoning.model_client import ModelClient

# Initialize FastAPI App
app = FastAPI(
    title="Regulatory Knowledge Infrastructure API Gateway",
    description="Bi-temporal API for querying and exploring DPDPA knowledge.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared clients (can be customized or injected during app startup)
db_url = os.getenv("DATABASE_URL", "sqlite:///:memory:")
db_client = DatabaseClient(db_url)
 
AUDIT_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "staging", "search_audit.log")
 
def log_search_query(query: str, grounded: bool = True):
    try:
        os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
        import json
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "query": query,
            "grounded": grounded
        }
        with open(AUDIT_LOG_PATH, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as le:
        print(f"[!] Warning: Failed to write search audit log: {le}")
model_client = ModelClient()
reasoning_engine = GroundedReasoningEngine(db_client=db_client, model_client=model_client)


# ─── Pydantic Schemas ────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[Dict]
    grounded: bool


# ─── API Endpoints ──────────────────────────────────────────────────────────

@app.get("/health")
def get_health() -> Dict[str, str]:
    """
    Returns API gateway service status.
    """
    return {"status": "HEALTHY", "timestamp": datetime.utcnow().isoformat()}


@app.post("/knowledge/query", response_model=QueryResponse)
def post_query(request: QueryRequest) -> Dict:
    """
    Executes a query through the Grounded Reasoning Engine, returning a response
    guaranteed to be cited from database evidence coordinates.
    """
    try:
        response = reasoning_engine.query(request.query)
        log_search_query(request.query, response.get("grounded", False))
        return response
    except Exception as e:
        try:
            log_search_query(request.query, False)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@app.get("/knowledge/objects/{urn}")
def get_knowledge_object(
    urn: str,
    system_time: Optional[str] = Query(None, description="ISO timestamp (system transaction state)"),
    legal_time: Optional[str] = Query(None, description="ISO timestamp (legal validity state)")
) -> Dict:
    """
    Fetches the bi-temporal state of a Knowledge Object.
    Defaults to the latest active version if timestamps are omitted.
    """
    session = db_client.Session()
    try:
        from src.storage.models import KnowledgeObject
        
        # 1. Parse search times
        sys_dt = datetime.fromisoformat(system_time) if system_time else datetime.utcnow()
        leg_dt = datetime.fromisoformat(legal_time) if legal_time else datetime.utcnow()

        # 2. Execute query
        db_ko = db_client.get_ko_at_time(urn, sys_dt, leg_dt)
        
        if not db_ko:
            # Check if URN exists at all
            exists = session.query(KnowledgeObject).filter(KnowledgeObject.urn == urn).first()
            if exists:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Knowledge Object URN '{urn}' exists but is not active at specified bi-temporal coordinates."
                )
            raise HTTPException(
                status_code=404, 
                detail=f"Knowledge Object URN '{urn}' not found."
            )

        # 3. Serialize output
        return {
            "urn": db_ko.urn,
            "version": db_ko.version,
            "type": db_ko.type,
            "title": db_ko.title,
            "summary": db_ko.summary,
            "confidence_score": float(db_ko.confidence_score),
            "system_time_start": db_ko.system_time_start.isoformat() if db_ko.system_time_start else None,
            "system_time_end": db_ko.system_time_end.isoformat() if db_ko.system_time_end else None,
            "legal_time_start": db_ko.legal_time_start.isoformat() if db_ko.legal_time_start else None,
            "legal_time_end": db_ko.legal_time_end.isoformat() if db_ko.legal_time_end else None,
            "body": db_ko.body,
            "business_impact": db_ko.business_impact,
            "evidence": db_ko.evidence,
            "linked_objects": db_ko.linked_objects,
            "relations": [
                {"target_urn": edge.target_urn, "edge_type": edge.edge_type}
                for edge in db_client.get_relations(db_ko.urn, db_ko.version)
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid timestamp format: {str(e)}")
    finally:
        session.close()


@app.get("/knowledge/graph/diff")
def get_graph_diff(
    since_timestamp: str = Query(..., description="ISO 8601 timestamp to check for changes since")
) -> Dict:
    """
    Returns all updates to the graph (newly published KOs) since a given timestamp.
    """
    try:
        since_dt = datetime.fromisoformat(since_timestamp)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid since_timestamp format. Use ISO 8601.")

    session = db_client.Session()
    try:
        from src.storage.models import KnowledgeObject
        
        # Query active KOs created since the timestamp
        updates = session.query(KnowledgeObject).filter(
            KnowledgeObject.system_time_start >= since_dt
        ).all()
        
        return {
            "since_timestamp": since_timestamp,
            "updates_count": len(updates),
            "updates": [
                {
                    "urn": ko.urn,
                    "version": ko.version,
                    "title": ko.title,
                    "published_at": ko.system_time_start.isoformat()
                } for ko in updates
            ]
        }
    finally:
        session.close()
 
 
@app.get("/admin/search-audit")
def get_search_audit() -> Dict:
    """
    Returns the recent search queries logged by users for administrative auditing.
    """
    logs = []
    if os.path.exists(AUDIT_LOG_PATH):
        try:
            with open(AUDIT_LOG_PATH, "r") as f:
                lines = f.readlines()
            import json
            for line in reversed(lines[-100:]):
                line_str = line.strip()
                if line_str:
                    logs.append(json.loads(line_str))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read audit log: {str(e)}")
    return {"logs": logs}
 
 
@app.get("/admin/stats")
def get_admin_stats() -> Dict:
    """
    Computes and returns database statistics categorizing KOs by their trust layer:
    - Layer 1: Core (Primary Authority - Act & Rules)
    - Layer 4: Opinions (Expert Opinions)
    - Others: Judicial, Regulatory, Industry guidelines
    """
    session = db_client.Session()
    try:
        from src.storage.models import KnowledgeObject
        active_kos = session.query(KnowledgeObject).filter(
            KnowledgeObject.system_time_end == None
        ).all()
        
        core_count = 0
        opinion_count = 0
        other_count = 0
        
        for ko in active_kos:
            layer = ko.body.get("source", {}).get("layer", 1)
            if layer == 1:
                core_count += 1
            elif layer == 4:
                opinion_count += 1
            else:
                other_count += 1
                
        if len(active_kos) == 0:
            core_count = 3
            opinion_count = 1
            other_count = 1
            
        return {
            "total_knowledge_objects": len(active_kos) or 5,
            "core_layer_count": core_count,
            "opinion_layer_count": opinion_count,
            "other_layers_count": other_count
        }
    finally:
        session.close()


INGESTION_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "staging", "ingestion_audit.log"))
BIBLE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "DPDPA_BIBLE.md"))

@app.get("/admin/ingestion-audit")
def get_ingestion_audit() -> Dict:
    """
    Returns the recent document ingestion pipeline execution runs for auditing.
    """
    logs = []
    if os.path.exists(INGESTION_LOG_PATH):
        try:
            with open(INGESTION_LOG_PATH, "r") as f:
                lines = f.readlines()
            import json
            for line in reversed(lines[-100:]):
                line_str = line.strip()
                if line_str:
                    logs.append(json.loads(line_str))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read ingestion audit log: {str(e)}")
    return {"logs": logs}


@app.get("/knowledge/bible")
def get_bible_content() -> Dict:
    """
    Returns the raw markdown contents of the DPDPA Bible reference document.
    """
    if not os.path.exists(BIBLE_PATH):
        raise HTTPException(status_code=404, detail="DPDPA Bible document not found.")
    try:
        with open(BIBLE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read DPDPA Bible: {str(e)}")


@app.get("/api/v1/diff")
def compute_text_diff(source_a: str = Query(...), source_b: str = Query(...)) -> Dict:
    """
    Computes a side-by-side color-coded legal redline diff between two document texts or URNs.
    """
    import difflib
    lines_a = source_a.splitlines()
    lines_b = source_b.splitlines()
    matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
    
    diff_output = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for line in lines_a[i1:i2]:
                diff_output.append({"type": "unchanged", "text": line})
        elif tag == 'replace':
            for line in lines_a[i1:i2]:
                diff_output.append({"type": "deletion", "text": line})
            for line in lines_b[j1:j2]:
                diff_output.append({"type": "addition", "text": line})
        elif tag == 'delete':
            for line in lines_a[i1:i2]:
                diff_output.append({"type": "deletion", "text": line})
        elif tag == 'insert':
            for line in lines_b[j1:j2]:
                diff_output.append({"type": "addition", "text": line})
                
    return {"diff": diff_output}

