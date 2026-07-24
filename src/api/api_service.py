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
from pydantic import BaseModel

from src.storage.db_client import DatabaseClient
from src.reasoning.reasoning_engine import GroundedReasoningEngine

# Initialize FastAPI App
app = FastAPI(
    title="Regulatory Knowledge Infrastructure API Gateway",
    description="Bi-temporal API for querying and exploring DPDPA knowledge.",
    version="1.0.0"
)

# Shared clients (can be customized or injected during app startup)
db_url = os.getenv("DATABASE_URL", "sqlite:///:memory:")
db_client = DatabaseClient(db_url)
reasoning_engine = GroundedReasoningEngine(db_client=db_client)


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
        return response
    except Exception as e:
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
